import unittest
import os
import pandas as pd
import csv
import divideById
import downloadBusStations
import downloadData
import downloadSchedule
import punctualityBuses
from datetime import datetime
import speedingBuses
import shutil
import utils
import constants
from unittest.mock import patch
import experiment
import tempfile


#                     divideById - TESTS
class TestRemoveDuplicates(unittest.TestCase):
    def setUp(self):
        self.test_folder = 'test_output'
        os.makedirs(self.test_folder, exist_ok=True)

    def tearDown(self):
        for filename in os.listdir(self.test_folder):
            file_path = os.path.join(self.test_folder, filename)
            os.remove(file_path)
        os.rmdir(self.test_folder)

    def test_remove_duplicates(self):
        test_data = {'A': [1, 2, 3, 3, 4],
                     'B': [4, 5, 6, 6, 7]}
        df = pd.DataFrame(test_data)
        test_file_path = os.path.join(self.test_folder, 'test_file.csv')
        df.to_csv(test_file_path, index=False)

        divideById.remove_duplicates(self.test_folder)

        self.assertTrue(os.path.exists(test_file_path))

        df_result = pd.read_csv(test_file_path)
        self.assertEqual(len(df_result), 4)


class TestProcessCSVFiles(unittest.TestCase):
    def setUp(self):
        self.test_folder = 'test_input'
        self.output_folder = 'test_output'
        os.makedirs(self.test_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

    def tearDown(self):
        for filename in os.listdir(self.test_folder):
            file_path = os.path.join(self.test_folder, filename)
            os.remove(file_path)
        for filename in os.listdir(self.output_folder):
            file_path = os.path.join(self.output_folder, filename)
            os.remove(file_path)
        os.rmdir(self.test_folder)
        os.rmdir(self.output_folder)

    def test_process_csv_files(self):
        test_data = [
            ['Lines', 'Lon', 'VehicleNumber', 'Time', 'Lat'],
            ['1', '10.1234', '123', '2024-02-14 10:00:00', '20.5678'],
            ['2', '10.4321', '456', '2024-02-14 10:05:00', '20.8765'],
            ['3', '10.9876', '123', '2024-02-14 10:10:00', '21.3456']
        ]
        test_path = os.path.join(self.test_folder, 'test_file.csv')
        with open(test_path, 'w', newline='', encoding='utf-8') as test_csv:
            csv_writer = csv.writer(test_csv)
            csv_writer.writerows(test_data)

        divideById.process_csv_files(self.test_folder, self.output_folder)

        expected_output_files = {'123.csv', '456.csv'}
        output_files = set(os.listdir(self.output_folder))
        self.assertEqual(output_files, expected_output_files)
        result1 = ['1', '10.1234', '123', '2024-02-14 10:00:00', '20.5678']
        result2 = ['3', '10.9876', '123', '2024-02-14 10:10:00', '21.3456']
        result3 = ['2', '10.4321', '456', '2024-02-14 10:05:00', '20.8765']
        head = ['Lines', 'Lon', 'VehicleNumber', 'Time', 'Lat']
        for filename in output_files:
            output = os.path.join(self.output_folder, filename)
            with open(output, 'r', newline='', encoding='utf-8') as output_csv:
                csv_reader = csv.reader(output_csv)
                headers = next(csv_reader)
                self.assertEqual(headers, head)
                data = [row for row in csv_reader]
                if filename == '123.csv':
                    self.assertEqual(data, [result1, result2])
                elif filename == '456.csv':
                    self.assertEqual(data, [result3])


#                     downloadBusStation - TESTS
class TestSaveToCSVBusStation(unittest.TestCase):

    def setUp(self):
        self.test_data = {
            'result': [
                {'values': [
                    {'value': '50.1234'},
                    {'value': '19.4567'},
                    {'value': '123'},
                    {'value': 'skip'},
                    {'value': 'Michal'},
                    {'value': 'trzy_dni_kichal'}
                ]},
                {'values': [
                    {'value': '51.2345'},
                    {'value': '20.5678'},
                    {'value': '456'},
                    {'value': 'skip'},
                    {'value': 'Michal'},
                    {'value': 'dwa_dni_kichal'}
                ]}
            ]
        }
        self.test = 'test_output.csv'

    def tearDown(self):
        if os.path.exists(self.test):
            os.remove(self.test)

    def test_save_to_csv(self):
        downloadBusStations.save_to_csv(self.test_data, self.test)

        self.assertTrue(os.path.exists(self.test))
        result1 = ['Michal', 'dwa_dni_kichal', '20.5678', '456', '51.2345']
        result2 = ['Michal', 'trzy_dni_kichal', '19.4567', '123', '50.1234']
        second = ['Szer_geo', 'Dlug_geo', 'Numer_slupka',
                  'Nazwa_zespolu', 'Wartosc_zespolu']
        with open(self.test, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            headers = next(csvreader)
            self.assertEqual(headers, second)

            data_rows = [row for row in csvreader]
            self.assertEqual(len(data_rows), 2)
            self.assertEqual(data_rows[0], result1)
            self.assertEqual(data_rows[1], result2)


#                     downloadData
class TestSaveToCSVDownloadData(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            'result': [
                {'Lines': '1', 'Lon': '10.1234',
                 'VehicleNumber': '123',
                 'Time': '2024-02-14 10:00:00',
                 'Lat': '20.5678'},
                {'Lines': '2', 'Lon': '10.4321',
                 'VehicleNumber': '456',
                 'Time': '2024-02-14 10:05:00',
                 'Lat': '20.8765'}
            ]
        }
        self.test = 'test_output.csv'

    def tearDown(self):
        if os.path.exists(self.test):
            os.remove(self.test)

    def test_save_to_csv(self):
        downloadData.save_to_csv(self.test_data, self.test)

        self.assertTrue(os.path.exists(self.test))
        header = ['Lines', 'Lon', 'VehicleNumber', 'Time', 'Lat']
        result1 = ['1', '10.1234', '123', '2024-02-14 10:00:00', '20.5678']
        result2 = ['2', '10.4321', '456', '2024-02-14 10:05:00', '20.8765']
        with open(self.test, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            headers = next(csvreader)
            self.assertEqual(headers, header)

            data_rows = [row for row in csvreader]
            self.assertEqual(len(data_rows), 2)

            self.assertEqual(data_rows[0], result1)
            self.assertEqual(data_rows[1], result2)


#                      downloadSchedule
class TestCreateTimetableCSV(unittest.TestCase):
    def setUp(self):
        self.test_folder = 'test_schedule'
        self.test_data = {
            'result': [
                {'values': [{'key': 'czas', 'value': '10:00'}]},
                {'values': [{'key': 'czas', 'value': '10:30'}]}
            ]
        }

    def tearDown(self):
        if os.path.exists(self.test_folder):
            for file in os.listdir(self.test_folder):
                os.remove(os.path.join(self.test_folder, file))
            os.rmdir(self.test_folder)

    def test_create_timetable_csv(self):
        downloadSchedule.create_timetable_csv('123',
                                              '456',
                                              'Line1',
                                              self.test_data,
                                              self.test_folder)

        file_path = os.path.join(self.test_folder, '123.csv')
        self.assertTrue(os.path.exists(file_path))

        with open(file_path, 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            headers = next(csvreader)
            self.assertEqual(headers, ['BusStopNr', 'Line', 'ArrivalTime'])
            data_rows = list(csvreader)
            self.assertEqual(len(data_rows), 2)
            self.assertEqual(data_rows[0], ['456', 'Line1', '10:00'])
            self.assertEqual(data_rows[1], ['456', 'Line1', '10:30'])


#                       punctualityBuses
class TestLoadStopsCoordinates(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            {'Wartosc_zespolu': '123',
             'Szer_geo': '50.1234',
             'Dlug_geo': '19.4567'},
            {'Wartosc_zespolu': '456',
             'Szer_geo': '51.2345',
             'Dlug_geo': '20.5678'}
        ]
        self.test = 'test_bus_stations.csv'
        self.expected_coordinates = {
            (50.1234, 19.4567): ['123'],
            (51.2345, 20.5678): ['456']
        }

    def tearDown(self):
        if os.path.exists(self.test):
            os.remove(self.test)

    def test_load_stops_coordinates(self):
        with open(self.test, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Wartosc_zespolu', 'Szer_geo', 'Dlug_geo']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.test_data)

        result = punctualityBuses.load_stops_coordinates(self.test)

        self.assertEqual(result, self.expected_coordinates)


class TestFindMatchingStops(unittest.TestCase):
    def test_find_matching_stops(self):
        bus_coord = (50.1234, 19.4567)
        stops_coord = {
            (50.1234, 19.4567): ['stop1', 'stop2'],
            (51.2345, 20.5678): ['stop3'],
            (52.3456, 21.6789): ['stop4', 'stop5']
        }

        result = punctualityBuses.find_matching_stops(bus_coord, stops_coord)

        expected_result = ['stop1', 'stop2']
        self.assertEqual(result, expected_result)


class TestProcessBusFiles(unittest.TestCase):
    def setUp(self):
        self.stops_coordinates = {
            (50.1234, 19.4567): ['stop1', 'stop2'],
            (51.2345, 20.5678): ['stop3'],
            (52.3456, 21.6789): ['stop4', 'stop5']
        }
        self.test_folder = 'test_bus_files'
        os.makedirs(self.test_folder, exist_ok=True)
        self.test_data = [
            {'Lat': '50.1234', 'Lon': '19.4567',
             'Time': '2024-02-14 10:00:00', 'Lines': '1'},
            {'Lat': '51.2345', 'Lon': '20.5678',
             'Time': '2024-02-14 10:15:00', 'Lines': '2'}
        ]
        for i, data in enumerate(self.test_data, start=1):
            csv_filename = f'test_bus_{i}.csv'
            file = os.path.join(self.test_folder, csv_filename)
            with open(file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Lat', 'Lon', 'Time', 'Lines']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)

    def tearDown(self):
        if os.path.exists(self.test_folder):
            for file in os.listdir(self.test_folder):
                os.remove(os.path.join(self.test_folder, file))
            os.rmdir(self.test_folder)

    def test_process_bus_files(self):
        result = punctualityBuses.process_bus_files(self.test_folder,
                                                    self.stops_coordinates)

        expected_result = {
            'test_bus_1':
                [(datetime(2024, 2, 14, 10, 0),
                  ['stop1', 'stop2'], '1')],
            'test_bus_2':
                [(datetime(2024, 2, 14, 10, 15),
                  ['stop3'], '2')]
        }
        self.assertEqual(result, expected_result)


class TestFilterMatchingStops(unittest.TestCase):
    def test_filter_matching_stops(self):
        matching_results = {
            'bus1': [
                (datetime(2024, 2, 14, 10, 0), ['stop1'], '1'),
                (datetime(2024, 2, 14, 10, 1), ['stop1'], '1'),
                (datetime(2024, 2, 14, 10, 4), ['stop2'], '2')
            ],
            'bus2': [
                (datetime(2024, 2, 14, 10, 7), ['stop3'], '3'),
                (datetime(2024, 2, 14, 10, 8), ['stop4'], '4'),
                (datetime(2024, 2, 14, 10, 9), ['stop4'], '4')
            ]
        }

        result = punctualityBuses.filter_matching_stops(matching_results)
        expected_result = [
            ('bus1', '1', datetime(2024, 2, 14, 10, 0), ['stop1']),
            ('bus1', '2', datetime(2024, 2, 14, 10, 4), ['stop2']),
            ('bus2', '3', datetime(2024, 2, 14, 10, 7), ['stop3']),
            ('bus2', '4', datetime(2024, 2, 14, 10, 8), ['stop4'])
        ]
        self.assertEqual(result, expected_result)


class TestOnTheTime(unittest.TestCase):
    def setUp(self):
        self.test_folder = 'test_data'
        os.makedirs(self.test_folder, exist_ok=True)

        self.create_test_files()

    def tearDown(self):
        shutil.rmtree(self.test_folder)

    def create_test_files(self):
        test_data = [
            ['BusStopId', 'StopID', 'Line', 'ArrivalTime'],
            ['1', '1', 'L1', '12:00:00'],
            ['2', '2', 'L2', '12:14:00'],
            ['3', '3', 'L3', '12:21:00']
        ]
        for stop_id in range(1, 4):
            file_name = f"{stop_id}.csv"
            file_path = os.path.join(self.test_folder, file_name)
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(test_data)

    def test_on_the_time(self):
        filtered_list = [
            ('bus1', 'L1', datetime.strptime('12:05:00', '%H:%M:%S'), ['1']),
            ('bus2', 'L2', datetime.strptime('12:15:00', '%H:%M:%S'), ['2']),
            ('bus3', 'L3', datetime.strptime('12:24:00', '%H:%M:%S'), ['3']),
        ]
        folder_path = self.test_folder
        save_path = self.test_folder
        output_filename = 'output.csv'

        punctualityBuses.on_the_time(filtered_list,
                                     folder_path, save_path,
                                     output_filename)
        output = os.path.join(self.test_folder, output_filename)
        msg = 'Plik wynikowy nie został utworzony'
        self.assertTrue(os.path.exists(output), msg)

        with open(output, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            lines = list(reader)
            expected_lines = [['Line', 'Minutes_Late'],
                              ['L1', '5.0'],
                              ['L2', '1.0'], ['L3', '3.0']]
            msg2 = 'Zawartość pliku wynikowego jest niepoprawna'
            self.assertEqual(lines, expected_lines, msg2)


#               speedingBuses
class TestAnalyzeData(unittest.TestCase):
    def setUp(self):
        self.test_folder = 'test_data'
        os.makedirs(self.test_folder, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_folder)

    def test_analyze_data(self):
        test_data = [
            ['Lat', 'Lon', 'Time', 'VehicleNumber'],
            ['51.2345', '20.5678', '2024-02-14 12:00:00', 'ABC123'],
            ['51.2346', '20.5679', '2024-02-14 12:00:10', 'ABC123'],
            ['51.2347', '20.5680', '2024-02-14 12:00:20', 'ABC123'],

            ['51.2348', '20.5681', '2024-02-14 12:00:30', 'JKL012'],
            ['51.2348', '20.5699', '2024-02-14 12:00:40', 'JKL012'],
        ]
        path = os.path.join(self.test_folder, 'test_data.csv')
        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(test_data)

        speedingBuses.analyze_data(self.test_folder, self.test_folder)

        path = os.path.join(self.test_folder, 'speed_buses.csv')
        msg = 'Plik CSV nie został utworzony'
        self.assertTrue(os.path.exists(path), msg)

        with open(path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            data = list(reader)

        expected_result = [['51.2348', '20.5699', '20.001599999992862']]
        self.assertEqual(data, expected_result)


class TestRoadHogPlaces(unittest.TestCase):
    def setUp(self):
        self.test_folder = 'test_data'
        os.makedirs(self.test_folder, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_folder)

    def test_road_hog_places(self):
        coordinates = [
            (51.2345, 20.5678, 21.0),
            (51.2346, 20.5679, 22.0),
            (51.2347, 20.5680, 23.0)
        ]
        output_folder = self.test_folder

        speedingBuses.road_hog_places(coordinates, output_folder)
        file = 'warsaw_map_places.html'
        expected_map_path = os.path.join(output_folder, file)
        msg = 'Plik HTML z mapą nie został utworzony'
        self.assertTrue(os.path.exists(expected_map_path), msg)


class TestShowPlaces(unittest.TestCase):
    def setUp(self):
        self.test_folder = 'test_data'
        os.makedirs(self.test_folder, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_folder)

    def test_show_places(self):
        points = [
            (52.2345, 21.5678, 55.0),
            (52.2346, 21.5679, 52.0),
            (52.2347, 21.5680, 49.0)
        ]
        speed_tolerance = 5
        output_folder = self.test_folder

        speedingBuses.show_places(points, speed_tolerance, output_folder)
        file = 'warsaw_map_single.html'
        expected_map_path = os.path.join(output_folder, file)
        msg = 'Plik HTML z mapą nie został utworzony'
        self.assertTrue(os.path.exists(expected_map_path), msg)


#               utils
class TestFetchData(unittest.TestCase):
    @patch('utils.urllib.request.urlopen')
    def test_fetch_data(self, mock_urlopen):
        m = b'{"result": "test_data"}'
        mock_urlopen.return_value.__enter__.return_value.read.return_value = m

        api_key = constants.api_key
        link_data_online = constants.link_data_online
        busestrams_url = f'{link_data_online}&apikey={api_key}&type=1'
        api_url = busestrams_url
        result = utils.fetch_data(api_url)

        self.assertEqual(result, {"result": "test_data"})
        mock_urlopen.assert_called_once_with(api_url)


class TestCheckData(unittest.TestCase):
    def test_check_data_valid(self):
        busestrams_data_valid = {"result": "some_data"}
        self.assertTrue(utils.check_data(busestrams_data_valid))

    def test_check_data_invalid(self):
        msg = "Błędna metoda lub parametry wywołania"
        busestrams_data_invalid = {"result": msg}
        self.assertFalse(utils.check_data(busestrams_data_invalid))


class TestFetchDataBusStations(unittest.TestCase):
    @patch('utils.fetch_data')
    def test_fetch_data_bus_stations(self, mock_fetch_data):
        api_key = constants.api_key

        mock_fetch_data.return_value = {"example_key": "example_value"}

        result = utils.fetch_bus_stations(api_key)

        mock_fetch_data.assert_called_once_with(
            constants.link_base + "?id=" + constants.id_data_bus_station
            + "&apikey=" + api_key + "&page=1&size=5")

        self.assertIsNotNone(result)


class TestFetchDataBusLine(unittest.TestCase):
    def test_fetch_bus_line(self):
        api_key = constants.api_key
        db_id = constants.id_data_line
        busstop_id = '7046'
        busstop_nr = '02'

        result = utils.fetch_bus_line(api_key, db_id, busstop_id, busstop_nr)
        self.assertIsNotNone(result)


class TestFetchSchedule(unittest.TestCase):
    def test_fetch_schedule(self):
        api_key = constants.api_key
        db_id_schedule = constants.id_data_schedule
        busstop_id = '7046'
        busstop_nr = '02'
        line = '116'

        result = utils.fetch_schedule(api_key, db_id_schedule,
                                      busstop_id, busstop_nr, line)
        self.assertIsNotNone(result)


#           Expreriment
class TestLoadLocations(unittest.TestCase):
    def test_load_locations(self):
        test_data = [
            ['name', 'lat', 'lon'],
            ['Muzeum Narodowe', '52.2315', '21.0238'],
            ['Muzeum Polin', '52.2497', '20.9939'],
            ['Pałac Kultury i Nauki', '52.2319', '21.0069']
        ]
        with tempfile.NamedTemporaryFile(mode='w',
                                         delete=False, newline='',
                                         encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(test_data)

        try:
            loaded_locations = experiment.load_locations(csvfile.name)

            expected_locations = {
                'Muzeum Narodowe': (52.2315, 21.0238),
                'Muzeum Polin': (52.2497, 20.9939),
                'Pałac Kultury i Nauki': (52.2319, 21.0069)
            }
            self.assertEqual(loaded_locations, expected_locations)
        finally:
            os.unlink(csvfile.name)


class TestFindMatchingPlaces(unittest.TestCase):
    def test_find_matching_places(self):
        bus_coordinates = (52.2297, 21.0122)
        tolerance = 600
        buildings = {
            'Muzeum Narodowe': (52.2315, 21.0238),
            'Muzeum Polin': (52.2497, 20.9939),
            'Pałac Kultury i Nauki': (52.2319, 21.0069)
        }
        expected_result = ['Pałac Kultury i Nauki']
        result = experiment.find_match_place(bus_coordinates,
                                             tolerance, buildings)
        self.assertEqual(result, expected_result)


class TestLoadLocations2(unittest.TestCase):
    def test_load_locations2(self):
        test_data = [
            ['name', 'lat', 'lon'],
            ['Muzeum Narodowe', '52.2315', '21.0238'],
            ['Muzeum Polin', '52.2497', '20.9939'],
            ['Pałac Kultury i Nauki', '52.2319', '21.0069']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                         newline='',
                                         encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(test_data)

        try:
            loaded_locations = experiment.load_locations2(csvfile.name)

            expected_locations = {
                (52.231, 21.024): 'Muzeum Narodowe',
                (52.25, 20.994): 'Muzeum Polin',
                (52.232, 21.007): 'Pałac Kultury i Nauki'
            }
            self.assertEqual(loaded_locations, expected_locations)
        finally:
            os.unlink(csvfile.name)


class TestFindMatchingPlaces2(unittest.TestCase):
    def test_find_matching_places2(self):
        bus_coordinates = (52.2297, 21.0122)
        buildings = {
            'Muzeum Narodowe': (52.2315, 21.0238),
            'Muzeum Polin': (52.2497, 20.9939),
            'Pałac Kultury i Nauki': (52.2319, 21.0069)
        }
        expected_result = []
        result = experiment.find_match_place2(bus_coordinates, buildings)
        self.assertEqual(result, expected_result)


class TestReadDataAccidents(unittest.TestCase):
    def test_read_data_accidents(self):
        test_data = [
            ['Latitude', 'Longitude', 'Severity'],
            ['52.2315', '21.0238', 'Low'],
            ['52.2497', '20.9939', 'Medium'],
            ['52.2319', '21.0069', 'High']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='',
                                         encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(test_data)

        try:
            loaded_data = experiment.read_data_accidents(
                os.path.dirname(csvfile.name),
                os.path.basename(csvfile.name))

            expected_data = [
                ['52.2315', '21.0238', 'Low'],
                ['52.2497', '20.9939', 'Medium'],
                ['52.2319', '21.0069', 'High']
            ]
            self.assertEqual(loaded_data, expected_data)
        finally:
            os.unlink(csvfile.name)


class TestReadDataSpeed(unittest.TestCase):
    def test_read_data_speed(self):
        test_data = [
            ['Latitude', 'Longitude', 'Velocity'],
            ['52.2315', '21.0238', '60'],
            ['52.2497', '20.9939', '70'],
            ['52.2319', '21.0069', '80']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                         newline='',
                                         encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(test_data)

        try:
            loaded_data = experiment.read_data_speed(
                os.path.dirname(csvfile.name),
                os.path.basename(csvfile.name))

            expected_data = [
                (52.2315, 21.0238, 60),
                (52.2497, 20.9939, 70),
                (52.2319, 21.0069, 80)
            ]
            self.assertEqual(loaded_data, expected_data)
        finally:
            os.unlink(csvfile.name)


class TestShowPlacesAccident(unittest.TestCase):
    def test_show_places_accident(self):
        accidents_data = [
            ['Street', 'Accidents', 'Latitude', 'Longitude'],
            ['Nowy Świat', '5', '52.2315', '21.0238'],
            ['Krakowskie Przedmieście', '3', '52.2497', '20.9939'],
            ['Marszałkowska', '7', '52.2319', '21.0069']
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                         newline='',
                                         encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(accidents_data)

        try:
            speed_data = [
                ['Latitude', 'Longitude', 'Velocity'],
                ['52.2315', '21.0238', '70'],
                ['52.2497', '20.9939', '80'],
                ['52.2319', '21.0069', '90']
            ]

            with (tempfile.NamedTemporaryFile(mode='w', delete=False,
                                              newline='',
                                              encoding='utf-8')
                  as speed_csvfile):
                writer = csv.writer(speed_csvfile)
                writer.writerows(speed_data)

            try:
                output_folder = os.path.dirname(csvfile.name)
                name = os.path.basename(csvfile.name)
                name_speed_csv = os.path.basename(speed_csvfile.name)
                speed_tolerance = 10
                experiment.show_places_accident(speed_tolerance,
                                                output_folder, name,
                                                name_speed_csv)

                output_path = os.path.join(output_folder,
                                           'warsaw_map_with_accidents.html')
                self.assertTrue(os.path.exists(output_path))
            finally:
                os.unlink(speed_csvfile.name)
        finally:
            os.unlink(csvfile.name)


class TestTrip2(unittest.TestCase):
    def tearDown(self):
        folder_path = 'test_bus_data'
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(folder_path)

    def test_trip2(self):
        buildings_data = [
            ['Name', 'Lat', 'Lon'],
            ['Muzeum Narodowe', '52.2315', '21.0238'],
            ['Muzeum Polin', '52.2497', '20.9939'],
            ['Pałac Kultury i Nauki', '52.2319', '21.0069']
        ]

        with (tempfile.NamedTemporaryFile(mode='w', delete=False,
                                          newline='',
                                          encoding='utf-8')
              as building_csvfile):
            writer = csv.writer(building_csvfile)
            writer.writerows(buildings_data)

        places_data = [
            ['Name', 'Lat', 'Lon'],
            ['Stare Miasto', '52.2297', '21.0122'],
            ['Łazienki Królewskie', '52.2113', '21.0184'],
            ['Park Ujazdowski', '52.2239', '21.0245']
        ]

        with (tempfile.NamedTemporaryFile(mode='w', delete=False,
                                          newline='',
                                          encoding='utf-8')
              as place_csvfile):
            writer = csv.writer(place_csvfile)
            writer.writerows(places_data)

        try:
            bus_folder = 'test_bus_data'
            os.makedirs(bus_folder, exist_ok=True)
            bus_file1_path = os.path.join(bus_folder, 'bus_route1.csv')
            with open(bus_file1_path, 'w', newline='',
                      encoding='utf-8') as bus_file1:
                writer = csv.writer(bus_file1)
                writer.writerow(['Lines', 'Lat', 'Lon'])
                writer.writerow(['L1', '52.2315', '21.0238'])
                writer.writerow(['L1', '52.2497', '20.9939'])
                writer.writerow(['L2', '52.2319', '21.0069'])

            try:
                output_file = 'test_trip_results.csv'
                output_folder = os.path.dirname(building_csvfile.name)
                building_csv = os.path.basename(building_csvfile.name)
                place_csv = os.path.basename(place_csvfile.name)
                result = experiment.trip2(bus_folder,
                                          output_file, output_folder,
                                          building_csv, place_csv)

                output_path = os.path.join(output_folder, output_file)
                self.assertTrue(os.path.exists(output_path))

                expected_results = {
                    'L1': {'Muzeum Narodowe', 'Muzeum Polin'},
                    'L2': {'Pałac Kultury i Nauki'}
                }
                self.assertEqual(result, expected_results)
            finally:
                os.remove(bus_file1_path)
        finally:
            os.remove(building_csvfile.name)
            os.remove(place_csvfile.name)


if __name__ == '__main__':
    unittest.main()
