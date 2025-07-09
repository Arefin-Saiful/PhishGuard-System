/* static/js/home.js  – update hero counters */

window.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("/api/stats");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    // only grab the two stats we still display
    const { emails_scanned, malicious_urls } = await res.json();

    // update the DOM
    document.getElementById("cntEmails").innerText = emails_scanned;
    document.getElementById("cntUrls"  ).innerText = malicious_urls;

  } catch (err) {
    console.error("Stats fetch failed:", err);
    // you could also show "N/A" or leave zeros here
  }
});
