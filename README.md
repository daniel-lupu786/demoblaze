# Test Automation Assessment – Playwright (sync) + pytest

This repository contains an automated test solution developed as part of a test automation assessment.

The focus is on:
- clean architecture
- reusable components (Page Objects)
- basic data strategy
- logging and reporting
- robustness and maintainability over completeness

---


## Setup
Precondition:
Python 3.X is already installed (recommended 3.13)

### Install dependencies

```bash
pip install playwright
playwright install
pip install -r requirements.txt
````

---
## Running Tests
Default (headless)
```bash
pytest
````

Headed mode
```bash
pytest --headed
````

Browser selection
```bash
pytest --browser chromium

````
```bash
pytest --browser firefox
````
Slow motion (for debugging)
```bash
pytest --headed --slowmo 200
````
---
## Logging

Logging is implemented using Python’s built-in logging module.

Features

One log file per test run:
````
artifacts/logs/test_run_YYYYMMDD_HHMMSS.log
````
Logs include:

- test-level messages (per-test logger)

- browser console output

- JavaScript runtime errors (pageerror)

- failed network requests (requestfailed)

- screenshot paths on failure
---
## Reporting & Artifacts

On test failure:

a full-page screenshot is automatically saved to:
````
artifacts/screenshots/<testname>_<timestamp>.png
`````

Optional HTML report (if pytest-html is installed):
```bash
pytest --html=artifacts/reports/report.html --self-contained-html
````

## Project Structure

```text
tests/
├─ UI/
│  ├─ pages/
│  │  ├─ home_page.py
│  │  ├─ product_page.py
│  │  ├─ cart_page.py
│  │  └─ checkout_modal.py
│  ├─ T001_add_to_cart_spec.py
│  ├─ T002_remove_from_cart_spec.py
│  └─ T003_checkout_item_spec.py
│
├─ API/
│  └─ test_tracking_api.py
│
├─ utils/
│  └─ data/
│     └─ checkout.json
│
└─ conftest.py

artifacts/
├─ test_run_*.log
├─ *.png
└─ report.html (optional)

````


