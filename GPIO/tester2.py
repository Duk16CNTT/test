from EmulatorGUI import GPIO
#import RPi.GPIO as GPIO
import time
import traceback
import Adafruit_DHT
from RPLCD.i2c import CharLCD

def Main():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
      
        # Thiết lập các chân GPIO
        GPIO.setup(4, GPIO.IN)  # Cảm biến DHT22
        GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)  # Rơ le 90cm
        GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW)  # Rơ le 45cm
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Cảm biến 90cm
        GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Cảm biến 45cm
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Nút nhấn Start
        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Nút nhấn Stop
        GPIO.setup(25, GPIO.OUT)  # Đèn LED

        # Thiết lập LCD
        lcd = CharLCD('PCF8574', 0x27)

        # Khởi tạo cảm biến DHT22
        sensor = Adafruit_DHT.DHT22
        pin = 4

        # Các biến để lưu trữ số lượng sản phẩm
        count_90cm = 0
        count_45cm = 0
        is_running = False

        def update_lcd(temp, humidity, count_90cm, count_45cm):
            lcd.clear()
            lcd.write_string(f"DEM SAN PHAM C\n")
            lcd.write_string(f"Temp: {temp:.1f}C Hum: {humidity:.1f}%\n")
            lcd.write_string(f"90c={count_90cm} 45c={count_45cm}")

        while True:
            if GPIO.input(23) == GPIO.LOW:  # Nút Start được nhấn
                is_running = True

            if GPIO.input(24) == GPIO.LOW:  # Nút Stop được nhấn
                is_running = False

            if is_running:
                # Đọc dữ liệu từ cảm biến DHT22
                humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
                if humidity is not None and temperature is not None:
                    # Cập nhật LCD
                    update_lcd(temperature, humidity, count_90cm, count_45cm)

                # Kiểm tra cảm biến 90cm
                if GPIO.input(22) == GPIO.LOW:
                    count_90cm += 1
                    GPIO.output(17, GPIO.HIGH)  # Kích hoạt rơ le 90cm
                    time.sleep(1)
                    GPIO.output(17, GPIO.LOW)

                # Kiểm tra cảm biến 45cm
                if GPIO.input(26) == GPIO.LOW:
                    count_45cm += 1
                    GPIO.output(27, GPIO.HIGH)  # Kích hoạt rơ le 45cm
                    time.sleep(1)
                    GPIO.output(27, GPIO.LOW)

                # Điều khiển LED nhấp nháy (bật tắt mỗi 2 giây)
                GPIO.output(25, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(25, GPIO.LOW)
                time.sleep(1)
            else:
                # Hiển thị LCD ban đầu
                humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
                if humidity is not None and temperature is not None:
                    lcd.clear()
                    lcd.write_string(f"DEM SAN PHAM C\n")
                    lcd.write_string(f"Temp: {temperature:.1f}C Hum: {humidity:.1f}%\n")

    except Exception as ex:
        traceback.print_exc()
    finally:
        GPIO.cleanup()  # Đảm bảo ngắt kết nối an toàn

Main()
