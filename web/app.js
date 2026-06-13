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
  optimizer: $('#tab-optimizer'),
  raw: $('#tab-raw'),
};

function setStatus(text, tone=null){
  statusPill.textContent = text;
  statusPill.style.color = tone ? tone : 'var(--color-text-muted)';
  statusPill.style.borderColor = tone ? tone : 'var(--color-border)';
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
    .replaceAll('<','&lt;')
    .replaceAll('>','&gt;')
    .replaceAll('"','&quot;')
    .replaceAll("'",'&#039;');
}

function badgeForRisk(r){
  const v = (r||'').toLowerCase();
  if(v==='high' || v==='critical') return 'badge-error';
  if(v==='medium') return 'badge-warn';
  return 'badge-success';
}

function renderKPI(label, value){
  return `
    <article class="kpi-card">
      <span class="kpi-label">${label}</span>
      <div class="kpi-value">${escapeHtml(value)}</div>
    </article>
  `;
}

function renderOverview(data){
  const a = data.analysis;
  const parsing = a.parsing || {};
  const types = (a.prompt_types||[]).join(', ') || 'N/A';

  const html = `
    <div class="result-kpis">
      ${renderKPI('Prompt Type', types)}
      ${renderKPI('Primary Task', parsing.task || 'N/A')}
      ${renderKPI('Assigned Role', parsing.role || 'N/A')}
    </div>
    
    <div style="margin-top:24px">
      <h3 style="font-size:12px; color:var(--color-text-muted); margin-bottom:12px; text-transform:uppercase; letter-spacing:0.05em">Structural Analysis</h3>
      <table class="data-table">
        <tr><td><strong>Context</strong></td><td>${escapeHtml(parsing.context || 'None provided')}</td></tr>
        <tr><td><strong>Output Format</strong></td><td>${escapeHtml(parsing.output_format || 'Auto')}</td></tr>
        <tr><td><strong>Constraints</strong></td><td>
          <ul style="padding-left:16px; margin:0">${(parsing.constraints||[]).map(c=>`<li>${escapeHtml(c)}</li>`).join('') || '<li>None</li>'}</ul>
        </td></tr>
        <tr><td><strong>Assumptions</strong></td><td>
          <ul style="padding-left:16px; margin:0">${(parsing.assumptions||[]).map(c=>`<li>${escapeHtml(c)}</li>`).join('') || '<li>None identified</li>'}</ul>
        </td></tr>
      </table>
    </div>
  `;
  panels.overview.innerHTML = html;
}

function renderScoring(data){
  const orig = data.comparison.original_scores;
  const imp = data.comparison.improved_scores;
  const delta = data.comparison.delta || {};

  const keys = Object.keys(orig).filter(k=>k!=='readability_score');
  
  const rows = keys.map(k=>{
    const v0 = orig[k];
    const v1 = imp[k];
    const d = delta[k];
    const deltaColor = d > 0 ? 'var(--color-success)' : d < 0 ? 'var(--color-error)' : 'inherit';
    return `
      <tr>
        <td>${escapeHtml(k.replace('_',' '))}</td>
        <td>${Number(v0).toFixed(1)}%</td>
        <td>${Number(v1).toFixed(1)}%</td>
        <td style="color:${deltaColor}; font-weight:700">${(d ?? 0)>=0?'+':''}${Number(d ?? 0).toFixed(1)}</td>
      </tr>
    `;
  }).join('');

  panels.scoring.innerHTML = `
    <table class="data-table">
      <thead>
        <tr><th>Quality Metric</th><th>Original</th><th>Hardened</th><th>Improvement</th></tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
    <div style="margin-top:24px; padding:16px; background:var(--color-pane); border-radius:var(--radius-md); border-left:4px solid var(--color-accent)">
      <h4 style="font-size:11px; color:var(--color-text-muted); margin-bottom:4px">EXECUTIVE SUMMARY</h4>
      <p style="font-size:13px">${data.comparison.key_improvements.join('. ')}.</p>
    </div>
  `;
}

function renderVulns(data){
  const vulns = data.analysis.vulnerabilities || [];
  panels.vulns.innerHTML = vulns.length
    ? `
      <div class="result-kpis">
        ${renderKPI('Findings', vulns.length)}
        ${renderKPI('Risk Level', vulns.length > 3 ? 'High' : 'Elevated')}
      </div>
      <ul style="padding-left:20px; color:var(--color-text)">
        ${vulns.map(v=>`<li style="margin-bottom:8px">${escapeHtml(v)}</li>`).join('')}
      </ul>
    `
    : `<div style="text-align:center; padding:48px; color:var(--color-text-muted)">No vulnerabilities detected in this prompt architecture.</div>`;
}

