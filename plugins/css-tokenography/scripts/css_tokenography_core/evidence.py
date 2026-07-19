from dataclasses import asdict, dataclass, field

from .provenance import Provenance
from .result import classify_observations


@dataclass(frozen=True)
class OracleObservation:
    oracle: str
    status: str
    value: object
    provenance: Provenance | None = None
    notes: tuple[str, ...] = ()


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
