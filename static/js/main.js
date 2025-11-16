// main.js

document.addEventListener('DOMContentLoaded', function () {
  const themeSwitch = document.getElementById('themeSwitch');
  const htmlEl = document.documentElement;
  const themeLabel = document.getElementById('themeLabel');

  // Load saved theme
  const saved = localStorage.getItem('theme') || 'light';
  htmlEl.setAttribute('data-theme', saved);
  if (themeSwitch) themeSwitch.checked = saved === 'dark';
  if (themeLabel) themeLabel.textContent = saved === 'dark' ? '☀️' : '🌙';

  // Toggle
  if (themeSwitch) {
    themeSwitch.addEventListener('change', () => {
      const t = themeSwitch.checked ? 'dark' : 'light';
      htmlEl.setAttribute('data-theme', t);
      localStorage.setItem('theme', t);
      if (themeLabel) themeLabel.textContent = t === 'dark' ? '☀️' : '🌙';
    });
  }

  // Show loading spinner on form submit
  const form = document.getElementById('predictForm');
  const loading = document.getElementById('loading');
  if (form && loading) {
    form.addEventListener('submit', () => { loading.style.display = 'block'; });
  }
});
