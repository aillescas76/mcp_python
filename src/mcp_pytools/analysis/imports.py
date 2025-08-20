# src/mcp_pytools/analysis/imports.py

import ast
import dataclasses
from typing import List, Optional

from mcp_pytools.astutils.parser import ParsedModule, Range


@dataclasses.dataclass
class ImportEdge:
    source_module_uri: str
    imported_name: str  # e.g., 'os' or 'os.path'
    target_module: str
    range: Range
    alias: Optional[str] = None
    is_wildcard: bool = False
    is_relative: bool = False


class ImportVisitor(ast.NodeVisitor):
    def __init__(self, module_uri: str):
        self.module_uri = module_uri
        self.imports: List[ImportEdge] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(
                ImportEdge(
                    source_module_uri=self.module_uri,
                    imported_name=alias.name,
                    target_module=alias.name,
                    alias=alias.asname,
                    range=node._range,
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom):
        prefix = "." * node.level
        is_relative = node.level > 0
        if node.module is None:
            # e.g. from . import foo
            for alias in node.names:
                self.imports.append(
                    ImportEdge(
                        source_module_uri=self.module_uri,
                        imported_name=f"{prefix}{alias.name}",
                        target_module=f"{prefix}{alias.name}",
                        alias=alias.asname,
                        range=node._range,
                        is_relative=is_relative,
                    )
                )
        else:
            # e.g. from .foo import bar
            module_name = prefix + node.module
            for alias in node.names:
                if alias.name == "*":
                    self.imports.append(
                        ImportEdge(
                            source_module_uri=self.module_uri,
                            imported_name=module_name,
                            target_module=module_name,
                            range=node._range,
                            is_wildcard=True,
                            is_relative=is_relative,
                        )
                    )
                    continue

                self.imports.append(
                    ImportEdge(
                        source_module_uri=self.module_uri,
                        imported_name=f"{module_name}.{alias.name}",
                        target_module=module_name,
                        alias=alias.asname,
                        range=node._range,
                        is_relative=is_relative,
                    )
                )


def import_edges(module: ParsedModule) -> List[ImportEdge]:
    """Extracts a list of import edges from a parsed module.

    This function traverses the AST of a parsed module and extracts
    information about all import statements.

    Args:
        module: The ParsedModule to analyze.

    Returns:
        A list of ImportEdge objects found in the module.
    """
    visitor = ImportVisitor(module.uri)
    visitor.visit(module.tree)
    return visitor.imports
