import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

def blink_led(pin, interval):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(interval)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(interval)
