from EmulatorGUI import GPIO
from lcd_display import LCD  # Import lớp giả lập LCD
import time
import traceback
import random  # Giả lập nhiệt độ, độ ẩm

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Cấu hình GPIO
GPIO.setup(4, GPIO.OUT)  # LED báo hiệu hoạt động
GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)  # Rơ le 90cm
GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW)  # Rơ le 45cm
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Nút Start
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Nút Stop
GPIO.setup(22, GPIO.IN)  # Cảm biến 90cm
GPIO.setup(26, GPIO.IN)  # Cảm biến 45cm

# Khởi tạo LCD giả lập
lcd = LCD()
lcd.lcd_display_string("DEM SAN PHAM C", 1)
lcd.lcd_display_string("Temp: --C Hum: --%", 2)

# Biến trạng thái
running = False
count_90cm = 0
count_45cm = 0

def read_temp_humidity():
    """Giả lập đọc nhiệt độ và độ ẩm từ cảm biến DHT22."""
    temp = round(random.uniform(20, 35), 1)
    humidity = round(random.uniform(40, 80), 1)
    return temp, humidity

try:
    while True:
        if GPIO.input(23) == 0:  # Nhấn Start
            running = True
            lcd.lcd_display_string("HE THONG CHAY...", 1)
            time.sleep(0.5)

        if GPIO.input(24) == 0:  # Nhấn Stop
            running = False
            lcd.lcd_display_string("HE THONG DUNG", 1)
            time.sleep(0.5)

        if running:
            # Xử lý cảm biến chiều cao
            if GPIO.input(22) == 0:  # Cảm biến 90cm kích hoạt
                GPIO.output(17, GPIO.HIGH)
                count_90cm += 1
                time.sleep(1)
                GPIO.output(17, GPIO.LOW)

            if GPIO.input(26) == 0:  # Cảm biến 45cm kích hoạt
                GPIO.output(27, GPIO.HIGH)
                count_45cm += 1
                time.sleep(1)
                GPIO.output(27, GPIO.LOW)

            # Cập nhật nhiệt độ, độ ẩm và hiển thị LCD
            temp, humidity = read_temp_humidity()
            lcd.lcd_display_string(f"Temp:{temp}C Hum:{humidity}%", 1)
            lcd.lcd_display_string(f"90c={count_90cm} 45c={count_45cm}", 2)

            # LED nhấp nháy
            GPIO.output(4, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(4, GPIO.LOW)
            time.sleep(1)

except KeyboardInterrupt:
    print("Thoát chương trình...")
finally:
    GPIO.cleanup()
