/* NexFlo Cloud — site behaviour */

/*
 * FORM DELIVERY
 * Every form posts to FORM_ENDPOINT as JSON: { form, to, page, fields: {...} }.
 * Point it at whatever forwards to your Microsoft 365 inbox, e.g. a Power Automate
 * "When an HTTP request is received" flow, an Azure Function, or a service like Formspree.
 * While it's empty, forms fall back to opening a pre-filled email to the right inbox.
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

  /* ---- Forms ---- */
  document.querySelectorAll("form[data-form]").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (form.querySelector(".hp input")?.value) return; // honeypot
      if (!form.reportValidity()) return;

      const data = Object.fromEntries(new FormData(form).entries());
      delete data.website;
      const payload = { form: form.dataset.form, to: form.dataset.to, page: location.pathname, fields: data };
      const btn = form.querySelector('[type="submit"]');
      const label = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }

      try {
        if (FORM_ENDPOINT) {
          const res = await fetch(FORM_ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) });
          if (!res.ok) throw new Error("Request failed");
        } else {
          const lines = Object.entries(data).filter(([, v]) => v).map(([k, v]) => `${k.replace(/_/g, " ")}: ${v}`);
          const subject = `[${form.dataset.form}] ${data.company || data.email || "New request"}`;
          location.href = `mailto:${form.dataset.to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
        }
        form.classList.add("sent");
      } catch (err) {
        alert(`Sorry, something went wrong. Please email us at ${form.dataset.to}.`);
      } finally {
        if (btn) { btn.disabled = false; btn.textContent = label; }
      }
    });
  });

  /* ---- Theme: follows the device setting; the footer switch can override it ---- */
  const root = document.documentElement;
  const mq = window.matchMedia ? matchMedia("(prefers-color-scheme: light)") : null;
  const saved = () => { try { return localStorage.getItem("nf-theme"); } catch (e) { return null; } };
  const apply = (mode, animate) => {
    const t = mode === "system" ? (mq && mq.matches ? "light" : "dark") : mode;
    if (animate) { root.classList.add("theme-anim"); setTimeout(() => root.classList.remove("theme-anim"), 450); }
    root.dataset.theme = t;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = t === "dark" ? "#050B1A" : "#FFFFFF";
    document.querySelectorAll("[data-theme-set]").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.themeSet === mode)));
  };
  apply(saved() || "system", false);
  document.querySelectorAll("[data-theme-set]").forEach((b) => b.addEventListener("click", () => {
    const mode = b.dataset.themeSet;
    try { mode === "system" ? localStorage.removeItem("nf-theme") : localStorage.setItem("nf-theme", mode); } catch (e) {}
    apply(mode, true);
  }));
  if (mq) mq.addEventListener("change", () => { if (!saved()) apply("system", true); });

  /* ---- Year ---- */
  document.querySelectorAll("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));
})();
