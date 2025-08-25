from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from .tool import Tool, ToolContext


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
                    "description": (
                        "If true, applies the changes directly to the files. If false, "
                        "returns a list of references that would be changed."
                    ),
                },
            },
            "required": ["old_name", "new_name"],
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
        grouped_references = defaultdict(list)
        for ref in references:
            grouped_references[ref["uri"]].append(ref)

        for file_uri, refs in grouped_references.items():
            file_path = file_uri.replace("file://", "")
            path = Path(file_path)
            if not path.is_file():
                continue

            content = path.read_text()
            lines = content.splitlines(True)

            # Sort refs by line and column in reverse order
            refs.sort(key=lambda r: (r["range"]["start"]["line"], r["range"]["start"]["column"]), reverse=True)

            for ref in refs:
                line_num = ref["range"]["start"]["line"]
                start_char = ref["range"]["start"]["column"]

                line = lines[line_num]
                # The range from find_references can be broad. Find the exact position.
                actual_start = line.find(old_name, start_char)
                if actual_start != -1:
                    end_char = actual_start + len(old_name)
                    lines[line_num] = line[:actual_start] + new_name + line[end_char:]

            modified_content = "".join(lines)
            path.write_text(modified_content)
            modified_files.add(str(path))
            context.project_index.file_cache.invalidate(path)

        return {"status": "ok", "modified_files": list(modified_files)}
