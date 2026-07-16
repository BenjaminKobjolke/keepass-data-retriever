# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KeePass Data Retriever is a Windows desktop application that provides quick KeePass database search via global hotkeys. It uses Python with Tkinter for the GUI and PyKeePass for database access. The application allows users to quickly search their KeePass database and auto-type or paste credentials into other applications.

## Coding Rules

Rules synced from: `D:\GIT\BenjaminKobjolke\claude-code\coding-rules`
(COMMON_RULES.md + AI_RULES.md in full, PYTHON_RULES.md applicable subset)

### Common Rules (all languages)

- **Keep CLAUDE.md in sync** — when rules change in the source folder, re-run `/coding-rules:add-or-update`.
- **Use objects for related values** — bundle related parameters into a DTO/Settings/Config object instead of long parameter lists.
- **No bag-of-keys returns at module boundaries** — public methods on managers/repositories/services return typed objects (DTO, value object, domain model), never raw dicts indexed by string keys. `get_thing() -> Thing | None` (zero or one) vs `get_things() -> list[Thing]` — never overload one return to mean both. `None` = not found; empty collection = found but empty. JSON-decoded blobs crossing a boundary get wrapped in a value object. Private in-method dict juggling is fine.
- **Reuse existing models before inventing shapes** — before designing a new DTO, grep for an existing domain class that already owns the data; extend it instead of creating a parallel shape.
- **Tests pin the shape before the refactor** — when converting a dict return to a typed object, write a characterization test against the old API first, run it green, then refactor; the test stays green.
- **TDD for features and bug fixes** — write tests first, confirm they fail, implement, confirm they pass.
- **Integration tests required** — in addition to unit tests.
- **Test runner scripts** — `tools/run_tests.bat` (unit) and `tools/run_integration_tests.bat` (integration) must exist.
- **Prefer type-safe values** — typed DTOs, enums, `Literal`, typed settings over stringly typed values.
- **String constants centralized** — in a dedicated module/class, not scattered raw strings.
- **Reusable tooling** — before building project-specific scripts (audits, codemods, build helpers), check the language's `*_setup_files/` folder in the coding-rules repo; if you build something new and general, copy it back there and document it.
- **README.md mandatory** — name, description, setup, usage, dependencies.
- **DRY** — extract repeated logic into shared helpers; constants for repeated values.
- **Derive, don't duplicate** — when one value strictly determines another, pass only the determinant and derive the rest (e.g. enum method with exhaustive match); never thread co-varying parameters side by side.
- **KISS / YAGNI** — simplest solution that works; no interface with one implementation, no factory for one product, no config for a value that never changes; boring over clever; deletion over addition.
- **Confirm dependency versions** — before adding any new package, confirm the version with the user.
- **Centralized error handling & logging** — one central handler, structured logging with levels and context; no ad-hoc scattered try/except.
- **Centralized logger, single off switch** — all logging goes through `AppLogger` (`app_logger.py`); never `print()` or `logging.getLogger()` at call sites. Levels and on/off live in the logger config.
- **Input validation at boundaries** — validate all external data (user input, files, external services) before processing; fail fast with clear errors.
- **Max file length 300 lines** — split by domain; exceptions: generated files, config, test files with many similar cases.
- **Naming conventions** — files/functions/variables `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- **Comments explain why, not what** — document workarounds, non-obvious constraints; delete stale comments.
- **Security baseline** — never commit secrets; escape output; parameterized queries; validate input; keep deps updated.
- **No hardcoded environment values** — paths, hosts, ports, URLs come from central config with a committed `.example` template (this project: `settings.ini` + `settings_example.ini`).
- **No god classes** — one responsibility per class; warning signs: >5 public methods, >4 constructor deps, unrelated domains in one class.
- **Self-describing classes** — when behavior depends on a class's fields (search, serialization, display, validation), the class declares its own fields via a contract (Protocol method or dataclass field metadata); never hardcode field lists in consumers.
- **Inject collaborators, don't fold dependencies in** — prefer constructor-injected collaborator objects over mixins/traits; never instantiate a service with a constructor call inside a method; collapse many one-line config getters into one config value object.

### AI Workflow Rules (always apply)

#### Feature / Change Workflow

After a plan is proposed and the user approves it, follow this chain. The DRY gate is a precondition for implementing — not just an earlier step.

```
plan approved
  → /plan:dry            check approved plan for DRY/consolidation BEFORE code
  → /plan:dry-checked    reload + review the DRY-adjusted plan
  → /convention:check    scan for existing patterns/components to reuse
  ─────────────────────  DRY GATE — must be cleared to proceed
  → restate Definition-of-Done aloud
  → implement
  → /dry:check           post-implementation DRY audit (template below)
  → /verify:after-change run tests + code analysis
