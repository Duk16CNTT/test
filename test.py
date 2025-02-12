import RPi.GPIO as GPIO
import time

# Định nghĩa các chân GPIO kết nối với 8 LED
LED_PINS = [2, 3, 4, 17, 27, 22, 10, 9]  # Thay bằng chân thực tế của bạn

# Cấu hình GPIO
GPIO.setmode(GPIO.BCM)  
GPIO.setup(LED_PINS, GPIO.OUT)

def display_led(pattern):
    """ Hàm hiển thị trạng thái LED dựa vào giá trị nhị phân của pattern """
    for i in range(8):
        GPIO.output(LED_PINS[i], (pattern >> (7 - i)) & 1)
    time.sleep(1)  # Trễ 1 giây để quan sát

def led_effect():
    """ Hiệu ứng LED chạy qua lại """
    patterns = [
        0b00011000,
        0b00100100,
        0b01000010,
        0b10000001,
        0b01000010,
        0b00100100,
        0b00011000
    ]

    while True:
        for pattern in patterns:
            display_led(pattern)

try:
    led_effect()
except KeyboardInterrupt:
    GPIO.cleanup()  # Dọn dẹp GPIO khi nhấn Ctrl+C
