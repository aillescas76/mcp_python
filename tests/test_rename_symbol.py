from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.rename_symbol import rename_symbol_tool

@pytest.fixture
def rename_project(tmp_path: Path) -> Path:
    # Module 1: Function and variable
    (tmp_path / "module1.py").write_text(
        """GLOBAL_VAR = 10

def my_function(a, b):
    return a + b

result = my_function(1, GLOBAL_VAR)
"""
    )

    # Module 2: Class and method, imports from module1
    (tmp_path / "module2.py").write_text(
        """from .module1 import my_function, GLOBAL_VAR

class MyClass:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return my_function(self.value, GLOBAL_VAR)

instance = MyClass(5)
"""
    )

    # Module 3: Usage of class and function from module2
    (tmp_path / "module3.py").write_text(
        """from .module2 import MyClass

def another_func():
    obj = MyClass(100)
    return obj.get_value()
"""
    )

    # __init__.py for package structure
    (tmp_path / "__init__.py").write_text("")

    return tmp_path

@pytest.mark.asyncio
async def test_rename_symbol_function_dry_run(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module1.py")
    old_symbol = "my_function"
    new_symbol = "new_function_name"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=False)

    assert "modified_content" in result
    modified_content = result["modified_content"]

    assert "new_function_name" in modified_content
    assert "my_function" not in modified_content

    # Verify file is not modified
    assert "my_function" in (root / "module1.py").read_text()

@pytest.mark.asyncio
async def test_rename_symbol_function_apply(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module1.py")
    old_symbol = "my_function"
    new_symbol = "new_function_name"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=True)

    assert result.get("status") == "ok"

    # Verify file is modified
    assert "new_function_name" in (root / "module1.py").read_text()
    assert "my_function" not in (root / "module1.py").read_text()

@pytest.mark.asyncio
async def test_rename_symbol_class_dry_run(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module2.py")
    old_symbol = "MyClass"
    new_symbol = "NewClass"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=False)

    assert "modified_content" in result
    modified_content = result["modified_content"]

    assert "NewClass" in modified_content
    assert "MyClass" not in modified_content

    # Verify file is not modified
    assert "MyClass" in (root / "module2.py").read_text()

@pytest.mark.asyncio
async def test_rename_symbol_class_apply(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module2.py")
    old_symbol = "MyClass"
    new_symbol = "NewClass"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=True)

    assert result.get("status") == "ok"

    # Verify file is modified
    assert "NewClass" in (root / "module2.py").read_text()
    assert "MyClass" not in (root / "module2.py").read_text()

@pytest.mark.asyncio
async def test_rename_symbol_method_dry_run(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module2.py")
    old_symbol = "get_value"
    new_symbol = "retrieve_value"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=False)

    assert "modified_content" in result
    modified_content = result["modified_content"]

    assert "retrieve_value" in modified_content
    assert "get_value" not in modified_content

    # Verify file is not modified
    assert "get_value" in (root / "module2.py").read_text()

@pytest.mark.asyncio
async def test_rename_symbol_method_apply(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module2.py")
    old_symbol = "get_value"
    new_symbol = "retrieve_value"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=True)

    assert result.get("status") == "ok"

    # Verify file is modified
    assert "retrieve_value" in (root / "module2.py").read_text()
    assert "get_value" not in (root / "module2.py").read_text()

@pytest.mark.asyncio
async def test_rename_symbol_variable_dry_run(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module1.py")
    old_symbol = "GLOBAL_VAR"
    new_symbol = "GLOBAL_FOO_VAR"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=False)

    assert "modified_content" in result
    modified_content = result["modified_content"]

    assert "GLOBAL_FOO_VAR" in modified_content
    assert "GLOBAL_VAR" not in modified_content

    # Verify file is not modified
    assert "GLOBAL_VAR" in (root / "module1.py").read_text()

@pytest.mark.asyncio
async def test_rename_symbol_variable_apply(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module1.py")
    old_symbol = "GLOBAL_VAR"
    new_symbol = "GLOBAL_FOO_VAR"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=True)

    assert result.get("status") == "ok"

    # Verify file is modified
    assert "GLOBAL_FOO_VAR" in (root / "module1.py").read_text()
    assert "GLOBAL_VAR" not in (root / "module1.py").read_text()

@pytest.mark.asyncio
async def test_rename_symbol_not_found(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module1.py")
    old_symbol = "non_existent_symbol"
    new_symbol = "new_name"
    result = await rename_symbol_tool(indexer, file_path, old_symbol, new_symbol, apply=False)

    assert "modified_content" in result
    assert old_symbol not in result["modified_content"]
    assert new_symbol not in result["modified_content"]

@pytest.mark.asyncio
async def test_rename_symbol_empty_names(rename_project: Path):
    root = rename_project
    indexer = ProjectIndex(root)
    indexer.build()

    file_path = str(root / "module1.py")
    result = await rename_symbol_tool(indexer, file_path, "", "new_name", apply=False)
    assert "error" in result

    result = await rename_symbol_tool(indexer, file_path, "old_name", "", apply=False)
    assert "error" in result