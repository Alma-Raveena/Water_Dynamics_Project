// -----------------------------
// Map centers
// -----------------------------
const centers = {
  UpperLake: { latlng: [23.25, 77.4], label: "Upper Lake, Bhopal" },
  Kuttanad: { latlng: [9.5, 76.4], label: "Kuttanad, Kerala" },
  Rayalaseema: { latlng: [14.5, 78.7], label: "Rayalaseema, AP" }
};

// -----------------------------
// Initialize Map
// -----------------------------
const map = L.map("map", { zoomControl: true }).setView(centers.UpperLake.latlng, 11);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

let marker = L.marker(centers.UpperLake.latlng).addTo(map);
marker.bindPopup(centers.UpperLake.label).openPopup();

let chart;

// -----------------------------
// Analyze Function
// -----------------------------
function analyze() {
  const location = document.getElementById("location").value;
  const y1 = parseInt(document.getElementById("year1").value);
  const y2 = parseInt(document.getElementById("year2").value);

  if (y1 === y2) {
    alert("Please select two different years for comparison.");
    return;
  }

  // Zoom and label on map
  const { latlng, label } = centers[location];
  map.setView(latlng, 11);
  marker.setLatLng(latlng);
  marker.bindPopup(label).openPopup();

  // Loading state
  document.getElementById("insightText").innerText = "Analyzing data...";
  document.getElementById("climateText").innerText = "";

  fetch(`https://AlmaRaveena28.pythonanywhere.com/compare?location=${location}&year1=${y1}&year2=${y2}`)
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }

      document.getElementById("kpi-location").innerText = `📍 Location: ${data.location}`;
      document.getElementById("kpi-change").innerText = `💧 Change: ${data.change} km²`;
      document.getElementById("kpi-percent").innerText = `📊 % Change: ${data.percent}%`;

      let status = "Stable";
      let color = "#f9a825";
      let severity = Math.min(Math.abs(data.percent), 100);

      if (data.percent <= -10) { status = "Decrease (Drying)"; color = "#e53935"; }
      else if (data.percent >= 10) { status = "Increase (Wetter)"; color = "#43a047"; }

      document.getElementById("status").innerText = `Status: ${status}`;
      const bar = document.getElementById("severity-bar");
      bar.style.width = severity + "%";
      bar.style.background = color;

      document.getElementById("insightText").innerText = data.insight;
      document.getElementById("climateText").innerText = data.climate;

      // -----------------------------
      // Chart
      // -----------------------------
      const ctx = document.getElementById("chart").getContext("2d");
      if (chart) chart.destroy();

      chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: [data.year1, data.year2],
          datasets: [{
            label: "Water Area (km²)",
            data: [data.area1, data.area2],
            borderColor: "#1e88e5",
            backgroundColor: "rgba(30,136,229,0.2)",
            fill: true,
            tension: 0.4,
            pointRadius: 5
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true } }
        }
      });
    })
    .catch(err => {
      console.error(err);
      alert("Backend is not reachable. Make sure Flask server is running.");
    });
}

// -----------------------------
// Light / Dark Theme Toggle
// -----------------------------
const themeBtn = document.getElementById("themeToggle");

themeBtn.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  themeBtn.textContent = document.body.classList.contains("dark") ? "☀️" : "🌙";
});

// -----------------------------
// Button Binding (safer than inline onclick)
// -----------------------------
document.getElementById("analyzeBtn").addEventListener("click", analyze);