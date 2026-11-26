# Changelog

## 1.0.0 — first public release prepared

- Read-only inventory investigation and reporting with six synthetic stock records, GBP variance metrics and fictional SOPs.
- Python core, local FastAPI REST service and MCP stdio server; reproducible JSON export and static dashboard.
- Optional on-device SmolLM2 inference selects a permitted investigation focus; independent validation renders canonical facts and SOP text, with deterministic fallback.
- Browser download consent, progress and cancellation; no commercial inference API or credentials.
- Regression coverage for backend, MCP round trip, reports, browser behaviour, all six real-model cases and invalid outputs.
- Pinned dependencies, vulnerability checks, reachable Git history and commit metadata privacy checks, and upstream model/runtime integrity checks.
- MIT licence for original project code; public static deployment via GitHub Pages is subject to final verification.

### Known limitations

- The model selected the first permitted option in all six evaluated cases; discriminative reasoning is not demonstrated.
- The REST API and MCP server are intended for local use, not public hosting.
- MCP 2.x migration is deferred because of API incompatibility. Runtime asset integrity is checked in CI, not enforced for every browser download.
- This is a training and portfolio demonstration, not a production ERP or authorisation system.
