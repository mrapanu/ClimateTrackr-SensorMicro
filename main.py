import network, ntptime, utime, ubinascii, gc, dht, urequests as requests, ujson as json
from machine import Pin

###################################################
################## CONFIGURATION ##################
###################################################


pin = Pin("LED", Pin.OUT)  # pin = Pin("LED", Pin.OUT) for pico W  pin = Pin(2, Pin.OUT) for esp
dht_sensor = dht.DHT11(Pin(4)) #Set Pin Number as you need
#dht_sensor = dht.DHT22(Pin(4)) #Set Pin Number as you need

# Network configuration
wifi_ssid = "<YOUR WIFI SSID>"
wifi_password = "<YOUR WIFI PASSWORD>"

# RabbitMQ configuration
rabbitmq_host = "<RABBITMQ HOST>"
rabbitmq_port = 15672  #RabbitMQ HTTP Port. Default: 15672
rabbitmq_username = "<RABBITMQ USER>"
rabbitmq_password = "<RABBITMQ PASSWORD>"
exchange = "<RABBITMQ_EXCHANGE>"
routing_key = "<RABBITMQ_KEY>"

# Define message interval
message_interval = 120  # number of seconds

# Define Room Name
room = "<YOUR ROOM NAME>"

# Define Your Local Time (ex: For GMT+2 ---> gmt = 2)
gmt = 2

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())
    try:
        ntptime.settime()
    except OSError as e:
        print('Failed to synchronize time with NTP server:', e)

def days_in_month(year, month):
    if month == 2:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            return 29  # Leap year
        else:
            return 28
    elif month in {4, 6, 9, 11}:
        return 30
    else:
        return 31

def get_local_time(gmt):
    utc_time = utime.localtime()
    local_hour = (utc_time[3] + gmt) % 24  # Ensure hour remains within 0-23 range
    local_day = utc_time[2] + (utc_time[3] + gmt) // 24  # Adjust day if hour goes beyond 23 or below 0
    local_month = utc_time[1]
    local_year = utc_time[0]
    
    while local_day > days_in_month(local_year, local_month) or local_day < 1:
        if local_day > days_in_month(local_year, local_month):
            local_day -= days_in_month(local_year, local_month)
            local_month += 1
            if local_month > 12:
                local_month = 1
                local_year += 1
        elif local_day < 1:
            local_month -= 1
            if local_month < 1:
                local_month = 12
                local_year -= 1
            local_day += days_in_month(local_year, local_month)
    
    local_time = (local_year, local_month, local_day, local_hour, utc_time[4], utc_time[5])
    return local_time

def read_dht_sensor():
    utime.sleep_ms(2000)
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temperature, humidity

def publish_data_to_rabbitmq(temperature, humidity, local_time):
    gc.collect()
    try:
        dt_string = "{:02d}/{:02d}/{:04d} {:02d}:{:02d}:{:02d}".format(
            local_time[1], local_time[2], local_time[0],
            local_time[3], local_time[4], local_time[5]
        )
        body = {
            "properties": {},
            "routing_key": f"{routing_key}",
            "payload": f'{{"room": "{room}", "date": "{dt_string}", "temperature": "{temperature}", "humidity": "{humidity}"}}',
            "payload_encoding": "string"
        }
        url = f"http://{rabbitmq_host}:{rabbitmq_port}/api/exchanges/%2f/{exchange}/publish"
        encoded_user_pass = ubinascii.b2a_base64(f"{rabbitmq_username}:{rabbitmq_password}".encode()).decode().strip()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + encoded_user_pass
        }
        response = requests.post(url, headers=headers, data=json.dumps(body))
        print("[INFO] Data published successfully to RabbitMQ.")
    except Exception as e:
        print(f"[ERROR] Failed to publish data to RabbitMQ: {e}")

def main():
    connect_wifi(wifi_ssid, wifi_password)
    pin_value = 0
    while True:
        pin_value ^= 1
        pin.value(pin_value)
        try:
            local_time = get_local_time(gmt)
            temperature, humidity = read_dht_sensor()
            publish_data_to_rabbitmq(temperature, humidity, local_time)
        except OSError as error:
            print("Failed to read DHT sensor:", error)
        utime.sleep(message_interval)

if __name__ == "__main__":
    main()
