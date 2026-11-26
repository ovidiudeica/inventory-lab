"""Loopback-only demonstration API; not an authenticated multi-user service."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from .core import stock, summary, investigate, report, PROCEDURES
from .ai import explain

app = FastAPI(title="Inventory Investigation Lab", version="1.0.0-rc.1")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    # The static demo never needs cross-origin API access.
    if request.method == "POST" and (
        request.headers.get("origin") is not None
        or request.headers.get("sec-fetch-site") in {"cross-site", "same-site"}
    ):
        response = JSONResponse({"detail": "Browser-origin POST requests are not accepted."}, status_code=403)
    else:
        response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


def lookup(fn, sku):
    try:
        return fn(sku)
    except KeyError:
        raise HTTPException(404, "Unknown SKU") from None


@app.get("/stock")
def get_stock(): return stock()


@app.get("/summary")
def get_summary(): return summary()


@app.get("/procedures")
def get_procedures(): return PROCEDURES


@app.get("/investigations/{sku}")
def get_case(sku: str): return lookup(investigate, sku)


@app.get("/reports/{sku}", response_class=PlainTextResponse)
def get_report(sku: str): return lookup(report, sku)


@app.post("/ai/explain/{sku}")
def get_explanation(sku: str):
    return lookup(explain, sku)
