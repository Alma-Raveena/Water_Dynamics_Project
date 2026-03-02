from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
from collections import defaultdict
import os

app = Flask(__name__)
CORS(app)

CSV_PATH = "water_area.csv"  # since app.py is inside backend/

# -----------------------------
# Load data from CSV
# -----------------------------
def load_data():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"{CSV_PATH} not found. Make sure water_area.csv is in backend/")

    data = defaultdict(dict)  # data[location][year] = area

    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Defensive: handle any header casing issues
            loc = row.get("location") or row.get("Location")
            year = int(row.get("year") or row.get("Year"))
            area = float(row.get("area_km2") or row.get("Water_Area_km2"))

            data[loc][year] = area

    return data

# -----------------------------
# Utils
# -----------------------------
def climate_insight(percent_change):
    if percent_change > 20:
        return "Significant increase in surface water suggests wetter climatic conditions or increased inflow."
    elif percent_change < -20:
        return "Significant decline in surface water suggests drying trends and possible climatic stress."
    else:
        return "Minor change in surface water suggests relatively stable hydrological conditions."

def climate_status(percent_change):
    if percent_change > 10:
        return "Increase (Wetter)"
    elif percent_change < -10:
        return "Decrease (Drying)"
    else:
        return "Stable"

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return jsonify({"status": "Surface Water Dynamics API running"})

@app.route("/compare")
def compare_years():
    location = request.args.get("location")
    year1 = request.args.get("year1", type=int)
    year2 = request.args.get("year2", type=int)

    if not location or not year1 or not year2:
        return jsonify({"error": "Provide location, year1, and year2"}), 400

    data = load_data()

    if location not in data:
        return jsonify({"error": f"Location '{location}' not found"}), 404

    if year1 not in data[location] or year2 not in data[location]:
        return jsonify({"error": "Data not available for selected year(s)"}), 400

    area1 = round(data[location][year1], 2)
    area2 = round(data[location][year2], 2)

    change = round(area2 - area1, 2)
    percent = round((change / area1) * 100, 2) if area1 != 0 else 0

    if change > 0:
        trend = f"Increasing trend ({year1} to {year2})"
    elif change < 0:
        trend = f"Decreasing trend ({year1} to {year2})"
    else:
        trend = f"No change ({year1} to {year2})"

    response = {
        "location": location,
        "year1": year1,
        "year2": year2,
        "area1": area1,
        "area2": area2,
        "change": change,
        "percent": percent,
        "trend": trend,
        "status": climate_status(percent),
        "climate": climate_insight(percent),
        "insight": climate_insight(percent),
    }

    return jsonify(response)

@app.route("/trend")
def trend_multi_year():
    location = request.args.get("location")

    if not location:
        return jsonify({"error": "Provide location"}), 400

    data = load_data()

    if location not in data:
        return jsonify({"error": f"Location '{location}' not found"}), 404

    years = sorted(data[location].keys())
    areas = [round(data[location][y], 2) for y in years]

    change = round(areas[-1] - areas[0], 2)
    percent = round((change / areas[0]) * 100, 2) if areas[0] != 0 else 0

    if percent > 20:
        overall_trend = f"Strong increasing trend in surface water from {years[0]} to {years[-1]}."
    elif percent < -20:
        overall_trend = f"Strong decreasing trend in surface water from {years[0]} to {years[-1]}."
    elif percent > 0:
        overall_trend = f"Slight increase in surface water from {years[0]} to {years[-1]}."
    elif percent < 0:
        overall_trend = f"Slight decrease in surface water from {years[0]} to {years[-1]}."
    else:
        overall_trend = f"No significant change in surface water from {years[0]} to {years[-1]}."

    response = {
        "location": location,
        "years": years,
        "areas": areas,
        "overall_change": change,
        "overall_percent": percent,
        "overall_trend": overall_trend,
        "climate_summary": climate_insight(percent)
    }

    return jsonify(response)

@app.route("/summary")
def summary_all_locations():
    data = load_data()
    summary = []

    for loc, years_data in data.items():
        years = sorted(years_data.keys())
        start_year = years[0]
        end_year = years[-1]

        start_area = years_data[start_year]
        end_area = years_data[end_year]

        change = round(end_area - start_area, 2)
        percent = round((change / start_area) * 100, 2) if start_area != 0 else 0

        if percent > 10:
            trend = "Increase"
        elif percent < -10:
            trend = "Decrease"
        else:
            trend = "Stable"

        summary.append({
            "location": loc,
            "from_year": start_year,
            "to_year": end_year,
            "start_area": round(start_area, 2),
            "end_area": round(end_area, 2),
            "change": change,
            "percent": percent,
            "trend": trend
        })

    return jsonify(summary)
# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)