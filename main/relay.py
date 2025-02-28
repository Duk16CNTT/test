import RPi.GPIO as GPIO
import time

RELAY_90CM = 17
RELAY_45CM = 27

GPIO.setup(RELAY_90CM, GPIO.OUT)
GPIO.setup(RELAY_45CM, GPIO.OUT)

def activate_relay(pin):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.5)  # Giữ relay trong 0.5s để đảm bảo gạt sản phẩm
    GPIO.output(pin, GPIO.LOW)
