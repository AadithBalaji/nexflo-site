/* NexFlo Cloud - animations: scroll reveals, growing circles, hero demo, typing code, chat, meter, dashboard, tabs */
(function () {
  /* Reduce Motion keeps things moving, just calmer: reveals fade without sliding (see styles.css),
     orbits run at half speed, and clouds don't grow on scroll. Everything else runs as normal. */
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
  const REVEAL = ".section-head, .how-head, .frow-text, .vis, .card, .feature, .step, .pain, .price-card, .form-card, .doc, .tile, .scard, .faq, .prow, .fact, .orbit-view, .notice, .cta2-box, .f4, .pkg-how li, .tf-side, .tf-engine, .tf-feats, .vs";
  if ("IntersectionObserver" in window) {
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
      setTimeout(() => { en.target.classList.remove("rv", "in"); en.target.style.removeProperty("--i"); }, 2200);
    }), { rootMargin: "0px 0px -6% 0px", threshold: 0.05 });
    els.forEach((e) => io.observe(e));
  }

  /* ---- Cloud shapes ease up as they scroll into view (smoothed, so they never jump with the scroll) ---- */
  const arcs = [...document.querySelectorAll("[data-arc]")].map((el) => ({ el, from: parseFloat(el.dataset.arc) || 0.7, cur: null, target: 1 }));
  if (arcs.length && !reduce) {
    let raf = 0;
    const measure = () => {
      const vh = innerHeight;
      arcs.forEach((a) => {
        const r = a.el.parentElement.getBoundingClientRect();
        const p = Math.min(Math.max((vh - r.top) / (vh * 1.1), 0), 1);
        a.target = a.from + (1 - a.from) * p;
        if (a.cur === null) a.cur = a.target;
      });
    };
    const tick = () => {
      let moving = false;
      arcs.forEach((a) => {
        const d = a.target - a.cur;
        if (Math.abs(d) > 0.0005) { a.cur += d * 0.06; moving = true; } else a.cur = a.target;
        a.el.style.setProperty("--s", a.cur.toFixed(4));
      });
      raf = moving ? requestAnimationFrame(tick) : 0;
    };
    const kick = () => { measure(); if (!raf) raf = requestAnimationFrame(tick); };
    addEventListener("scroll", kick, { passive: true });
    addEventListener("resize", kick);
    kick();
  }

  /* ---- Orbits: labels travel along ellipses but never rotate (position only, via translate) ---- */
  document.querySelectorAll("[data-orbit]").forEach((el) => {
    const [vw, vh] = el.dataset.vb.split(" ").map(Number);
    const orbits = JSON.parse(el.dataset.orbits);
    const ellipses = [...el.querySelectorAll(".o-paths ellipse")];
    const items = [...el.querySelectorAll("[data-o]")].map((n) => ({ n, o: +n.dataset.o, phase: +n.dataset.phase, speed: +n.dataset.speed }));
    const narrowK = parseFloat(el.dataset.narrow) || 0.8;
    let k = 1, scale = 1;
    const resize = () => {
      const w = el.clientWidth;
      scale = w / vw;
      k = w < 520 ? narrowK : 1;
      ellipses.forEach((e, i) => e.setAttribute("rx", orbits[i][0] * k));
    };
    const place = (secs) => {
      for (const it of items) {
        const [rx, ry, tilt] = orbits[it.o];
        const a = (it.phase + it.speed * secs) * Math.PI / 180, t = tilt * Math.PI / 180;
        const x = rx * k * Math.cos(a), y = ry * Math.sin(a);
        const X = x * Math.cos(t) - y * Math.sin(t), Y = x * Math.sin(t) + y * Math.cos(t);
        const front = Math.sin(a) >= 0;
        it.n.style.transform = `translate3d(${((vw / 2 + X) * scale).toFixed(1)}px, ${((vh / 2 + Y) * scale).toFixed(1)}px, 0) translate(-50%, -50%) scale(${front ? 1 : 0.92})`;
        it.n.style.zIndex = front ? 3 : 1;
        it.n.classList.toggle("back", !front);
      }
    };
    let visible = false, raf = 0, last = performance.now(), secs = 0;
    const rate = reduce ? 0.5 : 1;
    resize();
    addEventListener("resize", () => { resize(); place(secs); });
    place(0);
    el.classList.add("ready");
    const loop = (now) => {
      secs += Math.min((now - last) / 1000, 0.1) * rate;
      last = now;
      place(secs);
      raf = visible ? requestAnimationFrame(loop) : 0;
    };
    new IntersectionObserver((es) => es.forEach((e) => {
      visible = e.isIntersecting;
      if (visible && !raf) { last = performance.now(); raf = requestAnimationFrame(loop); }
    })).observe(el);
  });

  /* ---- Steps that light up in turn ---- */
  document.querySelectorAll("[data-cycle]").forEach((wrap) => {
    const items = [...wrap.children];
    if (!items.length) return;
    let i = 0;
    onVisible(wrap, () => {
      const go = () => { items.forEach((x, j) => { x.classList.toggle("active", j === i % items.length); x.classList.toggle("past", j < i % items.length); }); i++; };
      go(); setInterval(go, 2600);
    });
  });

  /* ---- Code windows that type themselves out ---- */
  document.querySelectorAll("[data-type]").forEach((w) => {
    const lines = splitLines(w.querySelector("pre code"));
    const r = w.getBoundingClientRect();
    if (r.top < innerHeight * 0.8) return;
    w.classList.add("is-animated");
    onVisible(w, async () => {
      await sleep(250);
      for (const l of lines) { l.classList.add("on", "cur"); await sleep(95); l.classList.remove("cur"); }
    });
  });

  /* ---- Support chat ---- */
  document.querySelectorAll("[data-chat]").forEach((c) => {
    const msgs = [...c.querySelectorAll(".msg")];
    const typing = c.querySelector(".typing");
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
    if (codes.length < 2) return;
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
    onVisible(d, () => setInterval(() => add(false), 2300));
  });

  /* ---- "How it works" diagrams (TradeFlo, CareFlo): step through examples. Each example lights parts by
     their data-on key in three beats: where it comes from (a), the middle with its label (m), where it goes (b). ---- */
  document.querySelectorAll("[data-tf]").forEach((tf) => {
    const ex = JSON.parse(tf.dataset.ex);
    const a = tf.querySelector("[data-a]"), b = tf.querySelector("[data-b]"), say = tf.querySelector(".tf-say");
    const light = (keys) => keys.forEach((k) => tf.querySelectorAll(`[data-on="${k}"]`).forEach((x) => x.classList.add("on")));
    const show = (e, animate) => {
      tf.querySelectorAll(".on").forEach((x) => x.classList.remove("on"));
      light(e.a);
      const middle = () => { a.textContent = e.pair[0]; b.textContent = e.pair[1]; say.textContent = e.say; light(e.m); };
      if (!animate) { middle(); return light(e.b); }
      say.classList.add("fade");
      setTimeout(() => { tf.classList.remove("go"); void tf.offsetWidth; tf.classList.add("go"); middle(); say.classList.remove("fade"); }, 600);
      setTimeout(() => light(e.b), 1300);
    };
    show(ex[0], false);
    let i = 0;
    onVisible(tf, () => setInterval(() => show(ex[++i % ex.length], true), 4200));
  });

  /* ---- Without NexFlo / With NexFlo (home). The buttons switch the map. While it's on screen it also switches
     by itself, with a thin bar under the other button counting down, until the visitor clicks, taps or tabs into
     it; a mouse resting on it pauses the countdown. Off screen, every animation in it stops. ---- */
  document.querySelectorAll("[data-vs]").forEach((vs) => {
    const tabs = [...vs.querySelectorAll('[role="tab"]')];
    const panel = vs.querySelector('[role="tabpanel"]');
    const hold = { without: reduce ? 8000 : 5500, with: reduce ? 11000 : 8000 };
    let state = vs.dataset.state || "without", auto = true, visible = false, hovered = false, timer = 0;
    const apply = () => {
      vs.dataset.state = state;
      tabs.forEach((t) => {
        const on = t.dataset.state === state;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        if (on) panel.setAttribute("aria-labelledby", t.id);
      });
      vs.querySelectorAll("[data-when]").forEach((el) => el.setAttribute("aria-hidden", String(el.dataset.when !== state)));
    };
    const schedule = () => {
      clearTimeout(timer);
      vs.classList.remove("tick");
      if (!auto || !visible || hovered) return;
      vs.style.setProperty("--hold", `${hold[state]}ms`);
      void vs.offsetWidth; // restart the countdown bar
      vs.classList.add("tick");
      timer = setTimeout(() => { state = state === "with" ? "without" : "with"; apply(); schedule(); }, hold[state]);
    };
    const stop = () => { auto = false; vs.classList.remove("is-auto"); schedule(); };
    /* "See it for": the same map for a TradeFlo or a CareFlo business. Picking one doesn't stop the auto-switch;
       it starts the story again from "without". ?product=careflo opens on CareFlo. */
    const auds = [...vs.querySelectorAll("[data-aud]")];
    const setAud = (a, animate) => {
      vs.dataset.for = a;
      auds.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.aud === a)));
      if (!animate) return;
      vs.classList.remove("aud-swap");
      void vs.offsetWidth;
      vs.classList.add("aud-swap");
      if (auto) { state = "without"; apply(); schedule(); }
    };
    auds.forEach((b) => b.addEventListener("click", () => setAud(b.dataset.aud, true)));
    const wanted = (new URLSearchParams(location.search).get("product") || "").toLowerCase().replace(/flo$/, "");
    if (auds.some((b) => b.dataset.aud === wanted)) setAud(wanted, false);
    tabs.forEach((t, k) => {
      t.addEventListener("click", () => { state = t.dataset.state; apply(); stop(); });
      t.addEventListener("keydown", (e) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) return;
        e.preventDefault();
        const n = e.key === "Home" ? 0 : e.key === "End" ? tabs.length - 1 : (k + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
        tabs[n].focus();
        tabs[n].click();
      });
    });
    vs.querySelector('[role="tablist"]').addEventListener("focusin", stop);
    vs.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") { hovered = true; schedule(); } });
    vs.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") { hovered = false; schedule(); } });
    vs.classList.add("is-auto");
    apply();
    if (!("IntersectionObserver" in window)) { visible = true; return schedule(); }
    new IntersectionObserver((es) => es.forEach((e) => {
      vs.classList.toggle("is-paused", !e.isIntersecting);
      const now = e.intersectionRatio >= 0.3;
      if (now !== visible) { visible = now; schedule(); }
    }), { threshold: [0, 0.3] }).observe(panel);
  });

  /* ---- Code tabs ---- */
  document.querySelectorAll("[data-tabs]").forEach((w) => {
    const tabs = [...w.querySelectorAll('[role="tab"]')];
    const panes = [...w.querySelectorAll('[role="tabpanel"]')];
    const select = (k) => {
      tabs.forEach((x, j) => { x.setAttribute("aria-selected", String(j === k)); x.tabIndex = j === k ? 0 : -1; });
      panes.forEach((p, j) => { p.hidden = j !== k; });
    };
    tabs.forEach((b, k) => {
      b.addEventListener("click", () => select(k));
      b.addEventListener("keydown", (e) => {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        const n = (k + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
        select(n); tabs[n].focus();
      });
    });
    const want = new URLSearchParams(location.search).get("product");
    const idx = want ? tabs.findIndex((t) => t.textContent.trim().toLowerCase() === want.toLowerCase()) : -1;
    select(idx > -1 ? idx : 0);
  });
})();
