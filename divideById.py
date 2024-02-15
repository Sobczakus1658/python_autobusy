import os
import csv
import pandas as pd


def write_header(csvwriter):
    csvwriter.writerow(['Lines', 'Lon', 'VehicleNumber', 'Time', 'Lat'])


def process_csv_files(folder_path, output_folder):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            headers = next(csvreader)
            vehicle_number_index = headers.index('VehicleNumber')

            for row in csvreader:
                vehicle_number = row[vehicle_number_index]
                output_filename = f"{vehicle_number}.csv"
                path = os.path.join(output_folder, output_filename)

                if not os.path.exists(path):
                    with open(path, 'w', newline='', encoding='utf-8') as out:
                        csvwriter = csv.writer(out)
                        write_header(csvwriter)

                with open(path, 'a', newline='', encoding='utf-8') as output:
                    csvwriter = csv.writer(output)
                    csvwriter.writerow(row)


def remove_duplicates(output_folder):
    for filename in os.listdir(output_folder):
        file_path = os.path.join(output_folder, filename)

        df = pd.read_csv(file_path)
        df.drop_duplicates(inplace=True)

        with open(file_path, 'w', newline='', encoding='utf-8') as output_csv:
            df.to_csv(output_csv, index=False)


def divide():
    folder_path = 'data'
    output_folder = 'autobuses2'
    os.makedirs(output_folder, exist_ok=True)
    process_csv_files(folder_path, output_folder)
    remove_duplicates(output_folder)
