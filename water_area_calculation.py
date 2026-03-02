import rasterio
import numpy as np
import csv
import os

water_mask_dir = "results/WaterMask"
output_csv = "backend/water_area.csv"

locations = ["Kuttanad", "Rayalaseema", "UpperLake"]
years = [2010, 2015, 2020, 2022, 2025]

# Pixel area (approx, adjust if you know resolution)
PIXEL_AREA_KM2 = (30 * 30) / 1e6  # 30m x 30m in km² (Landsat/Sentinel resampled)

# Write header if file not exists
file_exists = os.path.exists(output_csv)
with open(output_csv, "a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["location", "year", "area_km2"])

    for loc in locations:
        for year in years:
            mask_path = f"{water_mask_dir}/{loc}_{year}_WaterMask.tif"

            if not os.path.exists(mask_path):
                print(f"Missing mask: {mask_path}")
                continue

            with rasterio.open(mask_path) as src:
                mask = src.read(1)

            water_pixels = np.sum(mask == 1)
            area_km2 = water_pixels * PIXEL_AREA_KM2

            writer.writerow([loc, year, round(area_km2, 2)])
            print(f"{loc} {year} → {round(area_km2, 2)} km²")

print("✅ Water area calculation completed & CSV updated")