```

##### DRY gate (precondition for implementing)

Do not write a single line until ALL are true. Restate this gate aloud at the moment you start implementing — if you cannot, the gate is not cleared:

- [ ] `/plan:dry` ran and the plan was adjusted for any duplication found.
- [ ] `/plan:dry-checked` reloaded and confirmed the adjusted plan.
- [ ] `/convention:check` found the existing utilities/patterns to reuse.

The gate survives the `implement` step: if mid-implementation you add a new helper, type, or pattern the gate would have caught, stop and re-clear it before continuing.

##### Definition of Done — restate aloud before implementing

Before the first edit, state in chat what "done" means for THIS change:

- [ ] Scope: <one line — what changes, what does not>
- [ ] Reuse: <existing function/component this builds on, with path>
- [ ] DRY gate cleared (above)
- [ ] `/dry:check` clean
- [ ] `/verify:after-change` green (tests + analysis)

##### Post-implementation DRY audit — paste-in template

Run `/dry:check`, then paste and fill:

```
DRY audit — <change name>
Changed files:     <list>
Duplication found: <none | describe>
Consolidated into: <shared fn/module + path | n/a>
Convention reused: <name + path>
Verdict:           <clean | needs rework>
```

#### Bug-Fix Workflow

Bug fixes use a shorter variant (no plan-DRY phase):

```
bugs:fix
  → /verify:after-change
```

### Python Rules (applicable subset)

- **GUI framework** — new desktop projects use PySide6. **Exception: this project stays on Tkinter** (existing app); do not migrate.
- **`pyproject.toml` is the single source of truth** — deps via `uv add`, `uv.lock` committed, Python version pinned.
- **Formatting / lint / types enforced** — `uv run ruff check .`, `ruff format --check`, `uv run mypy .` must pass.
- **Type hints on public APIs** — typed parameters + return types; use `Protocol`, `TypedDict`, `Literal` where helpful; avoid `Any` except at I/O boundaries.
- **Centralized settings** — one settings module with env/INI overrides; this project's is `config.py` (backed by `settings.ini`). Nothing reads config values directly elsewhere.
- **Tests mandatory, fast, isolated** — pytest; no network in unit tests; tmp dirs/fixtures, no reliance on machine state.
- **`MagicMock(spec=RealClass)` always** — bare `MagicMock()` accepts nonexistent attributes and hides bugs; mock methods as methods (`mock.get_body.return_value`), not fake attributes.
- **Required batch files** — `start.bat` (root), `tools/run_tests.bat` (both exist).
- **Async** — `asyncio` for I/O-bound work; never block the event loop (`time.sleep`, sync HTTP) in async contexts.
- **Validation** — Pydantic for data validation at boundaries.
- **Structured logging** — all logging through `AppLogger` (`app_logger.py`) wrapping `logging`/`structlog`; never `print()` or direct `logging.getLogger()` in feature code.
- **Self-describing classes** — Protocol with `get_searchable_fields()`-style method for simple cases; dataclass field metadata for declarative per-field control.

Skipped as not applicable (Tkinter desktop app, no web/DB): Jinja2 template engine, localization / translation keys, SQLAlchemy, release workflow.

### Graphify Knowledge Graph

Opted in — see the `## graphify` section at the bottom of this file for usage and refresh rules.

## Architecture

### Core Components
- `main.py`: Entry point and main KeePassRetriever class that manages database connection and application lifecycle
- `config.py`: Configuration management using INI files with default fallbacks
- `ui/`: UI components
  - `search_window.py`: Main application window coordinator
  - `input/`: Input handling module
    - `input_manager.py`: Manages input fields and keyboard handling for different modes
    - `command_handler.py`: Handles /exit, /reload, /settings commands
  - `password_dialog.py`: Password entry dialog for database unlock
  - `state_manager.py`: Application state management (AppState enum)
  - `keyboard_handler.py`: Handles credential typing/pasting with special character support
  - `entry_actions_handler.py`: Manages actions for selected KeePass entries
  - `action_buttons.py`: Dynamic action buttons that adapt text based on paste_mode setting
  - `mode_indicator.py`: Visual indicator showing current app mode (RECENT/SEARCH/RESULTS/ACTIONS)
  - Window management: `window_manager.py`, `window_relations_manager.py`
  - UI components: `results_view.py`, `status_display.py`, `dark_entry.py`

