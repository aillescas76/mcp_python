# src/mcp_pytools/analysis/symbols.py

import ast
import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional

from mcp_pytools.astutils.parser import ParsedModule, Range, Position


class SymbolKind(Enum):
    FILE = 1
    MODULE = 2
    NAMESPACE = 3
    PACKAGE = 4
    CLASS = 5
    METHOD = 6
    PROPERTY = 7
    FIELD = 8
    CONSTRUCTOR = 9
    ENUM = 10
    INTERFACE = 11
    FUNCTION = 12
    VARIABLE = 13
    CONSTANT = 14
    STRING = 15
    NUMBER = 16
    BOOLEAN = 17
    ARRAY = 18
    OBJECT = 19
    KEY = 20
    NULL = 21
    ENUM_MEMBER = 22
    STRUCT = 23
    EVENT = 24
    OPERATOR = 25
    TYPE_PARAMETER = 26


@dataclasses.dataclass
class Symbol:
    name: str
    kind: SymbolKind
    range: Range
    container: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind.name,
            "range": self.range.to_dict(),
            "container": self.container,
        }


class SymbolVisitor(ast.NodeVisitor):
    def __init__(self):
        self.symbols: List[Symbol] = []
        self.container_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        start_pos = Position(
            line=node.lineno - 1,
            column=node.col_offset + len("class ")
        )
        end_pos = Position(
            line=node.lineno - 1,
            column=start_pos.column + len(node.name)
        )
        name_range = Range(start=start_pos, end=end_pos)

        self.symbols.append(
            Symbol(
                name=node.name,
                kind=SymbolKind.CLASS,
                range=name_range,
                container=".".join(self.container_stack) or None,
            )
        )
        self.container_stack.append(node.name)
        self.generic_visit(node)
        self.container_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        kind = SymbolKind.METHOD if self.container_stack else SymbolKind.FUNCTION
        start_pos = Position(
            line=node.lineno - 1,
            column=node.col_offset + len("def ")
        )
        end_pos = Position(
            line=node.lineno - 1,
            column=start_pos.column + len(node.name)
        )
        name_range = Range(start=start_pos, end=end_pos)

        self.symbols.append(
            Symbol(
                name=node.name,
                kind=kind,
                range=name_range,
                container=".".join(self.container_stack) or None,
            )
        )
        self.container_stack.append(node.name)
        self.generic_visit(node)
        self.container_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        kind = SymbolKind.METHOD if self.container_stack else SymbolKind.FUNCTION
        start_pos = Position(
            line=node.lineno - 1,
            column=node.col_offset + len("async def ")
        )
        end_pos = Position(
            line=node.lineno - 1,
            column=start_pos.column + len(node.name)
        )
        name_range = Range(start=start_pos, end=end_pos)

        self.symbols.append(
            Symbol(
                name=node.name,
                kind=kind,
                range=name_range,
                container=".".join(self.container_stack) or None,
            )
        )
        self.container_stack.append(node.name)
        self.generic_visit(node)
        self.container_stack.pop()

    def visit_Assign(self, node: ast.Assign):
        # Simple assignment: x = 1
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.symbols.append(
                    Symbol(
                        name=target.id,
                        kind=SymbolKind.VARIABLE,
                        range=target._range,
                        container=".".join(self.container_stack) or None,
                    )
                )
        self.generic_visit(node)


def document_symbols(module: ParsedModule) -> List[Symbol]:
    """Extracts a list of symbols from a parsed module.

    This function traverses the AST of a parsed module and extracts
    information about classes, functions, and variables.

    Args:
        module: The ParsedModule to analyze.

    Returns:
        A list of Symbol objects found in the module.
    """
    visitor = SymbolVisitor()
    visitor.visit(module.tree)
    return visitor.symbols