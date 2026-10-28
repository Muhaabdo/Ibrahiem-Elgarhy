/* VIBE Real Estate — project landing pages.
   Lead flow: CTA -> form -> Google Sheet -> /thank-you -> WhatsApp.
   Every step pushes a dataLayer event so GTM/GA4 can build the funnel:
   cta_click -> form_open -> form_start -> (form_error) -> generate_lead -> thank_you_view -> whatsapp_redirect */
(function () {
  "use strict";
  var CFG = window.VIBE || {};
  var LANG = CFG.lang || "ar";
  var T = CFG.t || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var RTL = document.documentElement.dir === "rtl";
  var DESKTOP = !!(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches);

  /* ---------------- Tracking ---------------- */
  window.dataLayer = window.dataLayer || [];
  function track(event, params) {
    var p = { event: event, project: CFG.project || "", page_lang: LANG };
    for (var k in params || {}) p[k] = params[k];
    window.dataLayer.push(p);
  }

  /* ---------------- Attribution (gclid / gbraid / wbraid / utm_*) ----------------
     Captured the first time they appear in the URL and kept for 90 days, so a visitor who
     browses to another project page (or comes back later) is still attributed. */
  var ATTR_KEYS = ["gclid", "gbraid", "wbraid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"];
  var ATTR_STORE = "vibe_attr", ATTR_TTL = 90 * 864e5;
  function readAttr() {
    try {
      var o = JSON.parse(localStorage.getItem(ATTR_STORE) || "{}");
      if (o._ts && Date.now() - o._ts > ATTR_TTL) return {};
      return o;
    } catch (e) { return {}; }
  }
  (function captureAttr() {
    var q = new URLSearchParams(location.search), o = readAttr(), hit = false;
    ATTR_KEYS.forEach(function (k) { var v = q.get(k); if (v) { o[k] = v; hit = true; } });
    if (!o.landing) { o.landing = location.pathname; o.referrer = document.referrer || ""; hit = true; }
    if (hit) { o._ts = Date.now(); try { localStorage.setItem(ATTR_STORE, JSON.stringify(o)); } catch (e) {} }
  })();

  /* ---------------- Nav ---------------- */
  var nav = $(".nav");
  if (nav) {
    var burger = $(".nav-burger", nav);
    if (burger) burger.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    $$(".nav-links a", nav).forEach(function (a) { a.addEventListener("click", function () { nav.classList.remove("is-open"); }); });
    var lastY = window.scrollY, ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY;
        if (!nav.classList.contains("is-open")) nav.classList.toggle("is-hidden", y > lastY && y > 400);
        lastY = y; ticking = false;
      });
    }, { passive: true });
  }

  /* ---------------- Cookie notice: once per session, auto-hides, no tracking ---------------- */
  var ck = $("#ck");
  if (ck) {
    var seen = false;
    try { seen = sessionStorage.getItem("vibe_ck") === "1"; } catch (e) {}
    if (!seen) {
      var hideCk = function () { ck.classList.add("hide"); try { sessionStorage.setItem("vibe_ck", "1"); } catch (e) {} };
      setTimeout(function () { ck.classList.remove("hide"); }, 900);
      setTimeout(hideCk, 8900);
      $$("[data-ck-close]", ck).forEach(function (b) { b.addEventListener("click", hideCk); });
    }
  }

  /* ---------------- Carousels (scroll-snap based, so touch swipe is native) ---------------- */
  function stepOf(track) {
    var first = track.children[0];
    if (!first) return track.clientWidth;
    var gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap) || 0;
    return first.getBoundingClientRect().width + gap;
  }
  function pos(track) { return Math.abs(track.scrollLeft); }
  function scrollToPos(track, x) { track.scrollTo({ left: RTL ? -x : x, behavior: "smooth" }); }

  $$(".car").forEach(function (car) {
    var track = $(".car-track", car), prev = $(".car-btn.prev", car), next = $(".car-btn.next", car), dotsBox = $(".car-dots", car);
    if (!track) return;
    var n = track.children.length, dots = [];
    function index() { return Math.round(pos(track) / stepOf(track)); }
    function maxPos() { return track.scrollWidth - track.clientWidth; }
    function sync() {
      var i = index();
      dots.forEach(function (d, k) { d.classList.toggle("on", k === i); });
      if (prev) prev.disabled = pos(track) < 4;
      if (next) next.disabled = pos(track) > maxPos() - 4;
    }
    if (dotsBox) {
      for (var i = 0; i < n; i++) (function (k) {
        var b = document.createElement("button");
        b.type = "button"; b.setAttribute("aria-label", String(k + 1));
        b.addEventListener("click", function () { scrollToPos(track, k * stepOf(track)); });
        dotsBox.appendChild(b); dots.push(b);
      })(i);
    }
    if (prev) prev.addEventListener("click", function () { scrollToPos(track, Math.max(0, pos(track) - stepOf(track))); });
    if (next) next.addEventListener("click", function () { scrollToPos(track, Math.min(maxPos(), pos(track) + stepOf(track))); });
    var t; track.addEventListener("scroll", function () { clearTimeout(t); t = setTimeout(sync, 60); }, { passive: true });
    window.addEventListener("resize", sync);
    sync();
  });

  /* Mini galleries inside cards */
  $$(".card-media").forEach(function (media) {
    var mini = $(".mini", media); if (!mini) return;
    var imgs = mini.children.length, dotsBox = $(".mini-dots", media), dots = [];
    if (imgs < 2) return;
    for (var i = 0; i < imgs; i++) { var d = document.createElement("i"); dotsBox.appendChild(d); dots.push(d); }
    function idx() { return Math.round(pos(mini) / mini.clientWidth); }
    function sync() { var k = idx(); dots.forEach(function (d, j) { d.classList.toggle("on", j === k); }); }
    function go(dir) { var k = (idx() + dir + imgs) % imgs; scrollToPos(mini, k * mini.clientWidth); }
    var p = $(".mini-nav.prev", media), nx = $(".mini-nav.next", media);
    if (p) p.addEventListener("click", function () { go(-1); });
    if (nx) nx.addEventListener("click", function () { go(1); });
    var t; mini.addEventListener("scroll", function () { clearTimeout(t); t = setTimeout(sync, 60); }, { passive: true });
    sync();
  });

  /* ---------------- Lightbox (swipe + arrows + Esc) ---------------- */
  (function () {
    var items = $$("[data-lb]"); if (!items.length) return;
    var lb = document.createElement("div");
    lb.className = "lb"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true");
    lb.innerHTML = '<button class="lb-x" type="button" aria-label="' + (T.close || "Close") + '">' + icon("x") + '</button>' +
      '<button class="lb-nav prev" type="button" aria-label="prev">' + icon(RTL ? "chev-r" : "chev-l") + '</button>' +
      '<img alt=""><button class="lb-nav next" type="button" aria-label="next">' + icon(RTL ? "chev-l" : "chev-r") + '</button>' +
      '<div class="lb-cap"></div>';
    document.body.appendChild(lb);
    var img = $("img", lb), cap = $(".lb-cap", lb), cur = 0, group = [];
    function show(i) {
      cur = (i + group.length) % group.length;
      img.src = group[cur].getAttribute("data-lb"); cap.textContent = group[cur].getAttribute("data-cap") || "";
      var multi = group.length > 1;
      $$(".lb-nav", lb).forEach(function (b) { b.style.display = multi ? "" : "none"; });
    }
    function close() { lb.classList.remove("on"); document.body.style.overflow = ""; }
    items.forEach(function (el) {
      el.addEventListener("click", function () {
        var g = el.getAttribute("data-lb-group") || "";
        group = items.filter(function (x) { return (x.getAttribute("data-lb-group") || "") === g; });
        show(group.indexOf(el)); lb.classList.add("on"); document.body.style.overflow = "hidden";
      });
    });
    $(".lb-x", lb).addEventListener("click", close);
    $(".lb-nav.prev", lb).addEventListener("click", function () { show(cur - 1); });
    $(".lb-nav.next", lb).addEventListener("click", function () { show(cur + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("on")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(cur + (RTL ? 1 : -1));
      if (e.key === "ArrowRight") show(cur + (RTL ? -1 : 1));
    });
    var sx = null;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (sx === null) return;
      var dx = e.changedTouches[0].clientX - sx; sx = null;
      if (Math.abs(dx) < 45) return;
      var fwd = dx < 0; if (RTL) fwd = !fwd;
      show(cur + (fwd ? 1 : -1));
    });
  })();

  function icon(name) { return '<svg class="ic" aria-hidden="true"><use href="/assets/img/icons.svg#i-' + name + '"></use></svg>'; }

  /* ---------------- Countries + phone validation ---------------- */
  var COUNTRIES = [], PRIORITY = 0;
  (function parseCountries() {
    var raw = (window.VIBE_COUNTRIES || "EG:20:10:10").split("|");
    var names; try { names = new Intl.DisplayNames([LANG], { type: "region" }); } catch (e) { names = null; }
    raw.forEach(function (chunk, ci) {
      var list = chunk.split(",").filter(Boolean).map(function (s) {
        var p = s.split(":"), name = p[0];
        try { if (names) name = names.of(p[0]) || p[0]; } catch (e) {}
        return { iso: p[0], dial: p[1], min: +(p[2] || 6), max: +(p[3] || p[2] || 12), name: name };
      });
      if (ci === 0) PRIORITY = list.length;
      else list.sort(function (a, b) { return a.name.localeCompare(b.name, LANG); });
      COUNTRIES = COUNTRIES.concat(list);
    });
  })();
  function countryByIso(iso) { for (var i = 0; i < COUNTRIES.length; i++) if (COUNTRIES[i].iso === iso) return COUNTRIES[i]; return COUNTRIES[0]; }
  function toLatinDigits(s) {
    return String(s).replace(/[٠-٩]/g, function (d) { return d.charCodeAt(0) - 0x0660; })
                    .replace(/[۰-۹]/g, function (d) { return d.charCodeAt(0) - 0x06F0; });
  }
  /* Returns {ok, e164, country, national}. Accepts "010…", "10…", "+2010…", "002010…". */
  function parsePhone(raw, country) {
    var s = toLatinDigits(raw).trim(), intl = /^(\+|00)/.test(s), d = s.replace(/\D/g, "");
    if (intl) {
      d = d.replace(/^00/, "");
      var best = null;
      COUNTRIES.forEach(function (c) { if (d.indexOf(c.dial) === 0 && (!best || c.dial.length > best.dial.length)) best = c; });
      if (best) { if (best.dial !== country.dial) country = best; d = d.slice(best.dial.length); }
    } else if (d.indexOf(country.dial) === 0 && d.length > country.max) {
      d = d.slice(country.dial.length);
    }
    d = d.replace(/^0+/, "");
    var ok = country.iso === "EG" ? /^1[0125]\d{8}$/.test(d) : (d.length >= country.min && d.length <= country.max);
    if (/^(\d)\1+$/.test(d)) ok = false;
    return { ok: ok, e164: "+" + country.dial + d, country: country, national: d };
  }

  /* ---------------- Lead forms ---------------- */
  var ctx = { unit: "", loc: "", started: false };

  function setupForm(form) {
    var phWrap = $(".ph", form), ccBtn = $(".ph-cc", form), pop = $(".cc-pop", form), list = $(".cc-list", form),
        search = $(".cc-search input", form), tel = $('input[type="tel"]', form), nameEl = $('input[name="name"]', form),
        unitEl = $('select[name="unit"]', form), submit = $(".lf-submit", form);
    var country = countryByIso("EG"), built = false;

    function setCountry(c) {
      country = c;
      $("img", ccBtn).src = "/assets/img/flags/" + c.iso + ".svg";
      $("img", ccBtn).alt = c.name;
      $("b", ccBtn).textContent = "+" + c.dial;
      tel.placeholder = c.iso === "EG" ? "10 1234 5678" : "";
    }
    function render(filter) {
      var f = (filter || "").trim().toLowerCase().replace(/^\+/, ""), html = "", n = 0;
      COUNTRIES.forEach(function (c, i) {
        if (f && c.name.toLowerCase().indexOf(f) < 0 && c.dial.indexOf(f) !== 0 && c.iso.toLowerCase() !== f) return;
        if (!f && i === PRIORITY) html += '<div style="height:1px;background:var(--line);margin:4px 0"></div>';
        html += '<button type="button" class="cc-opt" data-iso="' + c.iso + '"><img loading="lazy" width="24" height="16" alt="" src="/assets/img/flags/' +
          c.iso + '.svg"><span>' + c.name + '</span><b>+' + c.dial + '</b></button>';
        n++;
      });
      list.innerHTML = n ? html : '<div class="cc-empty">' + (T.noCountry || "—") + '</div>';
    }
    function openPop() { if (!built) { render(""); built = true; } pop.classList.add("on"); ccBtn.setAttribute("aria-expanded", "true"); setTimeout(function () { search.focus(); }, 30); }
    function closePop() { pop.classList.remove("on"); ccBtn.setAttribute("aria-expanded", "false"); }
    ccBtn.addEventListener("click", function () { pop.classList.contains("on") ? closePop() : openPop(); });
    search.addEventListener("input", function () { render(search.value); });
    search.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); var f = $(".cc-opt", list); if (f) f.click(); } if (e.key === "Escape") closePop(); });
    list.addEventListener("click", function (e) {
      var b = e.target.closest(".cc-opt"); if (!b) return;
      setCountry(countryByIso(b.getAttribute("data-iso"))); closePop(); search.value = ""; built = false; tel.focus();
    });
    document.addEventListener("click", function (e) { if (!phWrap.contains(e.target)) closePop(); });
    setCountry(country);

    function fieldBox(el) { return el.closest(".lf-f"); }
    function mark(el, bad) { var b = fieldBox(el); if (b) b.classList.toggle("bad", !!bad); }
    [nameEl, tel, unitEl].forEach(function (el) {
      if (!el) return;
      el.addEventListener("input", function () {
        mark(el, false);
        if (!form._started) { form._started = true; track("form_start", { form_location: form.getAttribute("data-loc") || ctx.loc, unit_type: currentUnit() }); }
      });
      el.addEventListener("change", function () { mark(el, false); });
    });
    /* typing a full international number switches the country automatically */
    tel.addEventListener("blur", function () {
      if (/^\s*(\+|00|٠٠)/.test(tel.value)) { var r = parsePhone(tel.value, country); if (r.country !== country) { setCountry(r.country); tel.value = r.national; } }
    });

    function currentUnit() {
      if (unitEl && fieldBox(unitEl).style.display !== "none") return unitEl.value || "";
      return form._unit || "";
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form._sending) return;
      var name = nameEl.value.replace(/\s+/g, " ").trim(), errs = [];
      var nameOk = name.length >= 2 && !/\d/.test(toLatinDigits(name)) && /[A-Za-z؀-ۿ]/.test(name);
      mark(nameEl, !nameOk); if (!nameOk) errs.push("name");
      var ph = parsePhone(tel.value, country);
      mark(tel, !ph.ok); if (!ph.ok) errs.push("phone");
      var unit = currentUnit(), unitVisible = unitEl && fieldBox(unitEl).style.display !== "none";
      if (unitVisible) { mark(unitEl, !unit); if (!unit) errs.push("unit"); }
      var loc = form.getAttribute("data-loc") || ctx.loc;
      if (errs.length) {
        track("form_error", { form_location: loc, error_fields: errs.join(","), unit_type: unit });
        var firstBad = $(".bad input, .bad select", form); if (firstBad) firstBad.focus();
        return;
      }
      if (ph.country !== country) setCountry(ph.country);
      if ($('input[name="website"]', form).value) return; /* honeypot */

      form._sending = true; submit.disabled = true; $("span", submit).textContent = T.sending || "…";
      var a = readAttr();
      var project = CFG.project || "";
      if (CFG.pickProject) { project = unit === "Not sure" ? "" : unit; unit = ""; }   /* home page: the select chooses the project */
      var lead = {
        name: name, phone: ph.e164, country: ph.country.iso, project: project, unit: unit,
        page: location.origin + location.pathname, lang: LANG, cta: loc,
        gclid: a.gclid || "", gbraid: a.gbraid || "", wbraid: a.wbraid || "",
        utm_source: a.utm_source || "", utm_medium: a.utm_medium || "", utm_campaign: a.utm_campaign || "",
        utm_term: a.utm_term || "", utm_content: a.utm_content || "",
        landing: a.landing || "", referrer: a.referrer || ""
      };
      track("generate_lead", { form_location: loc, unit_type: unit, phone_country: ph.country.iso, project: project });

      /* Desktop: WhatsApp opens in a NEW tab and this tab goes to the thank-you page, so the visitor
         gets WhatsApp with no extra click and the thank-you page is still there when they come back.
         A new tab is only allowed during the click itself, so it is opened blank now and pointed at
         WhatsApp once the lead is stored. If the browser blocks it, the thank-you page offers a button.
         Phones keep the same-tab flow: WhatsApp opens as an app and the browser stays on the page. */
      var waTab = null;
      if (DESKTOP && CFG.wa) {
        try {
          waTab = window.open("", "_blank");
          if (waTab) waTab.document.write('<!doctype html><meta charset="utf-8"><title>WhatsApp</title><body style="margin:0;display:flex;align-items:center;justify-content:center;height:100vh;font:16px system-ui;background:#092A21;color:#E4CE9E">' + (T.sending || "…") + "</body>");
        } catch (err) { waTab = null; }
      }
      function done() {
        var opened = false;
        if (waTab && !waTab.closed) {
          var msg = project ? (T.waMsg || "").replace("{p}", project).replace("{u}", unit ? " (" + unit + ")" : "") : (T.waMsgGeneric || "");
          try { waTab.location.href = "https://wa.me/" + CFG.wa + "?text=" + encodeURIComponent(msg); opened = true; } catch (err) {}
        }
        try {
          sessionStorage.setItem("vibe_lead", JSON.stringify({
            project: project, unit: unit, lang: LANG, cta: loc,
            back: location.pathname + location.search, backTitle: CFG.backTitle || project, ts: Date.now(),
            redirected: opened, newTab: opened
          }));
        } catch (err) {}
        if (opened) track("whatsapp_redirect", { method: "new_tab", unit_type: unit, project: project, form_location: loc });
        location.href = CFG.thankYou || "/thank-you";
      }
      if (!CFG.endpoint) { console.warn("[VIBE] No leads endpoint configured — lead not stored:", lead); return done(); }
      var finished = false, finish = function () { if (!finished) { finished = true; done(); } };
      setTimeout(finish, 4000);
      try {
        fetch(CFG.endpoint, { method: "POST", mode: "no-cors", keepalive: true, headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(lead) })
          .then(finish, finish);
      } catch (err) { finish(); }
    });

    form._setUnit = function (unit) {
      form._unit = unit || "";
      if (unitEl) { fieldBox(unitEl).style.display = unit ? "none" : ""; if (!unit) unitEl.value = ""; }
    };
    form._reset = function () { form._started = false; $$(".bad", form).forEach(function (b) { b.classList.remove("bad"); }); };
  }
  $$("form.lf").forEach(setupForm);

  /* Re-enable forms when the page is restored from the back/forward cache */
  window.addEventListener("pageshow", function (e) {
    if (!e.persisted) return;
    $$("form.lf").forEach(function (f) { f._sending = false; var s = $(".lf-submit", f); s.disabled = false; $("span", s).textContent = T.submit || ""; });
  });

  /* ---------------- Modal ---------------- */
  var modal = $("#leadModal"), modalForm = modal && $("form.lf", modal), lastFocus = null;
  function openModal(loc, unit) {
    if (!modal) return;
    ctx.loc = loc; ctx.unit = unit || "";
    modalForm.setAttribute("data-loc", loc);
    modalForm._setUnit(unit || ""); modalForm._reset();
    var tag = $(".modal-ctx", modal);
    tag.textContent = (CFG.projectName || "") + (unit ? " · " + unit : "");
    lastFocus = document.activeElement;
    modal.classList.add("on"); document.body.style.overflow = "hidden";
    track("form_open", { form_location: loc, unit_type: unit || "" });
    setTimeout(function () { var n = $('input[name="name"]', modalForm); if (n) n.focus({ preventScroll: true }); }, 80);
  }
  function closeModal() {
    if (!modal || !modal.classList.contains("on")) return;
    modal.classList.remove("on"); document.body.style.overflow = "";
    track("form_close", { form_location: ctx.loc, unit_type: ctx.unit, form_started: !!modalForm._started });
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  if (modal) {
    $$("[data-modal-close]", modal).forEach(function (b) { b.addEventListener("click", closeModal); });
    modal.addEventListener("mousedown", function (e) { if (e.target === modal) closeModal(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });
  }

  /* Every CTA: <a|button data-cta="hero" data-unit="…"> */
  $$("[data-cta]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      e.preventDefault();
      var loc = el.getAttribute("data-cta"), unit = el.getAttribute("data-unit") || "";
      track("cta_click", { cta_location: loc, unit_type: unit, cta_text: (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 60) });
      openModal(loc, unit);
    });
  });
  /* Inline (final) form counts as "open" the first time it scrolls into view */
  $$("form.lf[data-inline]").forEach(function (f) {
    if (!("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (en) {
      if (en[0].isIntersecting) { track("form_open", { form_location: f.getAttribute("data-loc"), unit_type: "" }); io.disconnect(); }
    }, { threshold: 0.5 });
    io.observe(f);
  });
  $$("[data-track]").forEach(function (el) {
    el.addEventListener("click", function () { track(el.getAttribute("data-track"), { link_location: el.getAttribute("data-loc") || "", target: el.getAttribute("data-target") || "" }); });
  });

  /* ---------------- Mobile sticky CTA: appears after the hero ---------------- */
  var stick = $(".stick"), hero = $(".hero");
  if (stick && hero && "IntersectionObserver" in window) {
    document.body.classList.add("has-stick");
    var finalForm = $("#contact");
    var heroOut = false, finalIn = false;
    var upd = function () { stick.classList.toggle("on", heroOut && !finalIn); };
    new IntersectionObserver(function (en) { heroOut = !en[0].isIntersecting; upd(); }, { threshold: 0.05 }).observe(hero);
    if (finalForm) new IntersectionObserver(function (en) { finalIn = en[0].isIntersecting; upd(); }, { threshold: 0.25 }).observe(finalForm);
  }

  var y = $("#year"); if (y) y.textContent = new Date().getFullYear();
})();