### Key Features
- Global hotkey activation (default: alt+shift+F8)
- Recent entries tracking per window with deletion capability (Del key)
- Paste mode for reliable credential insertion (handles special characters like ^)
- Auto-type functionality for username/password combinations
- Multi-clipboard support for username/password copying
- Auto-lock database after idle timeout
- Window positioning modes (mouse, center, center_screen)

## Development Commands

Project uses `uv` for dependency management. `pyproject.toml` is the single source of truth; `uv.lock` is committed.

### Environment Setup
```bash
# First-time setup: creates .venv/, installs all deps (incl. dev + build extras), runs tests
install.bat

# Update all deps to latest, refresh lock, re-run lint/type/test
update.bat
```

### Running the Application
```bash
# Standard launch
start.bat

# Or directly via uv
uv run python main.py

# With custom database (legacy support)
uv run python main.py --database path/to/database.kdbx

# With password from command line (legacy support)
uv run python main.py --password yourpassword
```

### Tests / Lint / Types
```bash
# Run tests
tools\run_tests.bat
# or: uv run pytest tests/ -v

# Lint
uv run ruff check .

# Type check
uv run mypy .
```

### Building
```bash
# Compile to standalone executable
compile_exe.bat

# Internally: uv sync --extra build && uv run pyinstaller --name KeepassDataRetriever --onefile --windowed main.py
# Output: dist/KeepassDataRetriever.exe
```

## Configuration

The application uses `settings.ini` for configuration. Copy `settings_example.ini` to `settings.ini` and modify:

```ini
[General]
database_path = C:/path/to/database.kdbx
search_reset_timeout = 180
database_idle_timeout = 3600
debug_mode = false
window_position = mouse
paste_mode = true  # Use Ctrl+V paste instead of character typing

[Hotkeys]
search_hotkey = alt + shift + F8
```

### Important Configuration Notes
- `paste_mode`: Controls how credentials are inserted
  - `true` (default): Uses clipboard paste (Ctrl+V) - more reliable with special characters
  - `false`: Types character by character - automatically uses paste for passwords with `^` to avoid dead key issues
- The GUI dynamically updates button labels based on paste_mode ("Paste username" vs "Type username")

## Database Management

- Database connection is managed in `main.py:KeePassRetriever`
- Password authentication via GUI dialog (`ui/password_dialog.py`)
- Auto-lock after idle timeout to protect sensitive data
- Window relations stored in `window-relations.json` for recent entries tracking

## UI State Management

The application uses a centralized state system:
- `AppState` enum defines application states (INITIAL, SEARCH, RESULTS_LIST, ENTRY_ACTIONS, HIDDEN)
- `StateManager` handles state transitions and notifies listeners
- Components register as state listeners and update their UI accordingly
- `InputManager` updates the mode indicator based on current state
- `SearchWindow` coordinates all UI components

## Keyboard Handler and Special Characters

The `KeyboardHandler` class in `ui/keyboard_handler.py` manages credential typing/pasting:
- Respects the `paste_mode` configuration setting
- Automatically detects passwords with problematic characters (like `^`) and uses paste mode
- Dead key handling: The `^` character is a dead key on many keyboard layouts that causes issues with character-by-character typing
- Solution: Use clipboard paste (Ctrl+V) which bypasses keyboard layout issues

## Testing

Automated tests use pytest (`tools\run_tests.bat` or `uv run pytest tests/ -v`). Manual testing is done using the provided `test.kdbx` database.

### Testing Credential Input
To test special character handling:
1. Create test entries with passwords containing `^`, `@`, `!`, etc.
2. Test with `paste_mode=true` and `paste_mode=false` in settings.ini
3. Verify that passwords with `^` always use paste mode to avoid dead key issues

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- Judge coupling by direction: high **fan-in** + low fan-out (shared base / constants / DTO) is healthy; high **fan-out** (>~20 outgoing deps) is god-class risk and a refactor signal.
- After modifying code, rebuild via the **directed skill flow**: re-run `/graphify . --directed` (code for this project: root-level `main.py`/`config.py` plus `ui/`), writing to the project-root graphify-out/.
- Do NOT use the bare `graphify update` CLI — it has no `--directed` flag and writes a full UNDIRECTED graph, desyncing the live graph. If a stray undirected graph appears, delete its graph.json (keep cache/).
- Verify after rebuild: graph.json has `directed: true` and lives in root graphify-out/.
