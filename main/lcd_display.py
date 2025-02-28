import smbus
import time

I2C_ADDR = 0x27
bus = smbus.SMBus(1)

def lcd_init():
    bus.write_byte_data(I2C_ADDR, 0, 0x38)
    bus.write_byte_data(I2C_ADDR, 0, 0x0C)
    bus.write_byte_data(I2C_ADDR, 0, 0x01)
    time.sleep(0.1)

def lcd_display(line1, line2):
    bus.write_byte_data(I2C_ADDR, 0, 0x80)
    for char in line1.ljust(16):
        bus.write_byte_data(I2C_ADDR, 1, ord(char))
    
    bus.write_byte_data(I2C_ADDR, 0, 0xC0)
    for char in line2.ljust(16):
        bus.write_byte_data(I2C_ADDR, 1, ord(char))
