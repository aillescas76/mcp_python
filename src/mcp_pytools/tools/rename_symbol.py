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

    def visit_alias(self, node: ast.alias) -> ast.alias:
        if node.name == self.old_name:
            node.name = self.new_name
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
                "file_path": {
                    "type": "string",
                    "description": "The path to the file where the rename originates.",
                },
                "old_name": {
                    "type": "string",
                    "description": "The symbol name to be replaced.",
                },
                "new_name": {
                    "type": "string",
                    "description": "The new name for the symbol.",
                },
                "apply": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, applies the changes directly to the files. If false, returns a list of references that would be changed.",
                },
            },
            "required": ["file_path", "old_name", "new_name"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, Any]:
        old_name = kwargs["old_name"]
        new_name = kwargs["new_name"]
        apply = kwargs.get("apply", False)

        if not old_name or not new_name:
            return {"error": "Old symbol name and new name cannot be empty."}

        find_references_tool = context.tool_registry.get_tool("find_references")
        references = await find_references_tool.handle(context, symbol=old_name)

        if not references:
            return {"error": f"No references found for symbol: {old_name}"}

        if not apply:
            return {"status": "ok", "references": references}

        modified_files = set()
        for ref in references:
            file_path = ref["uri"].replace("file://", "")
            path = Path(file_path)
            if not path.is_file():
                continue

            original_content = path.read_text()
            tree = ast.parse(original_content)

            transformer = RenameTransformer(old_name, new_name)
            new_tree = transformer.visit(tree)
            ast.fix_missing_locations(new_tree)

            modified_content = astunparse.unparse(new_tree)
            path.write_text(modified_content)
            modified_files.add(str(path))

        for file_path in modified_files:
            context.project_index.file_cache.invalidate(Path(file_path))

        return {"status": "ok", "modified_files": list(modified_files)}
