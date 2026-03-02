import rasterio
import numpy as np
import os

# -----------------------------
# PATHS
# -----------------------------

data_path = "data"
ndwi_out = "results/NDWI"
water_out = "results/WaterMask"

os.makedirs(ndwi_out, exist_ok=True)
os.makedirs(water_out, exist_ok=True)

locations = ["Kuttanad", "Rayalaseema", "UpperLake"]
years = [2010, 2015, 2020, 2022, 2025]

# -----------------------------
# PROCESSING
# -----------------------------

for loc in locations:
    for year in years:

        file_path = f"{data_path}/{loc}/{loc}_{year}_B03_B08.tif"

        if not os.path.exists(file_path):
            print(f"Missing file: {file_path}")
            continue

        with rasterio.open(file_path) as src:
            green = src.read(1).astype("float32")
            nir = src.read(2).astype("float32")
            profile = src.profile

        # NDWI (safe computation)
        den = green + nir
        ndwi = np.where(den == 0, 0, (green - nir) / den)

        # Water mask
        water = np.where(ndwi > 0, 1, 0)

        # Save NDWI
        profile.update(dtype=rasterio.float32, count=1, nodata=0)

        ndwi_file = f"{ndwi_out}/{loc}_{year}_NDWI.tif"
        with rasterio.open(ndwi_file, "w", **profile) as dst:
            dst.write(ndwi.astype("float32"), 1)

        # Save Water Mask
        profile.update(dtype=rasterio.uint8, nodata=0)

        water_file = f"{water_out}/{loc}_{year}_WaterMask.tif"
        with rasterio.open(water_file, "w", **profile) as dst:
            dst.write(water.astype("uint8"), 1)

        print(f"Completed → {loc} {year}")

print("✅ ALL NDWI AND WATER MASK GENERATED")