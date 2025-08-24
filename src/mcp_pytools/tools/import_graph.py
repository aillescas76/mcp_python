# src/mcp_pytools/tools/import_graph.py

import dataclasses
from pathlib import Path
from typing import Any, Dict, List

from .tool import Tool, ToolContext


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


class ImportGraphTool(Tool):
    """A tool that provides the import graph for a module."""

    @property
    def name(self) -> str:
        return "import_graph"

    @property
    def description(self) -> str:
        return "Shows a module's direct imports and its dependents (reverse imports)."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "moduleUri": {
                    "type": "string",
                    "description": "The URI of the module to query.",
                }
            },
            "required": ["moduleUri"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, List[str]]:
        """Handles an import graph request."""
        moduleUri = kwargs["moduleUri"]
        index = context.project_index
        imports = index.imports.get(moduleUri, [])

        resolved_imports = []
        for edge in imports:
            if not edge.is_relative:
                resolved_imports.append(edge.target_module)
                continue

            # Simple relative import resolution
            source_path = Path(moduleUri.replace("file://", ""))
            level = 0
            for char in edge.target_module:
                if char == ".":
                    level += 1
                else:
                    break

            base_path = source_path.parent
            for _ in range(level - 1):
                base_path = base_path.parent

            module_part = edge.target_module[level:]
            if module_part:
                resolved_path = (base_path / module_part).resolve()
            else:
                resolved_path = base_path.resolve()

            try:
                relative_to_root = resolved_path.relative_to(index.root.resolve())
                parts = list(relative_to_root.parts)
                if parts[-1] == "__init__.py":
                    parts.pop()

                resolved_imports.append(".".join(parts))
            except ValueError:
                # Could not make relative to root, just use the module name
                resolved_imports.append(module_part)


        import_names = sorted(resolved_imports)

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
                    break  # next module

        result = ImportGraphResult(
            imports=import_names,
            dependents=sorted(list(set(dependents))),
        )
        return result.to_dict()