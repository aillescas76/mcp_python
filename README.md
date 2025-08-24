# MCP Python Code Navigation Server

This project provides a powerful MCP (Model Context Protocol) server for Python that enhances AI-driven development by offering advanced code navigation, analysis, and refactoring capabilities.

## Features

The server provides a suite of tools to understand and manipulate Python codebases:

- **Find Definition**: Locate the definition of a symbol (variable, function, class, etc.).
- **Find References**: Find all references to a symbol across the project.
- **Document Symbols**: List all symbols (classes, functions, methods) in a given file.
- **Organize Imports**: Automatically sort and format import statements.
- **Rename Symbol**: Safely rename a symbol and all its references.
- **Import Graph**: Visualize the import relationships between modules.
- **And more...**: Check out the `src/mcp_pytools/tools` directory for a full list of available tools.

## Getting Started

### Prerequisites

- Python 3.10+
- `uv` (recommended for environment management)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/user/mcp_python.git # Replace with the actual URL
    cd mcp_python
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -e ".[dev]"
    ```

## Running the Server

To run the MCP server, use the `mcp-pytools-server` command. You can optionally provide a path to the root of the Python project you want to analyze. If no path is given, it will default to the current directory.

```bash
mcp-pytools-server [PROJECT_ROOT_PATH]
```

**Example:**

To run the server for a project located at `~/code/my-python-project`:

```bash
mcp-pytools-server ~/code/my-python-project
```

## Configuring IDEs and Editors

To use this server with your favorite AI-powered editor, you need to configure it as an MCP server. Here are examples for some popular clients.

**Note:** You must use the absolute path to the `mcp-pytools-server` executable, which is located in your virtual environment's `bin` directory (e.g., `/path/to/your/project/.venv/bin/mcp-pytools-server`).

### Gemini CLI / Claude Code / etc.

Create or edit your MCP configuration file (e.g., `~/.config/gemini/mcp.json` or `~/.cursor/mcp.json`) and add the following entry. This example sets up the server for a project located at `~/code/my-python-project`.

```json
{
  "mcpServers": {
    "python-code-tools": {
      "command": "/path/to/your/project/.venv/bin/mcp-pytools-server",
      "args": [
        "/path/to/your/project/src"
      ],
      "description": "MCP server for Python code navigation and refactoring."
    }
  }
}
```

Replace `/path/to/your/project/.venv/bin/mcp-pytools-server` with the actual absolute path to the server executable in your virtual environment and `/path/to/your/project/src` with the path to the code you want to analyze.

## Usage Tips

Once the server is running and your editor is configured, you can start using its capabilities through natural language prompts. Here are some examples of what you can ask your AI assistant:

- **"Find the definition of the `ServerContext` class."**
- **"Where is the `create_tool_handler` function used?"**
- **"Rename the `handler` variable to `tool_handler` in `server.py`."**
- **"List all the functions in `src/mcp_pytools/tools/find_definition.py`."**
- **"Clean up the imports in `src/mcp_pytools/server.py`."**

The server will process these requests and, with your confirmation, perform the corresponding actions on your codebase.
