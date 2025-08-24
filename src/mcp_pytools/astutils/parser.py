# src/mcp_pytools/astutils/parser.py

import ast
import dataclasses
from typing import Any, Dict, List, Optional


@dataclasses.dataclass
class Position:
    line: int
    column: int

    def to_dict(self) -> Dict[str, Any]:
        return {"line": self.line, "column": self.column}


@dataclasses.dataclass
class Range:
    start: Position
    end: Position

    def to_dict(self) -> Dict[str, Any]:
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclasses.dataclass
class ParsedModule:
    tree: ast.AST
    text: str
    lines: List[str]
    uri: str


class StructuredSyntaxError(Exception):
    def __init__(self, msg, filename, lineno, offset, text):
        self.msg = msg
        self.filename = filename
        self.lineno = lineno
        self.offset = offset
        self.text = text

    def __str__(self):
        return f"{self.filename}:{self.lineno}:{self.offset}: {self.msg}"


def get_node_at_position(tree: ast.AST, position: Position) -> Optional[ast.AST]:
    """Finds the innermost AST node at the given 0-indexed position.

    Args:
        tree: The root of the AST.
        position: The 0-indexed line and column.

    Returns:
        The innermost AST node at the position, or None if not found.
    """
    target_node = None
    for node in ast.walk(tree):
        if hasattr(node, "_range"):
            node_range = node._range
            if (
                node_range.start.line <= position.line <= node_range.end.line
                and (
                    (node_range.start.line == position.line and position.column >= node_range.start.column)
                    or node_range.start.line < position.line
                )
                and (
                    (node_range.end.line == position.line and position.column <= node_range.end.column)
                    or node_range.end.line > position.line
                )
            ):
                # This node contains the position. Check if it's a more specific match.
                if target_node is None or (
                    node_range.end.line - node_range.start.line
                    < target_node._range.end.line - target_node._range.start.line
                ) or (
                    node_range.end.line - node_range.start.line
                    == target_node._range.end.line - target_node._range.start.line
                    and node_range.end.column - node_range.start.column
                    < target_node._range.end.column - target_node._range.start.column
                ):
                    target_node = node
    return target_node


class ParentAndRangeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.parent = None

    def visit(self, node):
        if self.parent:
            node._parent = self.parent

        # Python 3.8+ provides end line and col offsets
        if hasattr(node, "lineno"):
            start = Position(line=node.lineno - 1, column=node.col_offset)
            if hasattr(node, "end_lineno") and node.end_lineno is not None:
                end = Position(line=node.end_lineno - 1, column=node.end_col_offset)
                node._range = Range(start=start, end=end)

        self.parent = node
        super().visit(node)
        self.parent = getattr(node, "_parent", None)


def parse_module(text: str, uri: str) -> ParsedModule:
    """Parses Python code into an AST with parent links and ranges.

    Args:
        text: The Python source code to parse.
        uri: The URI of the source file, used for error reporting.

    Returns:
        A ParsedModule instance containing the AST and metadata.

    Raises:
        StructuredSyntaxError: If the code contains a syntax error.
    """
    try:
        tree = ast.parse(text, filename=uri, type_comments=True)
        visitor = ParentAndRangeVisitor()
        visitor.visit(tree)
        lines = text.splitlines()
        return ParsedModule(tree=tree, text=text, lines=lines, uri=uri)
    except SyntaxError as e:
        raise StructuredSyntaxError(
            msg=e.msg,
            filename=e.filename,
            lineno=e.lineno,
            offset=e.offset,
            text=e.text,
        ) from e
