"""Local MCP stdio server; exposes read-only tools only."""
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from . import core

mcp = FastMCP("inventory-lab")
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


def known_sku(sku: str) -> str:
    if sku not in {row["sku"] for row in core.stock()}:
        raise ValueError("Unknown SKU")
    return sku


@mcp.tool(annotations=READ_ONLY)
def get_stock_summary() -> dict:
    """Calculate aggregate metrics for synthetic stock."""
    return core.summary()


@mcp.tool(annotations=READ_ONLY)
def investigate_sku(sku: str) -> dict:
    """Return evidence and unverified hypotheses for one synthetic SKU."""
    return core.investigate(known_sku(sku))


@mcp.tool(annotations=READ_ONLY)
def get_procedure(procedure_id: str) -> dict:
    """Read a fictional operating procedure."""
    if procedure_id not in core.PROCEDURES:
        raise ValueError("Unknown procedure")
    return core.PROCEDURES[procedure_id]


@mcp.tool(annotations=READ_ONLY)
def generate_report(sku: str) -> str:
    """Generate a read-only Markdown investigation report."""
    return core.report(known_sku(sku))


if __name__ == "__main__":
    mcp.run(transport="stdio")
