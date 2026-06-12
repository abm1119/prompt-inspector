const $ = (sel) => document.querySelector(sel);

const statusPill = $('#statusPill');
const runBtn = $('#runBtn');
const clearBtn = $('#clearBtn');
const promptEl = $('#prompt');
const resultsCard = $('#resultsCard');

const progressEl = $('#progress');
const errorEl = $('#error');

const panels = {
  overview: $('#tab-overview'),
  scoring: $('#tab-scoring'),
  vulns: $('#tab-vulns'),
  stress: $('#tab-stress'),
  prompt: $('#tab-prompt'),
  raw: $('#tab-raw'),
};

function setStatus(text, tone=null){
  statusPill.textContent = text;
  statusPill.style.borderColor = tone ? tone : 'rgba(255,255,255,.08)';
}

function showError(msg){
  errorEl.hidden = false;
  errorEl.textContent = msg;
}

function clearError(){
  errorEl.hidden = true;
  errorEl.textContent = '';
}

function escapeHtml(str){
  return (str ?? '')
    .replaceAll('&','&amp;')
    .replaceAll('<','<')
    .replaceAll('>','>')
    .replaceAll('"','"')
    .replaceAll("'",'&#039;');
}

function badgeForRisk(r){
  const v = (r||'').toLowerCase();
  if(v==='high') return 'bad';
  if(v==='medium') return 'warn';
  return 'ok';
}

function renderOverview(data){
  const a = data.analysis;
  const parsing = a.parsing || {};
  const types = (a.prompt_types||[]).join(', ') || 'N/A';

  const html = `
    <div class="result-kpis">
      <article class="mini-card"><strong>${escapeHtml(types || 'N/A')}</strong><span>Prompt types</span></article>
      <article class="mini-card"><strong>${escapeHtml(parsing.task || 'N/A')}</strong><span>Primary task</span></article>
      <article class="mini-card"><strong>${escapeHtml(parsing.role || 'N/A')}</strong><span>Assigned role</span></article>
    </div>
    <div class="kv">
      <div class="k">Types</div><div class="v">${escapeHtml(types)}</div>
      <div class="k">Task</div><div class="v">${escapeHtml(parsing.task || 'N/A')}</div>
      <div class="k">Role</div><div class="v">${escapeHtml(parsing.role || 'N/A')}</div>
      <div class="k">Output format</div><div class="v">${escapeHtml(parsing.output_format || 'N/A')}</div>
    </div>

    <div style="margin-top:14px">
      <div class="muted" style="font-size:12px;margin-bottom:8px">Constraints</div>
      <ul class="list">${(parsing.constraints||[]).map(c=>`<li>${escapeHtml(c)}</li>`).join('') || '<li class="muted">None</li>'}</ul>
    </div>
  `;
  panels.overview.innerHTML = html;
}

function renderScoring(data){
  const orig = data.comparison.original_scores;
  const imp = data.comparison.improved_scores;
  const delta = data.comparison.delta || {};

  const keys = Object.keys(orig).filter(k=>k!=='readability_score');
  const readOrig = data.comparison.original_scores.readability_score ?? 0;
  const readImp = data.comparison.improved_scores.readability_score ?? 0;

  const rows = keys.map(k=>{
    const v0 = orig[k];
    const v1 = imp[k];
    const d = delta[k];
    const tone = d>0 ? 'rgba(46,229,157,.95)' : d<0 ? 'rgba(255,77,109,.95)' : 'rgba(255,255,255,.8)';
    return `
      <tr>
        <td>${escapeHtml(k)}</td>
        <td style="text-align:center">${Number(v0).toFixed(1)}</td>
        <td style="text-align:center">${Number(v1).toFixed(1)}</td>
        <td style="text-align:right;font-weight:800;color:${tone}">${(d ?? 0).toFixed(1)>=0?'+':''}${Number(d ?? 0).toFixed(1)}</td>
      </tr>
    `;
  }).join('');

  const readTone = (readImp-readOrig) >= 0 ? 'rgba(109,94,252,.95)' : 'rgba(255,204,102,.95)';

  panels.scoring.innerHTML = `
    <table class="table">
      <thead>
        <tr>
          <th>Metric</th><th>Original</th><th>Improved</th><th>Delta</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
        <tr>
          <td><b>Readability (Flesch)</b></td>
          <td style="text-align:center">${Number(readOrig).toFixed(1)}</td>
          <td style="text-align:center">${Number(readImp).toFixed(1)}</td>
          <td style="text-align:right;font-weight:900;color:${readTone}">${(readImp-readOrig)>=0?'+':''}${(readImp-readOrig).toFixed(1)}</td>
        </tr>
      </tbody>
    </table>
  `;
}

