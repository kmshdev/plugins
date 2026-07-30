"""Versioned contracts for CSS Tokenography browser laboratory evidence.

The browser runner is an optional Node project.  This module deliberately uses
only the Python standard library so the report contract remains inspectable and
testable when Node or Playwright are not installed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


PROTOCOL = "css-tokenography-browser-lab/v1"
DETERMINISTIC_AND_BROWSER_STATUSES = frozenset({"pass", "fail", "unavailable"})
AGENTIC_STATUSES = frozenset(
    {"pass", "fail", "disagreement", "unavailable", "skipped"}
)
RELEASE_STATUSES = frozenset({"pass", "fail", "unavailable"})


class LaboratoryContractError(ValueError):
    """Raised when a laboratory report does not satisfy the public protocol."""


def _require_mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise LaboratoryContractError(f"{name} must be an object")
    return value


def _require_status(
    section: Mapping[str, object],
    name: str,
    allowed: frozenset[str],
) -> str:
    status = section.get("status")
    if not isinstance(status, str) or status not in allowed:
        choices = ", ".join(sorted(allowed))
        raise LaboratoryContractError(f"{name}.status must be one of: {choices}")
    return status


def _require_optional_list(section: Mapping[str, object], name: str, field: str) -> None:
    value = section.get(field)
    if value is not None and not isinstance(value, list):
        raise LaboratoryContractError(f"{name}.{field} must be an array when present")


def validate_sections(value: object) -> dict[str, dict[str, object]]:
    """Validate the three independent authority layers of a report.

    The section payloads intentionally remain extensible.  The core guarantees
    their identity and state fields without trying to interpret individual CSS
    observations owned by the browser runner.
    """

    report = _require_mapping(value, "report")
    protocol = report.get("protocol")
    if protocol != PROTOCOL:
        raise LaboratoryContractError(f"protocol must be {PROTOCOL!r}")

    deterministic = _require_mapping(report.get("deterministic"), "deterministic")
    browser = _require_mapping(report.get("browser"), "browser")
    agentic = _require_mapping(report.get("agentic"), "agentic")

    _require_status(deterministic, "deterministic", DETERMINISTIC_AND_BROWSER_STATUSES)
    _require_status(browser, "browser", DETERMINISTIC_AND_BROWSER_STATUSES)
    _require_status(agentic, "agentic", AGENTIC_STATUSES)
    _require_optional_list(deterministic, "deterministic", "checks")
    _require_optional_list(browser, "browser", "fixtures")
    _require_optional_list(agentic, "agentic", "evaluations")

    required = agentic.get("required")
    if not isinstance(required, bool):
        raise LaboratoryContractError("agentic.required must be a boolean")
    if required and agentic["status"] == "skipped":
        raise LaboratoryContractError("agentic.required evaluations cannot be skipped")

    return {
        "deterministic": dict(deterministic),
        "browser": dict(browser),
        "agentic": dict(agentic),
    }


def compute_release(
    deterministic: Mapping[str, object],
    browser: Mapping[str, object],
    agentic: Mapping[str, object],
) -> dict[str, object]:
    """Compute a monotonic release decision from separately validated layers.

    Lower-layer failures always win.  Agentic evidence can add a failure but a
    passing agentic evaluation can never upgrade a deterministic or browser
    failure/unavailability.
    """

    deterministic_status = _require_status(
        deterministic, "deterministic", DETERMINISTIC_AND_BROWSER_STATUSES
    )
    browser_status = _require_status(
        browser, "browser", DETERMINISTIC_AND_BROWSER_STATUSES
    )
    agentic_status = _require_status(agentic, "agentic", AGENTIC_STATUSES)
    agentic_required = agentic.get("required")
    if not isinstance(agentic_required, bool):
        raise LaboratoryContractError("agentic.required must be a boolean")

    failures: list[str] = []
    unavailable: list[str] = []
    if deterministic_status == "fail":
        failures.append("deterministic")
    elif deterministic_status == "unavailable":
        unavailable.append("deterministic")
    if browser_status == "fail":
        failures.append("browser")
    elif browser_status == "unavailable":
        unavailable.append("browser")

    # A failed or disagreeing workflow evaluation makes the gate stricter.
    # An optional unavailable evaluation is visible in its own section but does
    # not turn otherwise-complete deterministic evidence into an unavailable
    # release.  Required unavailable evidence does.
    if agentic_status in {"fail", "disagreement"}:
        failures.append(f"agentic:{agentic_status}")
    elif agentic_status == "unavailable" and agentic_required:
        unavailable.append("agentic")

    if failures:
        return {"status": "fail", "reasons": failures}
    if unavailable:
        return {"status": "unavailable", "reasons": unavailable}
    return {"status": "pass", "reasons": []}


def build_report(
    deterministic: Mapping[str, object],
    browser: Mapping[str, object],
    agentic: Mapping[str, object],
) -> dict[str, object]:
    """Create a protocol report while reserving ``release`` for this core."""

    sections = validate_sections(
        {
            "protocol": PROTOCOL,
            "deterministic": deterministic,
            "browser": browser,
            "agentic": agentic,
        }
    )
    return {
        "protocol": PROTOCOL,
        **sections,
        "release": compute_release(**sections),
    }


def validate_report(value: object) -> dict[str, object]:
    """Validate a complete report and reject adapter-supplied release verdicts."""

    sections = validate_sections(value)
    report = _require_mapping(value, "report")
    supplied_release = _require_mapping(report.get("release"), "release")
    supplied_status = _require_status(supplied_release, "release", RELEASE_STATUSES)
    supplied_reasons = supplied_release.get("reasons")
    if not isinstance(supplied_reasons, list) or not all(
        isinstance(reason, str) for reason in supplied_reasons
    ):
        raise LaboratoryContractError("release.reasons must be an array of strings")

    computed_release = compute_release(**sections)
    if supplied_status != computed_release["status"]:
        raise LaboratoryContractError(
            "release.status must equal the precedence decision computed from deterministic, "
            "browser, and agentic sections"
        )

    return {
        "protocol": PROTOCOL,
        **sections,
        "release": computed_release,
    }


def unavailable_report(component: str) -> dict[str, object]:
    """Return a protocol-valid report for a dependency that is not installed."""

    return build_report(
        {"status": "unavailable", "checks": [], "blockers": [component]},
        {"status": "unavailable", "fixtures": [], "blockers": [component]},
        {
            "status": "skipped",
            "required": False,
            "evaluations": [],
            "blockers": [component],
        },
    )


def failure_report(message: str) -> dict[str, object]:
    """Return a protocol-valid semantic failure for malformed runner output."""

    return build_report(
        {"status": "fail", "checks": [], "errors": [message]},
        {"status": "unavailable", "fixtures": []},
        {"status": "skipped", "required": False, "evaluations": []},
    )
