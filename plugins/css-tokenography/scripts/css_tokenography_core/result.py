from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .evidence import OracleObservation


def classify_observations(
    core: dict[str, object], observations: list["OracleObservation"]
) -> str:
    if any(item.status == "error" for item in observations):
        return "error"

    usable = [item for item in observations if item.status == "ok"]
    if not usable:
        return "unavailable"
    if any(item.status in ("unavailable", "unsupported") for item in observations):
        return "partial"

    relations = [item.relation_to_core for item in usable]
    if "bounded-subset" in relations:
        return "bounded-subset"
    if "different" in relations:
        return "divergence"
    if all(relation == "exact" for relation in relations):
        return "agreement"
    if "equivalent" in relations and all(
        relation in ("exact", "equivalent") for relation in relations
    ):
        return "equivalent"
    return "divergence"
