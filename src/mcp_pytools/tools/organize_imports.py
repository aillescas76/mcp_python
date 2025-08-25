import difflib
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from .tool import Tool, ToolContext


class OrganizeImportsTool(Tool):
    @property
    def name(self) -> str:
        return "organize_imports"

    @property
    def description(self) -> str:
        return "Sorts and formats import statements in a Python file according to PEP 8 standards using the 'ruff' linter. It can either return a diff of the changes or apply them directly to the file."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The file URI of the Python module to organize imports for.",
                },
                "apply": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, applies the changes directly to the file. If false, returns a diff of the proposed changes.",
                },
            },
            "required": ["uri"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, Any]:
        uri = kwargs["uri"]
        apply = kwargs.get("apply", False)

        if not uri.startswith("file://"):
            return {"error": "URI must be a file URI"}

        path = Path(uri[7:])
        if not path.is_file():
            return {"error": f"File not found: {path}"}

        original_content = context.project_index.file_cache.get_text(path)

        env = os.environ.copy()
        venv_bin_path = str(Path(sys.prefix) / "bin")
        if "PATH" in env:
            env["PATH"] = f"{venv_bin_path}:{env['PATH']}"
        else:
            env["PATH"] = venv_bin_path

        ruff_executable = "ruff"
        config_path = context.project_index.root / "pyproject.toml"

        if apply:
            subprocess.run(
                [
                    ruff_executable,
                    "check",
                    "--fix",
                    "--config",
                    str(config_path),
                    str(path),
                ],
                capture_output=True,
                text=True,
                cwd=context.project_index.root,
                env=env,
            )
            context.project_index.file_cache.invalidate(path)
            return {"status": "ok"}
        else:
            run_result = subprocess.run(
                [
                    ruff_executable,
                    "check",
                    "--fix",
                    "--config",
                    str(config_path),
                    "--stdin-filename",
                    str(path),
                ],
                input=original_content,
                capture_output=True,
                text=True,
                cwd=context.project_index.root,
                env=env,
            )

            fixed_content = run_result.stdout

            diff = "".join(
                difflib.unified_diff(
                    original_content.splitlines(keepends=True),
                    fixed_content.splitlines(keepends=True),
                    fromfile=str(path),
                    tofile=str(path),
                )
            )
            return {"diff": diff}
