/* NexFlo Cloud - product animations only: hero demo, translation demo, dashboard, code tabs */
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
    code.innerHTML = code.innerHTML.split("\n").map((l) => `<span class="ln">${l || " "}</span>`).join("");
    return [...code.children];
  };
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
