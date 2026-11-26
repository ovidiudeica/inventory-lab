// Browser-only inference. No remote inference endpoint or API key.
const MODEL = 'HuggingFaceTB/SmolLM2-135M-Instruct';
const REVISION = '1aa2c784701448c41116d0470738b551c29a99d2';
let generator, busy = false, suppressedTokens;
self.onmessage = async ({data}) => {
  if (busy || data?.type !== 'generate' || typeof data.prompt !== 'string' || data.prompt.length > 10000) return;
  busy = true;
  try {
    if (!generator) {
      self.postMessage({type:'progress', text:'Loading AI runtime…'});
      const {pipeline, env} = await import('https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1');
      env.allowLocalModels = false;
      env.allowRemoteModels = true;
      env.useBrowserCache = true;
      env.backends.onnx.wasm.numThreads = 1;
      env.backends.onnx.wasm.proxy = false;
      generator = await pipeline('text-generation', MODEL, {
        revision: REVISION, device:'wasm', dtype:'q4',
        progress_callback: info => {
          const pct = Number.isFinite(info.progress) ? Math.round(info.progress) + '%' : '';
          self.postMessage({type:'progress', text:'Loading model assets… ' + pct});
        },
      });
      // Restrict the first and only generated token to single-token letter variants.
      const ids = new Set();
      for (const letter of ['A','B','C',' A',' B',' C']) {
        const tokens = generator.tokenizer.encode(letter,{add_special_tokens:false});
        if (tokens.length === 1) ids.add(Number(tokens[0]));
      }
      const size = generator.model.config.vocab_size;
      if (!Number.isSafeInteger(size) || size < 3 || size > 1000000 || ids.size < 3 ||
          [...ids].some(id=>id<0 || id>=size)) throw new Error('Invalid choice vocabulary');
      suppressedTokens = Array.from({length:size},(_,i)=>i).filter(i=>!ids.has(i));
    }
    self.postMessage({type:'progress', text:'Selecting an approved focus on this device…'});
    const result = await generator([{role:'system',content:'Select one of the supplied letters only.'},{role:'user',content:data.prompt}], {
      max_new_tokens:1, do_sample:false, return_full_text:false,
      begin_suppress_tokens:suppressedTokens, forced_eos_token_id:null,
    });
    const generated = result?.[0]?.generated_text;
    const text = typeof generated === 'string' ? generated : Array.isArray(generated) ? generated.at(-1)?.content : '';
    self.postMessage({type:'result', text:typeof text === 'string' && text.length <= 16 ? text.trim() : ''});
  } catch {
    self.postMessage({type:'error'});
  } finally {
    busy = false;
  }
};
