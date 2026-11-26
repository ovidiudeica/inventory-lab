# Browser AI and zero-cost architecture

InventoryLab uses Transformers.js 3.8.1 and the pinned SmolLM2-135M-Instruct q4 ONNX model in a browser worker, using CPU WebAssembly. No paid inference, API keys or remote generation service are included. The Python engine remains the source of facts and SOPs.

## Quality control

Development CI showed that unconstrained generation produced repetitive text and invented procedure identifiers. The application therefore uses constrained one-token selection instead of free-form advice. Three permitted investigation focus options are derived from the selected case's SOPs. The model selects A, B or C with other first-token IDs suppressed. The application independently accepts only a single allowed letter, maps it to the canonical procedure step, and builds the explanation from the exact Python export. No arbitrary model prose is displayed. Invalid output, timeout, cancellation or model failure returns deterministic guidance. All SOPs remain required; a focus is neither an ordering nor an authorisation. The downloadable report never changes.

This is AI-assisted selection, not autonomous root-cause reasoning or free-form generative reporting. The model selected the first permitted option in all six evaluated cases; this does not demonstrate discriminative reasoning. It can select a less useful permitted focus. All available choices are safe training checks, and no selection changes an inventory record. Human review is still required.

## Downloads and privacy

The default dashboard uses same-origin static assets. Explicit opt-in downloads the runtime from jsDelivr and model assets from Hugging Face and its file storage; these may receive ordinary download metadata. No user-entered prompts or real records are used. All computation is on the visitor's device. There is no mandatory installation, but a potentially substantial download, device memory, electricity and metered data may be required. Source code, configuration, tests and release documentation are maintained in GitHub; upstream assets are not hosted by this repository.

## Testing and integrity

CI tests all six real-model selections, exact canonical output, unchanged reports, observed network methods and hosts, invalid model output and fallback. The independent asset audit compares public metadata, registry and CDN content, and pinned model weights against the SHA-256 values recorded during development CI. This is not browser-enforced runtime integrity or a complete transitive supply-chain audit.

## Cost policy

Standard GitHub runners within the included allocation and zero-spend budgets only. No paid inference, subscription, GPU runner, external compute service or automatic purchase. Pages publication and visibility changes require owner approval. See [RELEASE.md](RELEASE.md) and [THIRD_PARTY.md](THIRD_PARTY.md).
