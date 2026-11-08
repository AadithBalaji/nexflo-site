/* NexFlo Cloud — site behaviour */

/*
 * FORM DELIVERY
 * Every form posts to FORM_ENDPOINT as JSON: { form, to, page, fields: {...} }.
 * Point it at whatever forwards to your Microsoft 365 inbox, e.g. a Power Automate
 * "When an HTTP request is received" flow, an Azure Function, or a service like Formspree.
 * While it's empty, forms validate but don't send; they tell the visitor to email the inbox instead.
 */
const FORM_ENDPOINT = "";

(function () {
  const body = document.body;

  /* ---- Mobile menu ---- */
  const toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const open = body.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  /* ---- Dropdowns ---- */
  const items = document.querySelectorAll(".nav-item.has-dd");
  const isDesktop = () => window.matchMedia("(min-width: 1081px)").matches;
  const closeAll = (except) => items.forEach((i) => {
    if (i !== except) { i.classList.remove("open"); i.querySelector(".nav-link").setAttribute("aria-expanded", "false"); }
  });
  items.forEach((item) => {
    const btn = item.querySelector(".nav-link");
    let t;
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const open = !item.classList.contains("open");
      closeAll(item);
      item.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
    item.addEventListener("mouseenter", () => { if (!isDesktop()) return; clearTimeout(t); closeAll(item); item.classList.add("open"); btn.setAttribute("aria-expanded", "true"); });
    item.addEventListener("mouseleave", () => { if (!isDesktop()) return; t = setTimeout(() => { item.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); }, 120); });
  });
  document.addEventListener("click", (e) => { if (!e.target.closest(".nav-item")) closeAll(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { closeAll(); body.classList.remove("menu-open"); } });

  /* ---- Prefill from query string (?email=, ?product=) ---- */
  const params = new URLSearchParams(location.search);
  ["email", "product"].forEach((k) => {
    const v = params.get(k);
    if (!v) return;
    document.querySelectorAll(`[name="${k}"]`).forEach((el) => {
      if (el.tagName === "SELECT") {
        const opt = [...el.options].find((o) => o.value.toLowerCase() === v.toLowerCase());
        if (opt) el.value = opt.value;
      } else if (!el.value) el.value = v;
    });
  });

  /* ---- Forms ----
     Validates inline, blocks double submits, and shows success only after the endpoint confirms.
     Until FORM_ENDPOINT is set there is nowhere to send to, so the form says so and offers email instead. */
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const setError = (field, msg) => {
    const wrap = field.closest(".field");
    const form = field.closest("form");
    let el = wrap ? wrap.querySelector(".err-msg") : (form.nextElementSibling && form.nextElementSibling.classList.contains("err-msg") ? form.nextElementSibling : null);
    if (!msg) { field.removeAttribute("aria-invalid"); if (el) el.remove(); return; }
    field.setAttribute("aria-invalid", "true");
    if (!el) {
      el = document.createElement("p"); el.className = "err-msg"; el.setAttribute("role", "alert");
      wrap ? wrap.appendChild(el) : form.insertAdjacentElement("afterend", el);
    }
    el.textContent = msg;
  };
  const check = (field) => {
    const v = (field.value || "").trim();
    if (field.required && !v) return field.tagName === "SELECT" ? "Please choose an option." : "This field is required.";
    if (field.type === "email" && v && !EMAIL_RE.test(v)) return "Please enter a valid email address, like name@company.com.";
    return "";
  };
  document.querySelectorAll("form[data-form]").forEach((form) => {
    form.setAttribute("novalidate", "");
    const fields = [...form.querySelectorAll("input:not([type=hidden]):not([name=website]), select, textarea")];
    fields.forEach((f) => f.addEventListener("blur", () => { if (f.hasAttribute("aria-invalid")) setError(f, check(f)); }));
    let busy = false;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (busy) return;
      if (form.querySelector(".hp input")?.value) return; // honeypot
      let first = null;
      fields.forEach((f) => { const m = check(f); setError(f, m); if (m && !first) first = f; });
      if (first) { first.focus(); return; }
      let status = form.classList.contains("signup") ? form.parentNode.querySelector(".form-status") : form.querySelector(".form-status");
      if (!status) {
        status = Object.assign(document.createElement("p"), { className: "form-status" });
        const foot = form.querySelector(".form-foot");
        if (form.classList.contains("signup")) form.insertAdjacentElement("afterend", status);
        else if (foot) foot.insertAdjacentElement("afterend", status);
        else form.appendChild(status);
      }
      status.setAttribute("role", "status");
      status.textContent = "";
      if (!FORM_ENDPOINT) {
        status.className = "form-status warn";
        status.innerHTML = `Online sending isn't switched on yet, so this wasn't sent. Please email <a href="mailto:${form.dataset.to}">${form.dataset.to}</a>.`;
        return;
      }
      const data = Object.fromEntries(new FormData(form).entries());
      delete data.website;
      const btn = form.querySelector('[type="submit"]');
      const label = btn ? btn.textContent : "";
      busy = true;
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      try {
        const res = await fetch(FORM_ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ form: form.dataset.form, to: form.dataset.to, page: location.pathname, submitted_at: new Date().toISOString(), fields: data }) });
        if (!res.ok) throw new Error("Request failed");
        form.classList.add("sent");
        form.reset();
      } catch (err) {
        status.className = "form-status warn";
        status.innerHTML = `Sorry, that didn't go through. Please try again or email <a href="mailto:${form.dataset.to}">${form.dataset.to}</a>.`;
      } finally {
        busy = false;
        if (btn) { btn.disabled = false; btn.textContent = label; }
      }
    });
  });

  /* ---- TEMPORARY design preview: product name colours (Version 1 / Version 2) ----
     The version is set on <html data-pv> by a small script in <head>; this keeps the switches in sync,
     applies a click immediately to every product name on the page, and remembers it for other pages. */
  const pvButtons = [...document.querySelectorAll(".pv-toggle [data-pv]")];
  const pvSync = () => pvButtons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.pv === document.documentElement.dataset.pv)));
  pvButtons.forEach((b) => b.addEventListener("click", () => {
    document.documentElement.dataset.pv = b.dataset.pv;
    try { localStorage.setItem("nf-pv", b.dataset.pv); } catch (e) { /* private mode: still switches on this page */ }
    pvSync();
  }));
  pvSync();

  /* ---- Year ---- */
  document.querySelectorAll("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));
})();
