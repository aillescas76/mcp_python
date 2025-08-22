from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.organize_imports import organize_imports_tool

@pytest.fixture
def organize_imports_project(tmp_path: Path) -> Path:
    # Create a simplified pyproject.toml for ruff configuration
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["I"] # Only enable isort for this test
"""
    )

    file_path = tmp_path / "module_to_organize.py"
    file_path.write_text(
        """import os
import sys

from collections import defaultdict
import json

def my_func():
    pass
"""
    )
    return tmp_path

@pytest.mark.asyncio
async def test_organize_imports_dry_run(organize_imports_project: Path):
    root = organize_imports_project
    indexer = ProjectIndex(root)
    indexer.build()

    module_uri = (root / "module_to_organize.py").as_uri()
    result = await organize_imports_tool(indexer, module_uri, apply=False)

    assert "diff" in result
    assert result["diff"]
    # Expected diff for import reordering
    expected_diff_part = """--- {path}
+++ {path}
@@ -1,8 +1,8 @@
+import json
 import os
 import sys
+from collections import defaultdict
 
-from collections import defaultdict
-import json
 
 def my_func():
     pass
"""
    assert expected_diff_part.format(path=str(root / "module_to_organize.py")) == result["diff"]

    # Check that the file is not modified
    original_content = (root / "module_to_organize.py").read_text()
    assert "import os\nimport sys" in original_content

@pytest.mark.asyncio
async def test_organize_imports_apply(organize_imports_project: Path):
    root = organize_imports_project
    file_to_organize = root / "module_to_organize.py"
    original_content = file_to_organize.read_text()

    indexer = ProjectIndex(root)
    indexer.build()

    module_uri = file_to_organize.as_uri()
    result = await organize_imports_tool(indexer, module_uri, apply=True)

    assert result.get("status") == "ok"

    # Check that the file is modified
    modified_content = file_to_organize.read_text()
    assert modified_content != original_content
    assert "import json\nimport os\nimport sys\nfrom collections import defaultdict\n\n\ndef my_func():\n    pass\n" == modified_content
