import tkinter as tk
from tkinter import ttk
import math
import random
import time

# ==========================================
# 1. MODEL: Gul konfiguratsiyasi (Class)
# ==========================================
class FlowerConfig:
    """Gul turi, rangi va parametrlarini boshqaruvchi obyekt"""
    DEFAULT_COLOR = "#FF6B8B"
    DEFAULT_CENTER = "#FFD166"
    DEFAULT_PETALS = 6

    def __init__(self, name: str):
        self.name = name.strip().lower()
        self.color, self.petal_count, self.center_color = self._resolve_config()

    def _resolve_config(self):
        """Kiritilgan nomga mos rang va gul parametrlarini aniqlash"""
        configs = {
            'atirgul': ("#E63946", 5, "#F4A261"),
            'rose': ("#E63946", 5, "#F4A261"),
            'lola': ("#FF9F1C", 6, "#2B2D42"),
            'tulip': ("#FF9F1C", 6, "#2B2D42"),
            'kungaboqar': ("#FFD166", 16, "#6B4226"),
            'sunflower': ("#FFD166", 16, "#6B4226"),
            'binafsha': ("#9B5DE5", 5, "#FEE440"),
            'violet': ("#9B5DE5", 5, "#FEE440"),
            'romashka': ("#FFFFFF", 8, "#FFD166"),
            'daisy': ("#FFFFFF", 8, "#FFD166"),
        }
        # Qidiruvda qisqa qatnashlarni ham qabul qilish
        for key, val in configs.items():
            if key in self.name or self.name in key:
                return val
        return self.DEFAULT_COLOR, self.DEFAULT_PETALS, self.DEFAULT_CENTER


# ==========================================
# 2. BOSHQARUV: O'sish bosqichlari (Class)
# ==========================================
class GrowthModel:
    """O'sish jarayonini 0.0 dan 1.0 gacha progress orqali boshqaradi"""
    STAGES = [
        "Urug' va tuproqda",
        "Nish chiqishi",
        "Poya o'sishi",
        "Barglar paydo bo'lishi",
        "G'uncha hosil bo'lishi",
        "Gul to'liq ochilishi"
    ]

    def __init__(self):
        self.progress = 0.0
        self.current_stage_idx = 0

    def update(self, step: float):
        self.progress = min(1.0, self.progress + step)
        # Progressga qarab bosqichni aniqlash
        thresholds = [0.0, 0.15, 0.35, 0.55, 0.75, 0.90]
        for i, t in enumerate(thresholds):
            if self.progress >= t:
                self.current_stage_idx = min(i, len(self.STAGES) - 1)
        return self.progress >= 1.0

    def get_stage_name(self) -> str:
        return self.STAGES[self.current_stage_idx]

    def get_visual_params(self) -> dict:
        """Progressga qarab ko'rsatkichlarni hisoblash"""
        p = self.progress
        return {
            "stem_height": max(0, (p - 0.1) / 0.7) * 280,  # 0.1 dan boshlab o'sadi
            "leaf_size": max(0, min(1, (p - 0.35) / 0.2)) * 25,
            "bud_size": max(0, min(1, (p - 0.55) / 0.15)) * 20,
            "bloom_scale": max(0, min(1, (p - 0.75) / 0.25)),
            "soil_wetness": max(0, 1 - p * 2)  # 0.5 gacha nam, keyin quriydi
        }


