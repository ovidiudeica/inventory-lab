"""Chromium regression tests and opt-in real local model evaluation."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def url():
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / "docs"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/"
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        instance = p.chromium.launch()
        yield instance
        instance.close()


def test_dashboard_and_search(browser, url):
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(url)
    expect(page.locator("#metric-skus")).to_have_text("6")
    expect(page.locator("#metric-exceptions")).to_have_text("4")
    expect(page.locator("#metric-accuracy")).to_have_text("33.3%")
    expect(page.locator("#metric-value")).to_have_text("£406.50")
    expect(page.locator("#stock-body tr")).to_have_count(6)
    page.locator("#filter").select_option("review")
    expect(page.locator("#stock-body tr")).to_have_count(4)
    page.locator("#search").fill("cable")
    expect(page.locator("#count")).to_have_text("1 of 6 records")
    expect(page.locator("#case-heading")).to_contain_text("SKU-106")
    expect(page.locator("#case-value")).to_have_text("-£260.00")
    page.locator("#search").fill("not-a-sku")
    expect(page.locator("#stock-body")).to_contain_text("No matching stock records.")
    expect(page.locator("#case-content")).to_be_hidden()
    page.locator("#reset").click()
    expect(page.locator("#stock-body tr")).to_have_count(6)
    page.locator("#filter").select_option("match")
    expect(page.locator("#stock-body tr")).to_have_count(2)
    expect(page.locator("#case-procedures article")).to_have_count(1)
    assert errors == []
    page.close()


def test_report_and_procedures(browser, url):
    from inventory.core import report
    page = browser.new_page(accept_downloads=True)
    page.goto(url)
    page.get_by_role("button", name="SKU-103 Control bracket").click()
    expect(page.locator("#case-heading")).to_contain_text("SKU-103")
    expect(page.locator("#case-variance")).to_have_text("+4")
    expect(page.locator("#case-procedures article")).to_have_count(3)
    expect(page.locator("#procedure-library article")).to_have_count(3)
    expect(page.locator("#conclusion")).to_contain_text("Unverified hypothesis")
    with page.expect_download() as download:
        page.get_by_role("button", name="Download Markdown report").click()
    result = download.value
    assert result.suggested_filename == "SKU-103-investigation.md"
    assert result.path().read_text(encoding="utf-8") == report("SKU-103")
    page.close()


def test_mobile_and_failed_data_load(browser, url):
    page = browser.new_page(viewport={"width": 375, "height": 812})
    page.goto(url)
    expect(page.locator("#workspace")).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.get_by_role("button", name="SKU-101 Bearing housing").focus()
    page.keyboard.press("Enter")
    expect(page.locator("#case-heading")).to_contain_text("SKU-101")
    page.route("**/demo-data.json", lambda route: route.fulfill(status=503, body="Unavailable"))
    page.reload()
    expect(page.locator("#status")).to_contain_text("Unable to load")
    expect(page.locator("#workspace")).to_be_hidden()
    page.close()


def test_untrusted_text_is_not_executed(browser, url):
    import json
    payload = json.loads((ROOT / "docs" / "demo-data.json").read_text(encoding="utf-8"))
    payload["cases"]["SKU-101"]["item"]["evidence"] = '<img src=x onerror="window.compromised=true">'
    page = browser.new_page()
    page.route("**/demo-data.json", lambda route: route.fulfill(json=payload))
    page.goto(url)
    expect(page.locator("#evidence")).to_contain_text("<img src=x")
    assert page.locator("#evidence img").count() == 0
    assert not page.evaluate("Boolean(window.compromised)")
    page.close()


def test_ai_opt_in_and_result(browser, url):
    page = browser.new_page()
    external = []
    page.on("request", lambda req: external.append(req.url) if not req.url.startswith(url) else None)
    page.route("**/ai-worker.js", lambda route: route.fulfill(content_type="text/javascript", body=
        "self.onmessage=({data})=>{if(data.prompt.includes('SOP-01') && data.prompt.includes('SKU-101')) self.postMessage({type:'result',text:'B'});else self.postMessage({type:'error'});};"))
    page.goto(url)
    expect(page.locator("#ai-mode")).to_contain_text("Deterministic")
    assert external == []
    page.locator("#ai-start").click()
    expect(page.locator("#ai-mode")).to_contain_text("AI-assisted focus")
    expect(page.locator("#ai-output")).to_contain_text("AI-selected investigation focus: SOP-02")
    assert page.locator("#ai-output").get_attribute("data-choice") == "B"
    page.get_by_role("button", name="SKU-103 Control bracket").click()
    expect(page.locator("#ai-mode")).to_contain_text("Deterministic")
    assert external == []
    page.close()


def test_ai_failure_and_cancel(browser, url):
    page = browser.new_page()
    page.route("**/ai-worker.js", lambda route: route.fulfill(content_type="text/javascript", body=
        "self.onmessage=()=>self.postMessage({type:'error'});"))
    page.goto(url)
    page.locator("#ai-start").click()
    expect(page.locator("#ai-status")).to_contain_text("Model unavailable")
    expect(page.locator("#ai-mode")).to_contain_text("Deterministic")
    page.unroute("**/ai-worker.js")
    page.route("**/ai-worker.js", lambda route: route.fulfill(content_type="text/javascript", body="self.onmessage=()=>{};"))
    page.locator("#ai-start").click()
    page.locator("#ai-cancel").click()
    expect(page.locator("#ai-status")).to_contain_text("Cancelled")
    expect(page.locator("#report-preview")).to_contain_text("SKU-101")
    page.close()


def test_real_browser_model(browser, url):
    """Evaluate all six real-model selections and independently verify every displayed line."""
    import json
    import os
    from urllib.parse import urlsplit
    from inventory.core import stock, investigate, report
    if os.getenv("INVENTORY_REAL_MODEL_TEST") != "1":
        pytest.skip("Enable INVENTORY_REAL_MODEL_TEST=1 for the public model download.")
    page = browser.new_page()
    requests = []
    page.context.on("request", lambda req: requests.append((req.method, req.url)))
    page.goto(url)
    expect(page.locator("#workspace")).to_be_visible()
    assert all(target.startswith(url) for _, target in requests)
    for row in stock():
        sku = row["sku"]
        page.locator(f'button[data-sku="{sku}"]').click()
        page.locator("#ai-start").click()
        expect(page.locator("#ai-mode")).to_contain_text("AI-assisted focus", timeout=125000)
        draft = page.locator("#ai-output").inner_text()
        assert draft.strip()
        case = investigate(sku)
        code = page.locator("#ai-output").get_attribute("data-choice")
        assert code in {"A", "B", "C"}
        options = [("SOP-01",0),("SOP-01",1),("SOP-01",2)] if row["variance"] == 0 else [("SOP-01",1),("SOP-02",0),("SOP-02",2)]
        from inventory.core import PROCEDURES
        pid, index = options["ABC".index(code)]
        assert pid in case["procedure_ids"]
        variance = f'{row["variance"]:+d}' if row["variance"] > 0 else str(row["variance"])
        expected = "\n".join([
            f"Observed variance: {variance} units (physical minus system).",
            "Evidence: " + row["evidence"],
            "Possible explanation: " + case["hypothesis"],
            "Conclusion: " + case["conclusion"],
            "AI-selected investigation focus: " + pid + " — " + PROCEDURES[pid]["steps"][index],
            "Required procedures: " + ", ".join(case["procedure_ids"]) + ".",
            "The selected focus does not replace, reorder or authorise any procedure. Verify all evidence and follow the complete SOPs.",
        ])
        assert draft == expected
        assert page.locator("#report-preview").text_content() == report(sku)
        print("AI_EVALUATION " + json.dumps({
            "sku": sku, "variance": row["variance"], "evidence": row["evidence"],
            "hypothesis": investigate(sku)["hypothesis"],
            "allowed_sops": investigate(sku)["procedure_ids"], "selection": code, "selected_sop": pid, "validated_explanation": draft
        }, ensure_ascii=True))
    hosts = set()
    for method, target in requests:
        assert method in {"GET", "HEAD", "OPTIONS"}
        if target.startswith(url):
            continue
        parsed = urlsplit(target)
        if parsed.scheme in {"blob", "data"}:
            continue
        assert parsed.scheme == "https"
        host = parsed.hostname or ""
        assert host in {"cdn.jsdelivr.net", "huggingface.co"} or host.endswith((".hf.co", ".huggingface.co")), host
        hosts.add(host)
    assert "cdn.jsdelivr.net" in hosts and "huggingface.co" in hosts
    print("AI_PUBLIC_ASSET_HOSTS " + ", ".join(sorted(hosts)))
    page.close()


@pytest.mark.parametrize("invalid", ["SOP-04", "A and B", "<img src=x onerror=alert(1)>", "", "A\nSOP-05", None, 1])
def test_invalid_model_output_falls_back(browser, url, invalid):
    import json
    page = browser.new_page()
    body = "self.onmessage=()=>self.postMessage(" + json.dumps({"type":"result","text":invalid}) + ");"
    page.route("**/ai-worker.js", lambda route: route.fulfill(content_type="text/javascript", body=body))
    page.goto(url)
    page.locator("#ai-start").click()
    expect(page.locator("#ai-status")).to_contain_text("Model output rejected")
    expect(page.locator("#ai-mode")).to_contain_text("Deterministic")
    expect(page.locator("#ai-output")).to_contain_text("Unverified hypothesis")
    assert page.locator("#ai-output").get_attribute("data-choice") is None
    assert page.locator("#ai-output img").count() == 0
    page.close()


def test_match_case_only_permitted_sop(browser, url):
    page = browser.new_page()
    page.route("**/ai-worker.js", lambda route: route.fulfill(content_type="text/javascript", body="self.onmessage=()=>self.postMessage({type:'result',text:'C'});"))
    page.goto(url)
    page.locator('button[data-sku="SKU-102"]').click()
    page.locator("#ai-start").click()
    expect(page.locator("#ai-mode")).to_contain_text("AI-assisted focus")
    expect(page.locator("#ai-output")).to_contain_text("SOP-01 — Record quantity, time and evidence.")
    assert "SOP-02" not in page.locator("#ai-output").inner_text()
    assert "SOP-03" not in page.locator("#ai-output").inner_text()
    page.close()
