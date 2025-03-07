from EmulatorGUI import GPIO
#import RPi.GPIO as GPIO
import time
import traceback



# Cấu hình GPIO
led_pins = [2, 3, 4, 17, 27, 22, 10, 9]  # Chân GPIO cho 8 LED
BUTTON_PIN = 11  # Chân GPIO cho nút nhấn
# Biến để kiểm soát trạng thái nháy LED
running = False
 

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
 

for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Tắt tất cả LED ban đầu
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Thiết lập nút nhấn
 

def button_callback(channel):
    global running
    running = not running  # Đảo trạng thái chạy
    print("Nhay LED") if running==True else print("Dung nhay LED")
 

# Đăng ký sự kiện cho nút nhấn
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)
 

try:
    while True:
        if running:
            for pin in led_pins:
                GPIO.output(pin, GPIO.HIGH)  # Bật LED
                time.sleep(1)  # Đợi 1 giây
                GPIO.output(pin, GPIO.LOW)  # Tắt LED
        else:
            # Nếu không chạy, tắt tất cả LED
            for pin in led_pins:
                GPIO.output(pin, GPIO.LOW)
 

except Exception as ex:
        traceback.print_exc() # Báo lỗi
 

finally:
    GPIO.cleanup()  # Dọn dẹp GPIO khi thoát