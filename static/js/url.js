/*  static/js/url.js  ───────────────────────────────────────────────
 *  Handles URL-scanner page
 *   1 ▸ Enable / disable “Scan” while user types (any non-empty text)
 *   2 ▸ Prepend http:// if protocol missing
 *   3 ▸ Show a spinner while the back-end works
 *   4 ▸ POST the URL to /api/url and render verdict + gauge
 *  Requires: Chart.js is already loaded globally (see base.html)
 *  ---------------------------------------------------------------- */

const urlInput   = document.getElementById("urlInput");
const scanBtn    = document.getElementById("scanUrlBtn");
const busyIcon   = document.getElementById("urlBusy");
const resultCard = document.getElementById("urlResult");
const verdictEl  = document.getElementById("urlVerdict");
const confEl     = document.getElementById("urlConf");
const whyBlock   = document.getElementById("urlWhy");
const tokenList  = document.getElementById("urlTokenList");
const gaugeCtx   = document.getElementById("urlGauge").getContext("2d");

let gauge = null;  // Chart.js instance

/* ── 1 ▸ Button state: any non-empty → enabled ──────────────────── */
function toggleButton() {
  scanBtn.disabled = urlInput.value.trim() === "";
}
urlInput.addEventListener("input", toggleButton);
toggleButton();  // initialize on load

/* ENTER triggers the scan if button enabled */
urlInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !scanBtn.disabled) {
    scanBtn.click();
  }
});

/* ── 2 ▸ Draw / replace doughnut gauge ───────────────────────── */
function drawGauge(prob, colour) {
  if (gauge) gauge.destroy();

  gauge = new Chart(gaugeCtx, {
    type: "doughnut",
    data: {
      datasets: [{
        data: [prob, 1 - prob],
        backgroundColor: [colour, "#e9ecef"],
        borderWidth: 0
      }]
    },
    options: {
      cutout: "72%",
      animation: { duration: 300 },
      plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
  });
}

/* ── 3 ▸ Render the result card ───────────────────────────────── */
function showResult({ verdict, confidence, why_tokens = [] }) {
  const isPhish   = verdict === "Phishing";
  const colourTxt = isPhish ? "text-danger" : "text-success";
  const colourBar = isPhish ? "#dc3545"     : "#198754";

  verdictEl.textContent = verdict;
  verdictEl.className   = `card-title fw-bold ${colourTxt}`;

  confEl.textContent    = `Confidence ${(confidence * 100).toFixed(1)} %`;
  drawGauge(confidence, colourBar);

  if (isPhish && why_tokens.length) {
    tokenList.innerHTML = why_tokens.map(t => `<li>• ${t}</li>`).join("");
    whyBlock.classList.remove("d-none");
  } else {
    whyBlock.classList.add("d-none");
  }

  resultCard.classList.remove("d-none");
}

/* ── 4 ▸ Main click handler ───────────────────────────────────── */
scanBtn.addEventListener("click", async () => {
  let url = urlInput.value.trim();
  if (url === "") return;

  // 2-A) Prepend protocol if missing
  if (!/^https?:\/\//i.test(url)) {
    url = "http://" + url;
  }

  // UI → busy
  scanBtn.disabled = true;
  busyIcon.classList.remove("d-none");
  resultCard.classList.add("d-none");

  try {
    const res = await fetch("/api/url", {
      method : "POST",
      headers: { "Content-Type": "application/json" },
      body   : JSON.stringify({ url })
    });

    const data = await res.json();

    if (!res.ok) {
      const message = data?.error || "Unknown error";
      alert(`❌ Scan failed: ${message}`);
      return;
    }

    // Successful scan → display result
    showResult(data);

  } catch (err) {
    console.error("Fetch error:", err);
    alert("⚠️ Scan failed – could not reach the backend.");
  } finally {
    busyIcon.classList.add("d-none");
    toggleButton();
  }
});
