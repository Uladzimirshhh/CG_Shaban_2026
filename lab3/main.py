import math
import time
import tkinter as tk
from tkinter import ttk, messagebox


def iround(val: float) -> int:
    return int(math.floor(val + 0.5))


def raster_step_line(x1: int, y1: int, x2: int, y2: int) -> list[tuple[int, int]]:
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return [(x1, y1)]

    points = []
    if abs(dx) >= abs(dy):
        k = dy / dx
        b = y1 - k * x1
        step = 1 if x2 >= x1 else -1
        for x in range(x1, x2 + step, step):
            y = int(math.floor(k * x + b + 0.5))
            points.append((x, y))
    else:
        k_inv = dx / dy
        b_inv = x1 - k_inv * y1
        step = 1 if y2 >= y1 else -1
        for y in range(y1, y2 + step, step):
            x = int(math.floor(k_inv * y + b_inv + 0.5))
            points.append((x, y))
    return points


def raster_dda_line(x1: int, y1: int, x2: int, y2: int) -> list[tuple[int, int]]:
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x1, y1)]

    x_inc = dx / steps
    y_inc = dy / steps
    x = float(x1)
    y = float(y1)

    points = []
    for _ in range(steps + 1):
        points.append((int(math.floor(x + 0.5)), int(math.floor(y + 0.5))))
        x += x_inc
        y += y_inc
    return points


def raster_bresenham_line(x1: int, y1: int, x2: int, y2: int) -> list[tuple[int, int]]:
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    if dx == 0 and dy == 0:
        return [(x1, y1)]

    x, y = x1, y1
    sx = 1 if x1 < x2 else (-1 if x1 > x2 else 0)
    sy = 1 if y1 < y2 else (-1 if y1 > y2 else 0)

    points = []
    if dx >= dy:
        err = 2 * dy - dx
        two_dy = 2 * dy
        two_dx = 2 * dx
        for _ in range(dx + 1):
            points.append((x, y))
            if err >= 0:
                y += sy
                err -= two_dx
            x += sx
            err += two_dy
    else:
        err = 2 * dx - dy
        two_dx = 2 * dx
        two_dy = 2 * dy
        for _ in range(dy + 1):
            points.append((x, y))
            if err >= 0:
                x += sx
                err -= two_dy
            y += sy
            err += two_dx
    return points


def raster_bresenham_circle(xc: int, yc: int, r: int) -> list[tuple[int, int]]:
    if r < 0:
        return []
    if r == 0:
        return [(xc, yc)]

    points = []
    x = 0
    y = r
    d = 3 - 2 * r

    while x <= y:
        points.append((xc + x, yc + y))
        points.append((xc - x, yc + y))
        points.append((xc + x, yc - y))
        points.append((xc - x, yc - y))
        points.append((xc + y, yc + x))
        points.append((xc - y, yc + x))
        points.append((xc + y, yc - x))
        points.append((xc - y, yc - x))
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1
    return points


