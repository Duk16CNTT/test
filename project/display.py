from pnhLCD1602 import LCD1602  # Import thư viện LCD giả lập 

class Display:
    def __init__(self):
        """ Khởi tạo màn hình LCD 16x2 """
        try:
            self.lcd = LCD1602()
            self.lcd.clear()
            print("✅ LCD 16x2 giả lập đã sẵn sàng!")
        except Exception as e:
            print(f"⚠️ Lỗi LCD: {e}")
            self.lcd = None  # Nếu lỗi, bỏ qua LCD

    def update(self, temp, hum, soil, pump_status, nutrient_status):
        """ Cập nhật thông tin lên màn hình LCD """
        pump_text = "ON" if pump_status else "OFF"
        nutrient_text = "ON" if nutrient_status else "OFF"

        # Debug kiểm tra terminal
        print(f"📟 LCD Update: T={temp}C, H={hum}%, Soil={soil}%, Pump={pump_text}, Nutrient={nutrient_text}")

        if self.lcd:
            try:
                self.lcd.clear()
                self.lcd.set_cursor(0, 0)  
                self.lcd.write_string(f"T:{temp}C H:{hum}%")  

                self.lcd.set_cursor(1, 0)  
                self.lcd.write_string(f"{soil}% P:{pump_text} N:{nutrient_text}")

            except Exception as e:
                print(f"⚠️ Lỗi khi ghi LCD: {e}")

    def clear(self):
        """ Xóa màn hình LCD """
        if self.lcd:
            try:
                self.lcd.clear()
            except Exception as e:
                print(f"⚠️ Lỗi khi xóa LCD: {e}")

# 🛠 Kiểm tra nếu chạy riêng file này
if __name__ == "__main__":
    display = Display()
    display.update(25, 60, 40, True, False)
