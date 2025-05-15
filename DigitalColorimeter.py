import tkinter as tk
from tkinter import ttk
import pyautogui
from PIL import Image
import threading
import time
import numpy as np

# === HARDCODE YOUR MATRIX M HERE (Replace with real matrix) ===
M = np.array([
    [1.00582488e+00,  2.52775120e-04, -2.59556992e-03],
    [-5.08380082e-03,  1.00131323e+00, -2.76881088e-03],
    [-4.83919068e-03, -4.75540909e-03,  1.00098231e+00]
])  # Replace with your calibrated matrix (3x3)

# === GLOBALS ===
overlay = None
canvas = None

# === Color Sampling ===
def get_avg_color(x, y, size):
    offset = size // 2
    overlay.withdraw()
    time.sleep(0.02)
    img = pyautogui.screenshot(region=(x - offset, y - offset, size, size))
    overlay.deiconify()
    pixels = list(img.getdata())
    n = len(pixels)
    r = sum(p[0] for p in pixels) // n
    g = sum(p[1] for p in pixels) // n
    b = sum(p[2] for p in pixels) // n
    return (r, g, b)

# === Update GUI ===
def update_color():
    x, y = pyautogui.position()
    size = sample_size.get()
    r, g, b = get_avg_color(x, y, size)
    native_rgb = np.array([r, g, b])
    calibrated_rgb = np.clip(native_rgb @ M, 0, 255).astype(int)

    rgb_text.set(f"Native RGB: {r}, {g}, {b}")
    hex_text.set(f"Hex: #{r:02X}{g:02X}{b:02X}")
    srgb_text.set(f"sRGB: {calibrated_rgb[0]}, {calibrated_rgb[1]}, {calibrated_rgb[2]}")
    size_display.set(f"Sample Area: {size} × {size}")
    position_text.set(f"Position: ({x}, {y})")

    # Update color boxes
    color_preview_native.config(bg=f'#{r:02x}{g:02x}{b:02x}')
    color_preview_calibrated.config(bg=f'#{calibrated_rgb[0]:02x}{calibrated_rgb[1]:02x}{calibrated_rgb[2]:02x}')

    root.after(100, update_color)

# === Overlay Tracking ===
def overlay_tracker():
    while True:
        try:
            x, y = pyautogui.position()
            size = sample_size.get()
            offset = size // 2
            overlay.geometry(f"{size}x{size}+{x - offset}+{y - offset}")
            canvas.config(width=size, height=size)
            time.sleep(0.05)
        except:
            break

# === MAIN WINDOW ===
root = tk.Tk()
root.title("Digital Colorimeter (Calibrated)")
root.geometry("460x540")
root.configure(bg="#2c2c2c")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", background="#2c2c2c", foreground="white", font=("Segoe UI", 12))
style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
style.configure("TScale", troughcolor="#555", background="#2c2c2c")

# Variables
rgb_text = tk.StringVar()
hex_text = tk.StringVar()
srgb_text = tk.StringVar()
position_text = tk.StringVar()
size_display = tk.StringVar()
sample_size = tk.IntVar(value=25)

# Layout
ttk.Label(root, text="Digital Colorimeter", style="Title.TLabel").pack(pady=(15, 8))
ttk.Label(root, textvariable=position_text).pack(pady=4)
ttk.Label(root, textvariable=size_display).pack(pady=4)

ttk.Label(root, textvariable=rgb_text).pack(pady=4)
ttk.Label(root, textvariable=hex_text).pack(pady=4)
color_preview_native = tk.Label(root, width=30, height=2, bg="black", bd=2, relief="solid")
color_preview_native.pack(pady=5)

ttk.Label(root, textvariable=srgb_text).pack(pady=(10, 4))
color_preview_calibrated = tk.Label(root, width=30, height=2, bg="black", bd=2, relief="solid")
color_preview_calibrated.pack(pady=5)

ttk.Label(root, text="Adjust Sampling Area:", style="TLabel").pack(pady=(15, 5))
slider = ttk.Scale(root, from_=5, to=101, orient='horizontal', variable=sample_size, length=280)
slider.pack(pady=(0, 20))
slider.config(command=lambda _: size_display.set(f"Sample Area: {int(sample_size.get())} × {int(sample_size.get())}"))

# === OVERLAY RULER ===
overlay = tk.Toplevel(root)
overlay.overrideredirect(True)
overlay.attributes("-topmost", True)
overlay.attributes("-transparentcolor", "pink")
overlay.config(bg="pink")

canvas = tk.Canvas(overlay, bg='pink', highlightthickness=2, highlightbackground='red')
canvas.pack(fill="both", expand=True)

# Start threads
threading.Thread(target=overlay_tracker, daemon=True).start()
update_color()
root.mainloop()
