/* ==========================================================================
   ASSURIX DASHBOARD  ·  assurix-dashboard.js   (loaded with defer, after Chart.js)

   Draws three charts from the JSON block #axChartData (Django json_script):
     contracts_over_time · claims_by_status · payments
   - Colors come from the CSS tokens (--ax-chart-*), so light/dark just work.
   - Charts are rebuilt when the theme changes ("assurix:themechange").
   - States: loading (skeleton) · empty (no data) · error (Chart.js missing or failure).
   - The chart data is whatever the view provides: demo data today, real data later.
   ========================================================================== */
(function () {
  "use strict";

  var doc = document;
  var charts = {};
  var data = null;

  function qs(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function css(name) { return getComputedStyle(doc.documentElement).getPropertyValue(name).trim(); }
  function nf(value) { return new Intl.NumberFormat("fr-FR").format(value); }

  /* ---------- state overlays (loading / empty / error) ---------- */
  function setState(key, kind, message) {
    var box = qs('[data-ax-chart="' + key + '"]');
    if (!box) return;
    var state = qs("[data-ax-chart-state]", box);
    var canvas = qs("canvas", box);
    if (!state) return;
    if (!kind) { state.hidden = true; state.innerHTML = ""; if (canvas) canvas.style.visibility = ""; return; }
    state.hidden = false;
    if (canvas) canvas.style.visibility = "hidden";
    if (kind === "loading") {
      state.innerHTML = '<span class="ax-skeleton" style="width:88%;height:78%" aria-hidden="true"></span><span class="ax-sr-only">Chargement du graphique</span>';
    } else if (kind === "empty") {
      state.innerHTML = '<div class="ax-empty" style="padding:1rem"><span class="ax-empty__icon"><i class="bi bi-bar-chart" aria-hidden="true"></i></span>' +
        '<h3 class="ax-empty__title">Pas encore de données</h3><p class="ax-empty__text">' + (message || "Ce graphique s'affichera dès que des données seront disponibles.") + "</p></div>";
    } else {
      state.innerHTML = '<div class="ax-alert ax-alert--danger" role="alert" style="max-width:26rem"><i class="bi bi-x-octagon ax-alert__icon" aria-hidden="true"></i>' +
        '<div class="ax-alert__body"><p class="ax-alert__title">Graphique indisponible</p><p>' + (message || "Une erreur est survenue lors de l'affichage.") + "</p></div></div>";
    }
  }

  function describe(canvas, label, labels, values, unit) {
    var parts = labels.map(function (l, i) { return l + " : " + nf(values[i]) + (unit || ""); });
    canvas.setAttribute("aria-label", label + ". " + parts.join(", ") + ".");
  }

  function hasValues(arr) { return Array.isArray(arr) && arr.some(function (v) { return Number(v) > 0; }); }

  function baseOptions() {
    var text = css("--ax-text-3");
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? false : { duration: 500 },
      font: { family: css("--ax-font-sans") || "system-ui" },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: css("--ax-navy-900") || "#0a1730", titleColor: "#fff", bodyColor: "#dbe4f5",
          padding: 10, cornerRadius: 8, boxPadding: 4, displayColors: true
        }
      },
      scales: {
        x: { grid: { display: false }, border: { display: false }, ticks: { color: text, font: { size: 12 } } },
        y: { beginAtZero: true, grid: { color: css("--ax-chart-grid") }, border: { display: false }, ticks: { color: text, font: { size: 12 }, maxTicksLimit: 5 } }
      }
    };
  }

  function destroyAll() {
    Object.keys(charts).forEach(function (k) { if (charts[k]) charts[k].destroy(); });
    charts = {};
  }

  /* ---------- individual charts ---------- */
  function drawContracts() {
    var d = data.contracts_over_time;
    var canvas = qs("#chartContracts");
    if (!canvas || !d || !hasValues(d.values)) { setState("contracts", "empty"); return; }
    describe(canvas, "Contrats créés par mois", d.labels, d.values);
    var line = css("--ax-chart-1");
    var ctx = canvas.getContext("2d");
    var fill = ctx.createLinearGradient(0, 0, 0, canvas.parentElement.clientHeight || 280);
    fill.addColorStop(0, hexToRgba(line, 0.22));
    fill.addColorStop(1, hexToRgba(line, 0));
    var opts = baseOptions();
    opts.plugins.tooltip.callbacks = { label: function (c) { return " " + nf(c.parsed.y) + " contrats"; } };
    charts.contracts = new Chart(ctx, {
      type: "line",
      data: { labels: d.labels, datasets: [{ data: d.values, borderColor: line, backgroundColor: fill, fill: true, tension: 0.35, borderWidth: 2.5,
        pointRadius: 0, pointHoverRadius: 5, pointHoverBackgroundColor: line, pointHoverBorderColor: "#fff", pointHoverBorderWidth: 2 }] },
      options: opts
    });
    setState("contracts", null);
  }

  function drawClaims() {
    var d = data.claims_by_status;
    var canvas = qs("#chartClaims");
    if (!canvas || !d || !hasValues(d.values)) { setState("claims", "empty"); return; }
    describe(canvas, "Sinistres par statut", d.labels, d.values);
    var palette = [css("--ax-chart-2"), css("--ax-chart-3"), css("--ax-chart-1"), css("--ax-chart-6"), css("--ax-chart-4"), css("--ax-chart-5")];
    var total = d.values.reduce(function (a, b) { return a + Number(b); }, 0);
    var surface = css("--ax-surface");
    var opts = baseOptions();
    delete opts.scales;
    opts.cutout = "68%";
    opts.plugins.legend = { display: true, position: "bottom", labels: { color: css("--ax-text-2"), usePointStyle: true, pointStyle: "rectRounded", boxWidth: 8, boxHeight: 8, padding: 14, font: { size: 12 } } };
    opts.plugins.tooltip.callbacks = { label: function (c) { return " " + c.label + " : " + nf(c.parsed) + " (" + Math.round(c.parsed / total * 100) + " %)"; } };
    charts.claims = new Chart(canvas.getContext("2d"), {
      type: "doughnut",
      data: { labels: d.labels, datasets: [{ data: d.values, backgroundColor: palette, borderColor: surface, borderWidth: 3, hoverOffset: 4 }] },
      options: opts
    });
    setState("claims", null);
  }

  function drawPayments() {
    var d = data.payments;
    var canvas = qs("#chartPayments");
    if (!canvas || !d || !(hasValues(d.received) || hasValues(d.pending))) { setState("payments", "empty"); return; }
    canvas.setAttribute("aria-label", "Paiements encaissés et en attente par mois, de " + d.labels[0] + " à " + d.labels[d.labels.length - 1] + ".");
    var opts = baseOptions();
    opts.plugins.legend = { display: true, position: "top", align: "end", labels: { color: css("--ax-text-2"), usePointStyle: true, pointStyle: "rectRounded", boxWidth: 8, boxHeight: 8, font: { size: 12 } } };
    opts.plugins.tooltip.callbacks = { label: function (c) { return " " + c.dataset.label + " : " + nf(c.parsed.y) + " DT"; } };
    opts.scales.x.stacked = true;
    opts.scales.y.stacked = true;
    opts.scales.y.ticks.callback = function (v) { return v >= 1000 ? nf(v / 1000) + " k" : v; };
    charts.payments = new Chart(canvas.getContext("2d"), {
      type: "bar",
      data: { labels: d.labels, datasets: [
        { label: "Encaissé", data: d.received, backgroundColor: css("--ax-chart-1"), borderRadius: 4, borderSkipped: false, maxBarThickness: 26 },
        { label: "En attente", data: d.pending, backgroundColor: css("--ax-chart-3"), borderRadius: 4, borderSkipped: false, maxBarThickness: 26 }
      ] },
      options: opts
    });
    setState("payments", null);
  }

  function hexToRgba(color, alpha) {
    var c = color.replace("#", "");
    if (c.length === 3) c = c.split("").map(function (x) { return x + x; }).join("");
    if (c.length !== 6) return "rgba(10,127,114," + alpha + ")";
    var n = parseInt(c, 16);
    return "rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," + (n & 255) + "," + alpha + ")";
  }

  /* ---------- orchestration ---------- */
  function render() {
    destroyAll();
    try {
      drawContracts();
      drawClaims();
      drawPayments();
    } catch (err) {
      ["contracts", "claims", "payments"].forEach(function (k) { setState(k, "error", "Veuillez recharger la page."); });
      if (window.console) console.error("[Assurix] chart error:", err);
    }
  }

  function init() {
    ["contracts", "claims", "payments"].forEach(function (k) { setState(k, "loading"); });

    var node = qs("#axChartData");
    try { data = node ? JSON.parse(node.textContent) : null; } catch (e) { data = null; }

    if (!data) {                       // backend provides no chart data: honest empty state
      ["contracts", "claims", "payments"].forEach(function (k) { setState(k, "empty"); });
      return;
    }
    if (typeof window.Chart === "undefined") {
      ["contracts", "claims", "payments"].forEach(function (k) { setState(k, "error", "La bibliothèque de graphiques n'a pas pu être chargée."); });
      return;
    }
    render();
    doc.addEventListener("assurix:themechange", render);
  }

  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init);
  else init();
})();
