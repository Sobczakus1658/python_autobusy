import folium
import csv
import constants
import os
from geopy.distance import geodesic
from collections import defaultdict
import matplotlib.pyplot as plt


def read_data_accidents(output_folder, name):
    data = []
    output_path = os.path.join(output_folder, name)
    with open(output_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            data.append(row)

    return data


def read_data_speed(output_folder, name_csv):
    speed_buses_file = os.path.join(output_folder, name_csv)

    speeding_list = []
    with open(speed_buses_file, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            lat, lon, velocity = row
            speeding_list.append((float(lat), float(lon), float(velocity)))
    return speeding_list


def show_places_accident(speed_tolerance, output_folder, name, name_speed_csv):
    data = read_data_accidents(output_folder, name)

    speed_list = read_data_accidents(output_folder, name_speed_csv)
    v = constants.velocity
    tol = speed_tolerance
    speed_list = list(filter(lambda x: float(x[2]) > tol + v, speed_list))

    # Współrzędne Warszawy
    m = folium.Map(location=[52.2297, 21.0122], zoom_start=12)

    rounded_cord = []
    for lat, lon, v in speed_list:
        rounded_lat = round(float(lat), 2)
        rounded_lon = round(float(lon), 2)
        rounded_cord.append((rounded_lat, rounded_lon))

    coordinates_count = defaultdict(int)
    for coord in rounded_cord:
        coordinates_count[coord] += 1
    max_count = max(coordinates_count.values())
    for row in data:
        street = row[0]
        accidents = row[1]
        lat = float(row[2])
        lon = float(row[3])

        popup_text = f"{street}: {accidents} accidents"
        folium.Marker(location=(lat, lon), popup=popup_text).add_to(m)

    for lat, lon in rounded_cord:
        square_bounds = [(lat + 0.005, lon + 0.005),
                         (lat - 0.005, lon - 0.005)]
        color = 'green'
        count = coordinates_count[(lat, lon)]
        popup_text = f"Liczba przekroczeń prędkości: {count}"
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

    output_path = os.path.join(output_folder, 'warsaw_map_with_accidents.html')
    m.save(output_path)


def find_match_place(bus_coordinates, tolerance, buildings):
    places = []
    for name, building_coords in buildings.items():
        distance = geodesic(bus_coordinates, building_coords).meters
        if distance <= tolerance:
            places.append(name)
    return places


def load_locations(file_path):
    locations = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            name, lat, lon = row
            locations[name] = (float(lat), float(lon))
    return locations


def trip(b_tol, p_tol, bus_folder, folder, build_csv, place_csv, out_csv):
    b_tol = float(b_tol)
    p_tol = float(p_tol)
    buildings_path = os.path.join(folder, build_csv)
    places_path = os.path.join(folder, place_csv)

    buildings = load_locations(buildings_path)
    places = load_locations(places_path)
    matching_results = defaultdict(set)
    counter = 0
    for bus_file in os.listdir(bus_folder):
        if bus_file.endswith('.csv'):
            print(counter)
            counter = counter + 1
            bus_file_path = os.path.join(bus_folder, bus_file)

            with open(bus_file_path, 'r', encoding='utf-8') as bus_csv:
                bus_reader = csv.DictReader(bus_csv)
                for row in bus_reader:
                    bus_coord = (float(row['Lat']), float(row['Lon']))
                    match_build = find_match_place(bus_coord, b_tol, buildings)
                    match_places = find_match_place(bus_coord, p_tol, places)
                    line = row['Lines']
                    matching_results[line].update(match_build)
                    matching_results[line].update(match_places)

    output_file = os.path.join(folder, out_csv)
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for line, matches in matching_results.items():
            if matches:
                writer.writerow([line] + list(matches))
    print("Wyniki zapisane do:", output_file)


def find_match_place2(bus_coordinates, stops_coordinates):
    matching_stops = []
    for stop_coordinates, stop_name in stops_coordinates.items():
        if stop_coordinates == bus_coordinates:
            matching_stops.append(stop_name)
    return matching_stops


def load_locations2(file_path):
    locations = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            name = row[0]
            lat = round(float(row[1]), 3)
            lon = round(float(row[2]), 3)
            locations[(lat, lon)] = name
    return locations


def trip2(bus_folder, output_file, output_folder, building_csv, place_csv):
    buildings_path = os.path.join(output_folder, building_csv)
    places_path = os.path.join(output_folder, place_csv)

    buildings = load_locations2(buildings_path)
    places = load_locations2(places_path)
    matching_results = defaultdict(set)
    for bus_file in os.listdir(bus_folder):
        if bus_file.endswith('.csv'):
            bus_file_path = os.path.join(bus_folder, bus_file)

            with open(bus_file_path, 'r', encoding='utf-8') as bus_csv:
                bus_reader = csv.DictReader(bus_csv)
                for row in bus_reader:
                    bus_coord = (round(float(row['Lat']), 3),
                                 round(float(row['Lon']), 3))
                    match_buildings = find_match_place2(bus_coord, buildings)
                    matching_places = find_match_place2(bus_coord, places)
                    line = row['Lines']
                    matching_results[line].update(match_buildings)
                    matching_results[line].update(matching_places)

    output_file = os.path.join(output_folder, output_file)
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for line, matches in matching_results.items():
            if matches:
                writer.writerow([line] + list(matches))

    return matching_results


def show(number):
    file_path = f'myData/tour{number}.csv'

    lines_data = {}
    with open(file_path, 'r') as file:
        for line in file:
            line_data = line.strip().split(',')
            line_name = line_data[0]
            line_info = line_data[1:]
            lines_data[line_name] = line_info

    t6 = sorted(lines_data, key=lambda x: len(lines_data[x]), reverse=True)[:6]

    plt.figure(figsize=(12, 8))
    for i, line in enumerate(t6, 1):
        plt.subplot(2, 3, i)
        plt.text(0.5, 0.5, '\n'.join(lines_data[line]), ha='center',
                 va='center', fontsize=12, color='black')
        plt.title(f'Linia {line}', fontsize=14)
        plt.axis('off')
        plt.tight_layout()

    plt.savefig(f'myData/top_lines_info{number}.jpeg', dpi=300)


def accidents(speed_tolerance):
    folder_name = 'myData'
    data = 'data.csv'
    name_speed_csv = 'speed_buses.csv'
    show_places_accident(speed_tolerance, folder_name, data, name_speed_csv)


def warsaw_tour(build=-1, place=-1):
    folder = 'autobuses'
    folder_name = 'myData'
    file_name2 = 'tour2.csv'
    out_csv = 'tour3.csv'
    build_csv = 'building_locations.csv'
    place_csv = 'place_locations.csv'
    if build == -1:
        trip2(folder, file_name2, folder_name, build_csv, place_csv)
    else:
        trip(build, place, folder, folder_name, build_csv, place_csv, out_csv)
