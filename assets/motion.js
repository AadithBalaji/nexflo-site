/* NexFlo Cloud — motion: scroll reveals, glass spotlight, live product demos */
(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const onVisible = (el, fn, opts) => {
    if (!("IntersectionObserver" in window)) return fn();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { io.disconnect(); fn(); } });
    }, opts || { threshold: 0.25 });
    io.observe(el);
  };

  /* ---- Header gets more solid once you scroll ---- */
  const header = document.querySelector(".site-header");
  const onScroll = () => header && header.classList.toggle("scrolled", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---- Scroll reveal ---- */
  const SEL = ".section-head, .card, .step, .feature, .founder, .form-card, .translate, .dash, .code-tabs, .pain, .faq, .notice, .cta-box, .stat, .marquee-wrap, .checks, blockquote";
  if (!reduce && "IntersectionObserver" in window) {
    const els = [...document.querySelectorAll(SEL)].filter((e) => !e.closest(".hero, .dropdown, .portal-wrap") && !e.parentElement.closest(SEL));
    els.forEach((e) => {
      const sibs = [...e.parentElement.children].filter((c) => els.includes(c));
      e.style.setProperty("--i", Math.min(sibs.indexOf(e), 5));
      e.classList.add("reveal");
    });
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        const t = en.target;
        t.classList.add("in");
        io.unobserve(t);
        // Hand the element back to its normal styles once it has arrived.
        setTimeout(() => { t.classList.remove("reveal", "in"); t.style.removeProperty("--i"); }, 1200);
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.06 });
    els.forEach((e) => io.observe(e));
  }

  /* ---- Glass spotlight that follows the cursor ---- */
  document.addEventListener("pointermove", (e) => {
    const t = e.target.closest && e.target.closest(".card, .feature, .step, .glass, .founder");
    if (!t) return;
    const r = t.getBoundingClientRect();
    t.style.setProperty("--mx", `${e.clientX - r.left}px`);
    t.style.setProperty("--my", `${e.clientY - r.top}px`);
  }, { passive: true });

  /* ---- Hero: gentle parallax ---- */
  const hero = document.querySelector(".hero");
  const visuals = document.querySelectorAll(".hero-visual");
  if (hero && visuals.length && !reduce) {
    hero.addEventListener("pointermove", (e) => {
      const r = hero.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      visuals.forEach((v) => (v.style.transform = `translate3d(${x * -14}px, ${y * -10}px, 0)`));
    });
    hero.addEventListener("pointerleave", () => visuals.forEach((v) => (v.style.transform = "")));
  }

  /* ---- Hero: transaction toasts ---- */
  const toasts = [...document.querySelectorAll(".toast")];
  if (toasts.length) {
    const POS = ["pos-0", "pos-1", "pos-2"];
    let queue = [];
    let k = 0;
    const tick = () => {
      queue.unshift(k % toasts.length);
      k++;
      queue = queue.slice(0, 3);
      toasts.forEach((t, i) => {
        t.classList.remove(...POS);
        const at = queue.indexOf(i);
        if (at > -1) t.classList.add(POS[at]);
      });
    };
    if (reduce) { tick(); tick(); tick(); }
    else { setTimeout(() => { tick(); setInterval(tick, 2400); }, 900); }
  }

  /* ---- Counters ---- */
  document.querySelectorAll("[data-count]").forEach((el) => {
    const end = parseFloat(el.dataset.count);
    if (reduce) return;
    el.textContent = "0";
    onVisible(el, () => {
      const t0 = performance.now(), dur = 1200;
      const step = (now) => {
        const p = Math.min((now - t0) / dur, 1);
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))).toLocaleString();
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  });

  /* ---- How it works: steps light up in turn ---- */
  document.querySelectorAll("[data-cycle]").forEach((wrap) => {
    const items = [...wrap.children];
    if (reduce || !items.length) return;
    let i = 0;
    onVisible(wrap, () => {
      const go = () => { items.forEach((s, j) => s.classList.toggle("active", j === i % items.length)); i++; };
      go();
      setInterval(go, 2200);
    });
  });

  /* ---- Live translation demo ---- */
  document.querySelectorAll(".translate[data-animate]").forEach((t) => {
    const codes = [...t.querySelectorAll("pre code")];
    codes.forEach((c) => {
      c.innerHTML = c.innerHTML.split("\n").map((l) => `<span class="ln">${l || " "}</span>`).join("");
    });
    if (reduce || codes.length < 2) return;
    t.classList.add("is-animated");
    const [L, R] = codes.map((c) => [...c.children]);
    const status = t.querySelector(".translate-status");
    const done = t.dataset.done || "Delivered";
    const say = (s) => status && (status.textContent = s);
    const run = async () => {
      for (;;) {
        [...L, ...R].forEach((l) => l.classList.remove("on"));
        t.classList.remove("done");
        say("Waiting for document…");
        await sleep(350);
        say("Receiving…");
        for (const l of L) { l.classList.add("on", "cur"); await sleep(65); l.classList.remove("cur"); }
        t.classList.add("pulse");
        say("Validating…");
        await sleep(380);
        t.classList.remove("pulse");
        say("Translating…");
        for (const l of R) { l.classList.add("on"); await sleep(22); }
        t.classList.add("done");
        say(done);
        await sleep(3400);
      }
    };
    onVisible(t, run, { threshold: 0.3 });
  });

  /* ---- Dashboard preview ---- */
  document.querySelectorAll("[data-dash]").forEach((d) => {
    const rows = d.querySelector("[data-rows]");
    const docsEl = d.querySelector('[data-kpi="docs"]');
    const errEl = d.querySelector('[data-kpi="err"]');
    const feed = [
      ["Walmart", "850", "Purchase order", "Delivered"],
      ["Target", "850", "Purchase order", "Delivered"],
      ["Walmart", "856", "Ship notice", "Sent"],
      ["Home Depot", "810", "Invoice", "Sent"],
      ["Costco", "855", "PO acknowledgment", "Sent"],
      ["Kroger", "846", "Inventory advice", "Sent"],
      ["Target", "997", "Acknowledgment", "Accepted"],
      ["Walmart", "810", "Invoice", "Sent"],
      ["Home Depot", "850", "Purchase order", "Delivered"],
    ];
    let i = 0, docs = 1284, errs = 1, minute = 9 * 60 + 30;
    const fmt = (m) => `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
    const add = (instant) => {
      const [partner, code, name, final] = feed[i % feed.length];
      const flagged = i % 11 === 7;
      i++; minute++;
      const row = document.createElement("div");
      row.className = "dash-row" + (instant ? "" : " new");
      row.innerHTML = `<span class="mono">${fmt(minute)}</span><span class="partner">${partner}</span><span><b class="doc-chip">${code}</b> ${name}</span><span class="st st-rec">Received</span>`;
      rows.prepend(row);
      while (rows.children.length > 6) rows.lastElementChild.remove();
      const st = row.querySelector(".st");
      const finish = () => {
        if (flagged) { st.className = "st st-warn"; st.textContent = "Needs review"; errs++; errEl && (errEl.textContent = errs); }
        else { st.className = "st st-ok"; st.textContent = final; }
      };
      if (instant) finish();
      else {
        setTimeout(() => { st.className = "st st-tr"; st.textContent = "Translated"; }, 700);
        setTimeout(finish, 1500);
      }
      docs++;
      docsEl && (docsEl.textContent = docs.toLocaleString());
    };
    for (let n = 0; n < 6; n++) add(true);
    if (!reduce) onVisible(d, () => setInterval(() => add(false), 2300));
  });

  /* ---- Code tabs ---- */
  document.querySelectorAll("[data-tabs]").forEach((w) => {
    const tabs = [...w.querySelectorAll('[role="tab"]')];
    const panes = [...w.querySelectorAll('[role="tabpanel"]')];
    tabs.forEach((b, k) => b.addEventListener("click", () => {
      tabs.forEach((x) => x.setAttribute("aria-selected", String(x === b)));
      panes.forEach((p, j) => { p.hidden = j !== k; if (j === k) { p.classList.remove("swap"); void p.offsetWidth; p.classList.add("swap"); } });
    }));
  });
})();
