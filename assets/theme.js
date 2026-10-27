// Theme toggle: persists choice, respects OS preference on first visit.
// The blocking init snippet in each page's <head> sets data-theme before paint;
// this script only wires up the button. The button's mark is drawn by style.css.
(function () {
  const root = document.documentElement;
  const btn = document.getElementById('themeToggle');
  if (!btn) return;

  function setTheme(t) {
    root.dataset.theme = t;
    btn.setAttribute('aria-label', t === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    try { localStorage.setItem('ninjaapps-theme', t); } catch (e) { /* private mode */ }
  }

  setTheme(root.dataset.theme || 'light');
  btn.addEventListener('click', function () {
    setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark');
  });
})();
