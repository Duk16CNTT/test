import sys
import time
import random
import threading
import queue
import paho.mqtt.client as mqtt
from display import Display  # Quản lý LCD 16x2
from sensors import Sensors  # Quản lý cảm biến DHT22
from pH_sensor import PHSensor  # Đọc giá trị từ cảm biến pH thật
import os
from flask import Flask, request, jsonify
import requests  # Dùng để lấy dữ liệu từ Flask API
import subprocess
import json  # Thêm import này để làm việc với file JSON
import platform

try:
    from EmulatorGUI import GPIO  # Giả lập trên Windows
    print("🖥️ Đang chạy giả lập với EmulatorGUI")
    IS_RASPBERRY_PI = False
except ImportError:
    import RPi.GPIO as GPIO  # type: ignore
    print("🍓 Chạy trên Raspberry Pi")
    IS_RASPBERRY_PI = True

GPIO.setmode(GPIO.BCM)

# Chân GPIO
SENSOR_SOIL_MOISTURE = 17
SENSOR_PH = 18
PUMP_WATER = 27
VALVE_NUTRIENT = 22
LED_INDICATOR = 25
LED_BLINK = 5  # Chân giả lập LED nhấp nháy

GPIO.setup(PUMP_WATER, GPIO.OUT)
GPIO.setup(VALVE_NUTRIENT, GPIO.OUT)
GPIO.setup(LED_INDICATOR, GPIO.OUT)
GPIO.setup(LED_BLINK, GPIO.OUT)

BROKER = "mqtt.eclipseprojects.io"
TOPIC_SENSORS = "garden/sensors"

temp, hum, soil_moisture, ph_value = 0, 0, 0, 0  # Lưu giá trị cảm biến mới nhất
queue_gpio = queue.Queue()  # Hàng đợi xử lý GPIO trong luồng chính

app = Flask(__name__)

def safe_gpio_output(pin, state):
    """Đưa cập nhật GPIO vào hàng đợi để xử lý trên luồng chính."""
    queue_gpio.put((pin, state))

def enable_wifi_ap():
    if IS_RASPBERRY_PI:
        os.system("sudo systemctl start hostapd")
        os.system("sudo systemctl start dnsmasq")
        print("📡 WiFi AP đã bật!")
    else:
        print("🚫 Không thể bật WiFi AP trên Windows!")

def disable_wifi_ap():
    if IS_RASPBERRY_PI:
        os.system("sudo systemctl stop hostapd")
        os.system("sudo systemctl stop dnsmasq")
        print("📴 WiFi AP đã tắt!")
    else:
        print("🚫 Không thể tắt WiFi AP trên Windows!")

DEFAULT_THRESHOLD = {
    "soil_threshold": 30.0,  # Ngưỡng độ ẩm đất mặc định (%)
    "ph_min_threshold": 5.5,  # Ngưỡng pH tối thiểu mặc định
    "ph_max_threshold": 7.0   # Ngưỡng pH tối đa mặc định
}
    
def run_flask():
    subprocess.Popen(["python", "D:/nhúng/test-chi/project/flask_server.py"])

