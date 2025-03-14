from DHT22 import readSensor
import random  # Thêm thư viện để tạo số ngẫu nhiên

class Sensors:
    def __init__(self, pin=4):
        """ Khởi tạo cảm biến DHT22 giả lập """
        self.pin = pin

    def read_dht22(self):
        """ Đọc dữ liệu từ DHT22 """
        temp, hum = readSensor(self.pin)
        return round(temp, 1), round(hum, 1)

    def read_soil_moisture(self):
        """ Giả lập đọc độ ẩm đất (trả về % độ ẩm) """
        return round(random.uniform(20, 60), 1)  # Giá trị ngẫu nhiên từ 20% đến 60%

    def read_ph(self):
        """ Giả lập đọc giá trị pH đất """
        return round(random.uniform(5.0, 8.0), 1)  # Giá trị pH ngẫu nhiên từ 5.0 đến 8.0

# 🛠 Kiểm tra nếu chạy riêng file này
if __name__ == "__main__":
    sensor = Sensors()
    temp, hum = sensor.read_dht22()
    soil_moisture = sensor.read_soil_moisture()
    ph_value = sensor.read_ph()
    
    print(f"Nhiệt độ: {temp}°C, Độ ẩm: {hum}%")
    print(f"Độ ẩm đất: {soil_moisture}%, pH đất: {ph_value}")
