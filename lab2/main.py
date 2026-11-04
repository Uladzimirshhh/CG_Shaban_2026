import os
import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
VALID_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".webp")

def init_images_folder():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    existing = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(VALID_EXTS)]
    if not existing:
        w, h = 440, 320
        im1 = Image.new("RGB", (w, h), "#ffffff")
        for y in range(h):
            for x in range(w):
                f = (x + y) / (w + h)
                val = int(255 * (1.0 - 0.75 * f))
                im1.putpixel((x, y), (val, val, val))
        d1 = ImageDraw.Draw(im1)
        d1.text((30, 60), "Компьютерная графика БГУ", fill=(15, 23, 42))
        d1.text((30, 110), "Лабораторная работа № 2 (Вариант 13)", fill=(15, 23, 42))
        d1.text((30, 160), "Локальный порог: метод Ниблэка", fill=(15, 23, 42))
        d1.text((30, 210), "Глобальный порог Оцу провалится в тени", fill=(15, 23, 42))
        im1.save(os.path.join(IMAGES_DIR, "1_text_with_shadow.png"))

        im2 = Image.new("RGB", (w, h), "#fafafa")
        d2 = ImageDraw.Draw(im2)
        d2.rectangle([20, 20, w - 20, h - 20], outline="#cbd5e1", width=2)
        d2.text((40, 80), "Чистый белый лист с текстом", fill=(30, 41, 59))
        d2.text((40, 140), "Ниблэк демонстрирует чувствительность к фону.", fill=(30, 41, 59))
        d2.text((40, 180), "Отрегулируйте k для устранения шума на полях.", fill=(30, 41, 59))
        im2.save(os.path.join(IMAGES_DIR, "2_white_sheet.png"))

        im3 = Image.new("RGB", (w, h), "#f8fafc")
        d3 = ImageDraw.Draw(im3)
        d3.rectangle([40, 50, w - 40, h - 50], outline="#0284c7", width=6)
        d3.text((70, 110), "ТЕСТ РЕЗКОСТИ", fill=(15, 23, 42))
        d3.text((70, 160), "ВЫСОКОЧАСТОТНЫЙ ФИЛЬТР", fill=(15, 23, 42))
        im3 = im3.filter(ImageFilter.GaussianBlur(radius=3))
        im3.save(os.path.join(IMAGES_DIR, "3_blurred.png"))

        im4 = Image.new("RGB", (w, h), "#e2e8f0")
        d4 = ImageDraw.Draw(im4)
        d4.ellipse([80, 80, 220, 220], fill="#0284c7")
        d4.rectangle([250, 90, 380, 220], fill="#f43f5e")
        arr = np.array(im4)
        rand = np.random.rand(h, w)
        arr[rand < 0.04] = [0, 0, 0]
        arr[rand > 0.96] = [255, 255, 255]
        Image.fromarray(arr).save(os.path.join(IMAGES_DIR, "4_noisy.png"))

def moving_mean(img, r):
    k = 2 * r + 1
    pad_y = np.pad(img, ((r, r), (0, 0)), mode='edge')
    cs_y = np.pad(np.cumsum(pad_y, axis=0), ((1, 0), (0, 0)), mode='constant')
    sum_y = cs_y[k:, :] - cs_y[:-k, :]
    pad_x = np.pad(sum_y, ((0, 0), (r, r)), mode='edge')
    cs_x = np.pad(np.cumsum(pad_x, axis=1), ((0, 0), (1, 0)), mode='constant')
    sum_xy = cs_x[:, k:] - cs_x[:, :-k]
    return sum_xy / (k * k)

def niblack_threshold(gray, win_size, k):
    r = win_size // 2
    f_gray = gray.astype(np.float32)
    mean = moving_mean(f_gray, r)
    mean_sq = moving_mean(f_gray ** 2, r)
    variance = np.maximum(0.0, mean_sq - mean ** 2)
    std = np.sqrt(variance)
    th = mean + k * std
    bin_img = np.where(f_gray >= th, 255, 0).astype(np.uint8)
    return np.stack([bin_img, bin_img, bin_img], axis=-1)

def otsu_threshold(gray):
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    total = gray.size
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0
    max_var = 0.0
    th = 128
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        between = w_b * w_f * (m_b - m_f) ** 2
        if between > max_var:
            max_var = between
            th = t
    bin_img = np.where(gray >= th, 255, 0).astype(np.uint8)
    return np.stack([bin_img, bin_img, bin_img], axis=-1)

