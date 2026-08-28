import tkinter as tk
import json
import os
import pygame

RECORD_FILE = "record.json"
SOUND_FILE = "creamy-keyboard-once.mp3"

WIDTH, HEIGHT = 480, 660

BG_TOP = "#eafcfa"     
BG_BOTTOM = "#c7f0e8"  
TEXTURE_TINT = "#ffffff"

ACCENT = "#12b8a6"    
TEXT_MAIN = "#123a3a"
TEXT_MUTED = "#5f8f8a"

PLATE_FILL = "#0e3a37"
PLATE_BORDER = "#12b8a6"
SOCKET_FILL = "#092623"

KEY_TOP_OUTER_IDLE = "#ffffff"
KEY_TOP_OUTER_PRESSED = "#dbe6e4"
KEY_TOP_INNER_IDLE = "#ffffff"
KEY_TOP_INNER_PRESSED = "#eef4f3"
KEY_SKIRT_IDLE = "#b7c9c6"
KEY_SKIRT_PRESSED = "#6d827f"
KEY_LABEL = "#0e3a37"
SHADOW_COLOR = "#041412"

CLICKS_SHADOW = "#a9ded4"

CAP_W = 150
CAP_H = 138
MAX_TRAVEL = 13
PRESS_STEPS = 3
RELEASE_STEPS = 4
ANIM_DELAY = 11



def lerp_color(c1, c2, t):
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def rounded_rect_points(x1, y1, x2, y2, radius):
    radius = max(0, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
    return [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]


def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=18, **kwargs):
    return canvas.create_polygon(*rounded_rect_points(x1, y1, x2, y2, radius),
                                  smooth=True, **kwargs)


def move_rounded_rect(canvas, item_id, x1, y1, x2, y2, radius=18):
    canvas.coords(item_id, *rounded_rect_points(x1, y1, x2, y2, radius))


def draw_vertical_gradient(canvas, x1, y1, x2, y2, color_top, color_bottom):
    height = y2 - y1
    step = 2
    for offset in range(0, height, step):
        t = offset / height
        color = lerp_color(color_top, color_bottom, t)
        canvas.create_rectangle(x1, y1 + offset, x2, y1 + offset + step,
                                 outline="", fill=color, tags="bg")


def draw_diagonal_texture(canvas, width, height, base_color, tint, spacing=42):
    line_color = lerp_color(base_color, tint, 0.35)
    for x in range(-height, width, spacing):
        canvas.create_line(x, 0, x + height, height, fill=line_color,
                            width=1, tags="bg")


