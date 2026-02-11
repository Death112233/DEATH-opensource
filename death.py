import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import os
import webbrowser
import sys
from tkinterdnd2 import DND_FILES, TkinterDnD

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DeathWindows(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # प्रोफेशनल नाम: DEATH REF
        self.title("DEATH REF")
        self.geometry("800x600")
        self.attributes("-topmost", True)
        
        icon_path = resource_path("DEATH.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        self.is_menu_open = False
        self.sidebar_width = 38 
        self.expanded_width = 165
        self.zoom_level = 1.0
        self.current_file = None
        self.video_cap = None
        self.video_running = False
        
        self.start_x = 0
        self.start_y = 0
        self.offset_x = 0
        self.offset_y = 0

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.logo_path = resource_path("DEATH.jpg")
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="")
        self.logo_label.pack(pady=(15, 5))
        self.update_logo()

        self.menu_btn = ctk.CTkButton(self.sidebar_frame, text="≡", width=30, height=35, 
                                     fg_color="transparent", font=("Arial", 20), 
                                     command=self.toggle_menu)
        self.menu_btn.pack(pady=5)

        self.btn_viewer = self.create_menu_btn("Viewer", "home")
        self.btn_help = self.create_menu_btn("Settings", "help")
        self.btn_open = self.create_menu_btn("Import", "open")

        self.content_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#080808")
        self.content_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # क्लीन वेलकम टेक्स्ट
        self.display_label = ctk.CTkLabel(self.content_frame, text="DEATH REF\nSecure Reference Environment", font=("Segoe UI", 16, "bold"), text_color="#333333")
        self.display_label.place(relx=0.5, rely=0.5, anchor="center")

        self.text_display = ctk.CTkTextbox(self.content_frame, font=("Consolas", 14), fg_color="#080808", border_width=0)
        self.help_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        self.bind("<Control-MouseWheel>", self.handle_zoom)
        self.bind("<space>", lambda e: self.toggle_video_state())
        self.bind("r", lambda e: self.reset_view())
        self.bind("R", lambda e: self.reset_view())
        self.bind("<Configure>", self.check_responsive)
        
        self.display_label.bind("<Button-1>", self.start_pan)
        self.display_label.bind("<B1-Motion>", self.do_pan)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def process_logo(self, size):
        try:
            img = Image.open(self.logo_path).convert("RGBA")
            datas = img.getdata()
            newData = []
            for item in datas:
                # काले बैकग्राउंड को हटाने की बेहतर लॉजिक
                if item[0] < 55 and item[1] < 55 and item[2] < 55:
                    newData.append((0, 0, 0, 0))
                else:
                    newData.append(item)
            img.putdata(newData)
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        except:
            return None

    def update_logo(self):
        size = 120 if self.is_menu_open else 32
        new_logo = self.process_logo(size)
        if new_logo:
            self.logo_label.configure(image=new_logo)
        else:
            self.logo_label.configure(text="DW")

    def create_menu_btn(self, text, target):
        btn = ctk.CTkButton(self.sidebar_frame, text=text if self.is_menu_open else "", 
                           width=30, fg_color="transparent", anchor="w",
                           command=lambda: self.menu_handler(target))
        btn.pack(pady=6, padx=2, fill="x")
        return btn

    def toggle_menu(self):
        self.is_menu_open = not self.is_menu_open
        w = self.expanded_width if self.is_menu_open else self.sidebar_width
        self.sidebar_frame.configure(width=w)
        self.btn_viewer.configure(text="  Viewer" if self.is_menu_open else "")
        self.btn_help.configure(text="  Settings" if self.is_menu_open else "")
        self.btn_open.configure(text="  Import" if self.is_menu_open else "")
        self.update_logo()

    def check_responsive(self, event):
        if self.winfo_width() < 350:
            self.sidebar_frame.grid_forget()
        else:
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

    def handle_drop(self, event):
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.current_file, self.zoom_level = file_path, 1.0
            self.offset_x, self.offset_y = 0, 0
            self.process_file(file_path)

    def menu_handler(self, target):
        if target == "open": self.open_file()
        elif target == "home": self.show_tab("home")
        elif target == "help": self.show_tab("help")

    def show_tab(self, name):
        self.help_frame.pack_forget()
        self.text_display.pack_forget()
        if name == "home":
            self.display_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.show_help()

    def show_help(self):
        self.display_label.place_forget()
        for widget in self.help_frame.winfo_children(): widget.destroy()
        self.help_frame.pack(expand=True, fill="both", padx=30, pady=30)
        
        ctk.CTkLabel(self.help_frame, text="DEATH REF - CONFIG", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        self.op_slider = ctk.CTkSlider(self.help_frame, from_=0.1, to=1.0, command=lambda v: self.attributes("-alpha", v))
        self.op_slider.set(self.attributes("-alpha"))
        self.op_slider.pack(pady=10)

        ctk.CTkLabel(self.help_frame, text="Quick Controls:\n• Drag Files: Instant Load\n• Ctrl + Scroll: Focus Zoom\n• Space: Playback Toggle\n• R: Default View", 
                     justify="left", text_color="#666666", font=("Segoe UI", 12)).pack(pady=20)
        
        ctk.CTkButton(self.help_frame, text="DEATH SUPPORT", fg_color="#1f538d", 
                      command=lambda: webbrowser.open("https://t.me/udemydeath")).pack(side="bottom", pady=20)

    def reset_view(self):
        self.zoom_level, self.offset_x, self.offset_y = 1.0, 0, 0
        self.display_label.place(relx=0.5, rely=0.5, anchor="center")
        if self.current_file: self.process_file(self.current_file)

    def start_pan(self, event):
        self.start_x, self.start_y = event.x, event.y

    def do_pan(self, event):
        dx, dy = event.x - self.start_x, event.y - self.start_y
        self.offset_x += dx
        self.offset_y += dy
        self.display_label.place(x=self.content_frame.winfo_width()//2 + self.offset_x, 
                                 y=self.content_frame.winfo_height()//2 + self.offset_y, anchor="center")

    def handle_zoom(self, event):
        if event.delta > 0: self.zoom_level *= 1.1
        else: self.zoom_level = max(0.1, self.zoom_level / 1.1)
        if self.current_file: self.process_file(self.current_file)

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.current_file, self.zoom_level = path, 1.0
            self.offset_x, self.offset_y = 0, 0
            self.process_file(path)

    def process_file(self, path):
        self.stop_video()
        self.show_tab("home")
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp']: self.show_image(path)
        elif ext in ['.mp4', '.avi', '.mov']: self.play_video(path)
        elif ext in ['.txt', '.py', '.json']: self.show_text(path)

    def show_image(self, path):
        img = Image.open(path)
        nw, nh = self.calculate_size(img.width, img.height)
        img = img.resize((nw, nh), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.display_label.configure(image=photo, text="")
        self.display_label.image = photo

    def toggle_video_state(self):
        self.video_running = not self.video_running
        if self.video_running: self.update_video_frame()

    def play_video(self, path):
        self.video_cap = cv2.VideoCapture(path)
        self.video_running = True
        self.update_video_frame()

    def update_video_frame(self):
        if self.video_running and self.video_cap:
            ret, frame = self.video_cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                nw, nh = self.calculate_size(img.width, img.height)
                img = img.resize((nw, nh), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.display_label.configure(image=photo, text="")
                self.display_label.image = photo
                self.after(15, self.update_video_frame)
            else:
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.update_video_frame()

    def calculate_size(self, w, h):
        base_w = self.content_frame.winfo_width() - 20
        base_h = self.content_frame.winfo_height() - 20
        if base_w < 100: base_w, base_h = 700, 500
        ratio = min(base_w/w, base_h/h)
        return int(w * ratio * self.zoom_level), int(h * ratio * self.zoom_level)

    def show_text(self, path):
        self.display_label.place_forget()
        self.text_display.pack(expand=True, fill="both", padx=10, pady=10)
        with open(path, 'r', encoding='utf-8') as f:
            self.text_display.delete("0.0", "end")
            self.text_display.insert("0.0", f.read())

    def stop_video(self):
        self.video_running = False
        if self.video_cap: self.video_cap.release(); self.video_cap = None

if __name__ == "__main__":
    app = DeathWindows()
    app.mainloop()