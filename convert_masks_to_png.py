import os
import numpy as np
import rasterio
from PIL import Image

INPUT_DIR = "results/WaterMask"
OUTPUT_DIR = "frontend/assets/overlays"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def normalize_to_uint8(arr):
    arr = arr.astype(np.float32)
    arr_min, arr_max = arr.min(), arr.max()
    if arr_max - arr_min == 0:
        return np.zeros_like(arr, dtype=np.uint8)
    norm = (arr - arr_min) / (arr_max - arr_min)
    return (norm * 255).astype(np.uint8)

for fname in os.listdir(INPUT_DIR):
    if fname.lower().endswith(".tif"):
        in_path = os.path.join(INPUT_DIR, fname)

        with rasterio.open(in_path) as src:
            band = src.read(1)  # read first band (mask)

        img_arr = normalize_to_uint8(band)

        # Make water pixels blue-ish for visibility
        rgba = np.zeros((img_arr.shape[0], img_arr.shape[1], 4), dtype=np.uint8)
        rgba[..., 2] = img_arr       # Blue channel
        rgba[..., 3] = (img_arr > 0).astype(np.uint8) * 120  # Alpha transparency

        img = Image.fromarray(rgba, mode="RGBA")

        out_name = fname.replace("_WaterMask.tif", ".png")
        out_path = os.path.join(OUTPUT_DIR, out_name)

        img.save(out_path)
        print(f"Saved: {out_path}")

print("✅ All WaterMask TIFFs converted to PNG overlays.")