function renderStress(data){
  const items = data.stress_results || [];
  panels.stress.innerHTML = items.length
    ? `
      <table class="data-table">
        <thead><tr><th>Attack Vector</th><th>Status</th><th>Risk</th><th>Observation</th></tr></thead>
        <tbody>
          ${items.map(r=>{
            const riskClass = badgeForRisk(r.risk_level);
            const statusClass = r.passed ? 'badge-success' : 'badge-error';
            return `
              <tr>
                <td style="font-family:var(--font-mono); font-size:12px">${escapeHtml(r.variant_type)}</td>
                <td><span class="badge ${statusClass}">${r.passed ? 'PASS' : 'FAIL'}</span></td>
                <td><span class="badge ${riskClass}">${escapeHtml(r.risk_level)}</span></td>
                <td style="color:var(--color-text-muted)">${escapeHtml(r.observation)}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    `
    : `<div style="text-align:center; padding:48px; color:var(--color-text-muted)">No stress test data available.</div>`;
}

function renderPrompt(data){
  const text = data.analysis.improved_prompt || '';
  panels.prompt.innerHTML = `
    <div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:10px">
      <button id="copyPrompt" class="btn-small">Copy Hardened Prompt</button>
    </div>
    <div class="code-block">${escapeHtml(text)}</div>
  `;
  document.getElementById('copyPrompt').onclick = async () => {
    await navigator.clipboard.writeText(text);
    setStatus('Copied to clipboard', 'var(--color-success)');
    setTimeout(()=>setStatus('System Idle'), 2000);
  };
}

function renderOptimizer(data){
  const result = data.optimizer || {};
  const steps = (result.steps || []).map(s => `
    <li style="margin-bottom:12px">
      <strong style="color:var(--color-accent)">${escapeHtml(s.name)}</strong><br/>
      <span style="font-size:12px; color:var(--color-text-muted)">${escapeHtml(s.explanation)}</span>
    </li>
  `).join('');
  
  panels.optimizer.innerHTML = `
    <div class="result-kpis">
      ${renderKPI('Optimization Steps', (result.steps || []).length)}
      ${renderKPI('Clarity Boost', 'High')}
    </div>
    <div style="margin-bottom:24px">
      <h4 style="font-size:11px; color:var(--color-text-muted); margin-bottom:8px">LEAN REWRITE</h4>
      <div class="code-block">${escapeHtml(result.optimized_prompt || '')}</div>
    </div>
    <div style="margin-top:24px">
      <h4 style="font-size:11px; color:var(--color-text-muted); margin-bottom:12px">STRATEGY LOG</h4>
      <ul style="list-style:none; padding:0">${steps || '<li>No steps recorded.</li>'}</ul>
    </div>
  `;
}

function renderRaw(data){
  const json = JSON.stringify(data, null, 2);
  panels.raw.innerHTML = `
    <div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:10px">
      <button id="copyRaw" class="btn-small">Copy Raw Manifest</button>
    </div>
    <div class="code-block" style="font-size:11px">${escapeHtml(json)}</div>
  `;
  document.getElementById('copyRaw').onclick = async () => {
    await navigator.clipboard.writeText(json);
  };
}

function resetProgressState(){
  progressEl.hidden = true;
  progressEl.style.display = 'none';
  progressEl.style.opacity = '0';
}

function showProgressState(){
  progressEl.hidden = false;
  progressEl.style.display = 'flex';
  progressEl.style.opacity = '1';
}

function activateTab(tabName){
  document.querySelectorAll('.tab-btn').forEach(btn => {
    const isActive = btn.getAttribute('data-tab') === tabName;
    btn.classList.toggle('active', isActive);
  });
  Object.keys(panels).forEach(name => {
    panels[name].hidden = name !== tabName;
  });
}

async function runInspect(){
  const prompt = promptEl.value.trim();
  clearError();

  if(!prompt){
    showError('Please provide a prompt for analysis.');
    return;
  }

  runBtn.disabled = true;
  showProgressState();
  setStatus('Analyzing Prompt...', 'var(--color-accent)');
  resultsCard.hidden = true;

  try{
    const resp = await fetch('/api/inspect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });

    if(!resp.ok){
      const t = await resp.text();
      throw new Error(`Pipeline Error: ${t}`);
    }

    const data = await resp.json();

    renderOverview(data);
    renderScoring(data);
    renderVulns(data);
    renderStress(data);
    renderPrompt(data);
    renderOptimizer(data);
    renderRaw(data);

    const exportPath = data.export_path || '';
    $('#copyExport').onclick = async () => { 
      await navigator.clipboard.writeText(exportPath); 
      setStatus('Export path copied', 'var(--color-success)');
    };
    $('#openExport').href = exportPath.match(/^[A-Z]:\\/) ? 'file:///' + exportPath.replaceAll('\\','/') : '#';

    resultsCard.hidden = false;
    activateTab('overview');
    setStatus('Analysis Complete', 'var(--color-success)');

  }catch(e){
    showError(e.message);
    setStatus('Analysis Failed', 'var(--color-error)');
  }finally{
    runBtn.disabled = false;
    progressEl.style.opacity = '0';
    setTimeout(() => {
      resetProgressState();
    }, 300);
  }
}

// Event Listeners
runBtn.onclick = runInspect;
clearBtn.onclick = () => {
  promptEl.value = '';
  resultsCard.hidden = true;
  clearError();
  resetProgressState();
  setStatus('System Idle');
};

promptEl.onkeydown = (e) => {
  if (e.ctrlKey && e.key === 'Enter') runInspect();
};

document.addEventListener('DOMContentLoaded', () => {
  resetProgressState();
  setStatus('System Idle');
});

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.onclick = () => activateTab(btn.getAttribute('data-tab'));
});
