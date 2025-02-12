import time  

# Dãy ban đầu
bit = input("Nhập vào một dãy 8 bit: ")
while len(bit) != 8 or not all(char in "01" for char in bit):
    bit = input("Dãy không hợp lệ! Vui lòng nhập đúng 8 ký tự chỉ bao gồm 0 và 1: ")
print("Dãy số vừa nhập: ",bit)

def print_byte(bit1):
    print("".join(bit1))
bit1=["0"]*8

bit_list = list(bit)

while "0" in bit_list:
    time.sleep(1)  
    bit_list.remove("0")  
    print("Sau khi xóa:", "".join(bit_list))
    time.sleep(1) 

print("Dãy sau khi xóa hết số '0':", "".join(bit_list))

while True:
    bit1[3], bit1[4] = "1", "1"
    print_byte(bit1)
    time.sleep(1)

    for i in range(3, -1, -1):  
        bit1[i], bit1[7 - i] = "1", "1"
        bit1[i + 1], bit1[7 - (i + 1)] = "0", "0"  
        print_byte(bit1)
        time.sleep(1)

    bit1[0], bit1[7] = "0", "0"
    print_byte(bit1)
    time.sleep(1)

    for i in range(0, 4): 
        bit1[i], bit1[7 - i] = "1", "1"
        bit1[i - 1 if i > 0 else 0], bit1[7 - (i - 1 if i > 0 else 0)] = "0", "0"
        print_byte(bit1)
        time.sleep(1)

    bit1[3], bit1[4] = "0", "0"
    print_byte(bit1)
    time.sleep(1)
