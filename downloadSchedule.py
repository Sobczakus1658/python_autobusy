import os
import csv
import constants
import utils

'''
Plik ten odpowiada za pobranie rozkładów jazdy. Wyniki zapisuje
w folderze Schedule, w którym są dane następującej postaci:
- Plik ma nazwę id_przystanku.
- BusStopNr, ponieważ jeden przystanek może mieć kilka różnych BusStopNr
(Id_Przystanku, BusStopNr) jest Primery Key w tym pliku
- Linia, czyli której linii autobusowej tyczą się dane
- ArrivalTime, godzina przyjazdu autobusu.
Czyli dzięki tym danym, będę wiedział na jaki przystanek i
  której powinien przyjechać
dany autobus (konkretenj linii)
'''


def create_timetable_csv(bus_stop_id, bus_nr, line, time_data, folder_name):
    if 'result' in time_data and isinstance(time_data['result'], list):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_name = f'{folder_name}/{bus_stop_id}.csv'
        mode = 'a' if os.path.exists(file_name) else 'w'

        with open(file_name, mode, newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            if mode == 'w':
                csv_writer.writerow(['BusStopNr', 'Line', 'ArrivalTime'])

            for entry in time_data['result']:
                if 'values' in entry and isinstance(entry['values'], list):
                    arrival_time = None
                    for value in entry['values']:
                        if value.get('key') == 'czas':
                            arrival_time = value['value']
                            break

                    if arrival_time:
                        csv_writer.writerow([bus_nr, line, arrival_time])


def decide(buse_data, api_key, id, brig, post_id, folder):
    if buse_data is not None:
        for line in buse_data:
            time_data = utils.fetch_schedule(api_key, id, brig, post_id, line)

            if time_data:
                create_timetable_csv(brig, post_id, line, time_data, folder)


def download_schedule(folder_path):
    api_key = constants.api_key
    db_id = constants.id_data_schedule
    csv_filename = f'{folder_path}/bus_stations.csv'
    folder_name = 'schedule2'
    if os.path.exists(csv_filename):
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader)
            for row in csv_reader:
                print(row)
                data = dict(zip(headers, row))
                brig = data.get('Wartosc_zespolu', '')
                post_id = data.get('Numer_slupka', '')
                db = constants.id_data_line
                buse_data = utils.fetch_bus_line(api_key, db, brig, post_id)
                decide(buse_data, api_key, db_id, brig, post_id, folder_name)
