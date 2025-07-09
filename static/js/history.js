// static/js/history.js

// 1) Draw overall verdicts pie chart
fetch("/api/history/pie")
  .then(res => res.json())
  .then(data => {
    new Chart(document.getElementById("pieChart"), {
      type: "pie",
      data: {
        labels: Object.keys(data),
        datasets: [{
          data: Object.values(data),
          backgroundColor: ["#dc3545", "#0d6efd"]  // Phishing=red, Legit=blue
        }]
      },
      options: {
        plugins: { legend: { position: "bottom" } }
      }
    });
  })
  .catch(err => console.error("Error loading pie data:", err));

// 2) Draw daily scans line chart
fetch("/api/history/daily")
  .then(res => res.json())
  .then(data => {
    const days = Object.keys(data).sort();
    const phishing = days.map(day => data[day].Phishing || 0);
    const legit    = days.map(day => data[day].Legitimate || 0);

    new Chart(document.getElementById("lineChart"), {
      type: "line",
      data: {
        labels: days,
        datasets: [
          { label: "Legitimate", data: legit, fill: true, tension: 0.3 },
          { label: "Phishing",  data: phishing, fill: true, tension: 0.3 }
        ]
      },
      options: {
        scales: { y: { beginAtZero: true } },
        plugins: { legend: { position: "bottom" } }
      }
    });
  })
  .catch(err => console.error("Error loading daily data:", err));

// 3) Populate detailed history table
fetch("/api/history/all")
  .then(res => res.json())
  .then(records => {
    const tbody = document.getElementById("historyTableBody");
    // Sort newest first
    records.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    records.forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${new Date(r.timestamp).toLocaleString()}</td>
        <td>${r.type}</td>
        <td>${r.verdict}</td>
        <td>${(r.confidence*100).toFixed(1)}%</td>
      `;
      tbody.appendChild(tr);
    });
  })
  .catch(err => console.error("Error loading history records:", err));
