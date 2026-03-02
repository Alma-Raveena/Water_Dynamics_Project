import pandas as pd
import matplotlib.pyplot as plt
import os

# -----------------------------
# LOAD DATA
# -----------------------------

csv_path = "results/water_area.csv"
df = pd.read_csv(csv_path)

# Convert year to int
df["Year"] = df["Year"].astype(int)

# Create output folder
graph_folder = "results/graphs"
os.makedirs(graph_folder, exist_ok=True)

# -----------------------------
# GRAPH 1: LINE GRAPH
# -----------------------------

plt.figure()
for location in df["Location"].unique():
    subset = df[df["Location"] == location]
    plt.plot(subset["Year"], subset["Water_Area_km2"], marker='o', label=location)

plt.xlabel("Year")
plt.ylabel("Water Area (km²)")
plt.title("Year-wise Surface Water Variation")
plt.legend()
plt.grid(True)

plt.savefig(f"{graph_folder}/water_trend_line_graph.png", dpi=300)
plt.close()

# -----------------------------
# GRAPH 2: BAR COMPARISON
# -----------------------------

pivot = df.pivot(index="Year", columns="Location", values="Water_Area_km2")

pivot.plot(kind="bar")
plt.xlabel("Year")
plt.ylabel("Water Area (km²)")
plt.title("Surface Water Comparison Across Locations")
plt.grid(True)

plt.savefig(f"{graph_folder}/water_comparison_bar_graph.png", dpi=300)
plt.close()

print("✅ Graphs generated successfully")
