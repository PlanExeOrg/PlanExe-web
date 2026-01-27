(function () {
  const STORAGE_KEY = "planexe-theme";

  function getStoredTheme() {
    try {
      const v = window.localStorage.getItem(STORAGE_KEY);
      return v === "light" || v === "dark" ? v : null;
    } catch {
      return null;
    }
  }

  function setStoredTheme(themeOrNull) {
    try {
      if (themeOrNull) {
        window.localStorage.setItem(STORAGE_KEY, themeOrNull);
      } else {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // ignore
    }
  }

  function getSystemTheme() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function getEffectiveTheme() {
    const attr = document.documentElement.getAttribute("data-theme");
    if (attr === "light" || attr === "dark") return attr;
    return getSystemTheme();
  }

  function applyTheme(themeOrNull) {
    if (themeOrNull) {
      document.documentElement.setAttribute("data-theme", themeOrNull);
    } else {
      document.documentElement.setAttribute("data-theme", "");
    }
  }

  function toggleTheme() {
    const current = getEffectiveTheme();
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    setStoredTheme(next);
  }

  function resetToSystem() {
    applyTheme(null);
    setStoredTheme(null);
  }

  function onToggleClick(ev) {
    // Shift+click resets to system.
    if (ev.shiftKey) {
      resetToSystem();
      return;
    }
    toggleTheme();
  }

  // Wire up button
  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.querySelector("[data-theme-toggle]");
    if (btn) btn.addEventListener("click", onToggleClick);
  });

  // If user is on "system" mode (no explicit data-theme), follow system changes live.
  if (window.matchMedia) {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = function () {
      const stored = getStoredTheme();
      if (!stored) applyTheme(null);
    };
    if (mq.addEventListener) mq.addEventListener("change", handler);
    else if (mq.addListener) mq.addListener(handler);
  }
})();

