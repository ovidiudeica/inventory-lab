// Only canonical facts and approved SOP text reach the user-facing explanation.
export function choicesFor(c, procedures) {
  const choices = c.item.variance === 0
    ? [['SOP-01',0],['SOP-01',1],['SOP-01',2]]
    : [['SOP-01',1],['SOP-02',0],['SOP-02',2]];
  return choices.map(([id,index],i)=>{
    if (!c.procedure_ids.includes(id) || typeof procedures[id]?.steps[index] !== 'string') {
      throw new Error('Invalid procedure configuration');
    }
    return {code:'ABC'[i], id, step:procedures[id].steps[index]};
  });
}
export function makePrompt(c, procedures) {
  const r = c.item;
  return [
    'Choose one useful investigation focus from the permitted options.',
    'All required procedures still apply. Never authorise an adjustment.',
    'Case: ' + r.sku + '; physical minus system = ' + r.variance + '.',
    'Evidence: ' + r.evidence + '. Possible explanation: ' + c.hypothesis,
    ...choicesFor(c,procedures).map(x=>x.code + ': ' + x.id + ' — ' + x.step),
    'Answer with exactly one letter: A, B or C.',
  ].join('\n');
}
export function validatedExplanation(raw, c, procedures) {
  if (typeof raw !== 'string' || !/^[ABC]$/.test(raw.trim())) return null;
  const choice = choicesFor(c,procedures).find(x=>x.code===raw.trim());
  if (!choice) return null;
  const r = c.item;
  return {
    choice,
    text: [
      'Observed variance: ' + (r.variance>0?'+':'') + r.variance + ' units (physical minus system).',
      'Evidence: ' + r.evidence,
      'Possible explanation: ' + c.hypothesis,
      'Conclusion: ' + c.conclusion,
      'AI-selected investigation focus: ' + choice.id + ' — ' + choice.step,
      'Required procedures: ' + c.procedure_ids.join(', ') + '.',
      'The selected focus does not replace, reorder or authorise any procedure. Verify all evidence and follow the complete SOPs.',
    ].join('\n'),
  };
}
