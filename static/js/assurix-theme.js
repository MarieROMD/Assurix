/* ==========================================================================
   ASSURIX THEME  ·  assurix-theme.js
   Light/dark theme with persistence and system-preference fallback.

   IMPORTANT: load this file in <head> WITHOUT defer/async so the theme is
   applied before first paint (no flash of the wrong theme).

   - Stores the choice in localStorage under "assurix-theme" ("light" | "dark").
   - Without a stored choice, follows the operating system until the user picks.
   - Any element with [data-ax-theme-toggle] toggles the theme (event delegation,
     so it also works for buttons added later, e.g. the Phase 3 topbar).
   - Fires a "assurix:themechange" CustomEvent on document so charts
     (Phase 4) can re-read the CSS tokens.
   ========================================================================== */
(function () {
  "use strict";

  var KEY = "assurix-theme";
  var root = document.documentElement;
  var media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function readStored() {
    try {
      var v = window.localStorage.getItem(KEY);
      return v === "light" || v === "dark" ? v : null;
    } catch (e) {
      return null; // storage blocked (private mode, etc.)
    }
  }

  function writeStored(theme) {
    try { window.localStorage.setItem(KEY, theme); } catch (e) { /* ignore */ }
  }

  function systemTheme() {
    return media && media.matches ? "dark" : "light";
  }

  function current() {
    return root.getAttribute("data-bs-theme") === "dark" ? "dark" : "light";
  }

  function syncButtons(theme) {
    var buttons = document.querySelectorAll("[data-ax-theme-toggle]");
    for (var i = 0; i < buttons.length; i++) {
      var isDark = theme === "dark";
      buttons[i].setAttribute("aria-pressed", String(isDark));
      buttons[i].setAttribute("aria-label", isDark ? "Passer au thème clair" : "Passer au thème sombre");
      buttons[i].setAttribute("title", isDark ? "Passer au thème clair" : "Passer au thème sombre");
    }
  }

  function apply(theme, announce) {
    root.setAttribute("data-bs-theme", theme);
    syncButtons(theme);
    if (announce) {
      document.dispatchEvent(new CustomEvent("assurix:themechange", { detail: { theme: theme } }));
    }
  }

  // 1. Apply immediately (script runs in <head>)
  apply(readStored() || systemTheme(), false);

  // 2. Wire up once the DOM exists
  document.addEventListener("DOMContentLoaded", function () {
    syncButtons(current());
  });

  document.addEventListener("click", function (event) {
    var toggle = event.target.closest && event.target.closest("[data-ax-theme-toggle]");
    if (!toggle) return;
    var next = current() === "dark" ? "light" : "dark";
    writeStored(next);
    apply(next, true);
  });

  // 3. Follow the OS only while the user has not made an explicit choice
  if (media && media.addEventListener) {
    media.addEventListener("change", function () {
      if (!readStored()) apply(systemTheme(), true);
    });
  }

  // Small public API for other Assurix scripts
  window.AssurixTheme = {
    get: current,
    set: function (theme) {
      if (theme !== "light" && theme !== "dark") return;
      writeStored(theme);
      apply(theme, true);
    }
  };
})();
