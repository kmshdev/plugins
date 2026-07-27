from dataclasses import asdict, dataclass, field

from .provenance import Provenance
from .result import classify_observations


RELATIONS_TO_CORE = ("exact", "equivalent", "bounded-subset", "different")


@dataclass(frozen=True)
class OracleObservation:
    oracle: str
    status: str
    value: object
    relation_to_core: str | None = None
    provenance: Provenance | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status == "ok":
            if self.relation_to_core is None:
                raise ValueError("relation_to_core is required when status is ok")
            if self.relation_to_core not in RELATIONS_TO_CORE:
                raise ValueError(
                    f"invalid relation_to_core: {self.relation_to_core!r}"
                )
        elif self.status in ("unavailable", "unsupported", "error"):
            if self.relation_to_core is not None:
                raise ValueError(
                    f"relation_to_core must be absent when status is {self.status}"
                )


@dataclass
class EvidenceEnvelope:
    core: dict[str, object]
    observations: list[OracleObservation] = field(default_factory=list)

    def add(self, observation: OracleObservation) -> None:
        self.observations.append(observation)

    def to_dict(self) -> dict[str, object]:
        return {
            "core": self.core,
            "classification": classify_observations(self.core, self.observations),
            "observations": [asdict(item) for item in self.observations],
        }
