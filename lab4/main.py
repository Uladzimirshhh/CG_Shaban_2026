import math
import tkinter as tk
from tkinter import ttk, messagebox


INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def compute_outcode(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> int:
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code


def cohen_sutherland_clip(
    x1: float, y1: float, x2: float, y2: float,
    xmin: float, ymin: float, xmax: float, ymax: float,
) -> tuple[float, float, float, float] | None:
    cx1, cy1, cx2, cy2 = x1, y1, x2, y2
    code1 = compute_outcode(cx1, cy1, xmin, ymin, xmax, ymax)
    code2 = compute_outcode(cx2, cy2, xmin, ymin, xmax, ymax)

    step = 0
    while step < 12:
        if code1 == 0 and code2 == 0:
            return (cx1, cy1, cx2, cy2)

        if (code1 & code2) != 0:
            return None

        step += 1
        code_out = code1 if code1 != 0 else code2

        if code_out & TOP:
            y = ymax
            if abs(cy2 - cy1) > 1e-12:
                x = cx1 + (cx2 - cx1) * (ymax - cy1) / (cy2 - cy1)
            else:
                x = cx1
        elif code_out & BOTTOM:
            y = ymin
            if abs(cy2 - cy1) > 1e-12:
                x = cx1 + (cx2 - cx1) * (ymin - cy1) / (cy2 - cy1)
            else:
                x = cx1
        elif code_out & RIGHT:
            x = xmax
            if abs(cx2 - cx1) > 1e-12:
                y = cy1 + (cy2 - cy1) * (xmax - cx1) / (cx2 - cx1)
            else:
                y = cy1
        else:
            x = xmin
            if abs(cx2 - cx1) > 1e-12:
                y = cy1 + (cy2 - cy1) * (xmin - cx1) / (cx2 - cx1)
            else:
                y = cy1

        if code_out == code1:
            cx1, cy1 = x, y
            code1 = compute_outcode(cx1, cy1, xmin, ymin, xmax, ymax)
        else:
            cx2, cy2 = x, y
            code2 = compute_outcode(cx2, cy2, xmin, ymin, xmax, ymax)

    return None


def is_convex_polygon(pts: list[tuple[float, float]]) -> bool:
    n = len(pts)
    if n < 3:
        return False
    sign = 0
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        x3, y3 = pts[(i + 2) % n]
        cross = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
        if abs(cross) > 1e-9:
            cur = 1 if cross > 0 else -1
            if sign == 0:
                sign = cur
            elif sign != cur:
                return False
    return sign != 0


def sutherland_hodgman_clip(
    polygon: list[tuple[float, float]],
    xmin: float, ymin: float, xmax: float, ymax: float,
) -> list[tuple[float, float]]:
    if len(polygon) < 3:
        return []

    edges = [
        (
            lambda p: p[0] >= xmin - 1e-9,
            lambda a, b: (
                xmin,
                a[1] + (b[1] - a[1]) * (xmin - a[0]) / (b[0] - a[0])
                if abs(b[0] - a[0]) > 1e-12 else a[1],
            ),
        ),
        (
            lambda p: p[0] <= xmax + 1e-9,
            lambda a, b: (
                xmax,
                a[1] + (b[1] - a[1]) * (xmax - a[0]) / (b[0] - a[0])
                if abs(b[0] - a[0]) > 1e-12 else a[1],
            ),
        ),
        (
            lambda p: p[1] >= ymin - 1e-9,
            lambda a, b: (
                a[0] + (b[0] - a[0]) * (ymin - a[1]) / (b[1] - a[1])
                if abs(b[1] - a[1]) > 1e-12 else a[0],
                ymin,
            ),
        ),
        (
            lambda p: p[1] <= ymax + 1e-9,
            lambda a, b: (
                a[0] + (b[0] - a[0]) * (ymax - a[1]) / (b[1] - a[1])
                if abs(b[1] - a[1]) > 1e-12 else a[0],
                ymax,
            ),
        ),
    ]

    output = list(polygon)
    for inside_fn, intersect_fn in edges:
        if not output:
            break
        inp = output
        output = []
        s = inp[-1]
        for e in inp:
            e_in = inside_fn(e)
            s_in = inside_fn(s)
            if e_in:
                if not s_in:
                    output.append(intersect_fn(s, e))
                output.append(e)
            elif s_in:
                output.append(intersect_fn(s, e))
            s = e

        cleaned = []
        for pt in output:
            if not cleaned or math.hypot(pt[0] - cleaned[-1][0], pt[1] - cleaned[-1][1]) > 1e-8:
                cleaned.append(pt)
        if len(cleaned) > 1 and math.hypot(cleaned[0][0] - cleaned[-1][0], cleaned[0][1] - cleaned[-1][1]) <= 1e-8:
            cleaned.pop()
        output = cleaned

    if len(output) < 3:
        return []

    return output


def nice_step(min_world_span: float) -> float:
    if min_world_span <= 0:
        return 1.0
    exp = math.floor(math.log10(min_world_span))
    base = 10.0 ** exp
    frac = min_world_span / base
    if frac <= 1.5:
        return 1.0 * base
    if frac <= 3.5:
        return 2.0 * base
    if frac <= 7.5:
        return 5.0 * base
    return 10.0 * base


def format_tick(val: float, step: float) -> str:
    if abs(val) < 1e-9:
        return "0"
    if step >= 1.0 and abs(val - round(val)) < 1e-6:
        return str(int(round(val)))
    return f"{val:.4g}"


class ClippingApp(tk.Tk):
    DEMO_SEGMENTS = (
        "6\n"
        "-8 -4 12 8\n"
        "-2 2 6 5\n"
        "-12 6 -6 10\n"
        "3 -7 3 11\n"
        "-10 4 14 4\n"
        "5 -6 15 4\n"
        "-5 -3 10 7\n"
    )

    DEMO_POLYGON = (
        "6\n"
        "-7 1\n"
        "-3 9\n"
        "6 10\n"
        "13 4\n"
        "9 -5\n"
        "-2 -6\n"
        "-4 -3 10 7\n"
    )

    def __init__(self):
        super().__init__()
        self.title("ЛР №4 (Вариант 13): Алгоритмы отсечения — Шабан Владимир")
        self.geometry("1240x760")
        self.minsize(980, 620)
        self.configure(bg="#F1F5F9")

        self.mode_var = tk.StringVar(value="cohen")
        self.mouse_add_var = tk.BooleanVar(value=True)
        self.show_grid_var = tk.BooleanVar(value=True)

        self.scale = 26.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self._pan_start = None
        self._first_pt = None

        self.window_rect: tuple[float, float, float, float] = (-5.0, -3.0, 10.0, 7.0)
        self.segments: list[tuple[float, float, float, float]] = []
        self.clipped_segments: list[tuple[float, float, float, float] | None] = []
        self.polygon: list[tuple[float, float]] = []
        self.clipped_polygon: list[tuple[float, float]] = []

        self._setup_styles()
        self._build_ui()
        self.load_demo()

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

        left = ttk.Frame(main_pane, width=380, style="Panel.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)

        hdr = ttk.Frame(left, style="Panel.TFrame")
        hdr.pack(fill=tk.X, padx=12, pady=(10, 6))
        ttk.Label(hdr, text="Алгоритмы отсечения (Вариант 13)", style="Header.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Выполнил: Шабан Владимир", style="Sub.TLabel").pack(anchor="w")

        mode_frame = ttk.LabelFrame(left, text=" 1. Алгоритм ", style="Card.TLabelframe")
        mode_frame.pack(fill=tk.X, padx=10, pady=4)
        ttk.Radiobutton(
            mode_frame,
            text="Часть 1: Сазерленд–Коэн (отрезки)",
            value="cohen",
            variable=self.mode_var,
            command=self._on_mode_change,
        ).pack(anchor="w", padx=8, pady=2)
        ttk.Radiobutton(
            mode_frame,
            text="Часть 2: Сазерленд–Ходжмен (выпуклый многоуг.)",
            value="hodgman",
            variable=self.mode_var,
            command=self._on_mode_change,
        ).pack(anchor="w", padx=8, pady=2)

        data_frame = ttk.LabelFrame(left, text=" 2. Входные данные ", style="Card.TLabelframe")
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        top_btns = ttk.Frame(data_frame, style="Panel.TFrame")
        top_btns.pack(fill=tk.X, padx=8, pady=(6, 2))
        ttk.Button(top_btns, text="Демо-пример", command=self.load_demo).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(top_btns, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        txt_wrap = ttk.Frame(data_frame, style="Panel.TFrame")
        txt_wrap.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self.txt_input = tk.Text(txt_wrap, font=("monospace", 9),
                                 bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, borderwidth=1)
        sc_in = ttk.Scrollbar(txt_wrap, orient=tk.VERTICAL, command=self.txt_input.yview)
        self.txt_input.configure(yscrollcommand=sc_in.set)
        sc_in.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        apply_row = ttk.Frame(data_frame, style="Panel.TFrame")
        apply_row.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Button(apply_row, text="Выполнить отсечение", style="Accent.TButton",
                   command=self.run_from_editor).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(apply_row, text="Автомасштаб",
                   command=self.fit_view).pack(side=tk.LEFT)

        view_frame = ttk.LabelFrame(left, text=" 3. Управление и сетка ", style="Card.TLabelframe")
        view_frame.pack(fill=tk.X, padx=10, pady=(4, 10))
        opts = ttk.Frame(view_frame, style="Panel.TFrame")
        opts.pack(fill=tk.X, padx=8, pady=6)
        ttk.Checkbutton(opts, text="Добавлять кликом мыши", variable=self.mouse_add_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(opts, text="Сетка", variable=self.show_grid_var, command=self.redraw).pack(side=tk.LEFT)

        right = ttk.Frame(main_pane, style="Panel.TFrame")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        legend = tk.Frame(right, bg="#F8FAFC", padx=8, pady=5)
        legend.pack(fill=tk.X)
        self._add_legend_item(legend, "#2563EB", "Отсекающее окно")
        self._add_legend_item(legend, "#EF4444", "Исходные объекты (пунктир)")
        self._add_legend_item(legend, "#16A34A", "Видимые части после отсечения")
        tk.Label(legend, text="| Колёсико: зум, ПКМ: сдвиг", bg="#F8FAFC",
                 fg="#64748B", font=("sans-serif", 8)).pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(right, bg="#FFFFFF", highlightthickness=1,
                                highlightbackground="#CBD5E1", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Готов к работе.")
        tk.Label(right, textvariable=self.status_var, anchor="w", bg="#F8FAFC",
                 fg="#334155", font=("monospace", 9), padx=8, pady=4).pack(fill=tk.X)

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

    def _add_legend_item(self, parent, color: str, text: str):
        box = tk.Frame(parent, bg=color, width=14, height=10)
        box.pack(side=tk.LEFT, padx=(4, 4))
        box.pack_propagate(False)
        tk.Label(parent, text=text, bg="#F8FAFC", fg="#1E293B",
                 font=("sans-serif", 8, "bold")).pack(side=tk.LEFT, padx=(0, 12))

    def _on_mode_change(self):
        self._first_pt = None
        self.load_demo()

    def load_demo(self):
        self._first_pt = None
        self.txt_input.delete("1.0", tk.END)
        if self.mode_var.get() == "cohen":
            self.txt_input.insert("1.0", self.DEMO_SEGMENTS)
        else:
            self.txt_input.insert("1.0", self.DEMO_POLYGON)
        self.run_from_editor(auto_fit=True)

    def clear_all(self):
        self._first_pt = None
        xmin, ymin, xmax, ymax = self.window_rect
        self.segments = []
        self.clipped_segments = []
        self.polygon = []
        self.clipped_polygon = []
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert("1.0", f"0\n{xmin:g} {ymin:g} {xmax:g} {ymax:g}\n")
        self.redraw()
        self.status_var.set("Объекты очищены. Можете задать новые кликами мыши или в редакторе.")

    def _parse_input_text(self) -> tuple[str, list[tuple[float, ...]], tuple[float, float, float, float]]:
        raw_lines = self.txt_input.get("1.0", tk.END).splitlines()
        parsed_rows = []
        for line in raw_lines:
            clean = line.split("*")[0].split("#")[0].strip()
            if not clean:
                continue
            nums = [float(tok) for tok in clean.split()]
            if nums:
                parsed_rows.append(nums)

        if len(parsed_rows) < 2:
            raise ValueError("Недостаточно строк: ожидается число n, объекты и строка окна (Xmin Ymin Xmax Ymax).")

        if len(parsed_rows[0]) != 1:
            raise ValueError("Первая строка должна содержать одно целое число n (количество объектов).")
        n = int(round(parsed_rows[0][0]))
        if n < 0:
            raise ValueError("Количество объектов n не может быть отрицательным.")

        if len(parsed_rows) < n + 2:
            raise ValueError(f"Указано n={n}, но строк в файле меньше, чем n + 2.")

        win_row = parsed_rows[n + 1]
        if len(win_row) != 4:
            raise ValueError("Последняя строка окна должна содержать 4 числа: Xmin Ymin Xmax Ymax.")
        wx1, wy1, wx2, wy2 = win_row
        window = (min(wx1, wx2), min(wy1, wy2), max(wx1, wx2), max(wy1, wy2))

        obj_rows = parsed_rows[1:n + 1]
        if n == 0:
            return self.mode_var.get(), [], window

        if all(len(r) == 4 for r in obj_rows):
            return "cohen", [tuple(r) for r in obj_rows], window
        if all(len(r) == 2 for r in obj_rows):
            return "hodgman", [tuple(r) for r in obj_rows], window

        raise ValueError("Строки объектов должны иметь по 4 числа (для отрезков) или по 2 числа (для вершин многоугольника).")

    def run_from_editor(self, auto_fit: bool = False):
        try:
            detected_mode, items, window = self._parse_input_text()
        except ValueError as exc:
            messagebox.showerror("Ошибка формата данных", str(exc))
            return

        if items and detected_mode != self.mode_var.get():
            self.mode_var.set(detected_mode)

        self.window_rect = window
        xmin, ymin, xmax, ymax = window

        if self.mode_var.get() == "cohen":
            self.segments = items
            self.polygon = []
            self.clipped_polygon = []
            self.clipped_segments = []
            visible_count = 0
            for x1, y1, x2, y2 in self.segments:
                clipped = cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
                self.clipped_segments.append(clipped)
                if clipped is not None:
                    visible_count += 1
            self.status_var.set(
                f"Сазерленд–Коэн: всего отрезков {len(self.segments)}, видимых {visible_count}."
            )
        else:
            self.polygon = items
            self.segments = []
            self.clipped_segments = []
            self.clipped_polygon = sutherland_hodgman_clip(self.polygon, xmin, ymin, xmax, ymax)
            warn = ""
            if len(self.polygon) >= 3 and not is_convex_polygon(self.polygon):
                warn = " | Внимание: многоугольник невыпуклый"
            self.status_var.set(
                f"Сазерленд–Ходжмен: исходных вершин {len(self.polygon)}, после отсечения {len(self.clipped_polygon)}.{warn}"
            )

        if auto_fit:
            self.after(30, self.fit_view)
        else:
            self.redraw()

    def _sync_editor_from_state(self):
        xmin, ymin, xmax, ymax = self.window_rect
        lines = []
        if self.mode_var.get() == "cohen":
            lines.append(str(len(self.segments)))
            for x1, y1, x2, y2 in self.segments:
                lines.append(f"{x1:g} {y1:g} {x2:g} {y2:g}")
        else:
            lines.append(str(len(self.polygon)))
            for x, y in self.polygon:
                lines.append(f"{x:g} {y:g}")
        lines.append(f"{xmin:g} {ymin:g} {xmax:g} {ymax:g}")
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert("1.0", "\n".join(lines) + "\n")

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        sx = w / 2 + self.offset_x + wx * self.scale
        sy = h / 2 + self.offset_y - wy * self.scale
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        w = max(self.canvas.winfo_width(), 1)
        h = max(self.canvas.winfo_height(), 1)
        wx = (sx - w / 2 - self.offset_x) / self.scale
        wy = (h / 2 + self.offset_y - sy) / self.scale
        return wx, wy

    def fit_view(self):
        w = max(self.canvas.winfo_width(), 400)
        h = max(self.canvas.winfo_height(), 300)

        xs = [self.window_rect[0], self.window_rect[2], 0.0]
        ys = [self.window_rect[1], self.window_rect[3], 0.0]
        for x1, y1, x2, y2 in self.segments:
            xs.extend([x1, x2])
            ys.extend([y1, y2])
        for x, y in self.polygon:
            xs.append(x)
            ys.append(y)

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 4.0)
        span_y = max(max_y - min_y, 4.0)

        self.scale = min((w * 0.78) / span_x, (h * 0.78) / span_y)
        self.scale = max(0.05, min(200.0, self.scale))

        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0
        self.offset_x = -cx * self.scale
        self.offset_y = cy * self.scale
        self.redraw()

    def redraw(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 2 or h <= 2:
            return

        min_wx, max_wy = self.screen_to_world(0, 0)
        max_wx, min_wy = self.screen_to_world(w, h)
        step = nice_step(65.0 / self.scale)

        if self.show_grid_var.get():
            gx = math.floor(min_wx / step) * step
            while gx <= max_wx + step:
                sx, _ = self.world_to_screen(gx, 0)
                c.create_line(sx, 0, sx, h, fill="#E2E8F0")
                gx += step

            gy = math.floor(min_wy / step) * step
            while gy <= max_wy + step:
                _, sy = self.world_to_screen(0, gy)
                c.create_line(0, sy, w, sy, fill="#E2E8F0")
                gy += step

        ox, oy = self.world_to_screen(0, 0)
        c.create_line(0, oy, w, oy, fill="#1E293B", width=2, arrow=tk.LAST)
        c.create_text(w - 14, min(max(oy - 14, 14), h - 14), text="X",
                      fill="#0F172A", font=("sans-serif", 10, "bold"))
        c.create_line(ox, h, ox, 0, fill="#1E293B", width=2, arrow=tk.LAST)
        c.create_text(min(max(ox + 14, 14), w - 14), 14, text="Y",
                      fill="#0F172A", font=("sans-serif", 10, "bold"))

        gx = math.floor(min_wx / step) * step
        while gx <= max_wx + step:
            sx, _ = self.world_to_screen(gx, 0)
            if 18 < sx < w - 22 and abs(gx) > 1e-9:
                c.create_line(sx, oy - 4, sx, oy + 4, fill="#1E293B", width=1.5)
                lbl_y = min(max(oy + 13, 14), h - 12)
                c.create_text(sx, lbl_y, text=format_tick(gx, step),
                              fill="#334155", font=("monospace", 8))
            gx += step

        gy = math.floor(min_wy / step) * step
        while gy <= max_wy + step:
            _, sy = self.world_to_screen(0, gy)
            if 18 < sy < h - 18 and abs(gy) > 1e-9:
                c.create_line(ox - 4, sy, ox + 4, sy, fill="#1E293B", width=1.5)
                lbl_x = min(max(ox - 18, 22), w - 22)
                c.create_text(lbl_x, sy, text=format_tick(gy, step),
                              fill="#334155", font=("monospace", 8))
            gy += step

        if -20 < ox < w + 20 and -20 < oy < h + 20:
            c.create_text(ox - 10, oy + 12, text="0", fill="#0F172A", font=("monospace", 8, "bold"))

        xmin, ymin, xmax, ymax = self.window_rect
        wx1, wy1 = self.world_to_screen(xmin, ymax)
        wx2, wy2 = self.world_to_screen(xmax, ymin)
        c.create_rectangle(wx1, wy1, wx2, wy2, outline="#2563EB", width=2.5)
        c.create_text(wx1 + 4, wy1 - 10, text=f"({xmin:g}, {ymax:g})",
                      anchor="w", fill="#1D4ED8", font=("monospace", 8, "bold"))
        c.create_text(wx2 - 4, wy2 + 11, text=f"({xmax:g}, {ymin:g})",
                      anchor="e", fill="#1D4ED8", font=("monospace", 8, "bold"))

        if self.mode_var.get() == "cohen":
            for x1, y1, x2, y2 in self.segments:
                sx1, sy1 = self.world_to_screen(x1, y1)
                sx2, sy2 = self.world_to_screen(x2, y2)
                c.create_line(sx1, sy1, sx2, sy2, fill="#EF4444", width=2, dash=(6, 4))
                c.create_oval(sx1 - 3, sy1 - 3, sx1 + 3, sy1 + 3, fill="#EF4444", outline="#FFFFFF")
                c.create_oval(sx2 - 3, sy2 - 3, sx2 + 3, sy2 + 3, fill="#EF4444", outline="#FFFFFF")

            for seg in self.clipped_segments:
                if seg is None:
                    continue
                x1, y1, x2, y2 = seg
                sx1, sy1 = self.world_to_screen(x1, y1)
                sx2, sy2 = self.world_to_screen(x2, y2)
                c.create_line(sx1, sy1, sx2, sy2, fill="#16A34A", width=3.5)
                c.create_oval(sx1 - 4, sy1 - 4, sx1 + 4, sy1 + 4, fill="#16A34A", outline="#FFFFFF")
                c.create_oval(sx2 - 4, sy2 - 4, sx2 + 4, sy2 + 4, fill="#16A34A", outline="#FFFFFF")
        else:
            if len(self.polygon) >= 2:
                flat_orig = []
                for px, py in self.polygon:
                    sx, sy = self.world_to_screen(px, py)
                    flat_orig.extend([sx, sy])
                if len(self.polygon) >= 3:
                    c.create_polygon(*flat_orig, fill="", outline="#EF4444", width=2, dash=(6, 4))
                else:
                    c.create_line(*flat_orig, fill="#EF4444", width=2, dash=(6, 4))
                for idx, (px, py) in enumerate(self.polygon, start=1):
                    sx, sy = self.world_to_screen(px, py)
                    c.create_oval(sx - 3.5, sy - 3.5, sx + 3.5, sy + 3.5, fill="#EF4444", outline="#FFFFFF")
                    c.create_text(sx + 8, sy - 8, text=f"P{idx}", fill="#B91C1C", font=("monospace", 8))

            if len(self.clipped_polygon) >= 3:
                flat_clip = []
                for px, py in self.clipped_polygon:
                    sx, sy = self.world_to_screen(px, py)
                    flat_clip.extend([sx, sy])
                c.create_polygon(*flat_clip, fill="", outline="#16A34A", width=3.5)
                for px, py in self.clipped_polygon:
                    sx, sy = self.world_to_screen(px, py)
                    c.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill="#16A34A", outline="#FFFFFF")

        if self._first_pt is not None:
            sx, sy = self.world_to_screen(*self._first_pt)
            c.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, outline="#DC2626", width=2)

    def _zoom_step(self, factor: float, mx: float, my: float):
        wx_before, wy_before = self.screen_to_world(mx, my)
        new_scale = max(0.05, min(200.0, self.scale * factor))
        if abs(new_scale - self.scale) < 1e-9:
            return
        self.scale = new_scale
        sx_after, sy_after = self.world_to_screen(wx_before, wy_before)
        self.offset_x += (mx - sx_after)
        self.offset_y += (my - sy_after)
        self.redraw()

    def _on_mouse_wheel(self, event):
        factor = 1.12 if event.delta > 0 else 1 / 1.12
        self._zoom_step(factor, event.x, event.y)

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
        snap_x, snap_y = round(wx, 1), round(wy, 1)
        hint = " | Кликните 2-ю точку отрезка" if self._first_pt is not None else ""
        self.status_var.set(f"Курсор: ({snap_x:g}, {snap_y:g}){hint}")

    def _on_left_click(self, event):
        if not self.mouse_add_var.get():
            return
        wx, wy = self.screen_to_world(event.x, event.y)
        px = float(round(wx)) if self.scale >= 12 else round(wx, 1)
        py = float(round(wy)) if self.scale >= 12 else round(wy, 1)

        if self.mode_var.get() == "cohen":
            if self._first_pt is None:
                self._first_pt = (px, py)
                self.status_var.set(f"Начало отрезка ({px:g}, {py:g}). Кликните конечную точку.")
                self.redraw()
            else:
                x1, y1 = self._first_pt
                self._first_pt = None
                self.segments.append((x1, y1, px, py))
                self._sync_editor_from_state()
                self.run_from_editor(auto_fit=False)
        else:
            self.polygon.append((px, py))
            self._sync_editor_from_state()
            self.run_from_editor(auto_fit=False)


if __name__ == "__main__":
    app = ClippingApp()
    app.mainloop()