class SmartGarden:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connect_mqtt()

        self.running = True
        self.pump_running = False
        self.nutrient_running = False

        # Sử dụng giá trị mặc định
        self.soil_threshold = DEFAULT_THRESHOLD["soil_threshold"]
        self.ph_min_threshold = DEFAULT_THRESHOLD["ph_min_threshold"]
        self.ph_max_threshold = DEFAULT_THRESHOLD["ph_max_threshold"]

        # Đọc cấu hình từ file config.json
        self.load_config()

        self.display = Display()
        self.sensors = Sensors()
        self.ph_sensor = PHSensor()

        self.lock = threading.Lock()
        enable_wifi_ap()  # Bật WiFi khi khởi động hệ thống
        self.start_threads()

    def connect_mqtt(self):
        try:
            self.client.connect(BROKER, 1883, 60)
            self.client.loop_start()
            print("✅ Kết nối MQTT thành công!")
        except Exception as e:
            print(f"❌ Lỗi kết nối MQTT: {e}")
            
    def load_config(self):
        """Đọc config từ file JSON"""
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
            print(f"📂 Đọc dữ liệu từ file JSON: {config}")  # Debug xem file có gì
        
            # Gán giá trị sau khi kiểm tra
            self.system_on = config.get("system_on", True)
            print(f"✅ Trạng thái hệ thống sau khi load: {self.system_on}")  # Debug thêm

            self.soil_threshold = config.get("soil_threshold", DEFAULT_THRESHOLD["soil_threshold"])
            self.ph_min_threshold = config.get("ph_min_threshold", DEFAULT_THRESHOLD["ph_min_threshold"])
            self.ph_max_threshold = config.get("ph_max_threshold", DEFAULT_THRESHOLD["ph_max_threshold"])
        except Exception as e:
            print(f"⚠️ Lỗi đọc file config.json: {e}")
            self.system_on = True  # Nếu có lỗi, mặc định bật hệ thống

    def save_config(self):
        """Lưu trạng thái vào file JSON"""
        try:
            with open("config.json", "w") as file:
                json.dump({
                    "system_on": self.system_on,
                    "soil_threshold": self.soil_threshold,
                    "ph_min_threshold": self.ph_min_threshold,
                    "ph_max_threshold": self.ph_max_threshold
                }, file, indent=4)
                file.flush()  # Đảm bảo dữ liệu ghi ngay vào file
            print(f"💾 Đã lưu cấu hình: {self.system_on}")  # Debug xem giá trị lưu
        except Exception as e:
            print(f"⚠️ Lỗi lưu file config.json: {e}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"Connected with result code {rc}")
        client.subscribe(TOPIC_SENSORS)
    
    def on_message(self, client, userdata, msg):
        print(f"📩 MQTT nhận: {msg.topic} - {msg.payload.decode()}")

    def read_sensors(self):
        """Luồng đọc cảm biến và hiển thị"""
        global temp, hum, soil_moisture, ph_value
        while self.running:
            print(f"🟢 Hệ thống đang {'BẬT' if self.system_on else 'TẮT'}")
            if not self.system_on:
                time.sleep(5)  # Nếu hệ thống tắt, đợi 5 giây rồi kiểm tra lại
                continue

            with self.lock:
                temp = random.uniform(25, 30)
                hum = random.uniform(40, 60)
                soil_moisture = random.uniform(10, 50)
                ph_value = self.ph_sensor.read_ph()

                self.client.publish(TOPIC_SENSORS, f"{temp},{hum},{soil_moisture},{ph_value}")

                print(f"🌡 {temp:.1f}°C | 💧 {hum:.1f}% | 🌱 {soil_moisture:.1f}% | ⚗️ pH {ph_value:.1f}")
                print(f"🚰 Bơm: {'BẬT' if self.pump_running else 'TẮT'} | 🧪 Dinh dưỡng: {'BẬT' if self.nutrient_running else 'TẮT'}")

                self.display.update(round(temp, 1), round(hum, 1), round(soil_moisture, 1), self.pump_running, self.nutrient_running)

            time.sleep(2)

    def check_system_status(self):
        global system_on
        try:
            response = requests.get("http://127.0.0.1:5000/status")
            system_on = response.json()["system_on"]
        except Exception as e:
            print(f"⚠ Lỗi kết nối API: {e}")

    def control_pump(self):
        """Luồng điều khiển máy bơm với giới hạn thời gian chạy"""
        global soil_moisture
        pump_timer = 0
        while self.running:
            if not self.system_on:
                safe_gpio_output(PUMP_WATER, False)
                self.pump_running = False
                time.sleep(5)
                continue

            with self.lock:
                if soil_moisture < self.soil_threshold:
                    if not self.pump_running:
                        pump_timer = time.time()  # Bắt đầu đếm thời gian chạy bơm
                    safe_gpio_output(PUMP_WATER, True)
                    self.pump_running = True
                else:
                    safe_gpio_output(PUMP_WATER, False)
                    self.pump_running = False
        
                if self.pump_running and time.time() - pump_timer > 300:
                    print("⚠️ Máy bơm chạy quá lâu, tự động tắt!")
                    safe_gpio_output(PUMP_WATER, False)
                    self.pump_running = False

            time.sleep(1)

    def control_nutrient(self):
        """Luồng điều khiển bổ sung dinh dưỡng"""
        global ph_value
        while self.running:
            if not self.system_on:
                safe_gpio_output(VALVE_NUTRIENT, False)
                self.nutrient_running = False
                time.sleep(5)
                continue

            with self.lock:
                safe_gpio_output(VALVE_NUTRIENT, ph_value < self.ph_min_threshold or ph_value > self.ph_max_threshold)
                self.nutrient_running = ph_value < self.ph_min_threshold or ph_value > self.ph_max_threshold
            time.sleep(1)

    def blink_led(self):
        """Luồng nhấp nháy LED báo trạng thái"""
        while self.running:
            if not self.system_on:
                safe_gpio_output(LED_BLINK, False)
                time.sleep(5)
                continue

            safe_gpio_output(LED_BLINK, True)
            time.sleep(1)
            safe_gpio_output(LED_BLINK, False)
            time.sleep(1)

    def gpio_handler(self):
        """Luồng chính cập nhật GPIO từ queue"""
        while self.running:
            while not queue_gpio.empty():
                try:
                    pin, state = queue_gpio.get()
                    GPIO.output(pin, state)
                except RuntimeError:
                    print("⚠️ Lỗi cập nhật GPIO, hệ thống sẽ dừng!")
                    self.stop_system()
            time.sleep(1)

    def set_threshold(self, new_threshold):
        self.threshold = new_threshold
        print(f"🔄 Ngưỡng mới được cập nhật: {self.threshold}")

    def start_threads(self):
        """Bắt đầu các luồng"""
        threading.Thread(target=self.read_sensors, daemon=True).start()
        threading.Thread(target=self.control_pump, daemon=True).start()
        threading.Thread(target=self.control_nutrient, daemon=True).start()
        threading.Thread(target=self.blink_led, daemon=True).start()
        threading.Thread(target=self.gpio_handler, daemon=True).start()

    def stop_system(self):
        print("⏹ Dừng hệ thống!")
        self.running = False
        safe_gpio_output(PUMP_WATER, False)
        safe_gpio_output(VALVE_NUTRIENT, False)
        safe_gpio_output(LED_INDICATOR, False)
        safe_gpio_output(LED_BLINK, False)
        self.client.loop_stop()
        disable_wifi_ap() 
        GPIO.cleanup()
        sys.exit(0)

@app.route("/toggle_system", methods=["POST"])
def toggle_system():
    garden.load_config()  # Load lại cấu hình vào biến trong class
    settings = {
        "system_on": garden.system_on   
    }
    print(f"📌 Trước khi đổi trạng thái: {settings['system_on']}")

    settings["system_on"] = not settings.get("system_on", False)  # Đảo trạng thái
    print(f"🔄 Sau khi đổi trạng thái: {settings['system_on']}")

    # Chạy GPIO nếu trên Raspberry Pi
    if platform.system() == "Linux":
        GPIO.output(17, GPIO.HIGH if settings["system_on"] else GPIO.LOW)
    else:
        print(f"🖥️ Giả lập: {'Bật' if settings['system_on'] else 'Tắt'} hệ thống!")

    garden.save_config()    
    
    # Kiểm tra file lưu có đúng không
    with open("config.json", "r") as file:
        saved_data = json.load(file)
        print(f"📂 Kiểm tra file JSON sau khi ghi: {saved_data}")
    time.sleep(2)
    return jsonify({"system_on": settings["system_on"]})

if __name__ == "__main__":
    try:
        garden = SmartGarden()  # Khởi động hệ thống chính

        # Chạy Flask trong Thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        # Chờ Flask khởi động
        time.sleep(2)
        flask_ready = False
        for i in range(5):
            try:
                response = requests.get("http://127.0.0.1:5000/settings", timeout=3)
                if response.status_code == 200:
                    print("✅ Flask đã sẵn sàng:", response.json())
                    flask_ready = True
                    break
            except (requests.ConnectionError, requests.Timeout):
                print(f"⏳ Đang chờ Flask khởi động... ({i+1}/10)")
            time.sleep(1)

        if not flask_ready:
            print("🚫 Lỗi: Flask không khởi động sau 10 giây!")
            sys.exit(1)

        # Chạy chương trình chính
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("⏹ Dừng hệ thống do người dùng nhấn Ctrl+C!")
        garden.stop_system()
        sys.exit(0)  # Thoát chương trình an toàn
    except Exception as e:
        print(f"⚠️ Lỗi không mong muốn: {e}\n⏹ Dừng hệ thống!")
        garden.stop_system()
        sys.exit(1)