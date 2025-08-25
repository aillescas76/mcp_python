For any task related to MCP creation reference to the file @planning/implement_server_mcp_with_python.md

Technology Stack & Conventions
Language: Python 3.11+

Frameworks: mcp, Pydantic, Pytest.

Dependency Management: This project uses uv. All dependencies are managed in pyproject.toml.

Environment Setup:

Create a virtual environment: python3 -m venv.venv

Activate it: source.venv/bin/activate

Install dependencies: uv pip install -e ".[dev]"

Common Commands:

Run tests: uv run test

Lint & Format: uv run lint

Run dev server: uv run dev

</PROJECT_CONTEXT>

<STYLE_GUIDE>
Annotation: This section defines the exact coding style for the project. The AI must adhere to these rules when generating or modifying any code.

Base Standard: PEP 8.

Deviations:

Maximum line length is 100 characters.

Naming Conventions:

Functions/Variables: snake_case (e.g., get_user_tasks)

Constants: UPPER_SNAKE_CASE (e.g., DATABASE_URL)

Classes: CapWords (e.g., TaskService)

Test Functions: test_ prefix with snake_case (e.g., test_create_task_successfully)

Import Order:

Python standard library imports.

Third-party library imports (alphabetical).

Local application imports from src (alphabetical).

Docstring Format: Google Style. All public functions, methods, and classes must have a docstring.

Python

def example_function(param1: int, param2: str) -> bool:
    """Example summary line.

    Extended description of the function's behavior and purpose.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.

    Returns:
        A boolean indicating success or failure.
    """
    return True
</STYLE_GUIDE>

<NON_NEGOTIABLE_CONSTRAINTS>
Annotation: These are absolute rules that must be followed at all times, across all modes of operation. Violating these constraints is a critical failure.

Testing Mandate
All new features must be accompanied by unit tests.

All bug fixes must include a regression test that fails before the fix and passes after.

All tests must be written using pytest.

Version Control Protocol
Git is the only version control system.

All work must be done on a feature branch created from main.

Commit messages must follow the Conventional Commits specification (e.g., feat:, fix:, docs:).

The "Do Not" List
DO NOT modify the .github/ workflows without explicit instruction.

DO NOT read, open, or write to .env files.

DO NOT commit secrets, API keys, or credentials into the repository.

DO NOT use print() statements for debugging; use the configured logging module.

Responsible AI Guidelines
Privacy: Do not log any user-provided task content or personally identifiable information.

Security: All API endpoints that modify data must be protected by authentication and authorization logic. All user input must be validated using Pydantic models to prevent injection attacks.

</NON_NEGOTIABLE_CONSTRAINTS>
<CONTEXT_GENERATION_RULES>
Use python-code-tools to construct the context instead of read whole files. Just get the code for the methods that you need and only read the files that you need to edit. If you can do the edit just with the information got by python-code-tools, use it.
</CONTEXT_GENERATION_RULES>
