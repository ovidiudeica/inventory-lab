import {setupBrowserAI} from './browser-ai.js';
const browserAI = setupBrowserAI();
const byId = id => document.getElementById(id);
const money = value => new Intl.NumberFormat('en-GB', {style:'currency', currency:'GBP'}).format(value);
const signed = value => value > 0 ? '+' + value : String(value);
let data, selected = null;
function text(id, value) { byId(id).textContent = value; }
function node(tag, value, className) {
  const el = document.createElement(tag);
  if (value !== undefined) el.textContent = value;
  if (className) el.className = className;
  return el;
}
function procedure(id) {
  const p = data.procedures[id];
  const card = node('article', undefined, 'procedure');
  card.append(node('h3', id + ' — ' + p.title));
  const list = node('ol');
  p.steps.forEach(step => list.append(node('li', step)));
  card.append(list);
  return card;
}
function visibleRows() {
  const q = byId('search').value.trim().toLowerCase(), filter = byId('filter').value;
  return data.stock.filter(row =>
    [row.sku, row.name, row.bin].some(value => value.toLowerCase().includes(q)) &&
    (filter === 'all' || (filter === 'review' ? row.variance !== 0 : row.variance === 0)));
}
function renderCase() {
  const c = data.cases[selected];
  browserAI.select(c, data.procedures);
  byId('case-content').hidden = !c;
  byId('case-empty').hidden = Boolean(c);
  if (!c) { text('case-heading', 'Select a stock record'); return; }
  const r = c.item;
  text('case-heading', r.sku + ' — ' + r.name);
  text('case-meta', 'Bin ' + r.bin + ' · System ' + r.system + ' · Physical ' + r.physical);
  text('case-variance', signed(r.variance));
  text('case-value', money(r.value_variance));
  text('evidence', r.evidence);
  text('hypothesis', c.hypothesis);
  text('conclusion', c.conclusion);
  byId('case-procedures').replaceChildren(...c.procedure_ids.map(procedure));
  text('report-preview', data.reports[selected]);
}
function renderStock() {
  const rows = visibleRows();
  if (!rows.some(row => row.sku === selected)) selected = rows[0]?.sku ?? null;
  const body = byId('stock-body'); body.replaceChildren();
  text('count', rows.length + ' of ' + data.stock.length + ' records');
  if (!rows.length) {
    const tr = node('tr'), td = node('td', 'No matching stock records.');
    td.colSpan = 6; tr.append(td); body.append(tr);
  }
  for (const row of rows) {
    const tr = node('tr'), first = node('td'), button = node('button', row.sku, 'sku');
    button.type = 'button';
    button.dataset.sku = row.sku;
    button.setAttribute('aria-pressed', String(row.sku === selected));
    button.append(node('small', row.name));
    button.addEventListener('click', () => {
      selected = row.sku;
      body.querySelectorAll('button[data-sku]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.sku === selected)));
      renderCase();
    });
    first.append(button); tr.append(first);
    [row.bin,row.system,row.physical,signed(row.variance)].forEach(v => tr.append(node('td', v)));
    tr.append(node('td', row.status, row.variance ? 'review' : 'match'));
    body.append(tr);
  }
  renderCase();
}
function downloadReport() {
  if (!selected) return;
  const url = URL.createObjectURL(new Blob([data.reports[selected]], {type:'text/markdown;charset=utf-8'}));
  const a = node('a'); a.href = url; a.download = selected + '-investigation.md';
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function initialise() {
  try {
    const response = await fetch('./demo-data.json', {credentials:'omit', redirect:'error'});
    if (!response.ok) throw new Error('Data unavailable');
    data = await response.json();
    if (data.schema_version !== 1 || data.synthetic !== true || !Array.isArray(data.stock)) throw new Error('Invalid demo data');
    const s = data.summary;
    text('metric-skus', s.skus); text('metric-exceptions', s.exceptions);
    text('metric-accuracy', s.exact_match_pct.toFixed(1) + '%');
    text('metric-value', money(s.absolute_value));
    byId('procedure-library').replaceChildren(...Object.keys(data.procedures).map(procedure));
    byId('search').addEventListener('input', renderStock);
    byId('filter').addEventListener('change', renderStock);
    byId('reset').addEventListener('click', () => { byId('search').value = ''; byId('filter').value = 'all'; renderStock(); });
    byId('download').addEventListener('click', downloadReport);
    renderStock(); byId('workspace').hidden = false;
    text('status', 'Sample data loaded · All records are fictional.');
  } catch {
    byId('workspace').hidden = true;
    text('status', 'Unable to load the demonstration. Serve the docs directory over HTTP and reload.');
  }
}
initialise();
