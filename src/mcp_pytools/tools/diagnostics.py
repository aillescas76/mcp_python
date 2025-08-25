import dataclasses
from enum import Enum
from typing import Any, Dict

from ..astutils.parser import Range


class DiagnosticSeverity(Enum):
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4

@dataclasses.dataclass
class Diagnostic:
    range: Range
    message: str
    severity: DiagnosticSeverity
    source: str = "mcp-pytools"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "range": self.range.to_dict(),
            "message": self.message,
            "severity": self.severity.name,
            "source": self.source,
        }
