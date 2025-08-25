# Plan to fix MCP server tool name issue

The `mcp` server is rejecting tool names that contain dots. This is because the server expects tool names to match the pattern `^[a-zA-Z0-9_-]+$`. Several tools in this project use dots in their names, causing `400 Bad Request` errors.

The solution is to rename the affected tools by replacing the dots with underscores. This will make the tool names compliant with the `mcp` server's requirements.

Here are the files that need to be modified and the changes to be made:

1.  **`src/mcp_pytools/tools/index_build.py`**:
    -   Change the `name` property of the `IndexBuildTool` class from `"index.build"` to `"index_build"`.

2.  **`src/mcp_pytools/tools/index_invalidate.py`**:
    -   Change the `name` property of the `IndexInvalidateTool` class from `"index.invalidate"` to `"index_invalidate"`.

3.  **`src/mcp_pytools/tools/index_status.py`**:
    -   Change the `name` property of the `IndexStatusTool` class from `"index.status"` to `"index_status"`.

These changes will resolve the `Invalid 'tools[*].name'` errors and allow the `mcp` server to work correctly.
