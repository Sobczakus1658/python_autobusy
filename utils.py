# utils.py
import urllib.request
import json
import constants


# Ten plik odpowiada za łączenie się z API strony i pobieraniem danych
def fetch_data(api_url):
    with urllib.request.urlopen(api_url) as fileobj:
        data = json.loads(fileobj.read())
    return data


# Niekiedy pokazuje się ten błąd, na który nie mam wpływu.
def check_data(busestrams_data):
    msg = 'Błędna metoda lub parametry wywołania'
    if 'result' in busestrams_data and busestrams_data['result'] == msg:
        return False
    else:
        return True


def fetch_bus_stations(api_key, page=1, size=5, sort_by=None):
    base_url = constants.link_base
    db_id = constants.id_data_bus_station
    params = {
        'id': db_id,
        'apikey': api_key,
        'page': page,
        'size': size
    }

    if sort_by:
        params['sortBy'] = sort_by

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        return fetch_data(url)
    except Exception as e:
        print(f"Error: {e}")
        return None


def fetch_bus_line(api_key, db_id, busstop_id, busstop_nr):
    base_url = "https://api.um.warszawa.pl/api/action/dbtimetable_get"
    params = {
        'id': db_id,
        'apikey': api_key,
        'busstopId': busstop_id,
        'busstopNr': busstop_nr,
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url) as fileobj:
            data = json.loads(fileobj.read())
            lines = [entry['values'][0]['value'] for entry in data['result']]
            return lines
        # return data
    except Exception as e:
        print(f"Error: {e}")
        return None


def fetch_schedule(api_key, db_id, busstop_id, busstop_nr, line):
    base_url = "https://api.um.warszawa.pl/api/action/dbtimetable_get"
    params = {
        'id': db_id,
        'apikey': api_key,
        'busstopId': busstop_id,
        'busstopNr': busstop_nr,
        'line': line,
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url) as fileobj:
            data = json.loads(fileobj.read())
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None
