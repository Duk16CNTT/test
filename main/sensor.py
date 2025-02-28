import Adafruit_DHT
import RPi.GPIO as GPIO

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
SENSOR_90CM = 22
SENSOR_45CM = 26

GPIO.setup(SENSOR_90CM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SENSOR_45CM, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_dht22():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return temperature or 0, humidity or 0

def check_height_sensors():
    return GPIO.input(SENSOR_90CM) == 0, GPIO.input(SENSOR_45CM) == 0
