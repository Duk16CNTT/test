import tkinter as tk

class LCD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LCD Emulator")
        self.root.geometry("400x120")
        self.root.configure(bg="black")

        self.line1 = tk.Label(self.root, text=" "*16, font=("Courier", 20), fg="lime", bg="black")
        self.line2 = tk.Label(self.root, text=" "*16, font=("Courier", 20), fg="lime", bg="black")

        self.line1.pack()
        self.line2.pack()
        self.root.update()

    def lcd_display_string(self, text, line):
        """Hiển thị text lên dòng 1 hoặc dòng 2 của LCD"""
        text = text.ljust(16)[:16]  # Giới hạn 16 ký tự
        if line == 1:
            self.line1.config(text=text)
        elif line == 2:
            self.line2.config(text=text)
        self.root.update()

    def mainloop(self):
        self.root.mainloop()
