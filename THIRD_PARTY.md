# Third-party components

The owner approved the MIT licence for original project code and documentation on 26 November 2026. It does not relicense third-party assets.

| Component | Version or revision | Upstream licence and source |
| --- | --- | --- |
| Transformers.js | 3.8.1 | [Apache-2.0](https://github.com/huggingface/transformers.js/blob/3.8.1/LICENSE) |
| SmolLM2-135M-Instruct | 1aa2c784701448c41116d0470738b551c29a99d2, q4 ONNX | [Apache-2.0 model card](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct/tree/1aa2c784701448c41116d0470738b551c29a99d2) |
| ONNX Runtime Web | bundled by Transformers.js | [MIT](https://github.com/microsoft/onnxruntime/blob/main/LICENSE) |
| Python packages | exact versions in requirements files | upstream package metadata and licences; installed separately |

No third-party weights or runtime bundles are redistributed in this repository. Browser downloads come directly from upstream public hosts. If assets are later vendored, retain applicable licence and notice files and review all bundled dependencies. The table is not a comprehensive legal or transitive dependency audit.

The CI asset audit checks the registry package against its published integrity digest, the CDN entry against the registry package, and the q4 model weight against the pinned revision's upstream SHA-256. It is an independent check at test time; it does not enforce integrity of every browser download, tokenizer, WASM file or transitive module.

The release audit additionally pins the observed development CI SHA-256 digests for the CDN entry and q4 weight. This does not verify all browser assets at runtime.
