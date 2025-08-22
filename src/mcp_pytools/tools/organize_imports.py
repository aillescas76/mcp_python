import subprocess
import difflib
import sys
from pathlib import Path
from typing import Dict, Any
import os

from ..index.project import ProjectIndex

async def organize_imports_tool(
    index: ProjectIndex, uri: str, apply: bool = False
) -> Dict[str, Any]:
    """
    Organizes imports in a Python module using ruff.
    """
    if not uri.startswith("file://"):
        return {"error": "URI must be a file URI"}

    path = Path(uri[7:])
    if not path.is_file():
        return {"error": f"File not found: {path}"}

    original_content = index.file_cache.get_text(path)

    # Prepare environment to include virtual environment's bin in PATH
    env = os.environ.copy()
    venv_bin_path = str(Path(sys.prefix) / "bin")
    if "PATH" in env:
        env["PATH"] = f"{venv_bin_path}:{env["PATH"]}"
    else:
        env["PATH"] = venv_bin_path

    ruff_executable = "ruff"
    config_path = index.root / "pyproject.toml"

    if apply:
        # In-place formatting
        run_result = subprocess.run([ruff_executable, "check", "--fix", "--config", str(config_path), str(path)], capture_output=True, text=True, cwd=index.root, env=env)
        # ruff check returns non-zero if there are un-fixed issues, which is fine.
        # Invalidate cache so next read gets the fresh content
        index.file_cache.invalidate(path)
        return {"status": "ok"}
    else:
        # Get formatted content from stdin
        run_result = subprocess.run(
            [ruff_executable, "check", "--fix", "--config", str(config_path), "--stdin-filename", str(path)],
            input=original_content,
            capture_output=True,
            text=True,
            cwd=index.root,
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
