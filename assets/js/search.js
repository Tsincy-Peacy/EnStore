/* EnStory — Header Search Modal Logic */

// 初始化 Header 搜索 Overlay：跳转到探词页
function initHeaderSearch() {
  const toggle = document.getElementById('searchToggle');
  const overlay = document.getElementById('searchOverlay');
  const closeBtn = document.getElementById('searchClose');
  const input = document.getElementById('searchInput');
  if (!toggle || !overlay) return;

  toggle.addEventListener('click', () => {
    overlay.classList.add('active');
    setTimeout(() => input && input.focus(), 50);
  });

  closeBtn && closeBtn.addEventListener('click', closeOverlay);
  overlay.addEventListener('click', e => { if (e.target === overlay) closeOverlay(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeOverlay(); });

  function closeOverlay() {
    overlay.classList.remove('active');
    if (input) input.value = '';
  }

  // 回车跳转到探词页
  input && input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      const q = this.value.trim();
      if (q) {
        const base = window.SITE_BASE || '';
        window.location.href = base + '/lookup/?q=' + encodeURIComponent(q);
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initHeaderSearch();
});
