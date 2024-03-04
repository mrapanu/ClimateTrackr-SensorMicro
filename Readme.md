# ClimateTrackr Sensor Micro

ClimateTrackr Sensor Micro is a Python-based project for tracking temperature and humidity data using a DHT sensor and publishing it to RabbitMQ. This README provides an overview of the project, installation instructions, and basic usage guidelines.

## Table of Contents

1. [Introduction](#introduction)
2. [Usage](#usage)
3. [Configuration](#configuration)
    - [WiFi Configuration](#wifi-configuration)
    - [RabbitMQ Configuration](#rabbitmq-configuration)
    - [Sensor Configuration](#sensor-configuration)
4. [Notes](#notes)
5. [Dependencies](#dependencies)

## Introduction

ClimateTrackr is designed to monitor temperature and humidity using a DHT sensor on a Raspberry Pi or similar environment. It publishes the collected data to RabbitMQ for further processing.

## Usage

1. Configure the parameters directly in the `main.py` file.
2. Setup Visual Studio Code to work with MicroPython. See `Useful Links` from `Notes` section.
3. Upload the `main.py` file to your Raspberry Pi Pico / ESP device.
4. Connect your DHT sensor to the appropriate pin on your Raspberry Pi Pico / ESP device.
5. Power on your device.

## Configuration

Modify the variables in the `main.py` file to configure the project:

### WiFi Configuration

- `wifi_ssid`: Your WiFi network SSID.
- `wifi_password`: Your WiFi network password.

### RabbitMQ Configuration

- `rabbitmq_host`: The hostname or IP address of your RabbitMQ server.
- `rabbitmq_port`: The port for RabbitMQ HTTP (default is 15672).
- `rabbitmq_username`: Your RabbitMQ username.
- `rabbitmq_password`: Your RabbitMQ password.
- `exchange`: The name of the exchange to which data will be published.
- `routing_key`: The routing key for publishing messages.

### Sensor Configuration

- `pin`: The pin to which the LED is connected.
- `dht_sensor`: The type of DHT sensor being used (DHT11 or DHT22).
- `message_interval`: The interval (in seconds) between each data publication.
- `room`: The name of the room where the sensor is located.
- `gmt`: Your local timezone offset from GMT.

## Notes

- Ensure that your MicroPython device is properly connected to the internet before running the code.
- Adjust the DHT sensor pin configuration based on your setup.
- Make sure you have a RabbitMQ server set up and running.
- Ensure the RabbitMQ server is accessible from the network your MicroPython device is connected to.
- Check the console output for any error messages or debugging information.

Useful links:
- https://www.instructables.com/How-to-Use-VSCode-With-Raspberry-Pi-Pico-W-and-Mic/
- https://randomnerdtutorials.com/micropython-esp32-esp8266-vs-code-pymakr/

## Dependencies

- `urequests`: HTTP client for MicroPython.
- `ujson`: JSON encoder and decoder for MicroPython.
- `network`, `ntptime`, `utime`, `ubinascii`, `gc`, `dht`: Standard MicroPython libraries.
