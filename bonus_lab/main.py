import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


def mat4_identity() -> list[list[float]]:
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_mul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    res = [[0.0, 0.0, 0.0, 0.0] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            res[i][j] = (
                a[i][0] * b[0][j]
                + a[i][1] * b[1][j]
                + a[i][2] * b[2][j]
                + a[i][3] * b[3][j]
            )
    return res


def mat4_translate(tx: float, ty: float, tz: float) -> list[list[float]]:
    return [
        [1.0, 0.0, 0.0, tx],
        [0.0, 1.0, 0.0, ty],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_scale(sx: float, sy: float, sz: float) -> list[list[float]]:
    return [
        [sx, 0.0, 0.0, 0.0],
        [0.0, sy, 0.0, 0.0],
        [0.0, 0.0, sz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_rotate_x(deg: float) -> list[list[float]]:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_rotate_y(deg: float) -> list[list[float]]:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_rotate_z(deg: float) -> list[list[float]]:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return [
        [c, -s, 0.0, 0.0],
        [s, c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat4_transform_point(m: list[list[float]], p: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = p
    nx = m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3]
    ny = m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3]
    nz = m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]
    nw = m[3][0] * x + m[3][1] * y + m[3][2] * z + m[3][3]
    if abs(nw) > 1e-9 and abs(nw - 1.0) > 1e-9:
        return (nx / nw, ny / nw, nz / nw)
    return (nx, ny, nz)


def build_shaban_mesh():
    vertices: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    triangles: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
    edges: list[tuple[int, int]] = []

    cx = 11.3
    cy = 2.5
    z_front = 0.75
    z_back = -0.75

    def add_v(x: float, y: float, z: float) -> int:
        vertices.append((round(x - cx, 4), round(y - cy, 4), z))
        return len(vertices) - 1

    def add_uv(u: float, v: float) -> int:
        uvs.append((u, v))
        return len(uvs) - 1

    def add_quad_prism(q2d: list[tuple[float, float]]):
        f_idx = [add_v(px, py, z_front) for px, py in q2d]
        b_idx = [add_v(px, py, z_back) for px, py in q2d]

        for i in range(4):
            edges.append((f_idx[i], f_idx[(i + 1) % 4]))
            edges.append((b_idx[i], b_idx[(i + 1) % 4]))
            edges.append((f_idx[i], b_idx[i]))

        f_uv = [add_uv(px * 0.32, py * 0.32) for px, py in q2d]
        triangles.append(((f_idx[0], f_idx[1], f_idx[2]), (f_uv[0], f_uv[1], f_uv[2])))
        triangles.append(((f_idx[0], f_idx[2], f_idx[3]), (f_uv[0], f_uv[2], f_uv[3])))

        b_uv = [add_uv(px * 0.32, py * 0.32) for px, py in q2d]
        triangles.append(((b_idx[0], b_idx[2], b_idx[1]), (b_uv[0], b_uv[2], b_uv[1])))
        triangles.append(((b_idx[0], b_idx[3], b_idx[2]), (b_uv[0], b_uv[3], b_uv[2])))

        for i in range(4):
            j = (i + 1) % 4
            side_len = math.hypot(q2d[j][0] - q2d[i][0], q2d[j][1] - q2d[i][1]) * 0.32
            depth_uv = (z_front - z_back) * 0.45
            su0 = add_uv(0.0, 0.0)
            su1 = add_uv(side_len, 0.0)
            su2 = add_uv(side_len, depth_uv)
            su3 = add_uv(0.0, depth_uv)
            triangles.append(((b_idx[i], b_idx[j], f_idx[j]), (su0, su1, su2)))
            triangles.append(((b_idx[i], f_idx[j], f_idx[i]), (su0, su2, su3)))

    def rect(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    sh_x = 0.0
    add_quad_prism(rect(sh_x + 0.0, 0.0, sh_x + 4.0, 0.9))
    add_quad_prism(rect(sh_x + 0.0, 0.9, sh_x + 0.9, 5.0))
    add_quad_prism(rect(sh_x + 1.55, 0.9, sh_x + 2.45, 5.0))
    add_quad_prism(rect(sh_x + 3.1, 0.9, sh_x + 4.0, 5.0))

    for ax in (4.85, 14.15):
        add_quad_prism([(ax + 0.0, 0.0), (ax + 0.95, 0.0), (ax + 2.0, 5.0), (ax + 1.4, 5.0)])
        add_quad_prism([(ax + 3.05, 0.0), (ax + 4.0, 0.0), (ax + 2.6, 5.0), (ax + 2.0, 5.0)])
        add_quad_prism([(ax + 1.22, 1.3), (ax + 2.78, 1.3), (ax + 2.61, 2.1), (ax + 1.39, 2.1)])

    bx = 9.7
    add_quad_prism(rect(bx + 0.0, 0.0, bx + 0.9, 5.0))
    add_quad_prism(rect(bx + 0.9, 4.1, bx + 3.6, 5.0))
    add_quad_prism(rect(bx + 0.9, 2.1, bx + 3.6, 2.95))
    add_quad_prism(rect(bx + 0.9, 0.0, bx + 3.6, 0.85))
    add_quad_prism(rect(bx + 2.7, 0.85, bx + 3.6, 2.1))

    nx = 19.0
    add_quad_prism(rect(nx + 0.0, 0.0, nx + 0.9, 5.0))
    add_quad_prism(rect(nx + 2.7, 0.0, nx + 3.6, 5.0))
    add_quad_prism(rect(nx + 0.9, 2.05, nx + 2.7, 2.95))

    return vertices, uvs, triangles, edges


def generate_texture(name: str, size: int = 64) -> list[tuple[int, int, int]]:
    tex = []
    for y in range(size):
        for x in range(size):
            u = x / size
            v = y / size
            if name == "Дерево":
                ring = math.sin((u * 9.0 + math.sin(v * 6.2831) * 0.45) * 6.2831) * 0.5 + 0.5
                grain = math.sin(u * 90.0 + v * 12.0) * 0.08
                t = max(0.0, min(1.0, ring * 0.75 + grain + 0.15))
                r = int(115 + 95 * t)
                g = int(62 + 65 * t)
                b = int(28 + 32 * t)
            elif name == "Кирпич":
                row = (y // 16) % 2
                bx = (x + row * 16) % 32
                by = y % 16
                if bx < 2 or by < 2:
                    r, g, b = 205, 200, 192
                else:
                    noise = int(12 * math.sin(x * 1.7 + y * 2.3))
                    r = max(0, min(255, 185 + noise))
                    g = max(0, min(255, 78 + noise // 2))
                    b = max(0, min(255, 58 + noise // 2))
            elif name == "Шахматка":
                cell = ((x // 8) + (y // 8)) % 2
                if cell == 0:
                    r, g, b = 240, 244, 250
                else:
                    r, g, b = 42, 98, 210
            elif name == "Мрамор":
                vein = abs(math.sin((u * 3.0 + v * 2.0 + math.sin(u * 12.5 + v * 9.4) * 0.25) * math.pi))
                t = vein ** 0.45
                r = int(110 + 135 * t)
                g = int(120 + 128 * t)
                b = int(135 + 115 * t)
            else:
                if x % 16 < 2 or y % 16 < 2:
                    r, g, b = 56, 189, 248
                elif (x // 16 + y // 16) % 2 == 0:
                    r, g, b = 30, 41, 59
                else:
                    r, g, b = 44, 58, 82
            tex.append((r, g, b))
    return tex


class Surname3DApp(tk.Tk):
    RW = 360
    RH = 240
    ZOOM = 2
    TEX_SIZE = 64

    def __init__(self):
        super().__init__()
        self.title("Штрафная ЛР: 3D фамилия «ШАБАН» с текстурой — Шабан Владимир")
        self.geometry("1260x760")
        self.minsize(1020, 640)
        self.configure(bg="#F1F5F9")

        self.vertices, self.uvs, self.triangles, self.edges = build_shaban_mesh()
        self.textures = {
            name: generate_texture(name, self.TEX_SIZE)
            for name in ("Дерево", "Кирпич", "Шахматка", "Мрамор", "Техно-сетка")
        }
        self.current_tex_name = tk.StringVar(value="Дерево")
        self.current_tex = self.textures["Дерево"]

        self.var_rx = tk.DoubleVar(value=18.0)
        self.var_ry = tk.DoubleVar(value=-24.0)
        self.var_rz = tk.DoubleVar(value=0.0)
        self.var_tx = tk.DoubleVar(value=0.0)
        self.var_ty = tk.DoubleVar(value=0.0)
        self.var_tz = tk.DoubleVar(value=0.0)
        self.var_sx = tk.DoubleVar(value=1.0)
        self.var_sy = tk.DoubleVar(value=1.0)
        self.var_sz = tk.DoubleVar(value=1.0)

        self.proj_mode = tk.StringVar(value="perspective")
        self.show_wire = tk.BooleanVar(value=False)
        self.show_axes = tk.BooleanVar(value=True)

        self._drag_last = None
        self._render_pending = False
        self.ppm_prefix = f"P6\n{self.RW} {self.RH}\n255\n".encode("ascii")
        self.bg_row = bytes([245, 247, 250] * self.RW)
        self.empty_buf = self.bg_row * self.RH
        self.empty_z = [1e12] * (self.RW * self.RH)

        self._setup_styles()
        self._build_ui()
        self.after(60, self.render_scene)

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

    def _build_ui(self):
        main_pane = ttk.Frame(self, style="Bg.TFrame")
        main_pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(main_pane, width=430, style="Panel.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)

        hdr = ttk.Frame(left, style="Panel.TFrame")
        hdr.pack(fill=tk.X, padx=12, pady=(10, 4))
        ttk.Label(hdr, text="3D-модель фамилии «ШАБАН»", style="Header.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Выполнил: Шабан Владимир", style="Sub.TLabel").pack(anchor="w")

        tf_frame = ttk.LabelFrame(left, text=" 1. Трехмерные преобразования ", style="Card.TLabelframe")
        tf_frame.pack(fill=tk.X, padx=10, pady=4)

        self._add_slider(tf_frame, "Поворот X (°):", self.var_rx, -180, 180)
        self._add_slider(tf_frame, "Поворот Y (°):", self.var_ry, -180, 180)
        self._add_slider(tf_frame, "Поворот Z (°):", self.var_rz, -180, 180)
        self._add_slider(tf_frame, "Сдвиг X (Tx):", self.var_tx, -12, 12)
        self._add_slider(tf_frame, "Сдвиг Y (Ty):", self.var_ty, -8, 8)
        self._add_slider(tf_frame, "Сдвиг Z (Tz):", self.var_tz, -12, 12)
        self._add_slider(tf_frame, "Масштаб Sx:", self.var_sx, 0.2, 2.2)
        self._add_slider(tf_frame, "Масштаб Sy:", self.var_sy, 0.2, 2.2)
        self._add_slider(tf_frame, "Масштаб Sz:", self.var_sz, 0.2, 3.0)

        btn_reset = ttk.Button(tf_frame, text="Сбросить преобразования", command=self.reset_transforms)
        btn_reset.pack(fill=tk.X, padx=8, pady=(4, 6))

        tex_frame = ttk.LabelFrame(left, text=" 2. Текстура и проекция ", style="Card.TLabelframe")
        tex_frame.pack(fill=tk.X, padx=10, pady=4)

        tex_row = ttk.Frame(tex_frame, style="Panel.TFrame")
        tex_row.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(tex_row, text="Текстура:", background="#FFFFFF").pack(side=tk.LEFT)
        cb_tex = ttk.Combobox(
            tex_row,
            textvariable=self.current_tex_name,
            values=list(self.textures.keys()),
            state="readonly",
            width=14,
        )
        cb_tex.pack(side=tk.LEFT, padx=6)
        cb_tex.bind("<<ComboboxSelected>>", self._on_texture_selected)
        ttk.Button(tex_row, text="Свой файл...", command=self.load_custom_texture).pack(side=tk.RIGHT)

        proj_row = ttk.Frame(tex_frame, style="Panel.TFrame")
        proj_row.pack(fill=tk.X, padx=8, pady=(0, 6))
        ttk.Radiobutton(proj_row, text="Перспектива", value="perspective",
                        variable=self.proj_mode, command=self.schedule_render).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Radiobutton(proj_row, text="Ортограф.", value="ortho",
                        variable=self.proj_mode, command=self.schedule_render).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Checkbutton(proj_row, text="Каркас", variable=self.show_wire,
                        command=self.schedule_render).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Checkbutton(proj_row, text="Оси", variable=self.show_axes,
                        command=self.schedule_render).pack(side=tk.LEFT)

        nb = ttk.Notebook(left)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))

        tab_mat = ttk.Frame(nb, style="Panel.TFrame")
        nb.add(tab_mat, text="Матрица 4×4")
        self.txt_matrix = tk.Text(tab_mat, font=("monospace", 9), bg="#F8FAFC",
                                  fg="#0F172A", relief=tk.FLAT, height=9)
        self.txt_matrix.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        ttk.Button(tab_mat, text="Копировать матрицу в буфер",
                   command=self.copy_matrix).pack(fill=tk.X, padx=6, pady=(0, 6))

        tab_verts = ttk.Frame(nb, style="Panel.TFrame")
        nb.add(tab_verts, text="Массив вершин")
        self.txt_verts = tk.Text(tab_verts, font=("monospace", 8), bg="#F8FAFC",
                                 fg="#0F172A", relief=tk.FLAT, wrap=tk.NONE)
        sc_vy = ttk.Scrollbar(tab_verts, orient=tk.VERTICAL, command=self.txt_verts.yview)
        self.txt_verts.configure(yscrollcommand=sc_vy.set)
        sc_vy.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_verts.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._populate_vertices_tab()

        right = ttk.Frame(main_pane, style="Panel.TFrame")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_bar = tk.Frame(right, bg="#F8FAFC", padx=10, pady=6)
        top_bar.pack(fill=tk.X)
        tk.Label(
            top_bar,
            text="Управление мышью: зажмите ЛКМ для вращения X/Y | Колёсико мыши: масштаб",
            bg="#F8FAFC", fg="#334155", font=("sans-serif", 9),
        ).pack(side=tk.LEFT)

        self.viewport_frame = tk.Frame(right, bg="#E2E8F0")
        self.viewport_frame.pack(fill=tk.BOTH, expand=True)

        cw = self.RW * self.ZOOM
        ch = self.RH * self.ZOOM
        self.canvas = tk.Canvas(self.viewport_frame, width=cw, height=ch,
                                bg="#F5F7FA", highlightthickness=1, highlightbackground="#CBD5E1")
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        self.display_img = tk.PhotoImage(width=cw, height=ch)
        self.img_item = self.canvas.create_image(0, 0, anchor="nw", image=self.display_img)

        self.status_var = tk.StringVar(value="Готов.")
        tk.Label(right, textvariable=self.status_var, anchor="w", bg="#F8FAFC",
                 fg="#334155", font=("monospace", 9), padx=8, pady=4).pack(fill=tk.X)

        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_move)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self._scale_uniform(1.08))
        self.canvas.bind("<Button-5>", lambda e: self._scale_uniform(1 / 1.08))

    def _add_slider(self, parent, label: str, var: tk.DoubleVar, mn: float, mx: float):
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill=tk.X, padx=8, pady=1)
        ttk.Label(row, text=label, background="#FFFFFF", width=15).pack(side=tk.LEFT)
        val_lbl = ttk.Label(row, text=f"{var.get():.2f}", background="#FFFFFF", width=6)
        val_lbl.pack(side=tk.RIGHT)
        sc = ttk.Scale(
            row, from_=mn, to=mx, variable=var,
            command=lambda v, l=val_lbl, vr=var: (
                l.configure(text=f"{float(v):.2f}"),
                self.schedule_render(),
            ),
        )
        sc.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        var._lbl_widget = val_lbl

    def _populate_vertices_tab(self):
        lines = [
            f"Объект: ШАБАН",
            f"Всего вершин: {len(self.vertices)}",
            f"Треугольников: {len(self.triangles)}",
            "-" * 38,
            f"{'ID':>4} | {'X':>7} | {'Y':>7} | {'Z':>7}",
            "-" * 38,
        ]
        for idx, (x, y, z) in enumerate(self.vertices):
            lines.append(f"{idx:>4} | {x:>7.2f} | {y:>7.2f} | {z:>7.2f}")
        self.txt_verts.insert("1.0", "\n".join(lines))
        self.txt_verts.configure(state=tk.DISABLED)

    def _on_texture_selected(self, _event):
        name = self.current_tex_name.get()
        if name in self.textures:
            self.current_tex = self.textures[name]
            self.schedule_render()

    def load_custom_texture(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение текстуры",
            filetypes=[("Изображения", "*.png *.ppm *.pgm *.gif"), ("Все файлы", "*.*")],
        )
        if not path:
            return
        try:
            img = tk.PhotoImage(file=path)
        except Exception as exc:
            messagebox.showerror("Ошибка загрузки текстуры", f"Формат должен быть PNG, PPM или GIF.\n({exc})")
            return

        iw, ih = img.width(), img.height()
        if iw <= 0 or ih <= 0:
            return
        tex = []
        ts = self.TEX_SIZE
        for y in range(ts):
            sy = min(ih - 1, int(y * ih / ts))
            for x in range(ts):
                sx = min(iw - 1, int(x * iw / ts))
                col = img.get(sx, sy)
                if isinstance(col, str):
                    col = tuple(int(c) for c in col.split())
                tex.append((int(col[0]), int(col[1]), int(col[2])))
        self.textures["Своя текстура"] = tex
        self.current_tex_name.set("Своя текстура")
        self.current_tex = tex
        self.schedule_render()

    def reset_transforms(self):
        defaults = [
            (self.var_rx, 0.0),
            (self.var_ry, 0.0),
            (self.var_rz, 0.0),
            (self.var_tx, 0.0),
            (self.var_ty, 0.0),
            (self.var_tz, 0.0),
            (self.var_sx, 1.0),
            (self.var_sy, 1.0),
            (self.var_sz, 1.0),
        ]
        for vr, val in defaults:
            vr.set(val)
            vr._lbl_widget.configure(text=f"{val:.2f}")
        self.schedule_render()

    def copy_matrix(self):
        txt = self.txt_matrix.get("1.0", tk.END).strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self.status_var.set("Матрица преобразования скопирована в буфер обмена.")

    def compute_model_matrix(self) -> list[list[float]]:
        s = mat4_scale(self.var_sx.get(), self.var_sy.get(), self.var_sz.get())
        rx = mat4_rotate_x(self.var_rx.get())
        ry = mat4_rotate_y(self.var_ry.get())
        rz = mat4_rotate_z(self.var_rz.get())
        t = mat4_translate(self.var_tx.get(), self.var_ty.get(), self.var_tz.get())
        m = mat4_mul(rx, s)
        m = mat4_mul(ry, m)
        m = mat4_mul(rz, m)
        m = mat4_mul(t, m)
        return m

    def _update_matrix_display(self, m: list[list[float]]):
        lines = [
            "M = T * Rz * Ry * Rx * S:",
            "",
        ]
        for row in m:
            lines.append("[ " + "  ".join(f"{v:>7.3f}" for v in row) + " ]")
        self.txt_matrix.delete("1.0", tk.END)
        self.txt_matrix.insert("1.0", "\n".join(lines))

    def _project_point(self, p: tuple[float, float, float]) -> tuple[float, float, float] | None:
        cam_dist = 24.0
        depth = cam_dist - p[2]
        if depth <= 0.5:
            return None
        if self.proj_mode.get() == "perspective":
            fov = 340.0
            sx = self.RW * 0.5 + (p[0] * fov) / depth
            sy = self.RH * 0.5 - (p[1] * fov) / depth
        else:
            ortho = 13.8
            sx = self.RW * 0.5 + p[0] * ortho
            sy = self.RH * 0.5 - p[1] * ortho
        return (sx, sy, depth)

    def schedule_render(self):
        if not self._render_pending:
            self._render_pending = True
            self.after(15, self.render_scene)

    def render_scene(self):
        self._render_pending = False
        m = self.compute_model_matrix()
        self._update_matrix_display(m)

        t_verts = [mat4_transform_point(m, v) for v in self.vertices]
        projected = [self._project_point(v) for v in t_verts]

        buf = bytearray(self.empty_buf)
        zbuf = self.empty_z.copy()
        tex = self.current_tex
        ts = self.TEX_SIZE
        mask = ts - 1
        rw, rh = self.RW, self.RH
        is_persp = self.proj_mode.get() == "perspective"

        lx, ly, lz = 0.36, 0.52, 0.77
        visible_tris = 0

        for (i0, i1, i2), (t0, t1, t2) in self.triangles:
            p0 = projected[i0]
            p1 = projected[i1]
            p2 = projected[i2]
            if p0 is None or p1 is None or p2 is None:
                continue

            v0 = t_verts[i0]
            v1 = t_verts[i1]
            v2 = t_verts[i2]

            ux, uy, uz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
            wx, wy, wz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
            nx = uy * wz - uz * wy
            ny = uz * wx - ux * wz
            nz = ux * wy - uy * wx
            nlen = math.sqrt(nx * nx + ny * ny + nz * nz)
            if nlen < 1e-9:
                continue
            nx /= nlen
            ny /= nlen
            nz /= nlen

            if is_persp:
                if nx * (-v0[0]) + ny * (-v0[1]) + nz * (24.0 - v0[2]) <= 0.0:
                    continue
            else:
                if nz <= 0.0:
                    continue

            visible_tris += 1
            ndotl = nx * lx + ny * ly + nz * lz
            shade = 0.40 + 0.60 * (ndotl if ndotl > 0.0 else 0.0)

            uv0 = self.uvs[t0]
            uv1 = self.uvs[t1]
            uv2 = self.uvs[t2]

            iz0 = 1.0 / p0[2]
            iz1 = 1.0 / p1[2]
            iz2 = 1.0 / p2[2]

            pts = [
                (p0[0], p0[1], p0[2], uv0[0] * iz0, uv0[1] * iz0, iz0),
                (p1[0], p1[1], p1[2], uv1[0] * iz1, uv1[1] * iz1, iz1),
                (p2[0], p2[1], p2[2], uv2[0] * iz2, uv2[1] * iz2, iz2),
            ]
            pts.sort(key=lambda pt: pt[1])
            a, b, c = pts

            y_start = max(0, math.ceil(a[1] - 0.5))
            y_end = min(rh - 1, math.floor(c[1] - 0.5))
            if y_start > y_end:
                continue

            dy_ac = c[1] - a[1]
            if dy_ac < 1e-6:
                continue

            dy_ab = b[1] - a[1]
            dy_bc = c[1] - b[1]

            for y in range(y_start, y_end + 1):
                yc = y + 0.5
                t_ac = (yc - a[1]) / dy_ac
                xa = a[0] + (c[0] - a[0]) * t_ac
                uza = a[3] + (c[3] - a[3]) * t_ac
                vza = a[4] + (c[4] - a[4]) * t_ac
                iza = a[5] + (c[5] - a[5]) * t_ac

                if yc < b[1]:
                    if dy_ab < 1e-6:
                        continue
                    t_s = (yc - a[1]) / dy_ab
                    xb = a[0] + (b[0] - a[0]) * t_s
                    uzb = a[3] + (b[3] - a[3]) * t_s
                    vzb = a[4] + (b[4] - a[4]) * t_s
                    izb = a[5] + (b[5] - a[5]) * t_s
                else:
                    if dy_bc < 1e-6:
                        continue
                    t_s = (yc - b[1]) / dy_bc
                    xb = b[0] + (c[0] - b[0]) * t_s
                    uzb = b[3] + (c[3] - b[3]) * t_s
                    vzb = b[4] + (c[4] - b[4]) * t_s
                    izb = b[5] + (c[5] - b[5]) * t_s

                if xa > xb:
                    xa, xb = xb, xa
                    uza, uzb = uzb, uza
                    vza, vzb = vzb, vza
                    iza, izb = izb, iza

                x_start = max(0, math.ceil(xa - 0.5))
                x_end = min(rw - 1, math.floor(xb - 0.5))
                if x_start > x_end:
                    continue

                span = xb - xa
                if span < 1e-6:
                    continue

                inv_span = 1.0 / span
                duz = (uzb - uza) * inv_span
                dvz = (vzb - vza) * inv_span
                diz = (izb - iza) * inv_span

                dx0 = (x_start + 0.5) - xa
                uz_cur = uza + duz * dx0
                vz_cur = vza + dvz * dx0
                iz_cur = iza + diz * dx0

                row_off = y * rw
                for x in range(x_start, x_end + 1):
                    depth = 1.0 / iz_cur
                    idx = row_off + x
                    if depth < zbuf[idx]:
                        zbuf[idx] = depth
                        u = uz_cur * depth
                        v = vz_cur * depth
                        tx_i = int(u * ts) & mask
                        ty_i = int(v * ts) & mask
                        tr, tg, tb = tex[ty_i * ts + tx_i]
                        p_off = idx * 3
                        buf[p_off] = int(tr * shade)
                        buf[p_off + 1] = int(tg * shade)
                        buf[p_off + 2] = int(tb * shade)
                    uz_cur += duz
                    vz_cur += dvz
                    iz_cur += diz

        raw = tk.PhotoImage(data=self.ppm_prefix + bytes(buf), format="ppm")
        self.display_img.tk.call(self.display_img.name, "copy", raw.name, "-zoom", self.ZOOM, self.ZOOM)

        self.canvas.delete("overlay")
        zm = self.ZOOM

        if self.show_axes.get():
            origin = self._project_point((0.0, 0.0, 0.0))
            if origin is not None:
                ox, oy = origin[0] * zm, origin[1] * zm
                axes_defs = [
                    ((5.0, 0.0, 0.0), "#EF4444", "X"),
                    ((0.0, 5.0, 0.0), "#16A34A", "Y"),
                    ((0.0, 0.0, 5.0), "#2563EB", "Z"),
                ]
                for pt3, col, lbl in axes_defs:
                    ep = self._project_point(pt3)
                    if ep is not None:
                        ex, ey = ep[0] * zm, ep[1] * zm
                        self.canvas.create_line(ox, oy, ex, ey, fill=col, width=2,
                                                arrow=tk.LAST, tags="overlay")
                        self.canvas.create_text(ex + 8, ey - 8, text=lbl, fill=col,
                                                font=("sans-serif", 9, "bold"), tags="overlay")

        if self.show_wire.get():
            for a, b in self.edges:
                pa = projected[a]
                pb = projected[b]
                if pa is not None and pb is not None:
                    self.canvas.create_line(
                        pa[0] * zm, pa[1] * zm, pb[0] * zm, pb[1] * zm,
                        fill="#0F172A", width=1, tags="overlay",
                    )

        self.status_var.set(
            f"Вершин: {len(self.vertices)} | Видимых треугольников: {visible_tris}/{len(self.triangles)} | "
            f"Текстура: {self.current_tex_name.get()}"
        )

    def _on_drag_start(self, event):
        self._drag_last = (event.x, event.y)

    def _on_drag_move(self, event):
        if self._drag_last is None:
            return
        dx = event.x - self._drag_last[0]
        dy = event.y - self._drag_last[1]
        self._drag_last = (event.x, event.y)

        ny = self.var_ry.get() + dx * 0.6
        nx = self.var_rx.get() + dy * 0.6
        if ny > 180.0:
            ny -= 360.0
        elif ny < -180.0:
            ny += 360.0
        nx = max(-180.0, min(180.0, nx))

        self.var_ry.set(ny)
        self.var_rx.set(nx)
        self.var_ry._lbl_widget.configure(text=f"{ny:.2f}")
        self.var_rx._lbl_widget.configure(text=f"{nx:.2f}")
        self.schedule_render()

    def _scale_uniform(self, factor: float):
        for vr in (self.var_sx, self.var_sy, self.var_sz):
            nv = max(0.2, min(3.0, vr.get() * factor))
            vr.set(nv)
            vr._lbl_widget.configure(text=f"{nv:.2f}")
        self.schedule_render()

    def _on_mouse_wheel(self, event):
        self._scale_uniform(1.08 if event.delta > 0 else 1 / 1.08)


if __name__ == "__main__":
    app = Surname3DApp()
    app.mainloop()