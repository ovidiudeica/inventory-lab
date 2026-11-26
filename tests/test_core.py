import pytest
from inventory.core import stock, summary, investigate, report, PROCEDURES
from inventory.ai import explain
from tests.api_client import request

def test_summary():
    assert summary()==dict(skus=6,exceptions=4,system_units=489,physical_units=479,net_variance=-10,absolute_variance=18,absolute_value=406.5,exact_match_pct=33.3)

def test_signed_variance():
    assert investigate('SKU-103')['item']['variance']==4
    assert investigate('SKU-106')['item']['value_variance']==-260

def test_hypotheses():
    for r in stock():
        case=investigate(r['sku'])
        assert all(p in PROCEDURES for p in case['procedure_ids'])
        if r['variance']: assert 'Unverified' in case['conclusion']

def test_unknown():
    with pytest.raises(KeyError): investigate('INVALID')
    assert request("GET", '/investigations/INVALID').status_code==404
    assert request("POST", '/ai/explain/INVALID').status_code==404

def test_report():
    assert 'Synthetic data only' in report('SKU-101')
    assert 'SOP-03' in report('SKU-101')
    assert 'SOP-03' not in report('SKU-102')

def test_api():
    assert request("GET", '/summary').json()==summary()
    assert len(request("GET", '/stock').json())==6
    assert request("GET", '/reports/SKU-101').text==report('SKU-101')
    assert request("GET", '/procedures').json()==PROCEDURES

def test_offline(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-only")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")
    assert explain("SKU-101")["mode"] == "offline"
    response = request("POST", "/ai/explain/SKU-101")
    assert response.json() == explain("SKU-101")
    assert set(response.json()["procedures"]) == {"SOP-01", "SOP-02", "SOP-03"}


def test_legacy_live_header_cannot_enable_provider(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-only")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")
    import socket
    def denied(*args, **kwargs):
        raise AssertionError("Network access is forbidden")
    monkeypatch.setattr(socket.socket, "connect", denied)
    response = request("POST", "/ai/explain/SKU-101", headers={"X-Inventory-AI": "live"})
    assert response.status_code == 200
    assert response.json()["mode"] == "offline"
