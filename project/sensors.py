from DHT22 import readSensor

class Sensors:
    def __init__(self, pin=4):
        """ Khởi tạo cảm biến DHT22 giả lập """
        self.pin = pin

    def read_dht22(self):
        """ Đọc dữ liệu từ DHT22 """
        temp, hum = readSensor(self.pin)
        return round(temp, 1), round(hum, 1)

# 🛠 Kiểm tra nếu chạy riêng file này
if __name__ == "__main__":
    sensor = Sensors()
    temp, hum = sensor.read_dht22()
    print(f"Nhiệt độ: {temp}°C, Độ ẩm: {hum}%")
