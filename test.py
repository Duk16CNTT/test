import sys
import time
import random
import tkinter as tk
import paho.mqtt.client as mqtt
from display import Display  # Quản lý LCD 16x2
from sensors import Sensors  # Quản lý cảm biến DHT22

try:
    from EmulatorGUI import GPIO  # Giả lập trên Windows
    print("🖥️ Đang chạy giả lập với EmulatorGUI")
except ImportError:
    import RPi.GPIO as GPIO  # type: ignore
    print("🍓 Chạy trên Raspberry Pi")

GPIO.setmode(GPIO.BCM)

# Chân GPIO
SENSOR_SOIL_MOISTURE = 17
SENSOR_PH = 18
PUMP_WATER = 27
VALVE_NUTRIENT = 22
LED_INDICATOR = 25
LED_BLINK = 5  # Chân GPIO điều khiển LED nhấp nháy


# Cấu hình GPIO
GPIO.setup(PUMP_WATER, GPIO.OUT)
GPIO.setup(VALVE_NUTRIENT, GPIO.OUT)
GPIO.setup(LED_INDICATOR, GPIO.OUT)
GPIO.setup(LED_BLINK, GPIO.OUT)


# MQTT Configuration
BROKER = "mqtt.eclipseprojects.io"
TOPIC_SENSORS = "garden/sensors"
TOPIC_CONTROL = "garden/control"

class SmartGardenGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌱 Hệ thống chăm bón cây tự động")

        # MQTT
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connect_mqtt()

        self.running = False
        self.pump_running = False
        self.nutrient_running = False

        # Ngưỡng cảm biến
        self.soil_threshold = tk.DoubleVar(value=30)
        self.ph_min_threshold = tk.DoubleVar(value=5.5)
        self.ph_max_threshold = tk.DoubleVar(value=7.0)

        # Hiển thị thông tin
        self.temp_label = tk.Label(self.root, text="🌡 Nhiệt độ: --°C", font=("Arial", 14))
        self.hum_label = tk.Label(self.root, text="💧 Độ ẩm không khí: --%", font=("Arial", 14))
        self.soil_label = tk.Label(self.root, text="🌱 Độ ẩm đất: --%", font=("Arial", 14))
        self.ph_label = tk.Label(self.root, text="⚗️ Độ pH: --", font=("Arial", 14))
        self.pump_status_label = tk.Label(self.root, text="🚰 Máy bơm: TẮT", font=("Arial", 14), fg="red")
        self.nutrient_status_label = tk.Label(self.root, text="🧪 Dinh dưỡng: TẮT", font=("Arial", 14), fg="red")

        self.temp_label.pack(pady=5)
        self.hum_label.pack(pady=5)
        self.soil_label.pack(pady=5)
        self.ph_label.pack(pady=5)
        self.pump_status_label.pack(pady=5)
        self.nutrient_status_label.pack(pady=5)

        self.create_threshold_controls()

        #Đảm bảo tắt led
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.start_button = tk.Button(self.root, text="▶ Chạy hệ thống", command=self.start_system, font=("Arial", 12))
        self.stop_button = tk.Button(self.root, text="⏹ Dừng hệ thống", command=self.stop_system, font=("Arial", 12))
        self.update_button = tk.Button(self.root, text="🔄 Cập nhật ngưỡng", command=self.update_thresholds, font=("Arial", 12))

        self.start_button.pack(pady=5)
        self.stop_button.pack(pady=5)
        self.update_button.pack(pady=5)

        self.display = Display()
        self.sensors = Sensors()

        self.root.mainloop()

    def create_threshold_controls(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Ngưỡng độ ẩm đất (%):").grid(row=0, column=0)
        self.soil_threshold_entry = tk.Entry(frame)
        self.soil_threshold_entry.grid(row=0, column=1)
        self.soil_threshold_entry.insert(0, "30")  # Giá trị mặc định

        tk.Label(frame, text="pH Min:").grid(row=1, column=0)
        self.ph_min_threshold_entry = tk.Entry(frame)
        self.ph_min_threshold_entry.grid(row=1, column=1)
        self.ph_min_threshold_entry.insert(0, "5.5")  # Giá trị mặc định

        tk.Label(frame, text="pH Max:").grid(row=2, column=0)
        self.ph_max_threshold_entry = tk.Entry(frame)
        self.ph_max_threshold_entry.grid(row=2, column=1)
        self.ph_max_threshold_entry.insert(0, "7.0")  # Giá trị mặc định


    def update_thresholds(self):
        """ Cập nhật ngưỡng từ giao diện nhập liệu và kiểm tra tính hợp lệ """
        try:
            soil_value = int(self.soil_threshold_entry.get())  # Đọc từ Entry và chuyển đổi sang số nguyên
            ph_min_value = float(self.ph_min_threshold_entry.get())
            ph_max_value = float(self.ph_max_threshold_entry.get())

            # Cập nhật biến tk.DoubleVar thay vì ghi đè nó
            self.soil_threshold.set(soil_value)
            self.ph_min_threshold.set(ph_min_value)
            self.ph_max_threshold.set(ph_max_value)

            print(f"✅ Đã cập nhật ngưỡng: Độ ẩm đất={soil_value}%, pH=[{ph_min_value} - {ph_max_value}]")

        except ValueError:
            print("⚠️ Lỗi: Vui lòng nhập số hợp lệ cho ngưỡng!")

    def read_sensors(self):
        soil_moisture = random.uniform(10, 50)
        ph_value = random.uniform(4.5, 8.5)
        return soil_moisture, ph_value

    def update_display(self, temp, hum, soil, ph):
        """Cập nhật GUI & LCD với dữ liệu mới"""
        self.temp_label.config(text=f"🌡 Nhiệt độ: {temp:.1f}°C")
        self.hum_label.config(text=f"💧 Độ ẩm không khí: {hum:.1f}%")
        self.soil_label.config(text=f"🌱 Độ ẩm đất: {soil:.1f}%")
        self.ph_label.config(text=f"⚗️ Độ pH: {ph:.1f}")

        pump_status = "BẬT" if self.pump_running else "TẮT"
        nutrient_status = "BẬT" if self.nutrient_running else "TẮT"

        self.pump_status_label.config(text=f"🚰 Máy bơm: {pump_status}", fg="green" if self.pump_running else "red")
        self.nutrient_status_label.config(text=f"🧪 Dinh dưỡng: {nutrient_status}", fg="green" if self.nutrient_running else "red")

        print(f"Debug: Máy bơm={pump_status}, Dinh dưỡng={nutrient_status}")

        # Cập nhật màn hình LCD (truyền đủ 5 tham số)
        self.display.update(round(temp, 1), round(hum, 1), round(soil, 1), self.pump_running, self.nutrient_running)

    def blink_led(self):
        """ LED nhấp nháy mỗi giây khi hệ thống đang chạy """
        if self.running:
            GPIO.output(LED_BLINK, True)  # Bật LED
            self.root.after(500, self.turn_off_led)  # Sau 0.5s tắt LED
        else:
            GPIO.output(LED_BLINK, False)  # Đảm bảo LED tắt khi hệ thống dừng

    def turn_off_led(self):
        """ Tắt LED sau khi nhấp nháy 0.5s """
        if self.running:
            GPIO.output(LED_BLINK, False)  # Tắt LED
            self.root.after(500, self.blink_led)  # Sau 0.5s bật lại

    def start_system(self):
        print("✅ Hệ thống đã khởi động!")
        self.running = True
        self.run_system()
        self.blink_led()

    def stop_system(self):
        print("⏹ Hệ thống đã dừng!")
        self.running = False
    
        # Tắt tất cả thiết bị
        GPIO.output(PUMP_WATER, False)
        GPIO.output(VALVE_NUTRIENT, False)
        GPIO.output(LED_BLINK, False)

        # Đảm bảo trạng thái dừng cập nhật đúng
        self.pump_running = False
        self.nutrient_running = False
        self.update_status_labels()

        # Dừng MQTT loop
        self.client.loop_stop()

    def run_system(self):
        if not self.running:
            return

        temp = random.uniform(25, 30)
        hum = random.uniform(40, 60)
        soil, ph = self.read_sensors()

        self.control_pump_and_nutrient(soil, ph)
        self.update_display(temp, hum, soil, ph)  # Cập nhật UI
        self.client.publish(TOPIC_SENSORS, f"{temp},{hum},{soil},{ph}")

        self.root.after(2000, self.run_system)  # Sửa lỗi gọi đệ quy

    def control_pump_and_nutrient(self, soil, ph):
        """ Điều khiển bơm nước và bổ sung dinh dưỡng dựa trên giá trị cảm biến và ngưỡng """
        soil_threshold = self.soil_threshold.get()
        ph_min = self.ph_min_threshold.get()
        ph_max = self.ph_max_threshold.get()

        if soil < soil_threshold:
            GPIO.output(PUMP_WATER, True)
            self.pump_running = True
        else:
            GPIO.output(PUMP_WATER, False)
            self.pump_running = False

        if ph < ph_min or ph > ph_max:
            GPIO.output(VALVE_NUTRIENT, True)
            self.nutrient_running = True
        else:
            GPIO.output(VALVE_NUTRIENT, False)
            self.nutrient_running = False

        self.update_status_labels()


    def update_status_labels(self):
        self.pump_status_label.config(text=f"🚰 Máy bơm: {'BẬT' if self.pump_running else 'TẮT'}", fg="green" if self.pump_running else "red")
        self.nutrient_status_label.config(text=f"🧪 Dinh dưỡng: {'BẬT' if self.nutrient_running else 'TẮT'}", fg="green" if self.nutrient_running else "red")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"🔗 Kết nối MQTT với mã trạng thái {rc}")
        client.subscribe(TOPIC_SENSORS)

    def on_message(self, client, userdata, msg):
        print(f"📩 Nhận dữ liệu từ MQTT: {msg.payload.decode()}")

    def connect_mqtt(self):
        try:
            self.client.connect(BROKER, 1883, 60)
            self.client.loop_start()
            print("✅ Kết nối MQTT thành công!")
        except Exception as e:
            print(f"❌ Lỗi kết nối MQTT: {e}")
            self.root.after(5000, self.connect_mqtt)

    def on_closing(self):
        """ Đóng cửa sổ và giải phóng tài nguyên """
        print("🔌 Đóng chương trình, giải phóng GPIO...")

        # Ngừng hệ thống
        self.stop_system()

        # Ngừng MQTT nếu đang chạy
        if hasattr(self, 'client'):
            self.client.loop_stop()
            self.client.disconnect()

        #    Hủy bỏ toàn bộ biến Tkinter tránh lỗi "main thread is not in main loop"
        for widget in self.root.winfo_children():
            widget.destroy()

        # Giải phóng GPIO (chỉ thực hiện nếu trên Raspberry Pi)
        if "RPi" in sys.modules:
            GPIO.cleanup()

        # Đảm bảo cửa sổ Tkinter đóng đúng cách
        self.root.quit()
        self.root.destroy()

        # Thoát chương trình hoàn toàn
        sys.exit(0)


if __name__ == "__main__":
    SmartGardenGUI()