# ==========================================
# 3. KO'RINISH: Canvas chizish (Class)
# ==========================================
class FlowerCanvas:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.canvas.config(bg="#F8F9FA", highlightthickness=0)
        self.items = {}  # Chizilgan elementlarni ID saqlash

    def clear(self):
        self.canvas.delete("all")
        self.items.clear()

    def draw(self, config: FlowerConfig, params: dict, center_x: int = 400, base_y: int = 520):
        self.clear()
        self._draw_background()
        self._draw_soil(center_x, base_y, params)
        self._draw_stem(center_x, base_y, params)
        self._draw_leaves(center_x, base_y, config, params)
        self._draw_bud(center_x, base_y, config, params)
        self._draw_petals(center_x, base_y, config, params)

    def _draw_background(self):
        # Oddiy fon chizig'i (deraza hajmiga mos)
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.canvas.create_rectangle(0, 0, w, h, fill="#E8F0F2", outline="")

    def _draw_soil(self, cx, by, params):
        wet = params["soil_wetness"]
        color = f"#{int(90+wet*20):02x}{int(65+wet*15):02x}{int(40+wet*10):02x}"
        self.canvas.create_rectangle(0, by + 10, self.canvas.winfo_width(), by + 80, fill=color, outline="")
        # Urug' (dastlabki bosqichda)
        if params["stem_height"] < 5:
            self.canvas.create_oval(cx - 6, by - 2, cx + 6, by + 10, fill="#8B5A2B", outline="#5C3A1A")

    def _draw_stem(self, cx, by, params):
        h = params["stem_height"]
        if h <= 0: return
        top_y = by - h
        thickness = 4 + h / 50
        self.canvas.create_line(cx, by, cx, top_y, fill="#2D6A4F", width=thickness, capstyle=tk.ROUND)

    def _draw_leaves(self, cx, by, config, params):
        size = params["leaf_size"]
        if size <= 2: return
        stem_top = by - params["stem_height"]
        # Poyada 2 ta barg joylashadi
        for i, y_offset in enumerate([0.3, 0.6]):
            ly = by - params["stem_height"] * y_offset
            lx = cx + (20 if i == 0 else -20)
            angle = 0.3 if i == 0 else -0.3
            self._draw_leaf(lx, ly, size, angle, flip=(i % 2 == 1))

    def _draw_leaf(self, x, y, size, angle, flip=False):
        points = []
        for t in range(-30, 30, 2):
            rad = math.radians(t + (angle * 100))
            r = size * (0.8 + 0.2 * math.cos(rad))
            px = x + r * math.cos(rad + angle)
            py = y + r * math.sin(rad + angle) * 0.6
            points.extend([px, py])
        self.canvas.create_polygon(points, fill="#52B788", outline="#2D6A4F", smooth=True)

    def _draw_bud(self, cx, by, config, params):
        b_size = params["bud_size"]
        if b_size <= 2: return
        top_y = by - params["stem_height"]
        self.canvas.create_oval(cx - b_size, top_y - b_size, cx + b_size, top_y + b_size,
                                fill=config.color, outline="#D90429", width=2)

    def _draw_petals(self, cx, by, config, params):
        bloom = params["bloom_scale"]
        if bloom <= 0: return
        top_y = by - params["stem_height"]
        r_base = 15 + bloom * 40
        r_tip = r_base * (0.6 + bloom * 0.4)

        for i in range(config.petal_count):
            angle = (360 / config.petal_count) * i + (bloom * 15)
            rad = math.radians(angle)
            px = cx + r_base * math.cos(rad)
            py = top_y + r_base * math.sin(rad)

            # Gulbarg chizish (oddiy ko'pburchak)
            pts = [
                (cx, top_y),
                (cx + (px - cx) * 0.5, top_y + (py - top_y) * 0.3 - 20 * bloom),
                (px, py),
                (cx + (px - cx) * 0.5, top_y + (py - top_y) * 0.3 + 20 * bloom)
            ]
            flat_pts = [coord for pt in pts for coord in pt]
            self.canvas.create_polygon(flat_pts, fill=config.color, outline="#A4133C", width=1, smooth=True)

        # Markaz
        self.canvas.create_oval(cx - 8 * bloom, top_y - 8 * bloom, cx + 8 * bloom, top_y + 8 * bloom,
                                fill=config.center_color, outline="#D4A373")