def build_calculation_trace(algo_key: str, params: tuple[int, ...], max_rows: int = 120) -> str:
    lines = []

    if algo_key == "step":
        x1, y1, x2, y2 = params
        dx, dy = x2 - x1, y2 - y1
        lines.append("=== ПОШАГОВЫЙ АЛГОРИТМ ===")
        lines.append(f"Вход: P1=({x1}, {y1}), P2=({x2}, {y2})")
        lines.append(f"dx = {dx}, dy = {dy}")
        if dx == 0 and dy == 0:
            lines.append(f"Вырожденный отрезок: точка ({x1}, {y1}).")
            return "\n".join(lines)

        if abs(dx) >= abs(dy):
            k = dy / dx
            b = y1 - k * x1
            step = 1 if x2 >= x1 else -1
            lines.append("|dx| >= |dy| -> идём по X с шагом " + str(step))
            lines.append(f"k = dy/dx = {k:.4f}, b = y1 - k*x1 = {b:.4f}")
            lines.append("Формула: y = round(k * x + b)\n")
            lines.append(f"{'Шаг':>4} | {'x':>5} | {'y_точн':>9} | {'Пиксель (x, y)':>15}")
            lines.append("-" * 43)
            for idx, x in enumerate(range(x1, x2 + step, step)):
                if idx >= max_rows:
                    lines.append("... (вывод сокращён) ...")
                    break
                y_exact = k * x + b
                y_int = iround(y_exact)
                lines.append(f"{idx:>4} | {x:>5} | {y_exact:>9.3f} | ({x:>4}, {y_int:>4})")
        else:
            k_inv = dx / dy
            b_inv = x1 - k_inv * y1
            step = 1 if y2 >= y1 else -1
            lines.append("|dy| > |dx| -> идём по Y с шагом " + str(step))
            lines.append(f"k_inv = dx/dy = {k_inv:.4f}, b_inv = {b_inv:.4f}")
            lines.append("Формула: x = round(k_inv * y + b_inv)\n")
            lines.append(f"{'Шаг':>4} | {'y':>5} | {'x_точн':>9} | {'Пиксель (x, y)':>15}")
            lines.append("-" * 43)
            for idx, y in enumerate(range(y1, y2 + step, step)):
                if idx >= max_rows:
                    lines.append("... (вывод сокращён) ...")
                    break
                x_exact = k_inv * y + b_inv
                x_int = iround(x_exact)
                lines.append(f"{idx:>4} | {y:>5} | {x_exact:>9.3f} | ({x_int:>4}, {y:>4})")

    elif algo_key == "dda":
        x1, y1, x2, y2 = params
        dx, dy = x2 - x1, y2 - y1
        steps = max(abs(dx), abs(dy))
        lines.append("=== АЛГОРИТМ ЦДА (DDA) ===")
        lines.append(f"Вход: P1=({x1}, {y1}), P2=({x2}, {y2})")
        lines.append(f"dx = {dx}, dy = {dy}, L = max(|dx|, |dy|) = {steps}")
        if steps == 0:
            lines.append(f"Вырожденный отрезок: ({x1}, {y1}).")
            return "\n".join(lines)
        x_inc, y_inc = dx / steps, dy / steps
        lines.append(f"Приращения: dX = {x_inc:.4f}, dY = {y_inc:.4f}\n")
        lines.append(f"{'i':>3} | {'x_float':>8} | {'y_float':>8} | {'Пиксель':>13}")
        lines.append("-" * 41)
        x, y = float(x1), float(y1)
        for i in range(steps + 1):
            if i >= max_rows:
                lines.append("... (вывод сокращён) ...")
                break
            rx, ry = iround(x), iround(y)
            lines.append(f"{i:>3} | {x:>8.3f} | {y:>8.3f} | ({rx:>4}, {ry:>4})")
            x += x_inc
            y += y_inc

    elif algo_key == "bres_line":
        x1, y1, x2, y2 = params
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx = 1 if x1 < x2 else (-1 if x1 > x2 else 0)
        sy = 1 if y1 < y2 else (-1 if y1 > y2 else 0)
        lines.append("=== АЛГОРИТМ БРЕЗЕНХЕМА (ОТРЕЗОК) ===")
        lines.append(f"Вход: P1=({x1}, {y1}), P2=({x2}, {y2})")
        lines.append(f"|dx| = {dx}, |dy| = {dy}, sx = {sx}, sy = {sy}")
        if dx == 0 and dy == 0:
            lines.append(f"Вырожденный отрезок: ({x1}, {y1}).")
            return "\n".join(lines)

        x, y = x1, y1
        if dx >= dy:
            err = 2 * dy - dx
            lines.append("Ведущая ось: X (|dx| >= |dy|)")
            lines.append(f"Начальная ошибка: e0 = 2*|dy| - |dx| = {err}\n")
            lines.append(f"{'i':>3} | {'Пиксель':>12} | {'e_тек':>6} | {'Сдвиг':>10}")
            lines.append("-" * 40)
            for i in range(dx + 1):
                if i >= max_rows:
                    lines.append("... (вывод сокращён) ...")
                    break
                px, py = x, y
                e_cur = err
                if err >= 0:
                    shift = f"x+={sx},y+={sy}"
                    y += sy
                    err -= 2 * dx
                else:
                    shift = f"x+={sx}"
                lines.append(f"{i:>3} | ({px:>4}, {py:>4}) | {e_cur:>6} | {shift:>10}")
                x += sx
                err += 2 * dy
        else:
            err = 2 * dx - dy
            lines.append("Ведущая ось: Y (|dy| > |dx|)")
            lines.append(f"Начальная ошибка: e0 = 2*|dx| - |dy| = {err}\n")
            lines.append(f"{'i':>3} | {'Пиксель':>12} | {'e_тек':>6} | {'Сдвиг':>10}")
            lines.append("-" * 40)
            for i in range(dy + 1):
                if i >= max_rows:
                    lines.append("... (вывод сокращён) ...")
                    break
                px, py = x, y
                e_cur = err
                if err >= 0:
                    shift = f"y+={sy},x+={sx}"
                    x += sx
                    err -= 2 * dy
                else:
                    shift = f"y+={sy}"
                lines.append(f"{i:>3} | ({px:>4}, {py:>4}) | {e_cur:>6} | {shift:>10}")
                y += sy
                err += 2 * dx

    elif algo_key == "bres_circle":
        xc, yc, r = params
        lines.append("=== АЛГОРИТМ БРЕЗЕНХЕМА (ОКРУЖНОСТЬ) ===")
        lines.append(f"Центр: ({xc}, {yc}), Радиус R = {r}")
        if r < 0:
            lines.append("Ошибка: радиус должен быть >= 0.")
            return "\n".join(lines)
        if r == 0:
            lines.append(f"R = 0 -> единственная точка ({xc}, {yc}).")
            return "\n".join(lines)
        x, y = 0, r
        d = 3 - 2 * r
        lines.append(f"Начало: x = 0, y = {r}, d0 = 3 - 2*R = {d}")
        lines.append("По 8-кратной симметрии строим 1/8 дуги (x <= y):\n")
        lines.append(f"{'i':>3} | {'(x, y) локал.':>13} | {'d_тек':>6} | {'Выбор':>12}")
        lines.append("-" * 43)
        i = 0
        while x <= y:
            if i >= max_rows:
                lines.append("... (вывод сокращён) ...")
                break
            px, py = x, y
            d_cur = d
            if d < 0:
                choice = "вправо (d<0)"
                d = d + 4 * x + 6
            else:
                choice = "диаг. (d>=0)"
                d = d + 4 * (x - y) + 10
                y -= 1
            lines.append(f"{i:>3} | ({px:>4}, {py:>4}) | {d_cur:>6} | {choice:>12}")
            x += 1
            i += 1

    return "\n".join(lines)


