/* NexFlo Cloud - animations: scroll reveals, growing circles, hero demo, typing code, chat, meter, dashboard, tabs */
(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const onVisible = (el, fn) => {
    if (!("IntersectionObserver" in window)) return fn();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { io.disconnect(); fn(); } });
    }, { threshold: 0.25 });
    io.observe(el);
  };
  const splitLines = (code) => {
    if (!code.querySelector(".ln")) code.innerHTML = code.innerHTML.split("\n").map((l) => `<span class="ln">${l || " "}</span>`).join("");
    return [...code.querySelectorAll(".ln")];
  };

  /* ---- Reveal on scroll (home and inner pages) ---- */
  const REVEAL = ".section-head, .frow-text, .vis, .card, .feature, .step, .pain, .price-card, .form-card, .doc, .tile, .scard, .faq, .prow, .fact, .orbit, .notice, .cta2-box, .meter-wrap";
  if (!reduce && "IntersectionObserver" in window) {
    const els = [...document.querySelectorAll(REVEAL)].filter((e) => !e.closest(".hero-s, .page-hero, .dropdown") && !e.parentElement.closest(REVEAL));
    els.forEach((e) => {
      const sibs = [...e.parentElement.children].filter((c) => els.includes(c));
      e.style.setProperty("--i", Math.min(sibs.indexOf(e), 5));
      e.classList.add("rv");
    });
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (!en.isIntersecting) return;
      en.target.classList.add("in");
      io.unobserve(en.target);
      setTimeout(() => { en.target.classList.remove("rv", "in"); en.target.style.removeProperty("--i"); }, 1400);
    }), { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    els.forEach((e) => io.observe(e));
  }

  /* ---- Brand circles grow as they scroll into view ---- */
  const arcs = [...document.querySelectorAll("[data-arc]")];
  if (arcs.length && !reduce) {
    let ticking = false;
    const update = () => {
      const vh = innerHeight;
      arcs.forEach((a) => {
        const host = a.parentElement.getBoundingClientRect();
        const p = Math.min(Math.max((vh - host.top) / (vh * 0.9), 0), 1);
        const from = parseFloat(a.dataset.arc) || 0.7;
        a.style.setProperty("--s", (from + (1 - from) * p).toFixed(4));
      });
      ticking = false;
    };
    addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    addEventListener("resize", update);
    update();
  }

  /* ---- Code windows that type themselves out ---- */
  document.querySelectorAll("[data-type]").forEach((w) => {
    const lines = splitLines(w.querySelector("pre code"));
    if (reduce) return;
    const r = w.getBoundingClientRect();
    if (r.top < innerHeight * 0.8) return;
    w.classList.add("is-animated");
    onVisible(w, async () => {
      await sleep(250);
      for (const l of lines) { l.classList.add("on", "cur"); await sleep(70); l.classList.remove("cur"); }
    });
  });

  /* ---- Support chat ---- */
  document.querySelectorAll("[data-chat]").forEach((c) => {
    const msgs = [...c.querySelectorAll(".msg")];
    const typing = c.querySelector(".typing");
    if (reduce) { msgs.forEach((m) => m.classList.add("show")); if (typing) typing.hidden = true; return; }
    const loop = async () => {
      for (;;) {
        msgs.forEach((m) => m.classList.remove("show"));
        if (typing) typing.hidden = true;
        await sleep(500);
        msgs[0].classList.add("show");
        await sleep(900);
        if (typing) typing.hidden = false;
        await sleep(1500);
        if (typing) typing.hidden = true;
        for (const m of msgs.slice(1)) { m.classList.add("show"); await sleep(700); }
        await sleep(6500);
      }
    };
    onVisible(c, loop);
  });

  /* ---- Usage meter ---- */
  document.querySelectorAll("[data-meter]").forEach((m) => {
    const num = m.querySelector(".meter-num");
    const bar = m.querySelector(".meter-bar i");
    let value = parseInt(m.dataset.meter, 10) || 1000;
    const cap = value * 1.6;
    const show = () => { num.textContent = value.toLocaleString(); bar.style.setProperty("--w", `${Math.min(value / cap * 100, 100)}%`); };
    if (reduce) return show();
    num.textContent = "0";
    onVisible(m, () => {
      const t0 = performance.now(), dur = 1300, end = value;
      const step = (now) => {
        const p = Math.min((now - t0) / dur, 1);
        num.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))).toLocaleString();
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
      bar.style.setProperty("--w", `${end / cap * 100}%`);
      setInterval(() => { value += 1 + Math.floor(Math.random() * 3); if (value > cap * 0.95) value = end; show(); }, 2200);
    });
  });
  const clock = () => {
    const d = new Date();
    return [d.getHours(), d.getMinutes(), d.getSeconds()].map((n) => String(n).padStart(2, "0")).join(":");
  };

  /* ---- Hero: an order moving through NexFlo ---- */
  document.querySelectorAll("[data-demo]").forEach((demo) => {
    const [inCode, outCode] = demo.querySelectorAll("pre code");
    const L = splitLines(inCode), R = splitLines(outCode);
    const steps = [...demo.querySelectorAll(".demo-steps li")];
    const stamp = (i, text) => { const s = steps[i].querySelector("span"); if (s) s.textContent = text; };
    if (reduce) { steps.forEach((s) => s.classList.add("done")); return; }
    demo.classList.add("is-animated");
    const run = async () => {
      for (;;) {
        [...L, ...R].forEach((l) => l.classList.remove("on"));
        steps.forEach((s, i) => { s.classList.remove("on", "done"); stamp(i, "--:--:--"); });
        await sleep(400);
        steps[0].classList.add("on"); stamp(0, clock());
        for (const l of L) { l.classList.add("on", "cur"); await sleep(60); l.classList.remove("cur"); }
        steps[0].classList.replace("on", "done");
        steps[1].classList.add("on"); stamp(1, clock());
        await sleep(450);
        steps[1].classList.replace("on", "done");
        steps[2].classList.add("on"); stamp(2, clock());
        await sleep(300);
        steps[2].classList.replace("on", "done");
        steps[3].classList.add("on");
        for (const l of R) { l.classList.add("on"); await sleep(28); }
        steps[3].classList.replace("on", "done"); stamp(3, clock());
        await sleep(3800);
      }
    };
    run();
  });

  /* ---- Translation demo on product pages ---- */
  document.querySelectorAll(".translate[data-animate]").forEach((t) => {
    const codes = [...t.querySelectorAll("pre code")];
    const [L, R] = codes.map(splitLines);
    if (reduce || codes.length < 2) return;
    const status = t.querySelector(".translate-status");
    const say = (s) => status && (status.textContent = s);
    const done = t.dataset.done || "Delivered";
    onVisible(t, async () => {
      t.classList.add("is-animated");
      for (;;) {
        [...L, ...R].forEach((l) => l.classList.remove("on"));
        t.classList.remove("done");
        say("Waiting");
        await sleep(350);
        say("Receiving");
        for (const l of L) { l.classList.add("on", "cur"); await sleep(65); l.classList.remove("cur"); }
        t.classList.add("pulse"); say("Validating");
        await sleep(380);
        t.classList.remove("pulse"); say("Translating");
        for (const l of R) { l.classList.add("on"); await sleep(22); }
        t.classList.add("done"); say(done);
        await sleep(3400);
      }
    });
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
        setTimeout(() => { st.className = "st st-tr"; st.textContent = "Translated"; }, 600);
        setTimeout(finish, 1300);
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
      panes.forEach((p, j) => { p.hidden = j !== k; });
    }));
  });
})();