# ==========================================
# 4. INTERFEYS: Asosiy dastur (Class)
# ==========================================
class FlowerSimulatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🌱 Gul O'sishi Simulyatori")
        self.root.geometry("950x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#F0F2F5")

        self.config = None
        self.model = GrowthModel()
        self.renderer = None
        self.anim_id = None
        self.is_running = False

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#F0F2F5")
        style.configure("TLabel", background="#F0F2F5", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1D3557")
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=(15, 8))
        style.configure("Accent.TButton", background="#457B9D", foreground="white")
        style.map("Accent.TButton", background=[("active", "#1D3557")])
        style.configure("TProgressbar", thickness=12, background="#2A9D8F")
        style.configure("Status.TLabel", font=("Segoe UI", 9, "italic"), foreground="#666")

    def _build_ui(self):
        # Asosiy container
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sarlavha
        ttk.Label(main_frame, text="🌸 Gul O'sishi Simulyatori", style="Title.TLabel").pack(pady=(0, 15))

        # Grid layout: Chap (Canvas) | O'ng (Boshqaruv)
        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True)

        # Chap: Canvas
        canvas_frame = ttk.Frame(content, relief="solid", borderwidth=2)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        self.canvas = tk.Canvas(canvas_frame, width=600, height=520, bg="#E8F0F2")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.renderer = FlowerCanvas(self.canvas)

        # O'ng: Panel
        panel = ttk.Frame(content, width=280)
        panel.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Kiritish
        ttk.Label(panel, text="Gul nomi kiriting:").pack(anchor="w", pady=(10, 5))
        self.entry = ttk.Entry(panel, font=("Segoe UI", 11), width=25)
        self.entry.pack(fill=tk.X, pady=(0, 15))
        self.entry.insert(0, "atirgul")

        # Tugmalar
        btn_frame = ttk.Frame(panel)
        btn_frame.pack(fill=tk.X, pady=10)
        self.start_btn = ttk.Button(btn_frame, text="▶ Boshlash", style="Accent.TButton", command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.reset_btn = ttk.Button(btn_frame, text="↺ Qayta", command=self.reset_simulation)
        self.reset_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Holat paneli
        self.progress = ttk.Progressbar(panel, orient="horizontal", length=260, mode="determinate")
        self.progress.pack(fill=tk.X, pady=15)

        self.stage_label = ttk.Label(panel, text="Bosqich: Tayyor", style="TLabel")
        self.stage_label.pack(anchor="w", pady=(5, 10))

        self.info_text = tk.Text(panel, height=8, font=("Consolas", 10), bg="#FFFFFF", relief="flat", wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, pady=10)
        self.info_text.insert(tk.END, "💡 Maslahat: 'atirgul', 'lola', 'kungaboqar' yoki o'z xohishingizdagi gul nomini kiriting.")
        self.info_text.configure(state="disabled")

        # Pastki status
        self.status_bar = ttk.Label(main_frame, text="Tayyor. Gul nomini kiriting va 'Boshlash' tugmasini bosing.", style="Status.TLabel")
        self.status_bar.pack(fill=tk.X, pady=(15, 0))

        self.entry.focus()
        self.entry.bind("<Return>", lambda e: self.start_simulation())

    def start_simulation(self):
        if self.is_running:
            return
        name = self.entry.get().strip()
        if not name:
            self.status_bar.config(text="⚠️ Iltimos, gul nomini kiriting!")
            return

        self.config = FlowerConfig(name)
        self.model = GrowthModel()
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.status_bar.config(text=f"🌱 '{self.config.name.title()}' o'stirish boshlandi...")
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, f"📝 Gul: {self.config.name.title()}\n🎨 Asosiy rang: {self.config.color}\n🌸 Barglar soni: {self.config.petal_count}\n⏳ Jarayon kuting...")
        self.info_text.configure(state="disabled")

        self._animate_step()

    def _animate_step(self):
        if not self.is_running:
            return

        finished = self.model.update(0.012)  # ~0.012 * 80 frame = ~1.0
        self.progress["value"] = self.model.progress * 100
        self.stage_label.config(text=f"Bosqich: {self.model.get_stage_name()}")

        params = self.model.get_visual_params()
        self.renderer.draw(self.config, params)

        if finished:
            self.is_running = False
            self.start_btn.config(state="normal")
            self.status_bar.config(text="✅ Gul muvaffaqiyatli ochildi! Tabriklaymiz 🎉")
            self.info_text.configure(state="normal")
            self.info_text.insert(tk.END, "\n✅ O'sish tugallandi!")
            self.info_text.configure(state="disabled")
        else:
            self.anim_id = self.root.after(40, self._animate_step)

    def reset_simulation(self):
        self.is_running = False
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
        self.start_btn.config(state="normal")
        self.progress["value"] = 0
        self.stage_label.config(text="Bosqich: Tayyor")
        self.status_bar.config(text="Simulyator qayta ishga tushirildi.")
        self.renderer.clear()
        # Fonni chizish
        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill="#E8F0F2", outline="")
        self.canvas.create_rectangle(0, 520 + 10, self.canvas.winfo_width(), 520 + 80, fill="#7A5C43", outline="")


# ==========================================
# DASTURNI ISHGA TUSHIRISH
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = FlowerSimulatorApp(root)
    root.mainloop() 