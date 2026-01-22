import pytest
from playwright.sync_api import sync_playwright

import config

BASE = config.base_url_api

@pytest.fixture(scope="session")
def api():
    with sync_playwright() as p:
        req = p.request.new_context(base_url=BASE)
        yield req
        req.dispose()

@pytest.mark.parametrize("tn", ["6313616", "7234258", "9442984", "1094442"])
def test_tracking_valid(api, tn):
    r = api.get(f"/shipments/track/{tn}")
    assert r.status == 200
    body = r.json()
    assert isinstance(body, dict)

@pytest.mark.parametrize("tn", ["", "   ", "!!!", "<script>alert(1)</script>", "1"*200])
def test_tracking_invalid(api, tn):
    r = api.get(f"/shipments/track/{tn}")
    assert r.status in (400,404, 500, 429)
