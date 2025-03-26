import random
import time

class PHSensor:
    def __init__(self, min_ph=4.0, max_ph=9.0):
        """
        Mô phỏng cảm biến pH đất.
        :param min_ph: Giá trị pH tối thiểu (mặc định 4.0)
        :param max_ph: Giá trị pH tối đa (mặc định 9.0)
        """
        self.min_ph = min_ph
        self.max_ph = max_ph

    def read_ph(self):
        """
        Mô phỏng đọc giá trị pH từ cảm biến.
        :return: Giá trị pH ngẫu nhiên trong khoảng [min_ph, max_ph]
        """
        return round(random.uniform(self.min_ph, self.max_ph), 2)

if __name__ == "__main__":
    sensor = PHSensor()
    while True:
        ph_value = sensor.read_ph()
        print(f"Giá trị pH giả lập: {ph_value}")
        time.sleep(1)
