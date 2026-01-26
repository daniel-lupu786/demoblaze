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
├─ logs/
│  └─ test_run_*.log
├─ reports/
│  └─ report.html (optional)
└─ screenshots/
   └─ *.png




````
# Performance Testing (Task III)

Performance and load testing is implemented using k6 to evaluate the behavior of the Tracking API under different traffic conditions.

The focus is on:
- throughput (requests per second)
- response time percentiles (p90 / p95)
- technical stability (network errors and server-side failures)

Functional 4xx responses (e.g. unknown or invalid tracking numbers) are treated as expected behavior and are not considered technical failures.

## Tooling

k6 – script-based, CLI-driven performance testing tool

k6 was chosen because it allows:
- reproducible, version-controlled performance tests
- flexible load modeling
- clear separation between functional and technical failures
- easy integration into CI pipelines

## Scope

API under test

GET https://tracking.bosta.co/shipments/track/:trackingNumber

Workload characteristics

- mixed input set (valid-like and invalid-like tracking numbers)
- configurable ratio via environment variables
- constant arrival rate load model

UI performance testing was not automated due to browser limitations of k6.

## Load Profiles

Multiple load profiles are defined in the k6 script and can be selected via environment variables:

Profile	Description
- smoke:	Baseline verification and script validation
- load:	Steady-state performance under realistic load
- stress:	Gradual ramp-up to identify limits
- spike:	Sudden traffic increase and recovery
- soak:	Long-running stability test

For this assessment, smoke and load profiles were executed.

## Execution
- Smoke test (baseline)
````
k6 run -e PROFILE=smoke -e VALID_RATIO=1 k6/tracking_api_perf.js
````
with additional raw time-series data for visualization:
````
k6 run -e PROFILE=smoke -e VALID_RATIO=1 k6/tracking_api_perf.js --out json=artifacts\load_raw.json
````


- Load test (steady-state)
````
k6 run -e PROFILE=load -e VALID_RATIO=0.8 k6/tracking_api_perf.js
````

with additional raw time-series data for visualization:
````
k6 run -e PROFILE=load -e VALID_RATIO=0.8 k6/tracking_api_perf.js --out json=artifacts/load_raw.json
````

## Metrics & Thresholds

To avoid false negatives caused by expected 4xx responses, a custom metric is used.

Technical failures are defined as:
- network / timeout errors
- HTTP 5xx responses

Enforced thresholds

technical failure rate < 1%

p95 latency < 300 ms

p99 latency < 800 ms

Threshold violations cause the test run to fail automatically.

## Performance Test Results

### Smoke Test (Baseline)

#### Results

Throughput: ~2.0 requests/second

Technical failure rate: 0

Latency:
- p95: ~178 ms

**Interpretation**

The smoke test validates script correctness and baseline responsiveness.
No technical failures were observed and latency remained well below the defined SLA thresholds.
Findings – Rate Limiting & Latency
The latency graph shows stable p95 response times throughout the test, with a single short-lived spike.
This spike correlates with the occurrence of HTTP 429 responses and is interpreted as a result of rate limiting
rather than a systemic performance degradation.

The HTTP status distribution indicates that the majority of requests were throttled (HTTP 429).
This behavior is expected for a public tracking endpoint and demonstrates effective abuse prevention
and traffic protection mechanisms.

Importantly, the system maintains low latency for accepted requests and prefers throttling over gradual
performance degradation under load.

### Load Test (Steady-State)
#### Results

Throughput: ~19.96 requests/second (target: 20 RPS)

Technical failure rate: 0

Latency:
- p90: ~66.8 ms
- p95: ~87.7 ms

**Interpretation**

Under sustained steady-state load, the system handled the target throughput reliably.
Latency remained stable and significantly below SLA limits, indicating sufficient performance headroom.
No signs of saturation or instability were observed.

During the load test, p95 latency remained stable in the 60–90 ms range for accepted requests.
Several short-lived latency spikes were observed, which correlate with HTTP 429 responses and
are attributed to rate limiting rather than backend performance degradation.

The RPS graph shows a stable average throughput close to the target rate, with short drops and
bursts caused by throttling and constant-arrival-rate compensation behavior.

The HTTP status distribution is dominated by HTTP 429 responses, indicating active rate limiting.
This behavior is expected and desirable for a public tracking endpoint, as it protects the system
from abuse while maintaining low latency for accepted traffic.

### Overall Assessment

Across both smoke and load profiles, the tracking API demonstrated:
- stable throughput
- low and consistent latency
- no technical failures
- The system scales cleanly from baseline to steady-state load and meets all defined performance and reliability criteria.

### Notes & Limitations
Tests were executed against a public API; results may vary depending on network conditions.

No server-side resource metrics (CPU, memory) were available.

Additional profiles (stress, spike, soak) are implemented but were not executed due to scope and time constraints.

##### UI Performance Considerations

UI performance testing for DemoBlaze flows (UC1: browse, UC2: add-to-cart, UC3: checkout)
was not automated as part of this assessment.

Reasoning:
- Browser-based UI load testing is significantly more complex and infrastructure-heavy
  (e.g. Selenium/Playwright grids, session isolation).
- Tools such as k6 are not designed for browser-level UI performance testing.
- The DemoBlaze application is a public demo system with limited stability guarantees.

Instead, UI performance was evaluated conceptually:

- Key UI transaction SLAs were identified:
  - "Add to Cart" p95 < 2.0 seconds
  - "Checkout" completion p95 < 3.0 seconds
- In a production environment, UI performance testing would be implemented using:
  - synthetic monitoring (single-user transaction timing)
  - frontend performance metrics (LCP, TTI, TBT)
  - backend correlation via API performance and server metrics


### Artifacts

Performance test artifacts are stored under:

```text
artifacts/k6
├─ k6_summary_smoke.json
├─ k6_summary_load.json
├─ smoke_raw.json
├─ load_raw.json
└─ *.png (optional graphs)

````

