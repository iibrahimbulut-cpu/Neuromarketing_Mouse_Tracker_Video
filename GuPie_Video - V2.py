import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import numpy as np
import cv2
import matplotlib.pyplot as plt
import google.generativeai as genai
import os
import time
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

MODEL_NAME = "gemini-flash-latest" 
API_KEY = "apı key"

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"API Hatası: {e}")

class GuPie_Video_App:
    def __init__(self, root):
        self.root = root
        self.root.title("GuPie Video")
        self.root.geometry("550x600")
        
        try: self.root.iconbitmap("gupie.ico")
        except: pass
        
        self.video_path = None
        self.mouse_data = {} 
        self.is_recording = False
        self.cap = None
        self.video_fps = 30
        self.current_frame_idx = 0
        self.total_frames = 0
        
        self.disp_w = 0
        self.disp_h = 0
        
        self.summary_files = [] # [path_start, path_mid, path_end]

        tk.Label(root, text="GuPie VIDEO ", font=("Arial", 24, "bold"), fg="#FF6D00", bg="#222").pack(pady=10, fill=tk.X)
        tk.Label(root, text="Insight Explorer", font=("Arial", 10, "bold"), fg="gray").pack()
        
        f1 = tk.Frame(root, pady=10); f1.pack()
        self.btn_open_screen = tk.Button(f1, text="1. Kullanıcı Ekranını Aç", command=self.open_user_screen, bg="#ddd", width=35)
        self.btn_open_screen.pack()
        
        f2 = tk.Frame(root, pady=10); f2.pack()
        self.btn_load = tk.Button(f2, text="2. Video Yükle (.mp4)", command=self.load_video, width=35)
        self.btn_load.pack()
        self.lbl_file = tk.Label(f2, text="Dosya seçilmedi", fg="blue"); self.lbl_file.pack()
        
        f3 = tk.Frame(root, pady=10); f3.pack()
        self.btn_start = tk.Button(f3, text="3. Testi Başlat", command=self.initiate_start_sequence, state=tk.DISABLED, bg="green", fg="white", width=35)
        self.btn_start.pack()
        
        self.btn_analyze = tk.Button(root, text="4. GuPie Analizi Yap", command=self.analyze_timeline, state=tk.DISABLED, bg="#1565C0", fg="white", width=40, height=2)
        self.btn_analyze.pack(pady=20)
        
        self.lbl_status = tk.Label(root, text="GuPie Hazır.", fg="gray", wraplength=450)
        self.lbl_status.pack(side=tk.BOTTOM, pady=10)

    def open_user_screen(self):
        if hasattr(self, 'user_window') and self.user_window.winfo_exists(): return
        self.user_window = Toplevel(self.root)
        self.user_window.title("GuPie Video Player")
        self.user_window.configure(bg="black")
        try: self.user_window.iconbitmap("gupie2.ico")
        except: pass
        w = self.user_window.winfo_screenwidth()
        h = self.user_window.winfo_screenheight()
        try: self.user_window.geometry(f"{w}x{h}+{w}+0") 
        except: self.user_window.geometry(f"{w}x{h}+0+0")
        self.user_window.attributes('-fullscreen', True)
        self.lbl_display = tk.Label(self.user_window, bg="black", cursor="cross")
        self.lbl_display.place(relx=0.5, rely=0.5, anchor="center") 
        self.user_window.bind("<Motion>", self.track_mouse)
        self.lbl_status.config(text="Kullanıcı ekranı açıldı.")

    def load_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if path:
            self.video_path = path
            self.lbl_file.config(text=os.path.basename(path))
            self.btn_start.config(state=tk.NORMAL)
            self.lbl_status.config(text="Video yüklendi.")

    def initiate_start_sequence(self):
        if not hasattr(self, 'user_window') or not self.user_window.winfo_exists():
            messagebox.showerror("Hata", "Önce Kullanıcı Ekranını Açın!")
            return
        self.lbl_display.config(image="")
        self.lbl_display.configure(text="3", fg="white", font=("Arial", 100, "bold"))
        self.lbl_status.config(text="Başlıyor...")
        self.root.update()
        self.root.after(1000, lambda: self.lbl_display.configure(text="2"))
        self.root.after(2000, lambda: self.lbl_display.configure(text="1"))
        self.root.after(3000, self.start_test_actual)

    def start_test_actual(self):
        self.lbl_display.configure(text="") 
        self.mouse_data = {}
        self.current_frame_idx = 0
        self.cap = cv2.VideoCapture(self.video_path)
        self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        screen_w = self.user_window.winfo_screenwidth()
        screen_h = self.user_window.winfo_screenheight()
        self.is_recording = True
        self.lbl_status.config(text="Kayıt Başladı!")
        self.play_video_loop(screen_w, screen_h)

    def play_video_loop(self, screen_w, screen_h):
        if not self.is_recording: return
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail((screen_w, screen_h), Image.Resampling.LANCZOS)
            self.disp_w, self.disp_h = img.size
            tk_img = ImageTk.PhotoImage(img)
            self.lbl_display.config(image=tk_img)
            self.lbl_display.image = tk_img 
            delay = int(1000 / self.video_fps)
            self.current_frame_idx += 1
            self.root.after(delay, lambda: self.play_video_loop(screen_w, screen_h))
        else:
            self.end_test()

    def track_mouse(self, event):
        if self.is_recording:
            lbl_x = self.lbl_display.winfo_rootx()
            lbl_y = self.lbl_display.winfo_rooty()
            rel_x = event.x_root - lbl_x
            rel_y = event.y_root - lbl_y
            if 0 <= rel_x < self.disp_w and 0 <= rel_y < self.disp_h:
                self.mouse_data[self.current_frame_idx] = (rel_x, rel_y)

    def end_test(self):
        self.is_recording = False
        self.cap.release()
        self.lbl_display.config(image="")
        self.lbl_display.configure(text="Test Bitti", fg="white", font=("Arial", 30))
        self.lbl_status.config(text="GuPie görselleri hazırlanıyor...")
        self.root.update()
        self.root.after(500, self.process_video_output)

    def process_video_output(self):
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        base_name = os.path.splitext(os.path.basename(self.video_path))[0]
        out_video_path = f"GuPie_Result_{base_name}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter(out_video_path, fourcc, fps, (width, height))
        
        heatmap_start = np.zeros((height, width), dtype=np.float32)
        heatmap_mid = np.zeros((height, width), dtype=np.float32)
        heatmap_end = np.zeros((height, width), dtype=np.float32)
        
        limit_1 = total_frames * 0.33
        limit_2 = total_frames * 0.66
        
        scale_x = width / self.disp_w
        scale_y = height / self.disp_h
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 1
            
            if frame_idx in self.mouse_data:
                mx, my = self.mouse_data[frame_idx]
                real_x = int(mx * scale_x)
                real_y = int(my * scale_y)
                
                if frame_idx < limit_1:
                    if 0 <= real_x < width and 0 <= real_y < height: heatmap_start[real_y, real_x] += 3
                elif frame_idx < limit_2:
                    if 0 <= real_x < width and 0 <= real_y < height: heatmap_mid[real_y, real_x] += 3
                else:
                    if 0 <= real_x < width and 0 <= real_y < height: heatmap_end[real_y, real_x] += 3
                
                cv2.circle(frame, (real_x, real_y), 25, (0, 0, 0), 4)
                cv2.circle(frame, (real_x, real_y), 25, (0, 255, 255), 2)
                cv2.circle(frame, (real_x, real_y), 5, (0, 255, 255), -1)
                
            out.write(frame)
            if frame_idx % 50 == 0:
                self.lbl_status.config(text=f"İşleniyor: {int((frame_idx/total_frames)*100)}%")
                self.root.update()

        cap.release()
        out.release()
        
        self.summary_files = []
        phases = [
            ("1_Giris", heatmap_start, int(limit_1/2)), 
            ("2_Gelisme", heatmap_mid, int((limit_1+limit_2)/2)), 
            ("3_Sonuc", heatmap_end, int((limit_2+total_frames)/2))
        ]
        
        cap = cv2.VideoCapture(self.video_path)
        
        for name, h_matrix, bg_frame_idx in phases:
            cap.set(cv2.CAP_PROP_POS_FRAMES, bg_frame_idx)
            ret, bg_frame = cap.read()
            if not ret: continue
            
            sigma = int(max(width, height) / 40) | 1
            h_matrix = cv2.GaussianBlur(h_matrix, (0, 0), sigmaX=sigma, sigmaY=sigma)
            h_matrix = cv2.normalize(h_matrix, None, 0, 255, cv2.NORM_MINMAX)
            h_color = cv2.applyColorMap(np.uint8(h_matrix), cv2.COLORMAP_JET)
            
            final_img = cv2.addWeighted(bg_frame, 0.6, h_color, 0.4, 0)
            
            file_path = f"Timeline_{base_name}_{name}.jpg"
            cv2.imwrite(file_path, final_img)
            self.summary_files.append(file_path)
            
        cap.release()
        
        self.lbl_status.config(text=f"Bitti! Heatmap oluşturuldu.")
        self.btn_analyze.config(state=tk.NORMAL)
        messagebox.showinfo("Bitti", "3 Farklı Zaman Aşamalı Video Analizi Oluşturuldu.\nGuPie'ye Sorabilirsiniz.")

    def analyze_timeline(self):
        if len(self.summary_files) < 3: return
        
        self.lbl_status.config(text="GuPie Çalışıyor...Her zamanki gibi :(")
        self.root.update()
        
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            
            img_start = Image.open(self.summary_files[0])
            img_mid = Image.open(self.summary_files[1])
            img_end = Image.open(self.summary_files[2])
            
            prompt = """
            Sen nöropazarlama uzmanısın.
            Sana bir reklam videosunun "ZAMAN TÜNELİ" analizini gönderiyorum.
            3 farklı görsel var:
            1. Görsel: Videonun BAŞLANGICI (İlk İzlenim)
            2. Görsel: Videonun ORTASI (Hikaye Süreci)
            3. Görsel: Videonun SONU (Kapanış/Logo)
            
            Lütfen bu akışı analiz et:
            - **Giriş:** Video dikkat çekici başladı mı? Odak nerede?
            - **Gelişme:** Dikkat dağıldı mı yoksa ürün üzerinde kaldı mı?
            - **Sonuç:** Kullanıcı videoyu markayı/logoyu görerek mi bitirdi?
            - **Özet:** Bu video başarılı mı? İzleyici videodan sonra markayı hatırlayabilir mi? İyileştirme için ne yapılmalı?
            """
            
            response = model.generate_content([prompt, img_start, img_mid, img_end], safety_settings=safety_settings)
            
            win = Toplevel(self.root)
            win.title("GuPie Raporu")
            win.geometry("700x600")
            try: win.iconbitmap("gupie2.ico")
            except: pass
            
            txt = tk.Text(win, wrap=tk.WORD, font=("Arial", 11), padx=10, pady=10)
            scr = tk.Scrollbar(win, command=txt.yview); txt.configure(yscrollcommand=scr.set)
            scr.pack(side=tk.RIGHT, fill=tk.Y); txt.pack(expand=True, fill='both')
            
            txt.insert(tk.END, response.text)
            self.lbl_status.config(text="Analiz tamamlandı.")
            
        except Exception as e:
            messagebox.showerror("Hata", str(e))

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = GuPie_Video_App(root)
        root.mainloop()
    except Exception as e:
        print(f"Hata: {e}")
        input()