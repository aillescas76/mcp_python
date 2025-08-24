import ast
from pathlib import Path
from typing import Any, Dict

import astunparse

from .tool import Tool, ToolContext


class RenameTransformer(ast.NodeTransformer):
    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id == self.old_name:
            node.id = self.new_name
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        if node.name == self.old_name:
            node.name = self.new_name
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if node.name == self.old_name:
            node.name = self.new_name
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        if node.arg == self.old_name:
            node.arg = self.new_name
        self.generic_visit(node)
        return node


class RenameSymbolTool(Tool):
    @property
    def name(self) -> str:
        return "rename_symbol"

    @property
    def description(self) -> str:
        return "Renames a symbol and all its references across the project."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "old_name": {"type": "string"},
                "new_name": {"type": "string"},
                "apply": {"type": "boolean", "default": False},
            },
            "required": ["file_path", "old_name", "new_name"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, Any]:
        file_path = kwargs["file_path"]
        old_name = kwargs["old_name"]
        new_name = kwargs["new_name"]
        apply = kwargs.get("apply", False)

        if not old_name or not new_name:
            return {"error": "Old symbol name and new name cannot be empty."}

        path = Path(file_path)
        if not path.is_file():
            return {"error": f"File not found: {file_path}"}

        original_content = path.read_text()
        tree = ast.parse(original_content)

        transformer = RenameTransformer(old_name, new_name)
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)

        modified_content = astunparse.unparse(new_tree)

        if apply:
            path.write_text(modified_content)
            context.project_index.file_cache.invalidate(path)
            return {"status": "ok"}
        else:
            return {"modified_content": modified_content}
