import csv
import os
import constants
import utils


def custom_sort(data):
    pairs = []
    for item in data['result']:
        key1 = item['values'][4]['value']
        key2 = item['values'][5]['value']
        pairs.append((key1, key2, item))

    pairs.sort(key=lambda pair: (pair[0], pair[1]))

    return [pair[2] for pair in pairs]


def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        team = 'Nazwa_zespolu'
        value = 'Wartosc_zespolu'
        headers = ['Szer_geo', 'Dlug_geo', 'Numer_slupka', team, value]
        csvwriter.writerow(headers)
        sorted_data = custom_sort(data)

        for entry in sorted_data:
            row = [
                entry['values'][4]['value'],
                entry['values'][5]['value'],
                entry['values'][1]['value'],
                entry['values'][2]['value'],
                entry['values'][0]['value']
            ]
            csvwriter.writerow(row)


def download_bus_stations(folder_path):
    api_key = constants.api_key
    db_id = constants.id_data_bus_station
    busestrams_data = utils.fetch_bus_stations(api_key, db_id)
    if ('result' in busestrams_data
            and isinstance(busestrams_data['result'], list)):
        os.makedirs(folder_path, exist_ok=True)
        csv_filename = f'{folder_path}/bus_stations.csv'
        save_to_csv(busestrams_data, csv_filename)
