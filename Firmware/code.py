# code.py - XIAO RP2040, KMK, SSD1306 128x32 vertical orientation

import board
import busio
import time
import usb_cdc
import adafruit_ssd1306
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.modules.layers import Layers
from kmk.scanners import KeysScanner

# ── KMK Setup ────────────────────────────────────────────────────
keyboard = KMKKeyboard()
layers_mod = Layers()
keyboard.modules.append(layers_mod)

# Adjust pins to match your hackpad wiring
keyboard.matrix = KeysScanner([
    board.D0, board.D1, board.D2,
    board.D3, board.D4, board.D5,
    board.D6, board.D7, board.D8,
])

LAYER_NAMES = ["BASE", "NAV", "SYS"]

keyboard.keymap = [
    # Layer 0 — Base shortcuts
    [
        KC.LCTL(KC.C), KC.LCTL(KC.V), KC.LCTL(KC.X),
        KC.LCTL(KC.Z), KC.LCTL(KC.Y), KC.LCTL(KC.S),
        KC.TG(1),      KC.TG(2),      KC.TRNS,
    ],
    # Layer 1 — Nav
    [
        KC.HOME, KC.UP,   KC.END,
        KC.LEFT, KC.DOWN, KC.RIGHT,
        KC.TG(1), KC.TG(2), KC.TRNS,
    ],
    # Layer 2 — System
    [
        KC.LGUI(KC.L), KC.LGUI(KC.R),          KC.LSFT(KC.LGUI(KC.S)),
        KC.LALT(KC.F4), KC.LGUI(KC.E),         KC.LGUI(KC.D),
        KC.TG(1),       KC.TG(2),               KC.TRNS,
    ],
]

# ── Display Setup (rotated 90°) ───────────────────────────────────
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.rotation = 1   # rotate 90° so 32px becomes the width

# After rotation: display is 32px wide x 128px tall (logical)
W, H = 32, 128

# ── Stats state ───────────────────────────────────────────────────
cpu_pct    = 0.0
gpu_pct    = 0.0
cpu_temp   = 0.0
gpu_temp   = 0.0
serial_buf = ""

def read_serial():
    global cpu_pct, gpu_pct, cpu_temp, gpu_temp, serial_buf
    if usb_cdc.data.in_waiting > 0:
        chunk = usb_cdc.data.read(usb_cdc.data.in_waiting).decode("utf-8", "ignore")
        serial_buf += chunk
        while "\n" in serial_buf:
            line, serial_buf = serial_buf.split("\n", 1)
            parts = line.strip().split(",")
            if len(parts) == 4:
                try:
                    cpu_pct  = float(parts[0])
                    gpu_pct  = float(parts[1])
                    cpu_temp = float(parts[2])
                    gpu_temp = float(parts[3])
                except ValueError:
                    pass

# ── Drawing helpers ───────────────────────────────────────────────
def hline(y, color=1):
    oled.hline(0, y, W, color)

def draw_bar(y, pct, h=4):
    """Full-width horizontal bar at y, filled by pct (0-100)."""
    oled.rect(0, y, W, h, 1)
    fill = int((pct / 100) * (W - 2))
    if fill > 0:
        oled.fill_rect(1, y + 1, fill, h - 2, 1)

def centered_text(text, y, color=1):
    x = max(0, (W - len(text) * 6) // 2)
    oled.text(text, x, y, color)

# ── Render ────────────────────────────────────────────────────────
def render(active_layer):
    oled.fill(0)

    # == TOP SECTION: Layer indicator (0-51px) ====================

    # Title
    centered_text("LAYER", 2)

    # 3 layer slots stacked vertically
    slot_h = 13
    slot_y_start = 12
    for i in range(3):
        y = slot_y_start + i * slot_h
        if i == active_layer:
            oled.fill_rect(0, y, W, slot_h - 1, 1)      # filled bg
            centered_text(LAYER_NAMES[i], y + 3, 0)      # dark text
        else:
            oled.rect(0, y, W, slot_h - 1, 1)           # outline
            centered_text(LAYER_NAMES[i], y + 3, 1)      # light text

    # Divider
    hline(52)

    # == BOTTOM SECTION: PC stats (54-128px) ======================

    # CPU
    oled.text("CPU", 0, 55, 1)
    oled.text(f"{int(cpu_pct):3d}%", 0, 64, 1)
    draw_bar(73, cpu_pct, h=4)

    # CPU temp
    oled.text(f"{int(cpu_temp)}C", 0, 79, 1)

    # Divider between CPU/GPU
    hline(89)

    # GPU
    oled.text("GPU", 0, 91, 1)
    oled.text(f"{int(gpu_pct):3d}%", 0, 100, 1)
    draw_bar(109, gpu_pct, h=4)

    # GPU temp
    oled.text(f"{int(gpu_temp)}C", 0, 115, 1)

    oled.show()

# ── Main loop ─────────────────────────────────────────────────────
last_render = 0

while True:
    keyboard.go(hid_type=HIDTypes.USB)   # KMK tick

    read_serial()

    now = time.monotonic()
    if now - last_render >= 0.15:
        active = layers_mod.active_layers[0] if layers_mod.active_layers else 0
        render(active)
        last_render = now
