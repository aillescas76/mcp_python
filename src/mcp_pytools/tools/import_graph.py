# src/mcp_pytools/tools/import_graph.py

import dataclasses
from pathlib import Path
from typing import Any, Dict, List

from ..index.project import ProjectIndex


@dataclasses.dataclass
class ImportGraphResult:
    imports: List[str]
    dependents: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"imports": self.imports, "dependents": self.dependents}


def _module_name_from_uri(uri: str, root: Path) -> str:
    """Helper to convert a file URI to a Python module name."""
    try:
        # Assumes URI is a file URI
        path = Path(uri.replace("file://", ""))
        relative_path = path.relative_to(root)
        # remove .py extension and replace / with .
        parts = list(relative_path.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts)
    except (ValueError, IndexError):
        return Path(uri).stem


async def import_graph_tool(
    index: ProjectIndex, moduleUri: str
) -> Dict[str, List[str]]:
    """Handles an import graph request.

    This tool provides the list of modules imported by the given module, and
    the list of modules that import the given module (dependents).

    Note: Module resolution is simplified and may not correctly handle
    complex relative imports or namespace packages.

    Args:
        index: The project index.
        moduleUri: The URI of the module to query.

    Returns:
        A dictionary with 'imports' and 'dependents' lists,
        containing URIs of other modules.
    """
    imports = index.imports.get(moduleUri, [])
    import_names = sorted([edge.target_module for edge in imports])

    # Build reverse import graph
    dependents: List[str] = []
    
    # Get the module name for the given URI
    current_module_name = _module_name_from_uri(moduleUri, index.root)

    for uri, edges in index.imports.items():
        if uri == moduleUri:
            continue
        for edge in edges:
            # This is a simplified resolution for now
            if current_module_name in edge.imported_name:
                dependents.append(uri)
                break # next module

    result = ImportGraphResult(
        imports=import_names,
        dependents=sorted(list(set(dependents))),
    )
    return result.to_dict()