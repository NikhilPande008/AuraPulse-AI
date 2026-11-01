"""Data models for Pulse crisis execution results."""

from dataclasses import dataclass, field

from ...schemas import BOQDiffItem, ScheduleDiffItem


@dataclass
class CrisisExecutionResult:
    boq_diffs: list[BOQDiffItem] = field(default_factory=list)
    schedule_diffs: list[ScheduleDiffItem] = field(default_factory=list)
    mitigations: list[str] = field(default_factory=list)
    narrative_paragraphs: list[str] = field(default_factory=list)
