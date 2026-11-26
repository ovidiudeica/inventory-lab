# Inventory Investigation Lab

A small, read-only engineering portfolio project for inventory analysis, discrepancy investigation, procedural guidance and reporting. It bridges warehouse domain knowledge with Python, REST APIs, MCP and optional generative AI.

**Synthetic data only.** All records and procedures are fictional. This is not an operational ERP or a validated production system, and is not affiliated with any employer.

## Features

- Six synthetic stock records, aggregate metrics and signed quantity/GBP variances.
- Evidence-led investigations with explicitly unverified hypotheses.
- Fictional SOP library and downloadable Markdown investigation reports.
- Responsive static dashboard driven by a Python-generated JSON snapshot.
- FastAPI REST service, read-only MCP tools, and optional browser-based AI-assisted investigation focus.

The static website uses a deterministic Python export. Optional generative AI runs on the visitor's device after explicit consent to download public assets. No commercial inference adapter or API credentials are required. See [Browser AI and cost policy](AI.md).

## Live demonstration

The static dashboard is designed for [GitHub Pages](https://ovidiudeica.github.io/inventory-lab/). Once deployed, it requires no installation or API key. The REST API and MCP server are local development components, not hosted endpoints.

## Run locally

Requires Python 3.12. From the repository root, create and activate a virtual environment, then run:

```sh
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m inventory.build_demo
python -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open http://127.0.0.1:8000 in a browser. Do not open index.html directly from the file system.

In a separate activated terminal, start the REST API:

```sh
python -m uvicorn inventory.api:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001/docs for the interactive API documentation. For MCP and deterministic explanations, see [API and MCP guide](API.md).

## Test

```sh
python -m pip check
python -m inventory.build_demo --check
python -m pytest tests -q -ra
python -m pip install -r requirements-web.txt
python -m playwright install chromium
python -m pytest web_tests -q -ra
```

CI runs the Python regression tests, MCP stdio integration, JSON consistency checks and Chromium browser tests. On Linux, browser system packages may require `python -m playwright install --with-deps chromium`.

## Documentation

- [Architecture, metrics and limitations](TECHNICAL.md)
- [REST API and MCP reference](API.md)

- [Browser AI and zero-cost architecture](AI.md)
- [Security policy and audit procedure](SECURITY.md)
- [Release acceptance and publication runbook](RELEASE.md)
- [Third-party licences](THIRD_PARTY.md)
- [Changelog](CHANGELOG.md)

## Version and licence

Version 1.0.0. The release is subject to successful CI, privacy checks and deployment verification. See [CHANGELOG.md](CHANGELOG.md) and [RELEASE.md](RELEASE.md). Original project code is licensed under [MIT](LICENSE); third-party assets retain their upstream licences. This is a synthetic engineering demonstration, not an operational inventory system. The browser model selects a permitted focus; it does not establish autonomous reasoning.
