from dataclasses import dataclass


@dataclass(frozen=True)
class Provenance:
    source: str
    version: str | None = None
    revision: str | None = None
    browser: str | None = None
