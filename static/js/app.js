// helper functions will go here later
/*  static/js/app.js  ─────────────────────────────────────────
   global helpers (optional – site works fine without this)
----------------------------------------------------------------*/

// 1. Auto-dismiss Bootstrap .alert messages after 4 s
document.querySelectorAll(".alert").forEach(el => {
  setTimeout(() => {
    // fade-out then remove from DOM
    el.classList.remove("show");
    el.addEventListener("transitionend", () => el.remove());
  }, 4000);
});

// 2. Expose a lightweight toast() helper
export function toast(message, type = "info", delay = 4000) {
  const tpl = `
    <div class="toast align-items-center text-bg-${type} border-0" role="alert">
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto"
                data-bs-dismiss="toast"></button>
      </div>
    </div>`;
  const wrapper = document.createElement("div");
  wrapper.innerHTML = tpl.trim();
  const toastEl = wrapper.firstChild;
  document.body.appendChild(toastEl);
  const bsToast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay });
  bsToast.show();
  toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
}
