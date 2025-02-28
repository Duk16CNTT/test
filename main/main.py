import time
import RPi.GPIO as GPIO
from sensor import read_dht22, check_height_sensors
from relay import activate_relay
from lcd_display import lcd_init, lcd_display
from led import blink_led
from button import is_button_pressed

# GPIO setup
GPIO.setmode(GPIO.BCM)

# Chân GPIO
START_BUTTON = 23
STOP_BUTTON = 24
LED_PIN = 25

# Khởi tạo LCD
lcd_init()

# Biến trạng thái
running = False
count_90cm = 0
count_45cm = 0

try:
    while True:
        # Đọc nhiệt độ, độ ẩm
        temperature, humidity = read_dht22()
        lcd_display(f"Temp:{temperature:.1f}C Hum:{humidity:.1f}%", f"90c={count_90cm} 45c={count_45cm}")

        # Kiểm tra nút Start
        if is_button_pressed(START_BUTTON):
            running = True

        # Kiểm tra nút Stop
        if is_button_pressed(STOP_BUTTON):
            running = False

        # Nếu đang chạy, xử lý đếm sản phẩm
        if running:
            h_90cm, h_45cm = check_height_sensors()
            if h_90cm:
                count_90cm += 1
                activate_relay(17)
            elif h_45cm:
                count_45cm += 1
                activate_relay(27)

            # LED nhấp nháy báo trạng thái chạy
            blink_led(LED_PIN, 2)

        time.sleep(1)

except KeyboardInterrupt:
    print("Dừng chương trình")
    GPIO.cleanup()
