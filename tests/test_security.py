"""Regression tests for the demo trust boundaries."""
import pytest

from inventory import mcp_server
from tests.api_client import request


def test_api_headers_and_host():
    response = request("GET", "/summary")
    assert response.status_code == 200
    for name, expected in {
        "x-content-type-options": "nosniff", "x-frame-options": "DENY",
        "referrer-policy": "no-referrer", "cache-control": "no-store",
    }.items():
        assert response.headers[name] == expected
    assert request("GET", "/summary", headers={"Host": "untrusted.example"}).status_code == 400
    assert request("DELETE", "/stock").status_code == 405


def test_ai_post_origin_and_no_paid_provider():
    path = "/ai/explain/SKU-101"
    assert request("POST", path, headers={"Origin": "https://untrusted.example"}).status_code == 403
    assert request("POST", path).json()["mode"] == "offline"
    assert request("POST", path, headers={"X-Inventory-AI": "live"}).json()["mode"] == "offline"


def test_mcp_annotations_and_invalid_inputs():
    assert mcp_server.READ_ONLY.readOnlyHint is True
    assert mcp_server.READ_ONLY.destructiveHint is False
    for fn in (mcp_server.investigate_sku, mcp_server.generate_report, mcp_server.get_procedure):
        with pytest.raises(ValueError, match="Unknown"):
            fn("../not-a-record")
