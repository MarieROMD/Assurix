/* ==========================================================================
   ASSURIX APP  ·  assurix-app.js   (vanilla JavaScript, loaded with defer)

   Features
   1. Sidebar: desktop collapse (persisted) + mobile drawer (focus trap, Esc)
   2. Quick search: jump to a module (keyboard: "/" or Ctrl/Cmd+K, arrows, Enter)
   3. Table filters: text search + status chips, result count, "no results"
   4. Dismissible alerts
   5. "Unavailable action" modal (features without a backend yet)
   6. Client profile panel (read-only, filled from the selected row)

   Nothing here simulates saving data or authentication.
   The theme toggle lives in assurix-theme.js.
   ========================================================================== */
(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;

  function qs(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function qsa(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }
  function normalize(text) {
    return String(text || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
  }

  /* ---------------------------------------------------------------- 1. Sidebar */
  var sidebar = qs("#axSidebar");
  var scrim = qs("[data-ax-scrim]");
  var openBtn = qs("[data-ax-sidebar-open]");
  var closeBtn = qs("[data-ax-sidebar-close]");
  var collapseBtn = qs("[data-ax-sidebar-collapse]");
  var mobileQuery = window.matchMedia("(max-width: 991.98px)");
  var lastFocus = null;

  function isCollapsed() { return root.getAttribute("data-ax-sidebar") === "collapsed"; }

  function syncCollapsedUI() {
    if (!collapseBtn) return;
    var collapsed = isCollapsed();
    collapseBtn.setAttribute("aria-pressed", String(collapsed));
    collapseBtn.setAttribute("aria-label", collapsed ? "Développer le menu" : "Réduire le menu");
    // Native tooltips on icons only while the labels are hidden
    qsa(".ax-nav-link[data-ax-label]").forEach(function (link) {
      if (collapsed && !mobileQuery.matches) link.setAttribute("title", link.getAttribute("data-ax-label"));
      else link.removeAttribute("title");
    });
  }

  function setCollapsed(value) {
    if (value) root.setAttribute("data-ax-sidebar", "collapsed");
    else root.removeAttribute("data-ax-sidebar");
    try { localStorage.setItem("assurix-sidebar", value ? "collapsed" : "expanded"); } catch (e) { /* ignore */ }
    syncCollapsedUI();
  }

  function isDrawerOpen() { return sidebar && sidebar.classList.contains("is-open"); }

  function openDrawer() {
    if (!sidebar) return;
    lastFocus = doc.activeElement;
    sidebar.classList.add("is-open");
    sidebar.inert = false;
    if (scrim) scrim.classList.add("is-visible");
    doc.body.classList.add("ax-no-scroll");
    if (openBtn) openBtn.setAttribute("aria-expanded", "true");
    var first = qs(".ax-nav-link.is-active", sidebar) || qs(".ax-nav-link", sidebar);
    if (first) first.focus();
  }

  function closeDrawer(returnFocus) {
    if (!sidebar) return;
    sidebar.classList.remove("is-open");
    if (scrim) scrim.classList.remove("is-visible");
    doc.body.classList.remove("ax-no-scroll");
    if (openBtn) openBtn.setAttribute("aria-expanded", "false");
    applyInert();
    if (returnFocus !== false && lastFocus && lastFocus.focus) lastFocus.focus();
  }

  // On mobile the closed drawer must not be reachable with Tab or by screen readers
  function applyInert() {
    if (!sidebar) return;
    sidebar.inert = mobileQuery.matches && !isDrawerOpen();
  }

  function onBreakpointChange() {
    if (!mobileQuery.matches && isDrawerOpen()) closeDrawer(false);
    applyInert();
    syncCollapsedUI();
  }

  if (sidebar) {
    if (openBtn) openBtn.addEventListener("click", openDrawer);
    if (closeBtn) closeBtn.addEventListener("click", function () { closeDrawer(); });
    if (scrim) scrim.addEventListener("click", function () { closeDrawer(); });
    if (collapseBtn) collapseBtn.addEventListener("click", function () { setCollapsed(!isCollapsed()); });

    // Close the drawer after choosing a destination
    qsa(".ax-nav-link", sidebar).forEach(function (link) {
      link.addEventListener("click", function () { if (mobileQuery.matches) closeDrawer(false); });
    });

    // Focus trap + Escape while the drawer is open
    sidebar.addEventListener("keydown", function (event) {
      if (!isDrawerOpen()) return;
      if (event.key === "Escape") { event.preventDefault(); closeDrawer(); return; }
      if (event.key !== "Tab") return;
      var focusable = qsa("a[href], button:not([disabled])", sidebar).filter(function (el) { return el.offsetParent !== null; });
      if (!focusable.length) return;
      var first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && doc.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && doc.activeElement === last) { event.preventDefault(); first.focus(); }
    });

    if (mobileQuery.addEventListener) mobileQuery.addEventListener("change", onBreakpointChange);
    else if (mobileQuery.addListener) mobileQuery.addListener(onBreakpointChange);
    applyInert();
    syncCollapsedUI();
  }

  /* ---------------------------------------------------------------- 2. Quick search */
  (function initSearch() {
    var wrap = qs("#axSearch");
    var input = qs("#axSearchInput");
    var panel = qs("#axSearchPanel");
    var dataNode = qs("#axSearchItems");
    var toggle = qs("[data-ax-search-toggle]");
    if (!wrap || !input || !panel || !dataNode) return;

    var items = [];
    try { items = JSON.parse(dataNode.textContent) || []; } catch (e) { items = []; }
    var selected = -1;
    var visible = [];

    function setExpanded(open) {
      panel.hidden = !open;
      input.setAttribute("aria-expanded", String(open));
      if (!open) input.removeAttribute("aria-activedescendant");
    }

    function render(query) {
      var q = normalize(query);
      visible = items.filter(function (it) {
        return !q || normalize(it.label).indexOf(q) !== -1 || normalize(it.hint).indexOf(q) !== -1;
      });
      panel.innerHTML = "";
      if (!visible.length) {
        var empty = doc.createElement("div");
        empty.className = "ax-search__empty";
        empty.textContent = "Aucun module ne correspond à « " + query + " ».";
        panel.appendChild(empty);
        selected = -1;
        return;
      }
      visible.forEach(function (it, index) {
        var a = doc.createElement("a");
        a.className = "ax-search__option";
        a.href = it.url;
        a.id = "axSearchOpt" + index;
        a.setAttribute("role", "option");
        a.setAttribute("aria-selected", "false");
        var icon = doc.createElement("i");
        icon.className = "bi " + it.icon;
        icon.setAttribute("aria-hidden", "true");
        var text = doc.createElement("span");
        var strong = doc.createElement("strong");
        strong.textContent = it.label;
        var small = doc.createElement("small");
        small.textContent = it.hint;
        text.appendChild(strong);
        text.appendChild(small);
        a.appendChild(icon);
        a.appendChild(text);
        panel.appendChild(a);
      });
      select(q ? 0 : -1);
    }

    function select(index) {
      var options = qsa(".ax-search__option", panel);
      options.forEach(function (o) { o.setAttribute("aria-selected", "false"); });
      selected = index;
      if (index >= 0 && options[index]) {
        options[index].setAttribute("aria-selected", "true");
        input.setAttribute("aria-activedescendant", options[index].id);
        options[index].scrollIntoView({ block: "nearest" });
      } else {
        input.removeAttribute("aria-activedescendant");
      }
    }

    function openPanel() { render(input.value); setExpanded(true); }
    function closePanel() { setExpanded(false); }

    input.addEventListener("focus", openPanel);
    input.addEventListener("input", openPanel);
    input.addEventListener("keydown", function (event) {
      var count = visible.length;
      if (event.key === "ArrowDown") { event.preventDefault(); if (panel.hidden) openPanel(); select(count ? (selected + 1) % count : -1); }
      else if (event.key === "ArrowUp") { event.preventDefault(); if (panel.hidden) openPanel(); select(count ? (selected <= 0 ? count - 1 : selected - 1) : -1); }
      else if (event.key === "Enter") {
        var target = selected >= 0 ? visible[selected] : (visible.length === 1 ? visible[0] : null);
        if (target) { event.preventDefault(); window.location.href = target.url; }
      } else if (event.key === "Escape") {
        if (!panel.hidden) { event.preventDefault(); closePanel(); }
        else if (input.value) { input.value = ""; }
        else { closeMobileSearch(true); }
      }
    });

    doc.addEventListener("click", function (event) {
      if (!wrap.contains(event.target) && !(toggle && toggle.contains(event.target))) closePanel();
    });

    // Global shortcuts: "/" and Ctrl/Cmd+K
    doc.addEventListener("keydown", function (event) {
      var tag = (event.target.tagName || "").toLowerCase();
      var typing = tag === "input" || tag === "textarea" || tag === "select" || event.target.isContentEditable;
      var isSlash = event.key === "/" && !typing && !event.ctrlKey && !event.metaKey && !event.altKey;
      var isK = (event.key === "k" || event.key === "K") && (event.ctrlKey || event.metaKey);
      if (isSlash || isK) {
        event.preventDefault();
        openMobileSearch();
        input.focus();
        input.select();
      }
    });

    // Mobile: the search sits in a row under the topbar
    function openMobileSearch() {
      if (!toggle || toggle.offsetParent === null) return;
      wrap.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
    }
    function closeMobileSearch(returnFocus) {
      if (!toggle) return;
      wrap.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      closePanel();
      if (returnFocus && toggle.offsetParent !== null) toggle.focus();
    }
    if (toggle) {
      toggle.addEventListener("click", function () {
        if (wrap.classList.contains("is-open")) closeMobileSearch(false);
        else { openMobileSearch(); input.focus(); }
      });
    }
  })();

  /* ---------------------------------------------------------------- 3. Table filters */
  qsa("[data-ax-table]").forEach(function (table) {
    var rows = qsa("[data-ax-row]", table);
    var searchInput = qs("[data-ax-table-search]", table);
    var chips = qsa("[data-ax-filter]", table);
    var noResults = qs("[data-ax-no-results]", table);
    var counter = qs("[data-ax-count]", table);
    var scroller = qs(".ax-table-scroll", table);
    var list = scroller || (rows.length ? rows[0].parentElement : null);
    var status = "";

    // Pre-compute normalized text per row
    var texts = rows.map(function (row) { return normalize(row.textContent); });

    function apply() {
      var query = normalize(searchInput ? searchInput.value : "");
      var shown = 0;
      rows.forEach(function (row, i) {
        var okText = !query || texts[i].indexOf(query) !== -1;
        var okStatus = !status || row.getAttribute("data-status") === status;
        var show = okText && okStatus;
        row.hidden = !show;
        if (show) shown++;
      });
      if (counter && rows.length) counter.textContent = shown + " sur " + rows.length + " résultat" + (rows.length > 1 ? "s" : "");
      if (noResults) {
        var none = rows.length > 0 && shown === 0;
        noResults.hidden = !none;
        if (list && list !== noResults) list.hidden = none;
      }
    }

    if (searchInput) searchInput.addEventListener("input", apply);
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        status = chip.getAttribute("data-ax-filter") || "";
        chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
        apply();
      });
    });
    apply();
  });

  /* ---------------------------------------------------------------- 4. Dismissible alerts */
  doc.addEventListener("click", function (event) {
    var btn = event.target.closest && event.target.closest("[data-ax-dismiss]");
    if (!btn) return;
    var alert = btn.closest(".ax-alert");
    if (alert) alert.remove();
  });

  /* ---------------------------------------------------------------- 5. "Unavailable" modal */
  var unavailable = qs("#axUnavailableModal");
  if (unavailable) {
    unavailable.addEventListener("show.bs.modal", function (event) {
      var trigger = event.relatedTarget;
      var title = qs("#axUnavailableTitle", unavailable);
      var detail = qs("#axUnavailableDetail", unavailable);
      var label = trigger && trigger.getAttribute("data-ax-unavailable");
      var text = trigger && trigger.getAttribute("data-ax-unavailable-detail");
      title.textContent = label ? label + " : indisponible" : "Action indisponible";
      detail.textContent = text || "Cette fonctionnalité sera disponible lorsque le modèle de données correspondant existera.";
    });
  }

  /* ---------------------------------------------------------------- 6. Client profile panel */
  var clientPanel = qs("#axClientPanel");
  if (clientPanel) {
    clientPanel.addEventListener("show.bs.offcanvas", function (event) {
      var src = event.relatedTarget;
      if (!src) return;
      function set(field, value) {
        var el = qs('[data-ax-client="' + field + '"]', clientPanel);
        if (el) el.textContent = value || "—";
      }
      set("name", src.dataset.name);
      set("ref", src.dataset.ref);
      set("kind", src.dataset.kind);
      set("email", src.dataset.email);
      set("phone", src.dataset.phone);
      set("city", src.dataset.city);
      set("contracts", src.dataset.contracts);
      set("since", src.dataset.since);
      set("initials", src.dataset.initials);
      var badge = qs('[data-ax-client="status"]', clientPanel);
      if (badge) {
        badge.textContent = src.dataset.status || "—";
        badge.className = "ax-badge" + (src.dataset.tone ? " ax-badge--" + src.dataset.tone : "");
      }
    });
  }
})();
