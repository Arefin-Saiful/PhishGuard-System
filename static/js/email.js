/* static/js/email.js  – v3
   --------------------------------------------------------------
   Handles the e-mail-scanner page
   • Enables / disables the Scan button
   • Shows a spinner while the request is running
   • Posts the .eml file to /api/email and renders verdict + gauge
   • Doughnut gauge with % in the centre (pure Chart.js v4)
   -------------------------------------------------------------- */


/* ── 1 ▸ DOM elements ────────────────────────────────────────── */
const fileInput  = document.getElementById("emlInput");
const scanBtn    = document.getElementById("scanEmailBtn");
const busyIcon   = document.getElementById("emailBusy");        // spinner

const card       = document.getElementById("emailResult");
const verdictTxt = document.getElementById("verdictText");
const whyBox     = document.getElementById("whyBox");
const tokenList  = document.getElementById("tokenList");

const gaugeCtx   = document.getElementById("gaugeCanvas").getContext("2d");


/* ── 2 ▸ Enable the button once a file is chosen ─────────────── */
fileInput.addEventListener("change", () => {
  scanBtn.disabled = fileInput.files.length === 0;
});


/* ── 3 ▸ Gauge helper – draws doughnut + % text in the centre ── */
let gaugeChart = null;

/* tiny plug-in that writes text in the centre */
const centreText = {
  id: "centreText",
  beforeDraw(chart, _args, opts) {
    const { ctx, chartArea: { width, height } } = chart;
    ctx.save();
    ctx.font         = opts.font   || "600 22px system-ui, sans-serif";
    ctx.fillStyle    = opts.colour || "#000";
    ctx.textAlign    = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(opts.text, width / 2, height / 2);
    ctx.restore();
  }
};

function drawGauge(conf, isPhish) {
  const colour     = isPhish ? "#dc3545" : "#198754";            // red ↔ green
  const percentTxt = `${(conf * 100).toFixed(1)} %`;

  if (gaugeChart) gaugeChart.destroy();                          // remove old chart

  gaugeChart = new Chart(gaugeCtx, {
    type   : "doughnut",
    data   : {
      datasets: [{
        data            : [conf * 100, 100 - conf * 100],
        backgroundColor : [colour, "#e9ecef"],
        borderWidth     : 0
      }]
    },
    options: {
      cutout    : "70%",                                         // inner radius
      plugins   : {
        legend     : { display: false },
        tooltip    : { enabled: false },
        centreText : { text: percentTxt, colour }                // text plug-in
      },
      animation : { duration: 500 }
    },
    plugins: [centreText]
  });
}


/* ── 4 ▸ Populate the result card ────────────────────────────── */
function renderResult(verdict, conf, topTokens = []) {
  const isPhish = verdict === "Phishing";

  verdictTxt.textContent = verdict;
  verdictTxt.className   = isPhish
    ? "text-danger fw-bold"
    : "text-success fw-bold";

  drawGauge(conf, isPhish);

  if (topTokens.length) {
    whyBox.classList.remove("d-none");
    tokenList.innerHTML = topTokens
      .map(tok => `<li>⚠️ ${tok}</li>`)
      .join("");
  } else {
    whyBox.classList.add("d-none");
  }

  card.classList.remove("d-none");
  card.classList.add("aos-animate");            // re-trigger AOS fade-in
}


/* ── 5 ▸ Click → upload → show result ───────────────────────── */
scanBtn.addEventListener("click", async () => {
  if (fileInput.files.length === 0) return;

  scanBtn.disabled = true;
  busyIcon.classList.remove("d-none");          // show spinner
  card.classList.add("d-none");                 // hide previous result

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch("/api/email", { method: "POST", body: formData });
    if (!res.ok) throw new Error(await res.text());

    const { verdict, confidence, top_tokens: topTokens = [] } = await res.json();
    renderResult(verdict, confidence, topTokens);

  } catch (err) {
    console.error(err);
    alert("Scan failed – please check console.");
  } finally {
    busyIcon.classList.add("d-none");           // hide spinner
    scanBtn.disabled = false;
  }
});
