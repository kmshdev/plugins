#!/usr/bin/env python3
"""Analyze normalized, Lighthouse, or Web Vitals JSON against performance budgets."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, TextIO


DEFAULT_BUDGET = {
    "lcp_ms": 2500,
    "cls": 0.1,
    "inp_ms": 200,
    "javascript_bytes": 300_000,
    "css_bytes": 60_000,
    "image_bytes": 500_000,
    "font_bytes": 100_000,
    "total_bytes": 1_000_000,
    "requests": 50,
    "third_party_requests": 10,
}


class BudgetInputError(ValueError):
    pass


def read_json(path: str, stdin: TextIO) -> dict[str, Any]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise BudgetInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise BudgetInputError("Input must be a JSON object")
    return value


def numeric(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise BudgetInputError(f"{field} must be a finite numeric value")
    if value < 0:
        raise BudgetInputError(f"{field} must not be negative")
    return float(value)


def normalize_input(data: dict[str, Any]) -> dict[str, float]:
    if isinstance(data.get("metrics"), dict) or isinstance(data.get("resources"), dict):
        result: dict[str, float] = {}
        for group in (data.get("metrics", {}), data.get("resources", {})):
            if not isinstance(group, dict):
                raise BudgetInputError("metrics and resources must be JSON objects")
            for key, value in group.items():
                result[key] = numeric(value, key)
        return result

    audits = data.get("audits")
    if isinstance(audits, dict):
        result = {}
        audit_map = {
            "lcp_ms": "largest-contentful-paint",
            "cls": "cumulative-layout-shift",
            "inp_ms": "interaction-to-next-paint",
            "total_bytes": "total-byte-weight",
        }
        for target, audit_name in audit_map.items():
            audit = audits.get(audit_name)
            if isinstance(audit, dict) and "numericValue" in audit:
                result[target] = numeric(audit["numericValue"], f"audits.{audit_name}.numericValue")
        requests = audits.get("network-requests")
        if isinstance(requests, dict):
            items = requests.get("details", {}).get("items") if isinstance(requests.get("details"), dict) else None
            if isinstance(items, list):
                result["requests"] = float(len(items))
                result["third_party_requests"] = float(sum(1 for item in items if isinstance(item, dict) and item.get("isThirdParty")))
        return result

    web_vitals = data.get("web_vitals")
    if isinstance(web_vitals, dict):
        aliases = {"LCP": "lcp_ms", "CLS": "cls", "INP": "inp_ms"}
        return {aliases[key]: numeric(value, key) for key, value in web_vitals.items() if key in aliases}

    raise BudgetInputError("Expected normalized metrics/resources, Lighthouse audits, or web_vitals JSON")


def load_budget(path: str | None) -> dict[str, float]:
    if path is None:
        return {key: float(value) for key, value in DEFAULT_BUDGET.items()}
    data = read_json(path, sys.stdin)
    unknown = sorted(set(data) - set(DEFAULT_BUDGET))
    if unknown:
        raise BudgetInputError(f"Unknown budget keys: {', '.join(unknown)}")
    budget = {key: float(value) for key, value in DEFAULT_BUDGET.items()}
    budget.update({key: numeric(value, key) for key, value in data.items()})
    return budget


def analyze(values: dict[str, float], budget: dict[str, float]) -> dict[str, Any]:
    failures = []
    missing = []
    checks = []
    for metric, limit in budget.items():
        if metric not in values:
            missing.append(metric)
            continue
        actual = values[metric]
        passed = actual <= limit
        checks.append({"metric": metric, "actual": actual, "limit": limit, "passed": passed})
        if not passed:
            failures.append({"metric": metric, "actual": actual, "limit": limit, "over_by": actual - limit})
    status = "fail" if failures else "incomplete" if missing else "pass"
    return {"status": status, "checks": checks, "failures": failures, "missing": missing, "source_kind": "analysis-only"}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Analyze Lighthouse, Web Vitals, or normalized JSON against explicit performance budgets.")
    result.add_argument("--input", default="-", help="Input JSON path, or '-' for stdin (default)")
    result.add_argument("--budget", help="Optional JSON file overriding default budget limits")
    result.add_argument("--format", choices=("json", "human"), default="human")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = analyze(normalize_input(read_json(args.input, sys.stdin)), load_budget(args.budget))
    except BudgetInputError as error:
        print(f"performance-budget: {error}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Performance budget: {report['status'].upper()}")
        for check in report["checks"]:
            mark = "PASS" if check["passed"] else "FAIL"
            print(f"{mark:4} {check['metric']}: {check['actual']:g} <= {check['limit']:g}")
        if report["missing"]:
            print("MISSING " + ", ".join(report["missing"]))
    return 2 if report["status"] == "fail" else 3 if report["status"] == "incomplete" else 0


if __name__ == "__main__":
    raise SystemExit(main())
