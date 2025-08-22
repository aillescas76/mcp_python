from typing import List, Dict, Any

from ..index.project import ProjectIndex
from ..astutils.parser import parse_module, StructuredSyntaxError, Position, Range
from .diagnostics import Diagnostic, DiagnosticSeverity

async def syntax_check_tool(
    index: ProjectIndex, uri: str
) -> List[Dict[str, Any]]:
    """
    Checks for syntax errors in a Python module.
    """
    diagnostics: List[Diagnostic] = []
    try:
        path = index.root / uri.replace("file://", "")
        content = index.file_cache.get_text(path)
        parse_module(content, uri)
    except StructuredSyntaxError as e:
        pos = Position(line=e.lineno - 1, column=e.offset - 1 if e.offset else 0)
        error_range = Range(start=pos, end=pos)
        diagnostics.append(
            Diagnostic(
                range=error_range,
                message=e.msg,
                severity=DiagnosticSeverity.ERROR,
                source="syntax-check",
            )
        )
    except Exception:
        pass

    return [d.to_dict() for d in diagnostics]
