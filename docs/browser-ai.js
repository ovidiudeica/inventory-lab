import {makePrompt, validatedExplanation} from './ai-quality.js';

export function setupBrowserAI() {
  const el = id => document.getElementById(id);
  let worker = null, timer = null, current = null, currentSku = undefined;
  function stop() {
    clearTimeout(timer);
    timer = null;
    if (worker) worker.terminate();
    worker = null;
    el('ai-start').disabled = false;
    el('ai-cancel').disabled = true;
  }
  function fallback(message) {
    stop();
    el('ai-status').textContent = message;
    el('ai-mode').textContent = 'Deterministic guidance (not AI-generated)';
    el('ai-output').textContent = current ? current.case.hypothesis + ' ' + current.case.conclusion : '';
    delete el('ai-output').dataset.choice;
  }
  function select(c, procedures) {
    if (currentSku === (c?.item.sku ?? null)) return;
    current = c ? {case:c,procedures} : null;
    currentSku = c?.item.sku ?? null;
    fallback('Optional model is not loaded. The original report remains available.');
  }
  el('ai-cancel').addEventListener('click',()=>fallback('Cancelled. Deterministic guidance remains available.'));
  el('ai-start').addEventListener('click',()=>{
    if (!current || el('ai-start').disabled) return;
    el('ai-start').disabled = true;
    el('ai-cancel').disabled = false;
    el('ai-mode').textContent = 'Deterministic guidance (not AI-generated)';
    el('ai-output').textContent = current.case.hypothesis + ' ' + current.case.conclusion;
    delete el('ai-output').dataset.choice;
    el('ai-status').textContent = 'Starting optional model…';
    try {
      if (!worker) worker = new Worker(new URL('./ai-worker.js',import.meta.url),{type:'module'});
      const active = worker;
      active.onmessage = ({data})=>{
        if (worker !== active || timer === null) return;
        if (data?.type === 'progress') el('ai-status').textContent = 'Model loading or selecting a focus…';
        else if (data?.type === 'result') {
          let validated;
          try { validated = validatedExplanation(data.text,current.case,current.procedures); }
          catch { validated = null; }
          if (!validated) { fallback('Model output rejected. Deterministic guidance remains available.'); return; }
          clearTimeout(timer);
          timer = null;
          el('ai-mode').textContent = 'AI-assisted focus — validated against the supplied SOPs';
          el('ai-output').textContent = validated.text;
          el('ai-output').dataset.choice = validated.choice.code;
          el('ai-status').textContent = 'Focus selected on this device. Verify before use.';
          el('ai-start').disabled = false;
          el('ai-cancel').disabled = true;
        } else fallback('Model unavailable. Deterministic guidance remains available.');
      };
      active.onerror = ()=>{if(worker===active) fallback('Model unavailable. Deterministic guidance remains available.');};
      timer = setTimeout(()=>fallback('Model timed out. Deterministic guidance remains available.'),120000);
      active.postMessage({type:'generate',prompt:makePrompt(current.case,current.procedures)});
    } catch { fallback('Model unavailable. Deterministic guidance remains available.'); }
  });
  return {select};
}
