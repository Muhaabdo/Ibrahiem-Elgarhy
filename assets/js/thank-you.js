/* Thank-you page.
   - Fires `thank_you_view` ONCE per submitted lead (this is the Google Ads conversion trigger).
     A refresh, a direct visit, or coming back from WhatsApp never fires it again.
   - Sends the visitor on to WhatsApp automatically, once, after a short delay that gives the
     conversion tag time to fire. The visible button is the fallback (some iPhones need a tap). */
(function () {
  "use strict";
  var CFG = window.VIBE || {}, T = CFG.t || {};
  var REDIRECT_MS = 1800;
  var $ = function (s) { return document.querySelector(s); };
  window.dataLayer = window.dataLayer || [];

  var lead = null;
  try { lead = JSON.parse(sessionStorage.getItem("vibe_lead") || "null"); } catch (e) {}
  function save() { try { sessionStorage.setItem("vibe_lead", JSON.stringify(lead)); } catch (e) {} }

  var label = lead ? (lead.project + (lead.unit ? " · " + lead.unit : "")) : "";
  var msg = lead && lead.project ? (T.waMsg || "").replace("{p}", lead.project).replace("{u}", lead.unit ? " (" + lead.unit + ")" : "") : (T.waMsgGeneric || "");
  var waUrl = "https://wa.me/" + CFG.wa + "?text=" + encodeURIComponent(msg);

  var btn = $("#tyWa"), back = $("#tyBack"), ctx = $("#tyCtx"), count = $("#tyCount"), bar = $("#tyBar");
  btn.href = waUrl;
  if (lead && lead.back && lead.back.charAt(0) === "/" && lead.back.charAt(1) !== "/") {
    back.href = lead.back;
    $("#tyBackText").textContent = (T.backTo || "").replace("{p}", lead.backTitle || lead.project);
  }
  if (label) { ctx.textContent = label; ctx.hidden = false; }

  function push(event, extra) {
    var p = { event: event, project: lead ? lead.project : "", unit_type: lead ? lead.unit : "", page_lang: CFG.lang, form_location: lead ? lead.cta : "" };
    for (var k in extra || {}) p[k] = extra[k];
    window.dataLayer.push(p);
  }

  btn.addEventListener("click", function () {
    cancel(); btn.classList.remove("pulse");
    if (lead) { lead.redirected = true; save(); }
    push("whatsapp_redirect", { method: "button" });
  });

  var timer = null;
  function cancel() { if (timer) { clearTimeout(timer); timer = null; } count.textContent = ""; bar.hidden = true; }

  if (!lead) { $("#tyTitle").textContent = T.titleGeneric || ""; $("#tyText").textContent = T.textGeneric || ""; $("#tyPoints").hidden = true; bar.hidden = true; return; }
  if (lead.project && T.titleProject) $("#tyTitle").textContent = T.titleProject.replace("{p}", lead.project);

  if (!lead.confirmed) { lead.confirmed = true; save(); push("thank_you_view"); }

  /* Desktop: WhatsApp goes to a NEW tab so this page stays open. Browsers only allow a new tab
     that follows a click, so the automatic attempt is usually blocked — then the page simply
     stays here and the button (a real click) opens WhatsApp in a new tab.
     Phones: same-tab redirect; WhatsApp opens as an app and the browser stays on this page. */
  var DESKTOP = !!(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches);
  if (DESKTOP) btn.target = "_blank";
  if (lead.newTab) count.textContent = T.openedNewTab || "";

  if (!lead.redirected) {
    count.textContent = T.redirecting || "";
    bar.querySelector("i").style.transitionDuration = REDIRECT_MS + "ms";
    requestAnimationFrame(function () { bar.classList.add("run"); });
    timer = setTimeout(function () {
      timer = null;
      lead.redirected = true; save();
      bar.hidden = true;
      if (DESKTOP) {
        var w = null;
        try { w = window.open(waUrl, "_blank"); } catch (e) {}
        if (w) { push("whatsapp_redirect", { method: "auto_new_tab" }); count.textContent = T.openedNewTab || ""; }
        else { count.textContent = T.clickToOpen || ""; btn.classList.add("pulse"); }
      } else {
        push("whatsapp_redirect", { method: "auto" });
        count.textContent = T.notOpened || "";
        window.location.href = waUrl;
      }
    }, REDIRECT_MS);
  } else {
    bar.hidden = true;
  }
})();
