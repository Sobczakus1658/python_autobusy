import os
import csv
import math
from operator import itemgetter
from datetime import datetime
import constants
import folium
import matplotlib.pyplot as plt
from collections import defaultdict


# Obliczam które autobusy przekroczyły prędkośc 50 km/h.
# Jeżeli taka sytuacja miała miejsce to zapisuje je.
def analyze_data(folder_path, output_folder):
    road_hog_vehicle = set()
    road_hog_place = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            headers = next(csvreader)

            data = list(csvreader)

            sorted_data = sorted(data, key=itemgetter(headers.index('Time')))
            if len(sorted_data) > 1:
                prev_row = sorted_data[0]
                for row in sorted_data[1:]:
                    lat = float(row[headers.index('Lat')])
                    lon = float(row[headers.index('Lon')])
                    lat_diff = lat - float(prev_row[headers.index('Lat')])
                    lon_diff = lon - float(prev_row[headers.index('Lon')])
                    try:
                        form_time = '%Y-%m-%d %H:%M:%S'
                        head = headers.index('Time')
                        curr_time = datetime.strptime(row[head], form_time)
                        pre_time = datetime.strptime(prev_row[head], form_time)
                    except ValueError:
                        continue
                    time_diff = (curr_time - pre_time).total_seconds()

                    # obliczam z twierdzenia Pitagorasa przemieszczenie
                    distance = math.sqrt(lat_diff ** 2 + lon_diff ** 2)
                    distance = distance * 60 * constants.conversion_factor

                    if time_diff > 0:
                        velocity = distance / time_diff
                        # zakładam, że bus nie przekracza 28 metrow na sekundę
                        max_v = constants.max_velocity
                        if constants.velocity < velocity < max_v:
                            header = headers.index('VehicleNumber')
                            road_hog_vehicle.add(row[header])
                            new_element = (lat, lon, velocity)
                            road_hog_place.append(new_element)
                    prev_row = row

    output_path = os.path.join(output_folder, "speed_buses.csv")
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Latitude', 'Longitude', 'Velocity'])
        csvwriter.writerows(road_hog_place)


def create_statistics(list_of_road_hog_vehicles, output_folder):
    round_to_int = [int(v * 3.6) for a, b, v in list_of_road_hog_vehicles]
    round_to_even = [(x if x % 2 == 0 else x - 1) for x in round_to_int]
    counter = {}
    for value in round_to_even:
        counter[value] = counter.get(value, 0) + 1

    values = list(counter.keys())
    repeat_counter = list(counter.values())

    plt.figure(figsize=(10, 6))
    plt.bar(values, repeat_counter, color='skyblue')
    plt.title('Wykres prędkości autobusów')
    plt.xlabel('Prędkość')
    plt.ylabel('Liczba autobusów')
    plt.xticks(values)
    plt.grid(axis='y')
    output_path = os.path.join(output_folder, 'buses_velocity.png')
    plt.savefig(output_path)


# Wyświetla miejsca na mapie w których autobus
# przekroczył prędkość 50 + speed_tolerance km/h
def show_places(points, speed_tolerance, output_folder):
    warsaw_coordinates = (52.2297, 21.0122)
    m = folium.Map(location=warsaw_coordinates, zoom_start=12)
    for point_x, point_y, velocity in points:
        if velocity > speed_tolerance + constants.velocity:
            folium.Marker(location=(point_x, point_y)).add_to(m)
    output_path = os.path.join(output_folder, 'warsaw_map_single.html')
    m.save(output_path)


# Tworzy podział Warszawy na prostokąty
# i pokazuje w jakim rejonie było najwięcej przekroczonych prędkości
def road_hog_places(coord, output_folder):
    rounded_coord = [(round(lat, 2), round(lon, 2)) for lat, lon, v in coord]

    coordinates_count = defaultdict(int)
    for cord in rounded_coord:
        coordinates_count[cord] += 1
    max_count = max(coordinates_count.values())

    m = folium.Map(location=[coord[0][0], coord[0][1]], zoom_start=12)

    for lat, lon in rounded_coord:
        square_bounds = [(lat + 0.005, lon + 0.005),
                         (lat - 0.005, lon - 0.005)]
        color = 'green'
        count = coordinates_count[(lat, lon)]
        popup_text = f"Liczba przekroczeń prędkośći: {count}"
        if count > 0:
            if count > max_count * 0.7:
                color = 'red'
            elif count > max_count * 0.4:
                color = 'yellow'
        folium.Rectangle(bounds=square_bounds,
                         color='black',
                         weight=0.2,
                         fill=False,
                         fill_color=color,
                         popup=popup_text,
                         fill_opacity=0.02).add_to(m)
    output_path = os.path.join(output_folder, 'warsaw_map_places.html')
    m.save(output_path)


def speeding():
    folder_path = 'autobuses'
    output_folder = "myData"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    analyze_data(folder_path, output_folder)


def statistic(speed_tolerance):
    output_folder = "myData"
    speed_buses_file = os.path.join(output_folder, "speed_buses.csv")

    speed_list = []
    with open(speed_buses_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            lat, lon, velocity = row
            speed_list.append((float(lat), float(lon), float(velocity)))

    v = constants.velocity
    speed_list = list(filter(lambda x: x[2] > speed_tolerance + v, speed_list))

    create_statistics(speed_list, output_folder)

    show_places(speed_list, speed_tolerance, output_folder)

    road_hog_places(speed_list, output_folder)