# App
class ClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mechanical Clicker")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)

        self.clicks = 0
        self.record = self.load_record()
        self.offset = 0
        self._anim_job = None

        pygame.mixer.init()
        try:
            self.click_sound = pygame.mixer.Sound(SOUND_FILE)
        except (FileNotFoundError, pygame.error):
            self.click_sound = None
            print(f"Advertencia: No se encontró el archivo '{SOUND_FILE}'. El juego funcionará sin sonido.")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                 highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_background()
        self.draw_header()
        self.draw_key_plate()
        self.create_key_layers()
        self.update_key(0)

        self.canvas.tag_bind("key_hit", "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind("key_hit", "<ButtonRelease-1>", self.on_release)
        self.canvas.tag_bind("key_hit", "<Enter>",
                              lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("key_hit", "<Leave>",
                              lambda e: self.canvas.config(cursor="arrow"))

    # ---------------- Background & static chrome ----------------

    def draw_background(self):
        draw_vertical_gradient(self.canvas, 0, 0, WIDTH, HEIGHT, BG_TOP, BG_BOTTOM)
        draw_diagonal_texture(self.canvas, WIDTH, HEIGHT,
                               lerp_color(BG_TOP, BG_BOTTOM, 0.5), TEXTURE_TINT)

    def draw_header(self):
        # --- Clicks: hero centrado arriba ---
        self.canvas.create_text(WIDTH / 2, 78, text="CLICKS ACTUALES",
                                 font=("Helvetica", 10, "bold"), fill=TEXT_MUTED)
        self.canvas.create_text(WIDTH / 2 + 2, 128 + 2, text="0",
                                 font=("Helvetica", 46, "bold"), fill=CLICKS_SHADOW,
                                 tags="clicks_shadow")
        self.txt_clicks = self.canvas.create_text(WIDTH / 2, 128, text="0",
                                                    font=("Helvetica", 46, "bold"),
                                                    fill=TEXT_MAIN)

        # --- Récord: badge arriba a la derecha (sincronizado con el valor cargado) ---
        pill_w, pill_h = 118, 58
        px2, py1 = WIDTH - 20, 20
        px1, py2 = px2 - pill_w, py1 + pill_h
        draw_rounded_rect(self.canvas, px1, py1, px2, py2, radius=16,
                           fill="#ffffff", outline=ACCENT, width=1)
        self.canvas.create_text((px1 + px2) / 2, py1 + 18, text="★ RÉCORD",
                                 font=("Helvetica", 9, "bold"), fill=ACCENT)
        self.txt_record = self.canvas.create_text((px1 + px2) / 2, py1 + 40,
                                                    text=str(self.record),
                                                    font=("Helvetica", 18, "bold"),
                                                    fill=TEXT_MAIN)

    def draw_key_plate(self):
        self.key_cx = WIDTH / 2
        self.key_cy = HEIGHT * 0.56

        plate_pad_x, plate_pad_y = 46, 40
        draw_rounded_rect(self.canvas,
                           self.key_cx - CAP_W / 2 - plate_pad_x,
                           self.key_cy - CAP_H / 2 - plate_pad_y,
                           self.key_cx + CAP_W / 2 + plate_pad_x,
                           self.key_cy + CAP_H / 2 + plate_pad_y + MAX_TRAVEL,
                           radius=30, fill=PLATE_FILL, outline=PLATE_BORDER, width=2)

        draw_rounded_rect(self.canvas,
                           self.key_cx - CAP_W / 2 - 14,
                           self.key_cy - CAP_H / 2 - 10,
                           self.key_cx + CAP_W / 2 + 14,
                           self.key_cy + CAP_H / 2 + MAX_TRAVEL + 16,
                           radius=24, fill=SOCKET_FILL, outline="")

    # ---------------- Key layers (dynamic) ----------------

    def create_key_layers(self):
        cx, cy = self.key_cx, self.key_cy

        self.shadow = self.canvas.create_oval(0, 0, 0, 0, fill=SHADOW_COLOR,
                                                outline="")
        self.skirt = draw_rounded_rect(self.canvas, 0, 0, 1, 1, radius=18,
                                        fill=KEY_SKIRT_IDLE, outline="")
        self.cap_outer = draw_rounded_rect(self.canvas, 0, 0, 1, 1, radius=18,
                                            fill=KEY_TOP_OUTER_IDLE, outline="")
        self.cap_inner = draw_rounded_rect(self.canvas, 0, 0, 1, 1, radius=13,
                                            fill=KEY_TOP_INNER_IDLE, outline="")
        self.dish_highlight = self.canvas.create_line(0, 0, 1, 1,
                                                        fill="#ffffff", width=2,
                                                        capstyle=tk.ROUND)
        self.dish_shadow = self.canvas.create_line(0, 0, 1, 1,
                                                     fill="#d3ddda", width=3,
                                                     capstyle=tk.ROUND)
        self.key_label = self.canvas.create_text(cx, cy, text="CLICK",
                                                   font=("Helvetica", 15, "bold"),
                                                   fill=KEY_LABEL)

        for item in (self.cap_outer, self.cap_inner, self.dish_highlight,
                     self.key_label, self.skirt):
            self.canvas.addtag_withtag("key_hit", item)

    def update_key(self, offset):
        cx, cy = self.key_cx, self.key_cy
        travel_ratio = max(0.0, min(1.0, offset / MAX_TRAVEL))

        shadow_w = CAP_W * 0.62 - travel_ratio * 20
        shadow_h = 14 - travel_ratio * 6
        shadow_y = cy + CAP_H / 2 + MAX_TRAVEL + 6 - (offset * 0.3)
        self.canvas.coords(self.shadow,
                            cx - shadow_w, shadow_y - shadow_h,
                            cx + shadow_w, shadow_y + shadow_h)

        skirt_color = lerp_color(KEY_SKIRT_IDLE, KEY_SKIRT_PRESSED, travel_ratio)
        skirt_h = max(3, MAX_TRAVEL - offset) + 8
        move_rounded_rect(self.canvas, self.skirt,
                           cx - CAP_W / 2, cy - CAP_H / 2 + offset + 5,
                           cx + CAP_W / 2, cy + CAP_H / 2 + offset + skirt_h,
                           radius=18)
        self.canvas.itemconfig(self.skirt, fill=skirt_color)

        outer_color = lerp_color(KEY_TOP_OUTER_IDLE, KEY_TOP_OUTER_PRESSED, travel_ratio)
        top_y1 = cy - CAP_H / 2 + offset
        top_y2 = cy + CAP_H / 2 + offset
        move_rounded_rect(self.canvas, self.cap_outer,
                           cx - CAP_W / 2, top_y1, cx + CAP_W / 2, top_y2, radius=18)
        self.canvas.itemconfig(self.cap_outer, fill=outer_color)

        inner_color = lerp_color(KEY_TOP_INNER_IDLE, KEY_TOP_INNER_PRESSED, travel_ratio)
        m = 12
        move_rounded_rect(self.canvas, self.cap_inner,
                           cx - CAP_W / 2 + m, top_y1 + m,
                           cx + CAP_W / 2 - m, top_y2 - m, radius=13)
        self.canvas.itemconfig(self.cap_inner, fill=inner_color)

        self.canvas.coords(self.dish_highlight,
                            cx - CAP_W / 2 + 26, top_y1 + m + 6,
                            cx + CAP_W / 2 - 26, top_y1 + m + 6)
        self.canvas.coords(self.dish_shadow,
                            cx - CAP_W / 2 + m + 10, top_y2 - m - 6,
                            cx + CAP_W / 2 - m - 10, top_y2 - m - 6)

        self.canvas.coords(self.key_label, cx, (top_y1 + top_y2) / 2 + 2)
        label_color = lerp_color(KEY_LABEL, "#000000", travel_ratio * 0.3)
        self.canvas.itemconfig(self.key_label, fill=label_color)

        self.offset = offset

    # ---------------- Animation ----------------

    def _animate_waypoints(self, waypoints, steps_per_segment):
        if self._anim_job:
            self.root.after_cancel(self._anim_job)
            self._anim_job = None

        sequence = []
        current = self.offset
        for target in waypoints:
            for step in range(1, steps_per_segment + 1):
                sequence.append(current + (target - current) * (step / steps_per_segment))
            current = target

        def tick(i):
            if i >= len(sequence):
                self.update_key(sequence[-1] if sequence else self.offset)
                return
            self.update_key(sequence[i])
            self._anim_job = self.root.after(ANIM_DELAY, lambda: tick(i + 1))

        tick(0)

    # ---------------- Events ----------------

    def on_press(self, event):
        self._animate_waypoints([MAX_TRAVEL], PRESS_STEPS)
        self.register_click()

    def on_release(self, event):
        self._animate_waypoints([-2, 0], RELEASE_STEPS)

    def register_click(self):
        if self.click_sound:
            self.click_sound.play()

        self.clicks += 1
        self.canvas.itemconfig(self.txt_clicks, text=str(self.clicks))
        self.canvas.itemconfig("clicks_shadow", text=str(self.clicks))

        if self.clicks > self.record:
            self.record = self.clicks
            self.canvas.itemconfig(self.txt_record, text=str(self.record))
            self.save_record()

    # ---------------- Persistencia ----------------

    def load_record(self):
        if os.path.exists(RECORD_FILE):
            try:
                with open(RECORD_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("record", 0)
            except json.JSONDecodeError:
                return 0
        return 0

    def save_record(self):
        with open(RECORD_FILE, "w") as f:
            json.dump({"record": self.record}, f)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClickerApp(root)
    root.mainloop()