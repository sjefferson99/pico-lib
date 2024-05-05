## WIFI
WIFI_SSID = ""
WIFI_PASSWORD = ""
WIFI_COUNTRY = "GB"
WIFI_CONNECT_TIMEOUT_SECONDS = 10
WIFI_CONNECT_RETRIES = 1
WIFI_RETRY_BACKOFF_SECONDS = 5

## BME280
i2c_pins = {"sda": 0, "scl": 1}

## Light
led_pin = 22
default_brightness_pc = 100

## Open Meteo
# lat and long in decimal format array with Lattitude in 0
# postion and Longitude in 1
# e.g. latlong[50.9048, -1.4043] for Southampton UK
lat_long = [50.9048, -1.4043]