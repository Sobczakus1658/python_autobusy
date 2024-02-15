import os
import csv
from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def load_stops_coordinates(file_path):
    stops_coordinates = defaultdict(list)
    with open(file_path, 'r', encoding='utf-8') as stops_file:
        stops_reader = csv.DictReader(stops_file)
        for stop in stops_reader:
            stop_id = stop['Wartosc_zespolu']
            first = round(float(stop['Szer_geo']), 4)
            second = round(float(stop['Dlug_geo']), 4)
            coordinates = (first, second)
            stops_coordinates[coordinates].append(stop_id)

    return stops_coordinates


# Sprawdź, czy dany autobus jest na przystanku
def find_matching_stops(bus_coordinates, stops_coordinates):
    matching_stops = []
    for stop_coordinates, stop_ids in stops_coordinates.items():
        if stop_coordinates == bus_coordinates:
            matching_stops.extend(stop_ids)

    return matching_stops


# Sprawdź czy dany autobus był na przystanku. Uznajemy, że
# autobus znjaduje się na przystanku, gdy zgadzają się
# pierwsze cztery cyfry znaczące
def process_bus_files(bus_folder, stops_coord):
    result = defaultdict(list)
    for bus_file in os.listdir(bus_folder):
        if bus_file.endswith('.csv'):
            bus_id = os.path.splitext(bus_file)[0]
            bus_file_path = os.path.join(bus_folder, bus_file)

            with open(bus_file_path, 'r', encoding='utf-8') as bus_csv:
                bus_reader = csv.DictReader(bus_csv)
                for row in bus_reader:
                    first = round(float(row['Lat']), 4)
                    second = round(float(row['Lon']), 4)
                    bus_coord = (first, second)
                    match_stops = find_matching_stops(bus_coord, stops_coord)
                    if match_stops:
                        time_str = row['Time']
                        line = row['Lines']
                        format_t = "%Y-%m-%d %H:%M:%S"
                        time_obj = datetime.strptime(time_str, format_t)
                        result[bus_id].append((time_obj, match_stops, line))
    return result


# Możemy mieć sytuację gdzie autobus przez jakiś czas stał na przystanku.
# Wtedy chciałbym wziąć czas najwcześniejszy, ponieważ ten czas będzie
# najbardziej rzetelny do opóźnienia. Wszystkie czasy do 2 minut
# od pierwszego pojawienia się na przystanku pomijam.
def filter_matching_stops(matching_results):
    filtered_list = []

    for bus_id, stop_info_list in matching_results.items():
        stop_info_list.sort()

        prev_time = None
        prev_stop = None

        for time_obj, matching_stops, line in stop_info_list:
            curr_time = time_obj
            stops = list(set(matching_stops))
            if len(stop_info_list) > 1 and prev_time:
                if curr_time - prev_time < timedelta(minutes=2):
                    if prev_stop == stops[0]:
                        continue
                    else:
                        filtered_list.append((bus_id, line, curr_time, stops))
                else:
                    filtered_list.append((bus_id, line, curr_time, stops))
            else:
                filtered_list.append((bus_id, line, curr_time, stops))
            prev_time = curr_time
            prev_stop = stops[0]
    return filtered_list


# Sprawdzamy o ile się spóźnił jaki autobus oraz jaką linią on jeździ
def on_the_time(filtered_list, folder_path, save_path, output_filename):
    bus_id_late = []
    # line_late_file = os.path.join(folder_path, output_path)
    for bus_id, line, time_obj, matching_stops in filtered_list:
        id_stopbus = matching_stops[0]
        time_string = time_obj.strftime("%H:%M")
        csv_file_name = f"{id_stopbus}.csv"
        path = os.path.join(folder_path, csv_file_name)
        # będziemy godziny w rozkładzie, która jest najbliższa naszej.
        # Zakładam tutaj, że opóźnienia nie są gigantyczne
        # i tyczą się najbliższej godziny
        min_hours = 24
        min_minutes = 60
        if os.path.isfile(path):
            # Otwórz rozkład dla danego przystanku
            with open(path, 'r', newline='', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    line_csv = row[2]
                    # Sprawdzamy wyłącznie moją linie
                    if line_csv == line:

                        # Pomijamy wiersz, jeśli czas
                        # nie jest w poprawnym formacie
                        try:
                            row_time = datetime.strptime(row[-1], "%H:%M:%S")
                        except ValueError:
                            continue
                        time_obj = datetime.strptime(time_string, "%H:%M")
                        if time_obj < row_time:
                            continue
                        time_diff = abs(time_obj - row_time).total_seconds()

                        hours = time_diff % 86400 // 3600
                        minutes = (time_diff % 3600) // 60
                        if hours < min_hours:
                            min_hours = hours
                            min_minutes = minutes
                        elif hours == min_hours and min_minutes > minutes:
                            min_minutes = minutes
                            min_hours = hours
        if min_hours != 24:
            bus_id_late.append((line, min_hours * 60 + min_minutes))
    output_path = os.path.join(save_path, output_filename)
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Line', 'Minutes_Late'])
        csvwriter.writerows(bus_id_late)


# Tworzymy wykres, ile razy opóźniła się dana linia. Na wykresie late_tolerance
# znaczy do ilu minut tolerujemy spóźnienia. Min_delay_count znaczy że dana
# linia musiała się spóźnić tyle razy, aby zostala uwzględniona na wykresie.
# Jeżeli jakiś autobus jest od samego początku opóźniony bardzo dużo,
# to będzie tutaj policzony kilka razy.
def create_statistic(file_path, late_tolerance, min_delay_count, name):
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        data = [(line, float(delay)) for line, delay in csvreader]

    lines_delay_count = {}
    for line, delay_minutes in data:
        # Jeżeli opóźnienie jest większe niż dopuszczalne opóźnienie,
        # zapamiętujemy linię
        if delay_minutes > late_tolerance:
            if line not in lines_delay_count:
                lines_delay_count[line] = 1
            else:
                lines_delay_count[line] += 1

    selected_lines = {}
    for line, count in lines_delay_count.items():
        if count >= min_delay_count:
            selected_lines[line] = count
    output_folder = "myData"
    output_path = os.path.join(output_folder, name)

    plt.figure(figsize=(10, 6))
    plt.bar(selected_lines.keys(), selected_lines.values(), color='skyblue')
    plt.xlabel('Linia autobusu', fontsize=12)
    plt.ylabel('Liczba opóźnień', fontsize=12)
    plt.title('Liczba opóźnień dla każdej linii autobusowej', fontsize=14)
    plt.xticks(rotation=90, fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=1000)


# Funkcja ta odpowiada za stworzenie listy lini autobusów
# ile się spóźniły na przystanek
def punctuality():
    bus_folder = 'autobuses'
    file_path = 'bus_stations/bus_stations.csv'
    stops_coordinates = load_stops_coordinates(file_path)
    matching_results = process_bus_files(bus_folder, stops_coordinates)
    filtered_list = filter_matching_stops(matching_results)
    folder_path = "schedule"
    output_path = "myData"
    output = "line_late.csv"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    on_the_time(filtered_list, folder_path, output_path, output)


# Funkcja ta tworzy wykresy w zależności od parametrów
def statistic_punctuality(late_tolerance, min_delay_count):
    name = "punctualityBuses.png"
    file_path = "myData/line_late.csv"
    create_statistic(file_path, late_tolerance, min_delay_count, name)
