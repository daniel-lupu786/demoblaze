from datetime import datetime, UTC
import logging
import os

import pytest
from playwright.sync_api import sync_playwright

from utils.logging_config import _configure_logging


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chromium")
    parser.addoption("--headed", action="store_true", help="Run headed")
    parser.addoption("--slowmo", action="store", default="0", help="Slow motion in ms")
    parser.addoption(
        "--enable-logging",
        action="store_true",
        help="Enable framework logging"
    )

@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright, pytestconfig):
    browser_name = pytestconfig.getoption("--browser")
    headed = pytestconfig.getoption("--headed")
    slowmo = int(pytestconfig.getoption("--slowmo"))

    b = getattr(playwright, browser_name).launch(
        headless=not headed,
        slow_mo=slowmo if slowmo > 0 else None,
    )
    yield b
    b.close()

@pytest.fixture
def context(browser, request):
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    yield ctx
    ctx.close()

@pytest.fixture
def page(context, log):
    p = context.new_page()

    # Browser console logs
    p.on("console", lambda msg: log.info("BROWSER CONSOLE [%s]: %s", msg.type, msg.text))

    # Page errors (JS errors)
    p.on("pageerror", lambda err: log.error("PAGE ERROR: %s", err))

    # Failed network requests
    p.on("requestfailed", lambda req: log.warning("REQUEST FAILED: %s %s", req.method, req.url))

    yield p
    p.close()

def pytest_configure(config):
    if config.getoption("--enable-logging"):
        _configure_logging()
    else:
        logging.disable(logging.CRITICAL)

@pytest.fixture
def log(request):
    """
    Logger pro Test
    """
    return logging.getLogger(request.node.name)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    On test failure, capture a full-page screenshot (if 'page' fixture exists).
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page", None)
        if page:
            os.makedirs("artifacts", exist_ok=True)
            ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            path = f"artifacts/screenshots/{item.name}_{ts}.png"
            try:
                page.screenshot(path=path, full_page=True)
                logging.getLogger(item.name).error("Saved screenshot -> %s", path)
            except Exception as e:
                logging.getLogger(item.name).error("Failed to save screenshot: %s", e)
