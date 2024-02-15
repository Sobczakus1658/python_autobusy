import csv
from datetime import datetime
import os
import time
import constants
import utils
import downloadSchedule
import downloadBusStations


# Funkcja do zapisywania danych do pliku CSV
def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        headers = ['Lines', 'Lon', 'VehicleNumber', 'Time', 'Lat']
        csvwriter.writerow(headers)

        for entry in data['result']:
            lines = entry['Lines']
            number = entry['VehicleNumber']
            row = [lines, entry['Lon'], number, entry['Time'], entry['Lat']]
            csvwriter.writerow(row)


def managment():
    api_key = constants.api_key
    link_data_online = constants.link_data_online
    busestrams_url = f'{link_data_online}&apikey={api_key}&type=1'
    busestrams_data = utils.fetch_data(busestrams_url)
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # powinna być zmiana
    folder_path = 'data2'
    os.makedirs(folder_path, exist_ok=True)
    csv_filename = f'{folder_path}/data_{current_datetime}.csv'
    if utils.check_data(busestrams_data):
        save_to_csv(busestrams_data, csv_filename)


def prepare_data():
    folder_path = 'bus_stations'
    # to powinno zostać odkomentowane
    # downloadBusStations.download_bus_stations(folder_path)

    # Uwaga, ta część wykonuje sie naprawdę długo
    # downloadSchedule.download_schedule(folder_path)
    repeat_count = 0
    # tu powinno być 360
    while repeat_count < 3:
        managment()
        time.sleep(10)
        repeat_count = repeat_count + 1
