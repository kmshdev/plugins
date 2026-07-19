from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .evidence import OracleObservation


def classify_observations(
    core: dict[str, object], observations: list["OracleObservation"]
) -> str:
    if not observations or all(item.status == "unavailable" for item in observations):
        return "unavailable"
    if any(item.status == "error" for item in observations):
        return "error"

    comparable = [item.value for item in observations if item.status == "ok"]
    if comparable:
        if all(value == core for value in comparable):
            return "agreement"
        if len(comparable) > 1 and all(
            value == comparable[0] for value in comparable[1:]
        ):
            return "equivalent"
        return "divergence"

    if any(item.status == "bounded-subset" for item in observations):
        return "bounded-subset"
    if any(item.status == "unsupported" for item in observations):
        return "unsupported"
    return "divergence"