def convolve3x3(img, kernel, offset=0):
    pad = np.pad(img.astype(np.float32), ((1, 1), (1, 1), (0, 0)), mode='edge')
    h, w, c = img.shape
    res = np.zeros((h, w, c), dtype=np.float32)
    for dy in range(3):
        for dx in range(3):
            res += pad[dy:dy+h, dx:dx+w] * kernel[dy, dx]
    return np.clip(res + offset, 0, 255).astype(np.uint8)

def unsharp_mask(img, alpha):
    k_gauss = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32) / 16.0
    blur = convolve3x3(img, k_gauss)
    f_orig = img.astype(np.float32)
    f_blur = blur.astype(np.float32)
    res = f_orig + alpha * (f_orig - f_blur)
    return np.clip(res, 0, 255).astype(np.uint8)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа 2 | Вариант 13 | Шабан Владимир")
        self.configure(bg="#f1f5f9")
        self.geometry("1100x720")
        self.resizable(True, True)

        init_images_folder()

        self.current_img = None
        self.tk_orig = None
        self.tk_proc = None

        self.build_ui()
        self.refresh_images_list()
        self.update_controls_state()

    def build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", background="#f1f5f9", foreground="#0f172a", font=("Segoe UI", 9))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0284c7")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 9), foreground="#64748b")
        style.configure("TButton", font=("Segoe UI", 9, "bold"), background="#0284c7", foreground="#ffffff")
        style.map("TButton", background=[("active", "#0369a1")])

        header = ttk.Frame(self, padding=(10, 14, 10, 10))
        header.pack(fill="x")
        ttk.Label(header, text="Основы обработки цифровых изображений", style="Title.TLabel", anchor="center").pack()
        ttk.Label(header, text="Лабораторная работа № 2 | Вариант 13 (Пороговая обработка + ВЧ фильтры)", style="Subtitle.TLabel", anchor="center").pack()
        ttk.Label(header, text="Шабан Владимир", font=("Segoe UI", 9, "bold"), foreground="#0f172a", anchor="center").pack()

        toolbar = tk.Frame(self, bg="#ffffff", highlightthickness=1, highlightbackground="#cbd5e1", padx=12, pady=8)
        toolbar.pack(fill="x", padx=20, pady=(0, 14))

        tk.Label(toolbar, text="ФАЙЛ ИЗ ПАПКИ IMAGES/:", bg="#ffffff", font=("Segoe UI", 8, "bold"), fg="#64748b").pack(side="left", padx=(0, 8))
        self.selected_file = tk.StringVar()
        self.cb_images = ttk.Combobox(toolbar, textvariable=self.selected_file, state="readonly", width=34)
        self.cb_images.bind("<<ComboboxSelected>>", self.on_file_selected)
        self.cb_images.pack(side="left", padx=4)

        ttk.Button(toolbar, text="Обновить список", command=self.refresh_images_list).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Добавить файл...", command=self.browse_file).pack(side="left", padx=6)

        ctrl_grid = tk.Frame(self, bg="#f1f5f9")
        ctrl_grid.pack(fill="x", padx=20, pady=(0, 14))
        ctrl_grid.columnconfigure(0, weight=1)
        ctrl_grid.columnconfigure(1, weight=1)

        c1 = tk.Frame(ctrl_grid, bg="#ffffff", highlightthickness=1, highlightbackground="#cbd5e1", padx=14, pady=12)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(c1, text="МЕТОД 1: ПОРОГОВАЯ ОБРАБОТКА", bg="#ffffff", font=("Segoe UI", 9, "bold"), fg="#0284c7").pack(anchor="w", pady=(0, 6))

        r_box = tk.Frame(c1, bg="#ffffff")
        r_box.pack(fill="x", pady=4)
        self.thresh_mode = tk.StringVar(value="niblack")
        for txt, val in [("Ниблэк (лок.)", "niblack"), ("Оцу (глоб.)", "otsu"), ("Откл.", "none")]:
            tk.Radiobutton(r_box, text=txt, variable=self.thresh_mode, value=val, bg="#ffffff", command=self.on_mode_change).pack(side="left", padx=4)

        w_row = tk.Frame(c1, bg="#ffffff")
        w_row.pack(fill="x", pady=4)
        self.w_title = tk.Label(w_row, text="Размер окна (W):", bg="#ffffff", fg="#64748b")
        self.w_title.pack(side="left")
        self.w_lbl = tk.Label(w_row, text="15", bg="#ffffff", font=("Segoe UI", 8, "bold"), fg="#0f172a")
        self.w_lbl.pack(side="right")
        self.w_slider = ttk.Scale(c1, from_=5, to=45, value=15, command=self.on_param_change)
        self.w_slider.pack(fill="x", pady=(0, 4))

        k_row = tk.Frame(c1, bg="#ffffff")
        k_row.pack(fill="x", pady=4)
        self.k_title = tk.Label(k_row, text="Коэффициент k:", bg="#ffffff", fg="#64748b")
        self.k_title.pack(side="left")
        self.k_lbl = tk.Label(k_row, text="-0.20", bg="#ffffff", font=("Segoe UI", 8, "bold"), fg="#0f172a")
        self.k_lbl.pack(side="right")
        self.k_slider = ttk.Scale(c1, from_=-1.0, to=1.0, value=-0.2, command=self.on_param_change)
        self.k_slider.pack(fill="x")

        c2 = tk.Frame(ctrl_grid, bg="#ffffff", highlightthickness=1, highlightbackground="#cbd5e1", padx=14, pady=12)
        c2.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(c2, text="МЕТОД 2: ВЧ ФИЛЬТРЫ РЕЗКОСТИ", bg="#ffffff", font=("Segoe UI", 9, "bold"), fg="#0284c7").pack(anchor="w", pady=(0, 6))

        hp_box = tk.Frame(c2, bg="#ffffff")
        hp_box.pack(fill="x", pady=4)
        self.hp_mode = tk.StringVar(value="none")
        for txt, val in [("Резкость 3x3", "sharpen"), ("Лаплас", "laplacian"), ("Unsharp Mask", "unsharp"), ("Откл.", "none")]:
            tk.Radiobutton(hp_box, text=txt, variable=self.hp_mode, value=val, bg="#ffffff", command=self.on_hp_change).pack(side="left", padx=4)

        s_row = tk.Frame(c2, bg="#ffffff")
        s_row.pack(fill="x", pady=4)
        self.s_title = tk.Label(s_row, text="Сила резкости (\u03b1):", bg="#ffffff", fg="#64748b")
        self.s_title.pack(side="left")
        self.s_lbl = tk.Label(s_row, text="1.0", bg="#ffffff", font=("Segoe UI", 8, "bold"), fg="#0f172a")
        self.s_lbl.pack(side="right")
        self.s_slider = ttk.Scale(c2, from_=0.0, to=3.0, value=1.0, command=self.on_param_change)
        self.s_slider.pack(fill="x")

        views = tk.Frame(self, bg="#f1f5f9")
        views.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        views.columnconfigure(0, weight=1)
        views.columnconfigure(1, weight=1)

        v1 = tk.Frame(views, bg="#ffffff", highlightthickness=1, highlightbackground="#cbd5e1", padx=8, pady=8)
        v1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(v1, text="ОРИГИНАЛЬНОЕ ИЗОБРАЖЕНИЕ", bg="#ffffff", font=("Segoe UI", 8, "bold"), fg="#64748b").pack(anchor="w")
        self.lbl_src = tk.Label(v1, bg="#ffffff")
        self.lbl_src.pack(expand=True, fill="both", pady=4)

        v2 = tk.Frame(views, bg="#ffffff", highlightthickness=1, highlightbackground="#cbd5e1", padx=8, pady=8)
        v2.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(v2, text="РЕЗУЛЬТАТ ОБРАБОТКИ", bg="#ffffff", font=("Segoe UI", 8, "bold"), fg="#64748b").pack(anchor="w")
        self.lbl_dst = tk.Label(v2, bg="#ffffff")
        self.lbl_dst.pack(expand=True, fill="both", pady=4)

    def update_controls_state(self):
        t_m = self.thresh_mode.get()
        if t_m in ["none", "otsu"]:
            self.w_slider.state(["disabled"])
            self.k_slider.state(["disabled"])
            self.w_title.config(fg="#cbd5e1")
            self.w_lbl.config(fg="#cbd5e1")
            self.k_title.config(fg="#cbd5e1")
            self.k_lbl.config(fg="#cbd5e1")
        else:
            self.w_slider.state(["!disabled"])
            self.k_slider.state(["!disabled"])
            self.w_title.config(fg="#64748b")
            self.w_lbl.config(fg="#0f172a")
            self.k_title.config(fg="#64748b")
            self.k_lbl.config(fg="#0f172a")

        hp_m = self.hp_mode.get()
        if hp_m == "none":
            self.s_slider.state(["disabled"])
            self.s_title.config(fg="#cbd5e1")
            self.s_lbl.config(fg="#cbd5e1")
        else:
            self.s_slider.state(["!disabled"])
            self.s_title.config(fg="#64748b")
            self.s_lbl.config(fg="#0f172a")

    def refresh_images_list(self):
        files = [f for f in sorted(os.listdir(IMAGES_DIR)) if f.lower().endswith(VALID_EXTS)]
        self.cb_images["values"] = files
        if files:
            current = self.selected_file.get()
            if current not in files:
                self.selected_file.set(files[0])
            self.load_image_from_file(os.path.join(IMAGES_DIR, self.selected_file.get()))

    def on_file_selected(self, event=None):
        name = self.selected_file.get()
        if not name:
            return
        path = os.path.join(IMAGES_DIR, name)
        self.load_image_from_file(path)

    def load_image_from_file(self, path):
        if not os.path.exists(path):
            return
        im = Image.open(path).convert("RGB")
        w, h = im.size
        max_side = 460
        if w > max_side or h > max_side:
            if w > h:
                h = int(h * max_side / w)
                w = max_side
            else:
                w = int(w * max_side / h)
                h = max_side
            im = im.resize((w, h), Image.Resampling.LANCZOS)
        self.current_img = np.array(im)
        self.update_image()

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if not path:
            return
        dest = os.path.join(IMAGES_DIR, os.path.basename(path))
        if os.path.abspath(path) != os.path.abspath(dest):
            Image.open(path).save(dest)
        self.refresh_images_list()
        self.selected_file.set(os.path.basename(dest))
        self.load_image_from_file(dest)

    def on_mode_change(self):
        self.update_controls_state()
        self.update_image()

    def on_hp_change(self):
        self.update_controls_state()
        self.update_image()

    def on_param_change(self, val=None):
        w = int(float(self.w_slider.get()))
        if w % 2 == 0:
            w += 1
        self.w_lbl.config(text=str(w))
        k = round(float(self.k_slider.get()), 2)
        self.k_lbl.config(text=f"{k:.2f}")
        alpha = round(float(self.s_slider.get()), 1)
        self.s_lbl.config(text=f"{alpha:.1f}")
        self.update_image()

    def update_image(self):
        if self.current_img is None:
            return
        res = self.current_img.copy()
        t_mode = self.thresh_mode.get()
        w = int(float(self.w_slider.get()))
        if w % 2 == 0:
            w += 1
        k = float(self.k_slider.get())

        if t_mode in ["niblack", "otsu"]:
            gray = (0.299 * res[:,:,0] + 0.587 * res[:,:,1] + 0.114 * res[:,:,2]).astype(np.uint8)
            if t_mode == "otsu":
                res = otsu_threshold(gray)
            else:
                res = niblack_threshold(gray, w, k)

        hp = self.hp_mode.get()
        alpha = float(self.s_slider.get())
        if hp == "sharpen":
            if alpha > 0.0:
                k_sharp = np.array([[0, -alpha, 0], [-alpha, 1 + 4*alpha, -alpha], [0, -alpha, 0]], dtype=np.float32)
                res = convolve3x3(res, k_sharp)
        elif hp == "laplacian":
            if alpha > 0.0:
                k_lap = np.array([[0, -alpha, 0], [-alpha, 4*alpha, -alpha], [0, -alpha, 0]], dtype=np.float32)
                res = convolve3x3(res, k_lap, offset=int(128 * min(1.0, alpha)))
            else:
                res = np.zeros_like(res)
        elif hp == "unsharp":
            if alpha > 0.0:
                res = unsharp_mask(res, alpha)

        p_src = Image.fromarray(self.current_img)
        p_dst = Image.fromarray(res)
        self.tk_orig = ImageTk.PhotoImage(p_src)
        self.tk_proc = ImageTk.PhotoImage(p_dst)
        self.lbl_src.config(image=self.tk_orig)
        self.lbl_dst.config(image=self.tk_proc)

if __name__ == "__main__":
    app = App()
    app.mainloop()