class RasterApp(tk.Tk):
    ALGO_META = {
        "step": {
            "name": "Пошаговый алгоритм (отрезок)",
            "color": "#2563EB",
            "border": "#1D4ED8",
            "mode": "line",
        },
        "dda": {
            "name": "Алгоритм ЦДА (отрезок)",
            "color": "#0D9488",
            "border": "#0F766E",
            "mode": "line",
        },
        "bres_line": {
            "name": "Алгоритм Брезенхема (отрезок)",
            "color": "#7C3AED",
            "border": "#6D28D9",
            "mode": "line",
        },
        "bres_circle": {
            "name": "Алгоритм Брезенхема (окружность)",
            "color": "#D97706",
            "border": "#B45309",
            "mode": "circle",
        },
    }

    def __init__(self):
        super().__init__()
        self.title("ЛР №3: Базовые алгоритмы растеризации — Шабан Владимир")
        self.geometry("1260x780")
        self.minsize(1020, 660)
        self.configure(bg="#F1F5F9")

        self.cell_size = 24.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self._pan_start = None
        self._click_stage = 0
        self._first_click_pt = None

        self.current_pixels: list[tuple[int, int]] = []
        self.current_algo = tk.StringVar(value="bres_line")
        self.show_ideal = tk.BooleanVar(value=True)
        self.show_grid = tk.BooleanVar(value=True)
        self.show_coords_in_cells = tk.BooleanVar(value=False)

        self.var_x1 = tk.StringVar(value="-6")
        self.var_y1 = tk.StringVar(value="-3")
        self.var_x2 = tk.StringVar(value="9")
        self.var_y2 = tk.StringVar(value="5")
        self.var_xc = tk.StringVar(value="0")
        self.var_yc = tk.StringVar(value="0")
        self.var_r = tk.StringVar(value="8")
        self.var_zoom = tk.DoubleVar(value=24.0)

        self._setup_styles()
        self._build_ui()
        self.after(80, self.run_current_algorithm)

    def _setup_styles(self):
        style = ttk.Style(self)
        for theme in ("clam", "vista", "alt", "default"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break
        style.configure("Panel.TFrame", background="#FFFFFF")
        style.configure("Bg.TFrame", background="#F1F5F9")
        style.configure("Header.TLabel", background="#FFFFFF", foreground="#0F172A",
                        font=("sans-serif", 11, "bold"))
        style.configure("Sub.TLabel", background="#FFFFFF", foreground="#475569",
                        font=("sans-serif", 9))
        style.configure("Card.TLabelframe", background="#FFFFFF")
        style.configure("Card.TLabelframe.Label", background="#FFFFFF",
                        foreground="#1E293B", font=("sans-serif", 9, "bold"))
        style.configure("TRadiobutton", background="#FFFFFF", font=("sans-serif", 9))
        style.configure("TCheckbutton", background="#FFFFFF", font=("sans-serif", 9))
        style.configure("Accent.TButton", font=("sans-serif", 9, "bold"))

    def _build_ui(self):
        main_pane = ttk.Frame(self, style="Bg.TFrame")
        main_pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left_panel = ttk.Frame(main_pane, width=420, style="Panel.TFrame")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_panel.pack_propagate(False)

        hdr = ttk.Frame(left_panel, style="Panel.TFrame")
        hdr.pack(fill=tk.X, padx=12, pady=(10, 6))
        ttk.Label(hdr, text="Растеризация отрезков и кривых", style="Header.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Выполнил: Шабан Владимир", style="Sub.TLabel").pack(anchor="w")

        algo_frame = ttk.LabelFrame(left_panel, text=" 1. Алгоритм ", style="Card.TLabelframe")
        algo_frame.pack(fill=tk.X, padx=10, pady=4)
        for key, meta in self.ALGO_META.items():
            rb = ttk.Radiobutton(
                algo_frame,
                text=meta["name"],
                value=key,
                variable=self.current_algo,
                command=self._on_algo_changed,
            )
            rb.pack(anchor="w", padx=8, pady=2)

        param_frame = ttk.LabelFrame(left_panel, text=" 2. Входные координаты ", style="Card.TLabelframe")
        param_frame.pack(fill=tk.X, padx=10, pady=4)

        self.line_inputs = ttk.Frame(param_frame, style="Panel.TFrame")
        self._make_coord_row(self.line_inputs, "Начало (X1, Y1):", self.var_x1, self.var_y1, 0)
        self._make_coord_row(self.line_inputs, "Конец  (X2, Y2):", self.var_x2, self.var_y2, 1)

        presets = ttk.Frame(self.line_inputs, style="Panel.TFrame")
        presets.grid(row=2, column=0, columnspan=3, sticky="we", pady=(4, 2))
        ttk.Button(presets, text="Пологий", width=9,
                   command=lambda: self._apply_line_preset(-6, -3, 9, 5)).pack(side=tk.LEFT, padx=2)
        ttk.Button(presets, text="Крутой", width=9,
                   command=lambda: self._apply_line_preset(-2, -7, 3, 8)).pack(side=tk.LEFT, padx=2)
        ttk.Button(presets, text="Исключ.", width=9,
                   command=lambda: self._apply_line_preset(0, 4, 8, 0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(presets, text="Вертик.", width=8,
                   command=lambda: self._apply_line_preset(4, -5, 4, 6)).pack(side=tk.LEFT, padx=2)

        self.circle_inputs = ttk.Frame(param_frame, style="Panel.TFrame")
        self._make_coord_row(self.circle_inputs, "Центр (Xc, Yc):", self.var_xc, self.var_yc, 0)
        r_row = ttk.Frame(self.circle_inputs, style="Panel.TFrame")
        r_row.grid(row=1, column=0, columnspan=3, sticky="w", pady=3)
        ttk.Label(r_row, text="Радиус R (целое):", background="#FFFFFF", width=18).pack(side=tk.LEFT)
        ttk.Entry(r_row, textvariable=self.var_r, width=8).pack(side=tk.LEFT, padx=4)

        self.line_inputs.pack(fill=tk.X, padx=8, pady=4)

        btn_row = ttk.Frame(param_frame, style="Panel.TFrame")
        btn_row.pack(fill=tk.X, padx=8, pady=(2, 6))
        ttk.Button(btn_row, text="Построить", style="Accent.TButton",
                   command=self.run_current_algorithm).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(btn_row, text="Очистить",
                   command=self.clear_canvas).pack(side=tk.LEFT, padx=(4, 0))

        view_frame = ttk.LabelFrame(left_panel, text=" 3. Масштаб и сетка ", style="Card.TLabelframe")
        view_frame.pack(fill=tk.X, padx=10, pady=4)

        zoom_row = ttk.Frame(view_frame, style="Panel.TFrame")
        zoom_row.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(zoom_row, text="Масштаб:", background="#FFFFFF").pack(side=tk.LEFT)
        self.zoom_scale = ttk.Scale(
            zoom_row, from_=6, to=60, variable=self.var_zoom,
            command=self._on_zoom_slider
        )
        self.zoom_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.lbl_zoom = ttk.Label(zoom_row, text="24 px", background="#FFFFFF", width=6)
        self.lbl_zoom.pack(side=tk.LEFT)
        ttk.Button(zoom_row, text="Центр", width=7, command=self.reset_view).pack(side=tk.LEFT, padx=(4, 0))

        chk_row = ttk.Frame(view_frame, style="Panel.TFrame")
        chk_row.pack(fill=tk.X, padx=8, pady=(0, 6))
        ttk.Checkbutton(chk_row, text="Идеальный контур", variable=self.show_ideal,
                        command=self.redraw).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Checkbutton(chk_row, text="Сетка", variable=self.show_grid,
                        command=self.redraw).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Checkbutton(chk_row, text="Подписи клеток", variable=self.show_coords_in_cells,
                        command=self.redraw).pack(side=tk.LEFT)

        nb = ttk.Notebook(left_panel)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))

        tab_calc = ttk.Frame(nb, style="Panel.TFrame")
        nb.add(tab_calc, text="Вычисления")
        self.txt_calc = tk.Text(tab_calc, wrap=tk.NONE, font=("monospace", 8),
                                bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT, height=12)
        sc_y = ttk.Scrollbar(tab_calc, orient=tk.VERTICAL, command=self.txt_calc.yview)
        sc_x = ttk.Scrollbar(tab_calc, orient=tk.HORIZONTAL, command=self.txt_calc.xview)
        self.txt_calc.configure(yscrollcommand=sc_y.set, xscrollcommand=sc_x.set)
        sc_y.pack(side=tk.RIGHT, fill=tk.Y)
        sc_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_calc.pack(fill=tk.BOTH, expand=True)
        ttk.Button(tab_calc, text="Копировать расчёт в буфер",
                   command=self._copy_calc).pack(fill=tk.X, padx=4, pady=3)

        tab_time = ttk.Frame(nb, style="Panel.TFrame")
        nb.add(tab_time, text="Время (Бенчмарк)")
        ttk.Button(tab_time, text="Запустить тест (2000 повторов каждого алгоритма)",
                   command=self.run_benchmark).pack(fill=tk.X, padx=6, pady=6)
        self.txt_bench = tk.Text(tab_time, wrap=tk.WORD, font=("monospace", 8),
                                 bg="#F8FAFC", fg="#0F172A", relief=tk.FLAT)
        self.txt_bench.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        self.txt_bench.insert("1.0", "Нажмите кнопку выше, чтобы замерить чистое\nвремя выполнения всех 4 алгоритмов.\n")

        tab_info = ttk.Frame(nb, style="Panel.TFrame")
        nb.add(tab_info, text="О сетке")
        info_text = (
            "ПРИВЯЗКА КООРДИНАТ К ДИСКРЕТНОЙ СЕТКЕ:\n\n"
            "1. Каждая целочисленная координата (x, y) задаёт центр\n"
            "   дискретного пикселя на координатной плоскости.\n\n"
            "2. Сам пиксель (x, y) занимает квадратную ячейку\n"
            "   размером 1×1 с границами:\n"
            "   [x - 0.5; x + 0.5] × [y - 0.5; y + 0.5].\n\n"
            "3. Линии пиксельной сетки проходят по полуцелым\n"
            "   значениям (..., -1.5, -0.5, 0.5, 1.5, ...), а оси\n"
            "   координат X=0 и Y=0 — через центры нулевых столбца\n"
            "   и строки. Поэтому идеальная линия проходит точно\n"
            "   через центры начального и конечного пикселей.\n\n"
            "УПРАВЛЕНИЕ ХОЛСТОМ:\n"
            "• Левый клик (2 раза): задать точки/радиус мышью.\n"
            "• Колёсико мыши: масштаб.\n"
            "• Правая (или средняя) кнопка: перемещение сетки."
        )
        txt_info = tk.Text(tab_info, wrap=tk.WORD, font=("sans-serif", 8),
                           bg="#F8FAFC", fg="#1E293B", relief=tk.FLAT)
        txt_info.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        txt_info.insert("1.0", info_text)
        txt_info.configure(state=tk.DISABLED)

        right_panel = ttk.Frame(main_pane, style="Panel.TFrame")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(right_panel, bg="#FFFFFF", highlightthickness=1,
                                highlightbackground="#CBD5E1", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Готов к работе.")
        status_bar = tk.Label(right_panel, textvariable=self.status_var, anchor="w",
                              bg="#F8FAFC", fg="#334155", font=("monospace", 9),
                              padx=8, pady=4, relief=tk.FLAT)
        status_bar.pack(fill=tk.X)

        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom_step(1.15, e.x, e.y))
        self.canvas.bind("<Button-5>", lambda e: self._zoom_step(1 / 1.15, e.x, e.y))
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)
        self.canvas.bind("<ButtonPress-2>", self._on_pan_start)
        self.canvas.bind("<B2-Motion>", self._on_pan_move)
        self.canvas.bind("<Motion>", self._on_mouse_move)

    def _make_coord_row(self, parent, label_text, var_x, var_y, row_idx):
        ttk.Label(parent, text=label_text, background="#FFFFFF", width=18).grid(
            row=row_idx, column=0, sticky="w", pady=2)
        pair = ttk.Frame(parent, style="Panel.TFrame")
        pair.grid(row=row_idx, column=1, sticky="w", pady=2)
        ttk.Entry(pair, textvariable=var_x, width=7).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(pair, textvariable=var_y, width=7).pack(side=tk.LEFT)

    def _on_algo_changed(self):
        self._click_stage = 0
        self._first_click_pt = None
        mode = self.ALGO_META[self.current_algo.get()]["mode"]
        if mode == "line":
            self.circle_inputs.pack_forget()
            self.line_inputs.pack(fill=tk.X, padx=8, pady=4)
        else:
            self.line_inputs.pack_forget()
            self.circle_inputs.pack(fill=tk.X, padx=8, pady=4)
        self.run_current_algorithm()

    def _apply_line_preset(self, x1, y1, x2, y2):
        self.var_x1.set(str(x1))
        self.var_y1.set(str(y1))
        self.var_x2.set(str(x2))
        self.var_y2.set(str(y2))
        self.run_current_algorithm()

    def _read_params(self) -> tuple[int, ...]:
        algo = self.current_algo.get()
        if self.ALGO_META[algo]["mode"] == "line":
            return (
                int(self.var_x1.get().strip()),
                int(self.var_y1.get().strip()),
                int(self.var_x2.get().strip()),
                int(self.var_y2.get().strip()),
            )
        else:
            r = int(self.var_r.get().strip())
            if r < 0:
                raise ValueError("Радиус должен быть >= 0")
            return (
                int(self.var_xc.get().strip()),
                int(self.var_yc.get().strip()),
                r,
            )

    def run_current_algorithm(self):
        try:
            params = self._read_params()
        except ValueError as exc:
            messagebox.showerror("Ошибка ввода", f"Введите корректные целые числа.\n({exc})")
            return

        algo = self.current_algo.get()
        if self.ALGO_META[algo]["mode"] == "line":
            if max(abs(params[2] - params[0]), abs(params[3] - params[1])) > 2000:
                messagebox.showwarning("Ограничение холста", "Разница координат > 2000 замедлит отрисовку.")
                return
        else:
            if params[2] > 1000:
                messagebox.showwarning("Ограничение холста", "Радиус > 1000 замедлит отрисовку.")
                return

        t0 = time.perf_counter_ns()
        if algo == "step":
            pts = raster_step_line(*params)
        elif algo == "dda":
            pts = raster_dda_line(*params)
        elif algo == "bres_line":
            pts = raster_bresenham_line(*params)
        else:
            pts = raster_bresenham_circle(*params)
        elapsed_ns = time.perf_counter_ns() - t0

        self.current_pixels = list(dict.fromkeys(pts))

        trace = build_calculation_trace(algo, params)
        self.txt_calc.delete("1.0", tk.END)
        self.txt_calc.insert("1.0", trace)

        self.redraw()
        self.status_var.set(
            f"{self.ALGO_META[algo]['name']} | Пикселей: {len(self.current_pixels)} | "
            f"Время расчёта: {elapsed_ns / 1000:.2f} мкс ({elapsed_ns} нс)"
        )

    def clear_canvas(self):
        self.current_pixels = []
        self._click_stage = 0
        self._first_click_pt = None
        self.txt_calc.delete("1.0", tk.END)
        self.redraw()
        self.status_var.set("Холст очищен.")

    def _copy_calc(self):
        text = self.txt_calc.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_var.set("Расчёт скопирован в буфер обмена.")

    def run_benchmark(self):
        iterations = 2000
        line_args = (-40, -18, 60, 27)
        circle_args = (0, 0, 50)

        tests = [
            ("Пошаговый (отрезок 100px)", raster_step_line, line_args),
            ("ЦДА / DDA (отрезок 100px)", raster_dda_line, line_args),
            ("Брезенхем (отрезок 100px)", raster_bresenham_line, line_args),
            ("Брезенхем (окружность R=50)", raster_bresenham_circle, circle_args),
        ]

        report = [
            f"Бенчмарк: {iterations} запусков каждого алгоритма",
            f"Тест отрезков: {line_args}, окружности: {circle_args}",
            "-" * 48,
        ]
        results_ns = []
        for label, fn, args in tests:
            fn(*args)
            t0 = time.perf_counter_ns()
            for _ in range(iterations):
                fn(*args)
            total_ns = time.perf_counter_ns() - t0
            avg_us = (total_ns / iterations) / 1000.0
            total_ms = total_ns / 1_000_000.0
            results_ns.append((label, total_ms, avg_us))
            report.append(f"{label}:\n  Всего: {total_ms:.3f} мс | 1 вызов: {avg_us:.3f} мкс")

        line_times = results_ns[:3]
        fastest = min(t[2] for t in line_times)
        report.append("-" * 48)
        report.append("Относительная скорость для отрезков:")
        for label, _, avg_us in line_times:
            ratio = avg_us / fastest if fastest > 0 else 1.0
            report.append(f"  {label.split('(')[0].strip():<14} -> x{ratio:.2f}")

        self.txt_bench.delete("1.0", tk.END)
        self.txt_bench.insert("1.0", "\n".join(report))

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        sx = w / 2 + self.offset_x + wx * self.cell_size
        sy = h / 2 + self.offset_y - wy * self.cell_size
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        wx = (sx - w / 2 - self.offset_x) / self.cell_size
        wy = (h / 2 + self.offset_y - sy) / self.cell_size
        return wx, wy

    def redraw(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 2 or h <= 2:
            return

        cs = self.cell_size
        min_wx, max_wy = self.screen_to_world(0, 0)
        max_wx, min_wy = self.screen_to_world(w, h)
        x_start = math.floor(min_wx) - 1
        x_end = math.ceil(max_wx) + 1
        y_start = math.floor(min_wy) - 1
        y_end = math.ceil(max_wy) + 1

        if self.show_grid.get():
            for gx in range(x_start, x_end + 1):
                sx, _ = self.world_to_screen(gx + 0.5, 0)
                c.create_line(sx, 0, sx, h, fill="#E2E8F0")
            for gy in range(y_start, y_end + 1):
                _, sy = self.world_to_screen(0, gy + 0.5)
                c.create_line(0, sy, w, sy, fill="#E2E8F0")

            for gx in range((x_start // 5) * 5, x_end + 1, 5):
                sx, _ = self.world_to_screen(gx, 0)
                c.create_line(sx, 0, sx, h, fill="#CBD5E1", dash=(2, 3))
            for gy in range((y_start // 5) * 5, y_end + 1, 5):
                _, sy = self.world_to_screen(0, gy)
                c.create_line(0, sy, w, sy, fill="#CBD5E1", dash=(2, 3))

        meta = self.ALGO_META[self.current_algo.get()]
        fill_col = meta["color"]
        border_col = meta["border"] if cs >= 10 else fill_col

        for px, py in self.current_pixels:
            if px < x_start - 1 or px > x_end + 1 or py < y_start - 1 or py > y_end + 1:
                continue
            sx1, sy1 = self.world_to_screen(px - 0.5, py + 0.5)
            sx2, sy2 = self.world_to_screen(px + 0.5, py - 0.5)
            c.create_rectangle(sx1, sy1, sx2, sy2, fill=fill_col, outline=border_col)
            if self.show_coords_in_cells.get() and cs >= 28:
                cx, cy = (sx1 + sx2) / 2, (sy1 + sy2) / 2
                c.create_text(cx, cy, text=f"{px},{py}", fill="#FFFFFF",
                              font=("monospace", 7))

        ox, oy = self.world_to_screen(0, 0)
        c.create_line(0, oy, w, oy, fill="#1E293B", width=2, arrow=tk.LAST)
        c.create_text(w - 14, oy - 14, text="X", fill="#0F172A", font=("sans-serif", 10, "bold"))
        c.create_line(ox, h, ox, 0, fill="#1E293B", width=2, arrow=tk.LAST)
        c.create_text(ox + 14, 14, text="Y", fill="#0F172A", font=("sans-serif", 10, "bold"))

        step_lbl = 1 if cs >= 26 else (2 if cs >= 13 else 5)
        for gx in range((x_start // step_lbl) * step_lbl, x_end + 1, step_lbl):
            sx, _ = self.world_to_screen(gx, 0)
            if 15 < sx < w - 20:
                c.create_line(sx, oy - 4, sx, oy + 4, fill="#1E293B", width=1.5)
                if gx != 0:
                    lbl_y = min(max(oy + 13, 14), h - 12)
                    c.create_text(sx, lbl_y, text=str(gx), fill="#334155", font=("monospace", 8))

        for gy in range((y_start // step_lbl) * step_lbl, y_end + 1, step_lbl):
            _, sy = self.world_to_screen(0, gy)
            if 18 < sy < h - 15:
                c.create_line(ox - 4, sy, ox + 4, sy, fill="#1E293B", width=1.5)
                if gy != 0:
                    lbl_x = min(max(ox - 16, 18), w - 18)
                    c.create_text(lbl_x, sy, text=str(gy), fill="#334155", font=("monospace", 8))

        c.create_text(ox - 10, oy + 12, text="0", fill="#0F172A", font=("monospace", 8, "bold"))

        if self.show_ideal.get() and self.current_pixels:
            try:
                params = self._read_params()
            except ValueError:
                params = None
            if params:
                if meta["mode"] == "line":
                    x1, y1, x2, y2 = params
                    sx1, sy1 = self.world_to_screen(x1, y1)
                    sx2, sy2 = self.world_to_screen(x2, y2)
                    c.create_line(sx1, sy1, sx2, sy2, fill="#EF4444", width=2, dash=(5, 3))
                    c.create_oval(sx1 - 4, sy1 - 4, sx1 + 4, sy1 + 4, fill="#EF4444", outline="#FFFFFF")
                    c.create_oval(sx2 - 4, sy2 - 4, sx2 + 4, sy2 + 4, fill="#EF4444", outline="#FFFFFF")
                else:
                    xc, yc, r = params
                    sx1, sy1 = self.world_to_screen(xc - r, yc + r)
                    sx2, sy2 = self.world_to_screen(xc + r, yc - r)
                    cx, cy = self.world_to_screen(xc, yc)
                    c.create_oval(sx1, sy1, sx2, sy2, outline="#EF4444", width=2, dash=(5, 3))
                    c.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="#EF4444", outline="#FFFFFF")

        if self._click_stage == 1 and self._first_click_pt is not None:
            px, py = self._first_click_pt
            sx, sy = self.world_to_screen(px, py)
            c.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, outline="#DC2626", width=2)

    def _on_zoom_slider(self, val):
        self.cell_size = float(val)
        self.lbl_zoom.configure(text=f"{int(round(self.cell_size))} px")
        self.redraw()

    def _zoom_step(self, factor: float, mx: float, my: float):
        wx_before, wy_before = self.screen_to_world(mx, my)
        new_size = max(6.0, min(60.0, self.cell_size * factor))
        if abs(new_size - self.cell_size) < 1e-6:
            return
        self.cell_size = new_size
        self.var_zoom.set(new_size)
        self.lbl_zoom.configure(text=f"{int(round(new_size))} px")

        sx_after, sy_after = self.world_to_screen(wx_before, wy_before)
        self.offset_x += (mx - sx_after)
        self.offset_y += (my - sy_after)
        self.redraw()

    def _on_mouse_wheel(self, event):
        factor = 1.12 if event.delta > 0 else 1 / 1.12
        self._zoom_step(factor, event.x, event.y)

    def reset_view(self):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.cell_size = 24.0
        self.var_zoom.set(24.0)
        self.lbl_zoom.configure(text="24 px")
        self.redraw()

    def _on_pan_start(self, event):
        self._pan_start = (event.x, event.y)

    def _on_pan_move(self, event):
        if self._pan_start is None:
            return
        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]
        self.offset_x += dx
        self.offset_y += dy
        self._pan_start = (event.x, event.y)
        self.redraw()

    def _on_mouse_move(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        px, py = iround(wx), iround(wy)
        hint = " | Кликните 2-ю точку" if self._click_stage == 1 else ""
        self.status_var.set(
            f"Курсор: ({wx:.2f}, {wy:.2f}) -> Пиксель сетки: ({px}, {py}){hint}"
        )

    def _on_left_click(self, event):
        wx, wy = self.screen_to_world(event.x, event.y)
        px, py = iround(wx), iround(wy)
        mode = self.ALGO_META[self.current_algo.get()]["mode"]

        if self._click_stage == 0:
            self._first_click_pt = (px, py)
            self._click_stage = 1
            if mode == "line":
                self.var_x1.set(str(px))
                self.var_y1.set(str(py))
                self.status_var.set(f"Задана точка P1=({px}, {py}). Кликните для выбора P2.")
            else:
                self.var_xc.set(str(px))
                self.var_yc.set(str(py))
                self.status_var.set(f"Задан центр ({px}, {py}). Кликните для задания радиуса.")
            self.redraw()
        else:
            x0, y0 = self._first_click_pt
            self._click_stage = 0
            self._first_click_pt = None
            if mode == "line":
                self.var_x2.set(str(px))
                self.var_y2.set(str(py))
            else:
                r = iround(math.hypot(px - x0, py - y0))
                self.var_r.set(str(r))
            self.run_current_algorithm()


if __name__ == "__main__":
    app = RasterApp()
    app.mainloop()