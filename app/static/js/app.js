// ResuMind — frontend logic

const $ = (sel) => document.querySelector(sel);

// ----- Tabs -----
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.querySelector(`[data-panel="${tab.dataset.tab}"]`).classList.add('active');
  });
});

// ----- Drag & drop file picker -----
const dz = $('#dropzone');
const fileInput = $('#resume-file');
const dzFile = $('#dz-file');

dz.addEventListener('click', () => fileInput.click());
['dragenter', 'dragover'].forEach(e => dz.addEventListener(e, ev => {
  ev.preventDefault(); dz.classList.add('dragover');
}));
['dragleave', 'drop'].forEach(e => dz.addEventListener(e, ev => {
  ev.preventDefault(); dz.classList.remove('dragover');
}));
dz.addEventListener('drop', ev => {
  if (ev.dataTransfer.files.length) {
    fileInput.files = ev.dataTransfer.files;
    showFile(ev.dataTransfer.files[0]);
  }
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) showFile(fileInput.files[0]);
});
function showFile(file) {
  dzFile.hidden = false;
  dzFile.textContent = `📎 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
}

// ----- Analyze -----
const analyzeBtn = $('#analyze-btn');
const resetBtn = $('#reset-btn');
const errorBox = $('#error');
const results = $('#results');
let lastResult = null;

analyzeBtn.addEventListener('click', async () => {
  errorBox.hidden = true;
  results.hidden = true;

  const formData = new FormData();
  const file = fileInput.files[0];
  const pasted = $('#resume-text').value.trim();
  const jd = $('#job-desc').value.trim();

  if (file) formData.append('resume_file', file);
  if (pasted) formData.append('resume_text', pasted);
  if (jd) formData.append('job_description', jd);

  if (!file && !pasted) {
    showError('Please upload a resume file or paste resume text.');
    return;
  }

  setLoading(true);
  try {
    const resp = await fetch('/api/analyze', { method: 'POST', body: formData });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Analysis failed.');
    lastResult = data;
    renderResults(data);
  } catch (e) {
    showError(e.message);
  } finally {
    setLoading(false);
  }
});

resetBtn.addEventListener('click', () => {
  results.hidden = true;
  resetBtn.hidden = true;
  errorBox.hidden = true;
  lastResult = null;
  fileInput.value = '';
  dzFile.hidden = true;
  $('#resume-text').value = '';
  $('#job-desc').value = '';
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

function setLoading(on) {
  analyzeBtn.disabled = on;
  analyzeBtn.querySelector('.btn-label').textContent = on ? 'Analyzing...' : '⚡ Analyze Resume';
  analyzeBtn.querySelector('.spinner').hidden = !on;
}

function showError(msg) {
  errorBox.textContent = '⚠️ ' + msg;
  errorBox.hidden = false;
  errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ----- Render -----
function renderResults({ analysis, ats }) {
  results.hidden = false;
  resetBtn.hidden = false;

  // Score
  const score = parseInt(analysis.score) || 0;
  animateNumber('#score-num', score);
  $('#score-fill').style.width = `${Math.max(0, Math.min(100, score))}%`;
  $('#verdict').textContent = analysis.verdict || '';

  // ATS
  $('#ats-num').textContent = ats?.similarity_pct ?? '—';

  // Summary
  $('#summary').textContent = analysis.summary || '';

  // Lists
  fillList('#strengths', analysis.strengths);
  fillList('#weaknesses', analysis.weaknesses);
  fillList('#suggestions', analysis.suggestions);

  // Chips
  fillChips('#matched-chips', ats?.matched_keywords || [], 'match');
  // Combine AI + ATS missing keywords
  const combined = Array.from(new Set([
    ...(analysis.missing_keywords || []),
    ...(ats?.missing_keywords || []),
  ])).slice(0, 30);
  fillChips('#missing-chips', combined, 'miss');

  // Sections
  const sections = $('#sections');
  sections.innerHTML = '';
  (analysis.section_scores || []).forEach(item => {
    const row = document.createElement('div');
    row.className = 'section-row';
    const score = parseFloat(item.score) || 0;
    const tier = score >= 4 ? 'good' : score >= 2.5 ? 'mid' : 'low';
    row.innerHTML = `
      <strong>${escapeHtml(item.section || '')}</strong>
      <span class="score-pill ${tier}">${item.score}/5</span>
      <span class="muted">${escapeHtml(item.note || '')}</span>
    `;
    sections.appendChild(row);
  });

  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function fillList(sel, items) {
  const ul = $(sel);
  ul.innerHTML = '';
  (items || []).forEach(t => {
    const li = document.createElement('li');
    li.textContent = t;
    ul.appendChild(li);
  });
  if (!items || !items.length) {
    const li = document.createElement('li');
    li.textContent = 'None reported.';
    li.className = 'muted';
    ul.appendChild(li);
  }
}

function fillChips(sel, items, cls) {
  const c = $(sel);
  c.innerHTML = '';
  if (!items.length) {
    c.innerHTML = '<span class="muted small">None.</span>';
    return;
  }
  items.forEach(t => {
    const span = document.createElement('span');
    span.className = `chip ${cls}`;
    span.textContent = t;
    c.appendChild(span);
  });
}

function animateNumber(sel, target) {
  const el = $(sel);
  const start = 0, dur = 900, t0 = performance.now();
  function tick(now) {
    const p = Math.min(1, (now - t0) / dur);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(start + (target - start) * eased);
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

// ----- PDF Download -----
$('#download-btn').addEventListener('click', async () => {
  if (!lastResult) return;
  const btn = $('#download-btn');
  const orig = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Generating PDF...';
  try {
    const resp = await fetch('/api/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lastResult),
    });
    if (!resp.ok) {
      const data = await resp.json().catch(() => ({}));
      throw new Error(data.error || 'PDF generation failed.');
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'resume-analysis.pdf';
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    showError(e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = orig;
  }
});