function renderVulns(data){
  const vulns = data.analysis.vulnerabilities || [];
  panels.vulns.innerHTML = vulns.length
    ? `
      <div class="result-kpis">
        <article class="mini-card"><strong>${vulns.length}</strong><span>Findings</span></article>
        <article class="mini-card"><strong>${vulns.some(v=>/high|critical/i.test(v)) ? 'Needs attention' : 'Stable'}</strong><span>Risk signal</span></article>
      </div>
      <ul class="list">${vulns.map(v=>`<li>${escapeHtml(v)}</li>`).join('')}</ul>
    `
    : `<div class="muted">No vulnerabilities detected by the analyzer.</div>`;
}

function renderStress(data){
  const items = data.stress_results || [];
  panels.stress.innerHTML = items.length
    ? `
      <table class="table">
        <thead><tr><th>Attack vector</th><th>Status</th><th>Risk</th><th>Observation</th></tr></thead>
        <tbody>
          ${items.map(r=>{
            const status = r.passed ? 'PASS' : 'FAIL';
            const riskClass = badgeForRisk(r.risk_level);
            const statusClass = r.passed ? 'ok' : 'bad';
            return `
              <tr>
                <td>${escapeHtml(r.variant_type)}</td>
                <td><span class="badge ${statusClass}">${status}</span></td>
                <td><span class="badge ${riskClass}">${escapeHtml(r.risk_level)}</span></td>
                <td>${escapeHtml(r.observation)}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    `
    : `<div class="muted">No stress results returned.</div>`;
}

function renderPrompt(data){
  const text = data.analysis.improved_prompt || '';
  panels.prompt.innerHTML = `
    <div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:10px">
      <button id="copyPrompt" class="small">Copy hardened prompt</button>
    </div>
    <div class="pre">${escapeHtml(text)}</div>
  `;
  const btn = document.getElementById('copyPrompt');
  btn.addEventListener('click', async ()=>{
    await navigator.clipboard.writeText(text);
  });
}

function renderRaw(data){
  panels.raw.innerHTML = `
    <div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:10px">
      <button id="copyRaw" class="small">Copy raw JSON</button>
    </div>
    <div class="pre">${escapeHtml(JSON.stringify(data, null, 2))}</div>
  `;
  const btn = document.getElementById('copyRaw');
  btn.addEventListener('click', async ()=>{
    await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
  });
}

function activateTab(tabName){
  for(const [name, el] of Object.entries(panels)){
    const btn = document.querySelector(`.tab[data-tab="${name}"]`);
    const isActive = name === tabName;
    el.hidden = !isActive;
    if(btn) btn.classList.toggle('active', isActive);
  }
}

function setOpenExportLink(exportPath){
  // In browsers we can’t directly open local folders reliably.
  // Provide a best-effort file:// link if it's an absolute Windows path.
  const a = $('#openExport');
  const copy = $('#copyExport');
  copy.onclick = async () => { await navigator.clipboard.writeText(exportPath); };

  const p = (exportPath||'').trim();
  $('#openExport').href = '#';
  if(p.match(/^[A-Za-z]:\\/)){
    // windows path -> file:///
    const url = 'file:///' + p.replaceAll('\\','/');
    a.href = url;
  }
}

async function runInspect(){
  const prompt = promptEl.value.trim();
  clearError();

  if(!prompt){
    showError('Paste a prompt first.');
    return;
  }

  runBtn.disabled = true;
  progressEl.hidden = false;
  setStatus('Running...', 'rgba(109,94,252,.65)');
  resultsCard.hidden = true;

  try{
    const resp = await fetch('/api/inspect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });

    if(!resp.ok){
      const t = await resp.text();
      throw new Error(`Backend error (${resp.status}): ${t}`);
    }

    const data = await resp.json();

    renderOverview(data);
    renderScoring(data);
    renderVulns(data);
    renderStress(data);
    renderPrompt(data);
    renderRaw(data);

    setOpenExportLink(data.export_path);

    resultsCard.hidden = false;
    activateTab('overview');
    setStatus('Done', 'rgba(46,229,157,.45)');

  }catch(e){
    showError(e.message || String(e));
    setStatus('Error', 'rgba(255,77,109,.55)');
  }finally{
    runBtn.disabled = false;
    progressEl.hidden = true;
  }
}

runBtn.addEventListener('click', runInspect);
clearBtn.addEventListener('click', ()=>{ promptEl.value=''; clearError(); resultsCard.hidden=true; setStatus('Idle'); });

// Tabs
document.querySelectorAll('.tab').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const name = btn.getAttribute('data-tab');
    activateTab(name);
  });
});

