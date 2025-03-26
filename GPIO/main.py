from EmulatorGUI import GPIO
from lcd_display import LCD  # Import lớp giả lập LCD
import time
import random
import threading
import queue

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Cấu hình GPIO
TRIG = 20  # Chân Trigger của cảm biến siêu âm
ECHO = 21  # Chân Echo của cảm biến siêu âm
PUMP = 16  # Chân điều khiển bơm
BTN_SET_K = 23  # Nút thiết lập giá trị k
LED = 4  # LED báo trạng thái

GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(PUMP, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BTN_SET_K, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)

# Khởi tạo LCD giả lập
lcd = LCD()
lcd.lcd_display_string("MUC CHAT LONG: -- cm", 1)
lcd.lcd_display_string("K: -- cm PUMP: OFF", 2)

# Biến trạng thái
k = 30  # Giá trị mức chất lỏng mong muốn (cm)
pump_running = False

# Hàng đợi để cập nhật LCD và LED
queue_lcd = queue.Queue()
queue_led = queue.Queue()

def measure_distance():
    """Giả lập đo khoảng cách từ cảm biến siêu âm."""
    return round(random.uniform(10, 50), 1)

def control_pump():
    """Luồng điều khiển bơm và đọc nút nhấn."""
    global k, pump_running
    while True:
        level = measure_distance()
        if GPIO.input(BTN_SET_K) == 0:
            k = round(random.uniform(20, 40), 1)
            time.sleep(0.5)
        if level > k + 5:
            GPIO.output(PUMP, GPIO.HIGH)
            pump_running = True
        elif level < k - 5:
            GPIO.output(PUMP, GPIO.LOW)
            pump_running = False
        
        # Đưa dữ liệu vào hàng đợi để xử lý trong luồng chính
        queue_lcd.put((level, k, pump_running))
        queue_led.put(pump_running)
        time.sleep(1)

try:
    threading.Thread(target=control_pump, daemon=True).start()
    while True:
        # Cập nhật LCD từ luồng chính
        while not queue_lcd.empty():
            level, k, pump_status = queue_lcd.get()
            lcd.lcd_display_string(f"MUC CHAT LONG:{level}cm", 1)
            lcd.lcd_display_string(f"K:{k}cm PUMP:{'ON' if pump_status else'OFF'}", 2)
        
        # Cập nhật LED từ luồng chính
        while not queue_led.empty():
            pump_status = queue_led.get()
            GPIO.output(LED, GPIO.HIGH if pump_status else GPIO.LOW)
        
        time.sleep(1)
except KeyboardInterrupt:
    print("Thoát chương trình...")
finally:
    GPIO.cleanup()
