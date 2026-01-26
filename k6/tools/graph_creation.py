import json
import argparse
from collections import defaultdict, Counter
from datetime import datetime

import matplotlib.pyplot as plt

def parse_k6_json_lines(path: str):

    points = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "Point":
                continue
            metric = obj.get("metric")
            data = obj.get("data", {})
            t = data.get("time")
            v = data.get("value")
            tags = data.get("tags", {})
            if metric and t is not None and v is not None:
                points.append((t, metric, v, tags))
    return points

def to_epoch_seconds(ts: str) -> float:
    """
    k6 json output time can vary:
    - Z suffix: 2026-01-25T12:34:56.123456789Z
    - timezone offset: 2026-01-25T12:34:56.123456+00:00
    - sometimes malformed trailing '+'
    We normalize to a datetime that Python can parse.
    """
    ts = ts.strip()

    # Remove trailing Z (UTC)
    if ts.endswith("Z"):
        ts = ts[:-1]

    # If it ends with a bare '+' or '-', drop it
    if ts.endswith("+") or ts.endswith("-"):
        ts = ts[:-1]

    # If timezone is missing, assume UTC
    # (k6 often emits Z; if not present, we still want a stable parse)
    has_tz = ("+" in ts[10:] or "-" in ts[10:])  # crude but works for ISO timestamps

    # Trim fractional seconds to microseconds (Python supports up to 6 digits)
    if "." in ts:
        base, frac = ts.split(".", 1)
        # If timezone is in frac, split it out
        tz_part = ""
        if "+" in frac:
            frac, tz_part = frac.split("+", 1)
            tz_part = "+" + tz_part
        elif "-" in frac:
            # be careful: split on last '-' after date portion; for frac it's safe
            frac, tz_part = frac.split("-", 1)
            tz_part = "-" + tz_part

        frac = (frac + "000000")[:6]  # pad/trim to 6
        ts = f"{base}.{frac}{tz_part}"

    # If timezone looks incomplete like +00 or +0000, normalize to +00:00
    # If timezone is entirely missing, append +00:00
    if not has_tz:
        ts = ts + "+00:00"
    else:
        # normalize "+HH" or "+HHMM" to "+HH:MM"
        if ts.endswith(("+00", "+01", "+02", "+03", "+04", "+05", "+06", "+07", "+08", "+09")):
            ts = ts + ":00"
        # "+HHMM" or "-HHMM"
        if len(ts) >= 5 and (ts[-5] in ["+", "-"]) and ts[-2] != ":":
            ts = ts[:-2] + ":" + ts[-2:]

    dt = datetime.fromisoformat(ts)
    return dt.timestamp()

def aggregate(points):
    buckets = defaultdict(lambda: {"http_reqs": 0, "durations": [], "tech_failures": 0, "tech_samples": 0})
    status_counter = Counter()

    for t, metric, v, tags in points:
        sec = int(to_epoch_seconds(t))
        b = buckets[sec]

        if metric == "http_reqs":
            b["http_reqs"] += v
        elif metric == "http_req_duration":
            b["durations"].append(v)
            s = tags.get("status")
            if s:
                status_counter[s] += 1
        elif metric == "tech_failures":
            b["tech_failures"] += v
            b["tech_samples"] += 1

    times = sorted(buckets.keys())
    rps = []
    p95 = []
    tech_rate = []

    for sec in times:
        b = buckets[sec]
        rps.append(b["http_reqs"])
        durs = sorted(b["durations"])
        if durs:
            idx = int(0.95 * (len(durs) - 1))
            p95.append(durs[idx])
        else:
            p95.append(None)

        if b["tech_samples"] > 0:
            tech_rate.append(b["tech_failures"] / b["tech_samples"])
        else:
            tech_rate.append(0.0)

    return times, rps, p95, tech_rate, status_counter

def plot_series(times, rps, p95, tech_rate, status_counter, out_prefix):
    t0 = times[0] if times else 0
    x = [t - t0 for t in times]

    plt.figure()
    plt.plot(x, rps)
    plt.xlabel("Time (s)")
    plt.ylabel("Requests per second")
    plt.title("RPS over time")
    plt.tight_layout()
    plt.savefig(f"{out_prefix}_rps.png", dpi=160)

    plt.figure()
    xs = [x[i] for i, v in enumerate(p95) if v is not None]
    ys = [v for v in p95 if v is not None]
    plt.plot(xs, ys)
    plt.xlabel("Time (s)")
    plt.ylabel("Latency p95 (ms) per second bucket")
    plt.title("Latency (p95) over time")
    plt.tight_layout()
    plt.savefig(f"{out_prefix}_latency_p95.png", dpi=160)

    # 3) Tech failure rate over time
    plt.figure()
    plt.plot(x, tech_rate)
    plt.xlabel("Time (s)")
    plt.ylabel("Tech failure rate (per second bucket)")
    plt.title("Technical failures over time")
    plt.tight_layout()
    plt.savefig(f"{out_prefix}_tech_failures.png", dpi=160)

    if status_counter:
        plt.figure()
        keys = sorted(status_counter.keys(), key=lambda k: int(k) if k.isdigit() else k)
        vals = [status_counter[k] for k in keys]
        plt.bar(keys, vals)
        plt.xlabel("HTTP status")
        plt.ylabel("Count")
        plt.title("HTTP status distribution (from tags, if available)")
        plt.tight_layout()
        plt.savefig(f"{out_prefix}_status_codes.png", dpi=160)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="k6 raw json output file (from --out json=...)")
    ap.add_argument("--out-prefix", default="artifacts/k6", help="output prefix for png files")
    args = ap.parse_args()

    points = parse_k6_json_lines(args.inp)
    if not points:
        raise SystemExit("No k6 Point data found. Did you run with: --out json=... ?")

    times, rps, p95, tech_rate, status_counter = aggregate(points)
    if not times:
        raise SystemExit("No time buckets created. Input might be empty.")

    plot_series(times, rps, p95, tech_rate, status_counter, args.out_prefix)
    print("Saved graphs:")
    print(f" - {args.out_prefix}_rps.png")
    print(f" - {args.out_prefix}_latency_p95.png")
    print(f" - {args.out_prefix}_tech_failures.png")
    if status_counter:
        print(f" - {args.out_prefix}_status_codes.png")

if __name__ == "__main__":
    main()
