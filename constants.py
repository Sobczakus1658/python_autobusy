# Klucz api
api_key = '33862623-bc5e-4d7a-9dcc-8ccaa1b1b670'
link_base = 'https://api.um.warszawa.pl/api/action/dbstore_get'
base_url = 'https://api.um.warszawa.pl/api/action/busestrams_get/'
resource_id = 'f2e5503e-927d-4ad3-9500-4ab9e55deb59'

link_data_online = f'{base_url}?resource_id={resource_id}'

id_data_bus_station = 'ab75c33d-3a26-4342-b36a-6e5fef0a3ac3'
id_data_line = '88cd555f-6f31-43ca-9de4-66c479ad5942'
id_data_schedule = 'e923fa0e-d96c-43f9-ae6e-60518c9f3238'

# to jest 50km/h tylko zapisana w metrach na sekundach
velocity = 13.89
max_velocity = 28

# jedna minuta w stopniach geograficznych to 1852 metry
conversion_factor = 1852
