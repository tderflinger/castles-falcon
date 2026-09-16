# AGENTS.md

This file defines sensible defaults for idiomatic Python development in this repository.

## Core Principles

- Prefer clarity over cleverness.
- Prefer idiomatic Python code.
- Keep functions small, composable, and testable.
- Make side effects explicit at the boundaries (CLI, I/O, network, DB).
- Use types and docstrings for public APIs.
- Fail fast with actionable error messages.

## Python Version And Environment

- Target Python 3.12+ unless project constraints require otherwise.
- Use `uv` for environment and dependency management.
- Keep the project virtual environment at `.venv/` (managed by `uv`).
- Do not rely on global Python packages.

Recommended setup:

```bash
uv python install 3.12
uv venv --python 3.12
uv sync
```

## Dependency Management

- Prefer a single source of truth in `pyproject.toml`.
- Use optional dependency groups for `dev`, `test`, and `docs` tooling.
- Pin major versions for runtime dependencies; keep tooling reasonably current.

Common `uv` workflows:

```bash
uv add <package>
uv add --dev <package>
uv sync
```

If `requirements.txt` is needed for deployment, generate it from lock data rather than maintaining duplicate manual lists:

```bash
uv export --format requirements-txt -o requirements.txt
```

## Project Layout

Use a `src/` layout for import safety:

```text
src/<package_name>/
tests/
pyproject.toml
```

- Place executable entry points in `src/<package_name>/cli.py`.
- Keep scripts minimal; move business logic into package modules.

## Style And Formatting

- Use `ruff` for linting and import ordering.
- Use `ruff format` (or `black` if already established) for formatting.
- Enforce a line length of 88 (unless project standard differs).

Suggested commands:

```bash
uv run ruff check .
uv run ruff format .
```

## Typing

- Add type hints to all new or changed functions.
- Prefer builtin generics (`list[str]`, `dict[str, int]`) and `|` unions.
- Type all public interfaces and module boundaries.

Type-check with `mypy` (or `pyright` if already used):

```bash
uv run mypy src
```

## Testing

- Use `pytest`.
- Co-locate unit tests under `tests/` mirroring package structure.
- Name tests by behavior, not implementation detail.
- Add regression tests for every bug fix.

Suggested command:

```bash
uv run pytest -q
```

## Documentation And Docstrings

- Write concise docstrings for public modules, classes, and functions.
- Document args, return values, and raised exceptions where non-obvious.
- Keep README examples executable and up to date.

## Logging And Errors

- Use `logging` instead of `print` in library code.
- Raise specific exceptions, not bare `Exception`.
- Preserve original tracebacks when re-raising (`raise ... from exc`).

## Git And CI Expectations

Before opening a PR, run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q
```

CI should enforce the same checks to keep local and remote behavior consistent.

## Agent Behavior Defaults

- Make minimal, targeted changes.
- Avoid unrelated refactors in feature or bug-fix branches.
- Update tests and docs in the same change when behavior changes.
- If requirements are ambiguous, pick the simplest robust option and document assumptions.
