/**
 * EnStory — wordbook.js
 * 单词本页面逻辑：localStorage 持久化，支持 JSON 文件导入/导出（File System Access API）
 */

(function () {
  'use strict';

  const KEY = 'enstory_wordbook';
  const baseUrl = (window.SITE_BASE || '/EnStory');

  // ── Storage ──────────────────────────────────────────────────────
  function getWordbook() {
    try { return JSON.parse(localStorage.getItem(KEY) || '[]'); }
    catch { return []; }
  }

  function saveWordbook(wb) {
    try { localStorage.setItem(KEY, JSON.stringify(wb)); }
    catch (e) { console.error(e); }
  }

  function removeWord(word) {
    let wb = getWordbook();
    wb = wb.filter(item => item.word !== word);
    saveWordbook(wb);
    render();
  }

  // ── 工具 ──────────────────────────────────────────────────────────
  function formatDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return `${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}`;
  }

  function escHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function todayStr() {
    return new Date().toISOString().slice(0, 10);
  }

  function defaultFilename(ext) {
    return `EnStory_单词本_${todayStr()}.${ext}`;
  }

  // ── Toast 提示 ───────────────────────────────────────────────────
  function showToast(msg, duration) {
    duration = duration || 2000;
    const existing = document.getElementById('wbToast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.id = 'wbToast';
    toast.style.cssText = [
      'position:fixed', 'bottom:28px', 'left:50%', 'transform:translateX(-50%)',
      'background:#1a1a2e', 'color:#fff', 'padding:10px 24px', 'border-radius:50px',
      'font-size:0.9rem', 'box-shadow:0 6px 20px rgba(0,0,0,0.2)', 'z-index:999',
      'opacity:0', 'transition:opacity 0.3s', 'pointer-events:none', 'white-space:nowrap'
    ].join(';');
    toast.textContent = msg;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.style.opacity = '1');
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  // ── 渲染 ─────────────────────────────────────────────────────────
  function renderCard(item) {
    return `
      <div class="wb-card" data-word="${escHtml(item.word)}">
        <div class="wb-card-top">
          <h3 class="wb-word">
            <a href="${baseUrl}/lookup/?q=${encodeURIComponent(item.word)}">${escHtml(item.word)}</a>
          </h3>
          <button class="wb-remove" data-word="${escHtml(item.word)}" title="从单词本移除">✕</button>
        </div>
        <div class="wb-meta">
          ${item.phonetic_en ? `<span class="wb-phonetic">[${escHtml(item.phonetic_en)}]</span>` : ''}
          ${item.pos ? `<span class="wb-pos">${escHtml(item.pos)}</span>` : ''}
          ${item.first_year ? `<span class="wb-year">${escHtml(item.first_year)}年</span>` : ''}
        </div>
        ${item.etymology_snippet ? `<p class="wb-snippet">${escHtml(item.etymology_snippet)}…</p>` : ''}
        <div class="wb-footer">
          <span class="wb-date">收藏于 ${formatDate(item.saved_at)}</span>
          <a class="wb-lookup-link" href="${baseUrl}/lookup/?q=${encodeURIComponent(item.word)}">查看词源 →</a>
        </div>
      </div>`;
  }

  function render() {
    const wb = getWordbook();
    const grid = document.getElementById('wordbookGrid');
    const empty = document.getElementById('wordbookEmpty');
    const count = document.getElementById('wordbookCount');

    count.textContent = `${wb.length} 个单词`;

    if (!wb.length) {
      grid.innerHTML = '';
      empty.style.display = 'block';
      return;
    }
    empty.style.display = 'none';
    grid.innerHTML = wb.map(renderCard).join('');

    grid.querySelectorAll('.wb-remove').forEach(btn => {
      btn.addEventListener('click', function () {
        const w = this.dataset.word;
        if (confirm(`从单词本移除「${w}」？`)) {
          removeWord(w);
        }
      });
    });
  }

  // ── 导出 JSON ────────────────────────────────────────────────────
  async function exportJson() {
    const wb = getWordbook();
    if (!wb.length) { alert('单词本是空的'); return; }

    const payload = JSON.stringify({
      app: 'EnStory',
      version: '1.0',
      exported_at: new Date().toISOString(),
      count: wb.length,
      words: wb,
    }, null, 2);

    const filename = defaultFilename('json');

    // 优先使用 File System Access API（Chrome/Edge）
    if ('showSaveFilePicker' in window) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{
            description: 'JSON 文件',
            accept: { 'application/json': ['.json'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(payload);
        await writable.close();
        showToast(`✓ 已保存至「${handle.name}」`);
        return;
      } catch (e) {
        if (e.name === 'AbortError') return; // 用户取消
        console.warn('File System Access API failed, falling back:', e);
      }
    }

    // 降级：普通下载
    const blob = new Blob([payload], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showToast('✓ 文件已下载（未使用系统保存对话框）');
  }

  // ── 导入 JSON ────────────────────────────────────────────────────
  async function importJson() {
    const filename = defaultFilename('json');

    let file;
    if ('showOpenFilePicker' in window) {
      try {
        const [handle] = await window.showOpenFilePicker({
          types: [{
            description: 'JSON 文件',
            accept: { 'application/json': ['.json'] },
          }],
        });
        file = await handle.getFile();
      } catch (e) {
        if (e.name === 'AbortError') return;
        console.warn('File System Access API failed, falling back:', e);
      }
    }

    // 降级：隐藏 file input
    if (!file) {
      const input = document.getElementById('importFileInput');
      if (!input.files || !input.files[0]) {
        input.click();
        input.addEventListener('change', async function () {
          if (this.files && this.files[0]) {
            await doImport(this.files[0]);
            this.value = '';
          }
        }, { once: true });
        return;
      }
      file = input.files[0];
    }

    await doImport(file);
  }

  async function doImport(file) {
    let text;
    try {
      text = await file.text();
    } catch (e) {
      alert('读取文件失败：' + e.message);
      return;
    }

    let data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      alert('文件格式错误，不是有效的 JSON 文件');
      return;
    }

    // 支持两种格式：直接是数组，或包格式 { app, words }
    const incoming = Array.isArray(data) ? data
      : (Array.isArray(data.words) ? data.words : null);

    if (!incoming || !incoming.length) {
      alert('文件中没有找到有效的单词数据');
      return;
    }

    // 合并去重：以新数据（文件中的数据）为准
    const existing = getWordbook();
    const existingMap = new Map(existing.map(item => [item.word, item]));
    let added = 0, skipped = 0;

    for (const item of incoming) {
      if (!item || !item.word) continue;
      const w = String(item.word).toLowerCase();
      if (existingMap.has(w)) {
        skipped++;
      } else {
        existingMap.set(w, item);
        added++;
      }
    }

    saveWordbook(Array.from(existingMap.values()));
    render();
    showToast(`✓ 导入完成：新增 ${added} 个，跳过重复 ${skipped} 个（共 ${existingMap.size} 个）`, 3000);
  }

  // ── 导出 TXT ────────────────────────────────────────────────────
  function exportTxt() {
    const wb = getWordbook();
    if (!wb.length) { alert('单词本是空的'); return; }
    const text = wb.map(item => {
      const lines = [`${item.word.toUpperCase()}`];
      if (item.phonetic_en) lines.push(`英 [${item.phonetic_en}]`);
      if (item.pos) lines.push(`词性：${item.pos}`);
      if (item.etymology_snippet) lines.push(`词源：${item.etymology_snippet}…`);
      lines.push('');
      return lines.join('\n');
    }).join('\n');

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = defaultFilename('txt');
    a.click();
    URL.revokeObjectURL(url);
    showToast('✓ TXT 文件已下载');
  }

  // ── 事件绑定 ────────────────────────────────────────────────────
  document.getElementById('exportJsonBtn').addEventListener('click', exportJson);
  document.getElementById('importBtn').addEventListener('click', importJson);
  document.getElementById('exportTxtBtn').addEventListener('click', exportTxt);

  document.getElementById('clearAllBtn').addEventListener('click', function () {
    if (!getWordbook().length) return;
    if (confirm('确定清空所有收藏的单词？此操作不可撤销。')) {
      saveWordbook([]);
      render();
    }
  });

  render();

})();
