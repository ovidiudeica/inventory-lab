# REST API and MCP reference

## REST API (local)

Run `python -m uvicorn inventory.api:app --host 127.0.0.1 --port 8001`. Swagger UI is available at http://127.0.0.1:8001/docs.

| Method | Path | Response |
| --- | --- | --- |
| GET | /stock | JSON array of synthetic stock records |
| GET | /summary | JSON aggregate metrics |
| GET | /procedures | JSON object of fictional SOPs |
| GET | /investigations/{sku} | JSON investigation, evidence, hypothesis and procedure identifiers |
| GET | /reports/{sku} | Plain-text Markdown report |
| POST | /ai/explain/{sku} | Deterministic JSON explanation, procedure references and warning |

Unknown SKUs return HTTP 404. The explanation endpoint always uses deterministic guidance, has no network provider and never changes stock. The host allowlist permits localhost and 127.0.0.1 only. Browser-origin POSTs are rejected.

Examples:

```sh
curl http://127.0.0.1:8001/summary
curl http://127.0.0.1:8001/investigations/SKU-101
curl -X POST http://127.0.0.1:8001/ai/explain/SKU-101
```

## MCP server

Run `python -m inventory.mcp_server` from the repository root using the project's virtual environment. The server uses stdio; connect a compatible client rather than typing into the terminal.

| Tool | Arguments | Output |
| --- | --- | --- |
| get_stock_summary | None | Aggregate metrics |
| investigate_sku | sku (string) | Investigation record |
| get_procedure | procedure_id (string) | Fictional SOP |
| generate_report | sku (string) | Markdown report |

Example client configuration (adapt the absolute paths to your machine and your client's configuration format):

```json
{
  "mcpServers": {
    "inventory-lab": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "inventory.mcp_server"],
      "cwd": "/absolute/path/to/inventory-lab"
    }
  }
}
```

If a client does not support `cwd`, launch it from the repository root or configure its working directory using its documented mechanism. Windows uses the virtual environment's `Scripts\\python.exe`. Tool errors are returned for unknown identifiers. The server does not invoke any external AI provider.

## Browser AI

Optional generative inference takes place in the browser, not in the REST API or MCP server. See [AI.md](AI.md). No API key or paid inference service is used.
