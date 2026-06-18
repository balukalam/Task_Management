// ── TaskFlow — script.js ──────────────────────────────────────────────────────

// Auto-set today's date on add form
document.addEventListener('DOMContentLoaded', () => {

  // Set default date to today if empty
  const dateInputs = document.querySelectorAll('input[type="date"]');
  dateInputs.forEach(input => {
    if (!input.value) {
      const today = new Date().toISOString().split('T')[0];
      input.value = today;
    }
  });

  // Animate stat values counting up
  const statValues = document.querySelectorAll('.stat-value');
  statValues.forEach(el => {
    const target = parseInt(el.textContent, 10);
    if (isNaN(target) || target === 0) return;
    let current = 0;
    const step = Math.ceil(target / 20);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 40);
  });

  // Animate progress bars on load
  const fills = document.querySelectorAll('.progress-bar-fill');
  fills.forEach(fill => {
    const w = fill.style.width;
    fill.style.width = '0%';
    setTimeout(() => { fill.style.width = w; }, 100);
  });

  // Highlight active nav link
  const links = document.querySelectorAll('.navbar-links a');
  links.forEach(link => {
    if (link.href === window.location.href) {
      link.style.color = 'var(--text)';
      link.style.background = 'var(--card)';
    }
  });

  // Delete confirmation with nicer UX
  const deleteLinks = document.querySelectorAll('.btn-delete');
  deleteLinks.forEach(link => {
    link.addEventListener('click', e => {
      if (!confirm('Are you sure you want to delete this task? This cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // Range slider live update (edit page)
  const range = document.getElementById('progressRange');
  const rangeVal = document.getElementById('progressVal');
  if (range && rangeVal) {
    range.addEventListener('input', () => {
      rangeVal.textContent = range.value + '%';
    });
  }

});
