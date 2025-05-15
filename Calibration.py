# -*- coding: utf-8 -*-
"""
Created on Fri May  2 16:44:00 2025

@author: Morteza
"""

import numpy as np
import cv2
import scipy.io as sio
import matplotlib.pyplot as plt

# === CONFIGURATION ===
image_path = 'C:/Users/Morteza/OneDrive/Desktop/YouTube/DigitalColormeter/MCC.png'         # your PNG image path
mat_file = 'C:/Users/Morteza/OneDrive/Desktop/YouTube/DigitalColormeter/MCC_sRGB.m'       # your .mat file
target_var = 'sRGB'                # variable name inside the .mat file

# === 1. Load image ===
img = cv2.imread(image_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
h, w, _ = img.shape

# === 2. Divide into 6x4 grid (Macbeth layout: 6 cols × 4 rows) ===
patch_rows = 4
patch_cols = 6
patch_RGBs = []

for row in range(patch_rows):
    for col in range(patch_cols):
        x_start = int(col * w / patch_cols)
        x_end = int((col + 1) * w / patch_cols)
        y_start = int(row * h / patch_rows)
        y_end = int((row + 1) * h / patch_rows)

        patch = img[y_start:y_end, x_start:x_end]
        mean_RGB = np.mean(patch.reshape(-1, 3), axis=0)
        patch_RGBs.append(mean_RGB)

measured_RGB = np.array(patch_RGBs)  # shape: (24, 3)

# === 3. Load sRGB reference from .mat file ===
mat_data = sio.loadmat(mat_file)
target_RGB = mat_data[target_var]

# Ensure shape is 24x3
if target_RGB.shape[0] == 3 and target_RGB.shape[1] == 24:
    target_RGB = target_RGB.T
elif target_RGB.shape[0] == 24 and target_RGB.shape[1] == 3:
    pass
else:
    raise ValueError("target_RGB must be 3x24 or 24x3")

# === 4. Auto-match scale ===
# Normalize measured and scale target if needed
if np.max(target_RGB) <= 1.0:
    target_RGB = target_RGB * 255

target_RGB = np.clip(target_RGB, 0, 255)
measured_RGB = np.clip(measured_RGB, 0, 255)

# === 5. Solve for M ===
M, _, _, _ = np.linalg.lstsq(measured_RGB, target_RGB, rcond=None)

# === 6. Show result ===
print("Calibration Matrix M (3x3):")
print(M)

# === 7. Quick comparison ===
for i in range(3):
    raw = measured_RGB[i]
    calibrated = raw @ M
    print(f"\nPatch {i+1}:")
    print(f"Measured RGB:    {np.round(raw)}")
    print(f"Calibrated RGB:  {np.round(calibrated)}")
    print(f"Target sRGB:     {np.round(target_RGB[i])}")