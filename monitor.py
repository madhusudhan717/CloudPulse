"""CloudPulse website monitoring engine.

Uses only Python's standard library plus the Requests package.
Run `python monitor.py` to perform one monitoring cycle.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "config.json"
LOG_PATH = BASE_DIR / "logs" / "uptime_log.csv"
SUMMARY_PATH = BASE_DIR / "reports" / "dashboard-data.json"
REPORT_PATH = BASE_DIR / "reports" / "uptime_report.txt"
CSV_FIELDS = [
    "timestamp_utc", "name", "url", "http_status", "response_time_ms",
    "state", "error"
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)

    targets = config.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("config/config.json must contain a non-empty 'targets' list")

    timeout = float(config.get("request_timeout_seconds", 10))
    threshold = float(config.get("latency_threshold_ms", 2000))
    if timeout <= 0 or threshold <= 0:
        raise ValueError("Request timeout and latency threshold must be greater than zero")

    for index, target in enumerate(targets, start=1):
        if not isinstance(target, dict) or not target.get("name") or not target.get("url"):
            raise ValueError(f"Target #{index} must contain both 'name' and 'url'")
        if not str(target["url"]).startswith(("http://", "https://")):
            raise ValueError(f"Target URL must start with http:// or https://: {target['url']}")
    return config


def ensure_log_file() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists() or LOG_PATH.stat().st_size == 0:
        with LOG_PATH.open("w", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=CSV_FIELDS).writeheader()


def read_history() -> list[dict[str, str]]:
    ensure_log_file()
    with LOG_PATH.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def append_log(row: dict[str, Any]) -> None:
    ensure_log_file()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writerow(row)


def check_endpoint(target: dict[str, str], config: dict[str, Any]) -> dict[str, Any]:
    """Check one endpoint and return an auditable result row."""
    started = time.perf_counter()
    http_status: int | None = None
    error = ""
    state = "DOWN"

    try:
        response = requests.get(
            target["url"],
            timeout=float(config.get("request_timeout_seconds", 10)),
            headers={"User-Agent": "CloudPulse-Monitor/1.0"},
            allow_redirects=True,
        )
        http_status = response.status_code
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        # A final 2xx or 3xx response is considered reachable. HTTP 4xx/5xx is DOWN.
        if 200 <= http_status < 400:
            state = "SLOW" if elapsed_ms > float(config.get("latency_threshold_ms", 2000)) else "UP"
        else:
            state = "DOWN"
            error = f"HTTP response {http_status}"
    except requests.RequestException as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        error = f"{type(exc).__name__}: {str(exc)[:220]}"

    return {
        "timestamp_utc": utc_now(),
        "name": str(target["name"]),
        "url": str(target["url"]),
        "http_status": http_status if http_status is not None else "",
        "response_time_ms": elapsed_ms,
        "state": state,
        "error": error,
    }


def send_webhook_alert(message: str) -> None:
    """Send an optional generic JSON webhook; no secret is stored in source."""
    webhook_url = os.getenv("ALERT_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return
    try:
        response = requests.post(webhook_url, json={"text": message}, timeout=8)
        response.raise_for_status()
        print("[ALERT] Webhook notification delivered.")
    except requests.RequestException as exc:
        print(f"[WARNING] Webhook delivery failed: {exc}")


def build_dashboard_data(history: list[dict[str, str]], config: dict[str, Any]) -> dict[str, Any]:
    latest_by_name: dict[str, dict[str, str]] = {}
    history_by_name: dict[str, list[dict[str, str]]] = {}
    for row in history:
        latest_by_name[row["name"]] = row
        history_by_name.setdefault(row["name"], []).append(row)

    target_summaries = []
    for target in config["targets"]:
        rows = history_by_name.get(target["name"], [])
        reachable = sum(1 for row in rows if row.get("state") in ("UP", "SLOW"))
        uptime = round((reachable / len(rows)) * 100, 2) if rows else 0.0
        latest = latest_by_name.get(target["name"])
        target_summaries.append({
            "name": target["name"],
            "url": target["url"],
            "state": latest.get("state", "PENDING") if latest else "PENDING",
            "http_status": latest.get("http_status", "") if latest else "",
            "response_time_ms": float(latest.get("response_time_ms", 0)) if latest else 0,
            "uptime_percent": uptime,
            "total_checks": len(rows),
            "last_checked": latest.get("timestamp_utc") if latest else None,
            "error": latest.get("error", "") if latest else "",
        })

    all_latencies = [float(row["response_time_ms"]) for row in history if row.get("response_time_ms")]
    reachable_checks = sum(1 for row in history if row.get("state") in ("UP", "SLOW"))
    total_checks = len(history)
    overall_uptime = round((reachable_checks / total_checks) * 100, 2) if total_checks else 0.0
    return {
        "generated_at": utc_now(),
        "overall_uptime_percent": overall_uptime,
        "average_response_time_ms": round(sum(all_latencies) / len(all_latencies), 2) if all_latencies else 0,
        "total_checks": total_checks,
        "incident_checks": sum(1 for row in history if row.get("state") == "DOWN"),
        "latency_threshold_ms": float(config.get("latency_threshold_ms", 2000)),
        "targets": target_summaries,
        "history": history[-120:],
    }


def write_reports(config: dict[str, Any]) -> dict[str, Any]:
    history = read_history()
    data = build_dashboard_data(history, config)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    lines = [
        "CLOUDPULSE UPTIME REPORT",
        "=" * 54,
        f"Generated (UTC): {data['generated_at']}",
        f"Overall uptime: {data['overall_uptime_percent']}%",
        f"Average response time: {data['average_response_time_ms']} ms",
        f"Total checks recorded: {data['total_checks']}",
        f"DOWN check events: {data['incident_checks']}",
        "",
        "ENDPOINT SUMMARY",
        "-" * 54,
    ]
    for target in data["targets"]:
        lines.append(
            f"{target['name']}: {target['state']} | HTTP {target['http_status'] or 'N/A'} "
            f"| {target['response_time_ms']} ms | uptime {target['uptime_percent']}% "
            f"| checks {target['total_checks']}"
        )
        if target["error"]:
            lines.append(f"  Detail: {target['error']}")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data


def run_monitoring_cycle() -> list[dict[str, Any]]:
    config = load_config()
    print(f"\nCloudPulse monitoring started at {utc_now()}")
    print(f"Latency alert threshold: {config.get('latency_threshold_ms', 2000)} ms\n")

    results = []
    for target in config["targets"]:
        result = check_endpoint(target, config)
        append_log(result)
        results.append(result)
        status = result["http_status"] or "N/A"
        print(
            f"[{result['state']:<4}] {result['name']:<18} "
            f"HTTP {status:<4} {result['response_time_ms']:>8} ms"
        )
        if result["state"] in ("DOWN", "SLOW"):
            message = (
                f"CloudPulse alert: {result['name']} is {result['state']} | "
                f"HTTP {status} | {result['response_time_ms']} ms | {result['error']}"
            )
            print(f"[ALERT] {message}")
            send_webhook_alert(message)

    data = write_reports(config)
    print("\nMonitoring cycle completed.")
    print(f"CSV log: {LOG_PATH.relative_to(BASE_DIR)}")
    print(f"Dashboard data: {SUMMARY_PATH.relative_to(BASE_DIR)}")
    print(f"Uptime report: {REPORT_PATH.relative_to(BASE_DIR)}")
    print(f"Overall uptime across recorded checks: {data['overall_uptime_percent']}%")
    return results


if __name__ == "__main__":
    try:
        run_monitoring_cycle()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
