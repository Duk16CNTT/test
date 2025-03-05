import sys
import time
import random
import tkinter as tk
from display import Display  # Quản lý LCD 16x2
from sensors import Sensors  # Quản lý cảm biến DHT22

# Dùng thư viện giả lập GPIO từ file bạn đã tải lên
try:
    from EmulatorGUI import GPIO  # Thư viện giả lập của bạn
    print("\U0001F5A5️ Đang chạy giả lập với EmulatorGUI")
except ImportError:
    import RPi.GPIO as GPIO  # type: ignore # Dùng trên Raspberry Pi thật
    print("\U0001F353 Chạy trên Raspberry Pi")

# Cấu hình GPIO
GPIO.setmode(GPIO.BCM)

# Chân GPIO mô phỏng cảm biến & thiết bị
SENSOR_SOIL_MOISTURE = 17
PUMP_WATER = 27
VALVE_NUTRIENT = 22
LED_INDICATOR = 25

GPIO.setup(SENSOR_SOIL_MOISTURE, GPIO.IN)
GPIO.setup(PUMP_WATER, GPIO.OUT)
GPIO.setup(VALVE_NUTRIENT, GPIO.OUT)
GPIO.setup(LED_INDICATOR, GPIO.OUT)

# GUI Giả lập
class SmartGardenGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("\U0001F331 Hệ thống chăm bón cây tự động")

        self.temp_label = tk.Label(self.root, text="\U0001F321 Nhiệt độ: --°C", font=("Arial", 14))
        self.hum_label = tk.Label(self.root, text="\U0001F4A7 Độ ẩm không khí: --%", font=("Arial", 14))
        self.soil_label = tk.Label(self.root, text="\U0001F33F Độ ẩm đất: --%", font=("Arial", 14))

        self.pump_status_label = tk.Label(self.root, text="\U0001F6B0 Máy bơm: TẮT", font=("Arial", 14), fg="red")
        self.nutrient_status_label = tk.Label(self.root, text="\U0001F48A Phân bón: TẮT", font=("Arial", 14), fg="red")

        self.start_button = tk.Button(self.root, text="\U0001F504 Chạy hệ thống", command=self.start_system, font=("Arial", 12))
        self.stop_button = tk.Button(self.root, text="⏹ Dừng hệ thống", command=self.stop_system, font=("Arial", 12))

        # Biến trạng thái của bơm nước và van phân bón
        self.pump_running = False
        self.nutrient_running = False
        self.running = False

        # Sắp xếp giao diện
        self.temp_label.pack(pady=5)
        self.hum_label.pack(pady=5)
        self.soil_label.pack(pady=5)
        self.pump_status_label.pack(pady=5)
        self.nutrient_status_label.pack(pady=5)
        self.start_button.pack(pady=5)
        self.stop_button.pack(pady=5)

        self.display = Display()
        self.sensors = Sensors()
        self.root.mainloop()

    def read_sensors(self):
        """ Đọc dữ liệu từ cảm biến nhiệt độ, độ ẩm và độ ẩm đất """
        temp, hum = self.sensors.read_dht22()
        soil = round(random.uniform(10, 80), 1)
        return temp, hum, soil

    def update_display(self, temp, hum, soil):
        """ Cập nhật GUI & LCD với dữ liệu mới """
        self.temp_label.config(text=f"\U0001F321 Nhiệt độ: {temp}°C")
        self.hum_label.config(text=f"\U0001F4A7 Độ ẩm không khí: {hum}%")
        self.soil_label.config(text=f"\U0001F33F Độ ẩm đất: {soil}%")

        pump_status = "ON" if self.pump_running else "OFF"
        nutrient_status = "ON" if self.nutrient_running else "OFF"

        self.pump_status_label.config(text=f"\U0001F6B0 Máy bơm: {pump_status}", fg="green" if self.pump_running else "red")
        self.nutrient_status_label.config(text=f"\U0001F48A Phân bón: {nutrient_status}", fg="green" if self.nutrient_running else "red")

        print(f"Debug: Pump={pump_status}, Nutrient={nutrient_status}")

        self.display.update(temp, hum, soil, self.pump_running, self.nutrient_running)

    def start_system(self):
        """ Bắt đầu hệ thống nếu chưa chạy """
        if not self.running:
            self.running = True
            self.run_system()

    def run_system(self):
        """ Chạy hệ thống tự động mà không làm treo GUI """
        if self.running:
            temp, hum, soil = self.read_sensors()
            self.update_display(temp, hum, soil)
            self.root.after(3000, self.run_system)  # Gọi lại sau 3 giây

    def stop_system(self):
        """ Dừng hệ thống """
        self.running = False
        GPIO.output(PUMP_WATER, GPIO.LOW)
        GPIO.output(VALVE_NUTRIENT, GPIO.LOW)
        self.pump_running = False
        self.nutrient_running = False

        self.pump_status_label.config(text="\U0001F6B0 Máy bơm: TẮT", fg="red")
        self.nutrient_status_label.config(text="\U0001F48A Phân bón: TẮT", fg="red")
        print("⏹ Hệ thống đã dừng")

# Chạy giao diện
if __name__ == "__main__":
    SmartGardenGUI()
