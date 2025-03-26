import json
import platform
from flask import Flask, request, jsonify, render_template

# Nếu chạy trên Raspberry Pi, import RPi.GPIO, nếu không thì giả lập
if platform.system() == "Linux":
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
else:
    print("🖥️ Đang chạy giả lập, không dùng GPIO thật!")

# Khởi tạo Flask
app = Flask(__name__)

# Đường dẫn lưu file cấu hình
CONFIG_FILE = "config.json"

# Hàm đọc cấu hình từ file JSON
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        default_config = {
            "soil_threshold": 30,
            "ph_min_threshold": 5.5,
            "ph_max_threshold": 7.0,
            "system_on": False
        }
        save_config(default_config)
        return default_config

# Hàm ghi cấu hình vào file JSON
def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

# Giao diện web chính
@app.route('/')
def index():
    settings = load_config()
    return render_template("index.html", settings=settings)

# Cập nhật ngưỡng từ giao diện web
@app.route('/settings', methods=['POST'])
def update_settings():
    settings = load_config()
    try:
        settings['soil_threshold'] = int(request.form['soil_threshold'])
        settings['ph_min_threshold'] = float(request.form['ph_min_threshold'])
        settings['ph_max_threshold'] = float(request.form['ph_max_threshold'])
        save_config(settings)
        message = "✅ Cập nhật thành công!"
    except ValueError:
        message = "❌ Lỗi: Giá trị nhập không hợp lệ!"
    
    return render_template("index.html", settings=settings, message=message)

# API lấy ngưỡng hiện tại
@app.route('/settings', methods=['GET'])
def get_settings():
    return jsonify(load_config())

# API bật/tắt hệ thống
@app.route("/toggle_system", methods=["POST"])
def toggle_system():
    settings = load_config()
    settings["system_on"] = not settings.get("system_on", False)  # Đảo trạng thái hệ thống

    # Chạy GPIO nếu trên Raspberry Pi
    if platform.system() == "Linux":
        GPIO.output(17, GPIO.HIGH if settings["system_on"] else GPIO.LOW)
    else:
        print(f"🖥️ Giả lập: {'Bật' if settings['system_on'] else 'Tắt'} hệ thống!")

    save_config(settings)
    return jsonify({"system_on": settings["system_on"]})

# API lấy trạng thái hệ thống
@app.route('/status', methods=['GET'])
def get_status():
    settings = load_config()
    return jsonify({"system_on": settings["system_on"]})

# Chạy Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
