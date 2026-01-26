import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

http.setResponseCallback(http.expectedStatuses({ min: 200, max: 499 }));

// ---------- Config ----------
const BASE_URL = __ENV.BASE_URL || "https://tracking.bosta.co";
const PROFILE = (__ENV.PROFILE || "smoke").toLowerCase();

const VALID = ["6636234", "7234258", "9442984", "1094442"];
const INVALID = ["", "   ", "!!!", "<script>alert(1)</script>", "1".repeat(200), "-1", "0"];

const VALID_RATIO = Number(__ENV.VALID_RATIO || 0.8);
const THINK_MIN = Number(__ENV.THINK_MIN || 0.5);
const THINK_MAX = Number(__ENV.THINK_MAX || 1.5);

// ---------- Custom metrics ----------
const trackLatency = new Trend("track_latency_ms", true);
const trackErrors = new Rate("track_errors");

// ---------- Load Profiles ----------
function optionsForProfile(profile) {
  switch (profile) {
    case "smoke":
      return {
        scenarios: {
          smoke: {
            executor: "constant-arrival-rate",
            rate: 2,
            timeUnit: "1s",
            duration: "5m",
            preAllocatedVUs: 5,
            maxVUs: 20,
          },
        },
      };

    case "load":
      return {
        scenarios: {
          load: {
            executor: "constant-arrival-rate",
            rate: 20,
            timeUnit: "1s",
            duration: "30m",
            preAllocatedVUs: 30,
            maxVUs: 200,
          },
        },
      };

    case "stress":
      return {
        scenarios: {
          stress: {
            executor: "ramping-arrival-rate",
            startRate: 10,
            timeUnit: "1s",
            stages: [
              { target: 20, duration: "5m" },
              { target: 30, duration: "5m" },
              { target: 40, duration: "5m" },
              { target: 50, duration: "5m" },
              { target: 60, duration: "5m" },
            ],
            preAllocatedVUs: 50,
            maxVUs: 400,
          },
        },
      };

    case "spike":
      return {
        scenarios: {
          spike: {
            executor: "ramping-arrival-rate",
            startRate: 0,
            timeUnit: "1s",
            stages: [
              { target: 100, duration: "30s" },
              { target: 100, duration: "2m" },
              { target: 0, duration: "30s" },
            ],
            preAllocatedVUs: 200,
            maxVUs: 600,
          },
        },
      };

    case "soak":
      return {
        scenarios: {
          soak: {
            executor: "constant-arrival-rate",
            rate: 30,
            timeUnit: "1s",
            duration: "2h",
            preAllocatedVUs: 60,
            maxVUs: 500,
          },
        },
      };

    default:
      throw new Error(`Unknown PROFILE: ${profile}`);
  }
}

export const options = {
  ...optionsForProfile(PROFILE),
  thresholds: {
 
    http_req_failed: ["rate<0.01"],

    http_req_duration: ["p(95)<300", "p(99)<800"],

    track_errors: ["rate<0.01"],
  },
  tags: { profile: PROFILE },
};

// ---------- Helpers ----------
function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomThink() {
  const t = THINK_MIN + Math.random() * (THINK_MAX - THINK_MIN);
  sleep(t);
}

function buildTrackingNumber() {
  const isValid = Math.random() < VALID_RATIO;
  return isValid ? pick(VALID) : pick(INVALID);
}

// ---------- Test ----------
export default function () {
  const trackingNumber = buildTrackingNumber();
  const url = `${BASE_URL}/shipments/track/${encodeURIComponent(trackingNumber)}`;

  const res = http.get(url, {
    headers: { Accept: "application/json", "User-Agent": "k6-performance-test" },
    tags: {
      endpoint: "track_shipment",
      input_type: trackingNumber && /^\d+$/.test(trackingNumber.trim())
        ? "valid_like"
        : "invalid_like",
    },
  });

  trackLatency.add(res.timings.duration);

  check(res, {
    "status is 200 or 4xx": (r) => r.status === 200 || (r.status >= 400 && r.status < 500),
    "json for 200": (r) => {
      if (r.status !== 200) return true;
      const ct = (r.headers["Content-Type"] || r.headers["content-type"] || "").toLowerCase();
      return ct.includes("application/json");
    },
  });

  // only count server-side failures as errors
  trackErrors.add(res.status >= 500);

  randomThink();
}

export function handleSummary(data) {
  const p = (q) => (data.metrics.http_req_duration?.values?.[`p(${q})`] ?? null);
  const rps = data.metrics.http_reqs?.values?.rate ?? null;
  const techFailRate = data.metrics.tech_failures?.values?.rate ?? null;

  const summary = {
    profile: PROFILE,
    base_url: BASE_URL,
    thresholds: options.thresholds,
    results: {
      http_reqs_per_sec: rps,
      tech_failures_rate: techFailRate,
      latency_ms: {
        p90: p(90),
        p95: p(95),
        p99: p(99),
      },
    },
  };

  return {
    [`artifacts/k6_summary_${PROFILE}.json`]: JSON.stringify(summary, null, 2),

    stdout: `\nK6 Summary (${PROFILE})\nRPS: ${rps}\nTechFailures: ${techFailRate}\np95: ${p(
      95
    )} ms | p99: ${p(99)} ms\n\n`,
  };
}