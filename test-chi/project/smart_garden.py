import sys
import time
import random
import tkinter as tk
import paho.mqtt.client as mqtt
from display import Display  # Quản lý LCD 16x2
from sensors import Sensors  # Quản lý cảm biến DHT22

try:
    from EmulatorGUI import GPIO  # Thư viện giả lập của bạn
    print("\U0001F5A5️ Đang chạy giả lập với EmulatorGUI")
except ImportError:
    import RPi.GPIO as GPIO  # type: ignore
    print("\U0001F353 Chạy trên Raspberry Pi")

GPIO.setmode(GPIO.BCM)

SENSOR_SOIL_MOISTURE = 17
PUMP_WATER = 27
VALVE_NUTRIENT = 22
LED_INDICATOR = 25

GPIO.setup(SENSOR_SOIL_MOISTURE, GPIO.IN)
GPIO.setup(PUMP_WATER, GPIO.OUT)
GPIO.setup(VALVE_NUTRIENT, GPIO.OUT)
GPIO.setup(LED_INDICATOR, GPIO.OUT)

BROKER = "mqtt.eclipseprojects.io"
TOPIC_SENSORS = "garden/sensors"
TOPIC_CONTROL = "garden/control"

class SmartGardenGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("\U0001F331 Hệ thống chăm bón cây tự động")

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER, 1883, 60)
        self.client.loop_start()

        self.soil_threshold = 30  
        self.hum_threshold = 40   

        self.temp_label = tk.Label(self.root, text="\U0001F321 Nhiệt độ: --°C", font=("Arial", 14))
        self.hum_label = tk.Label(self.root, text="\U0001F4A7 Độ ẩm không khí: --%", font=("Arial", 14))
        self.soil_label = tk.Label(self.root, text="\U0001F33F Độ ẩm đất: --%", font=("Arial", 14))

        self.pump_status_label = tk.Label(self.root, text="\U0001F6B0 Máy bơm: TẮT", font=("Arial", 14), fg="red")
        self.nutrient_status_label = tk.Label(self.root, text="\U0001F48A Phân bón: TẮT", font=("Arial", 14), fg="red")

        self.soil_threshold_entry = tk.Entry(self.root, font=("Arial", 12))
        self.soil_threshold_entry.insert(0, str(self.soil_threshold))
        self.hum_threshold_entry = tk.Entry(self.root, font=("Arial", 12))
        self.hum_threshold_entry.insert(0, str(self.hum_threshold))
        
        self.update_threshold_button = tk.Button(self.root, text="Cập nhật ngưỡng", command=self.update_threshold, font=("Arial", 12))
        
        self.start_button = tk.Button(self.root, text="\U0001F504 Chạy hệ thống", command=self.start_system, font=("Arial", 12))
        self.stop_button = tk.Button(self.root, text="⏹ Dừng hệ thống", command=self.stop_system, font=("Arial", 12))

        self.pump_running = False
        self.nutrient_running = False
        self.running = False

        self.temp_label.pack(pady=5)
        self.hum_label.pack(pady=5)
        self.soil_label.pack(pady=5)
        self.pump_status_label.pack(pady=5)
        self.nutrient_status_label.pack(pady=5)

        tk.Label(self.root, text="Ngưỡng độ ẩm đất (%):").pack()
        self.soil_threshold_entry.pack(pady=5)
        tk.Label(self.root, text="Ngưỡng độ ẩm không khí (%):").pack()
        self.hum_threshold_entry.pack(pady=5)
        self.update_threshold_button.pack(pady=5)

        self.start_button.pack(pady=5)
        self.stop_button.pack(pady=5)

        self.display = Display()
        self.sensors = Sensors()
        self.root.mainloop()

    def update_threshold(self):
        try:
            self.soil_threshold = int(self.soil_threshold_entry.get())
            self.hum_threshold = int(self.hum_threshold_entry.get())
            print(f"✅ Đã cập nhật ngưỡng: Độ ẩm đất={self.soil_threshold}%, Độ ẩm không khí={self.hum_threshold}%")
        except ValueError:
            print("⚠️ Lỗi: Vui lòng nhập số hợp lệ cho ngưỡng!")

    def on_connect(self, client, userdata, flags, rc):
        print("🔗 Kết nối MQTT thành công!")
        client.subscribe(TOPIC_CONTROL)

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        print(f"📩 Nhận lệnh từ MQTT: {message}")
        if message == "START":
            self.start_system()
        elif message == "STOP":
            self.stop_system()

    def read_sensors(self):
        temp, hum = self.sensors.read_dht22()
        soil = round(random.uniform(10, 80), 1)
        self.client.publish(TOPIC_SENSORS, f"{temp},{hum},{soil}")
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


    def run_system(self):
        if self.running:
            temp, hum, soil = self.read_sensors()
            
            self.pump_running = soil < self.soil_threshold
            self.nutrient_running = hum < self.hum_threshold
            
            GPIO.output(PUMP_WATER, GPIO.HIGH if self.pump_running else GPIO.LOW)
            GPIO.output(VALVE_NUTRIENT, GPIO.HIGH if self.nutrient_running else GPIO.LOW)
            
            self.update_display(temp, hum, soil)
            self.root.after(3000, self.run_system)

    def start_system(self):
        if not self.running:
            self.running = True
            self.run_system()

    def stop_system(self):
        self.running = False
        GPIO.output(PUMP_WATER, GPIO.LOW)
        GPIO.output(VALVE_NUTRIENT, GPIO.LOW)
        self.pump_status_label.config(text="\U0001F6B0 Máy bơm: TẮT", fg="red")
        self.nutrient_status_label.config(text="\U0001F48A Phân bón: TẮT", fg="red")
        print("⏹ Hệ thống đã dừng")

if __name__ == "__main__":
    SmartGardenGUI()
