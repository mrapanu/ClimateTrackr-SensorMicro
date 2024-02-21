import network, ntptime, utime, ubinascii, gc, dht, urequests as requests, ujson as json
from machine import Pin

###################################################
################## CONFIGURATION ##################
###################################################

pin = Pin("LED", Pin.OUT)
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

def get_local_time(gmt):
    utc_time = utime.localtime()
    local_time = (utc_time[0], utc_time[1], utc_time[2], utc_time[3] + gmt, utc_time[4], utc_time[5])
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
    
    while True:
        pin.toggle()
        try:
            local_time = get_local_time(gmt)
            temperature, humidity = read_dht_sensor()
            publish_data_to_rabbitmq(temperature, humidity, local_time)
        except OSError as error:
            print("Failed to read DHT sensor:", error)
        utime.sleep(message_interval)

if __name__ == "__main__":
    main()
