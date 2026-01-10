# Todo In-Memory Python Console App Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 1.1.0
Type: MINOR (Added Reusable Intelligence principle)

Modified Principles:
- ADDED: VI. Reusable Intelligence (Agent Skills)

Modified Sections:
- Success Criteria: Added "Skill Extraction" requirement
- Governance: Updated review schedule to include Skills audit

Templates Requiring Updates:
- ⚠ .specify/templates/plan-template.md (may need Agent Skills section)
- ⚠ .specify/templates/spec-template.md (may reference extracted patterns)
- ✅ .specify/templates/tasks-template.md (task structure compatible)

Follow-up TODOs:
- Create Agent Skills library directory structure
- Extract 3+ patterns from Phase I implementation
-->

## Core Principles

### I. SDD-RI Methodology (Spec-Driven Development with Rigorous Implementation)

**NON-NEGOTIABLE**: No implementation without a validated specification and task breakdown.

All feature development MUST follow this sequence:
1. **Specification** (`/sp.specify`): Define user stories, acceptance criteria, and requirements
2. **Planning** (`/sp.plan`): Architecture and design decisions
3. **Task Breakdown** (`/sp.tasks`): Granular, testable tasks
4. **Implementation** (`/sp.implement`): Execute tasks sequentially

**Rationale**: This prevents scope creep, ensures clarity before coding, and maintains traceability from requirements to implementation. Every line of code must trace back to a documented requirement.

### II. Pythonic Excellence

**MANDATORY**: All code MUST adhere to PEP 8 standards and leverage Python 3.13+ features.

Code quality requirements:
- Follow PEP 8 style guide without exception
- Use modern Python 3.13+ features (pattern matching, type unions with `|`, etc.)
- Prefer readability over cleverness
- Use meaningful variable and function names
- Keep functions small and focused (single responsibility)

**Rationale**: Consistency and readability are critical for maintainability. Python 3.13+ provides powerful features that improve code clarity and type safety.

### III. In-Memory State Management

**STRICT CONSTRAINT**: No persistence layer during Phase I. All data MUST reside in memory.

Prohibited in Phase I:
- File I/O (JSON, CSV, text files)
- Database connections (SQLite, PostgreSQL, etc.)
- External storage APIs
- Serialization for persistence purposes

Required:
- Clean data structures (classes or dictionaries)
- Proper encapsulation of state
- Zero global variables

**Rationale**: Phase I focuses exclusively on business logic and state management. Adding persistence introduces complexity that obscures the core logic. Persistence will be addressed in a future phase after logic is proven correct.

### IV. Type Safety & Documentation

**MANDATORY**: All functions MUST have complete type hints and comprehensive docstrings.

Requirements:
- Type hints for all function parameters and return values
- Use `typing` module types where appropriate (`list[str]`, `dict[str, Any]`, etc.)
- Docstrings in Google or NumPy format
- Document parameters, return values, and raised exceptions
- Include usage examples in docstrings where helpful

**Rationale**: Type hints catch errors at development time and serve as inline documentation. Comprehensive docstrings ensure code is self-explanatory and reduce onboarding time.

### V. Terminal-Based Verification

**REQUIREMENT**: All logic MUST be verifiable via terminal output. No GUI, no web interface.

Interaction model:
- Input via CLI (stdin, command-line arguments)
- Output via terminal (stdout for results, stderr for errors)
- Human-readable output format
- Clear success/failure indicators

**Rationale**: Terminal interaction is the simplest, most direct way to verify logic. It eliminates UI complexity and allows focus on core functionality. Testing is straightforward with command-line tools.

### VI. Reusable Intelligence (Agent Skills)

**MANDATORY**: All repeatable architectural patterns MUST be extracted and formalized as Agent Skills.

Pattern Extraction Requirements:
- Identify recurring design patterns during implementation (e.g., ID management, CLI formatting, error handling)
- Extract patterns into the project's skill library with clear documentation
- Each skill MUST include: purpose, usage examples, constraints, and rationale
- Skills MUST be language-agnostic where possible, implementation-specific where necessary

Subagent Governance:
- Any subagent created during development MUST adhere to this Constitution
- Subagents MUST utilize established Agent Skills to maintain consistency
- New patterns discovered by subagents MUST be proposed for skill library inclusion
- Skills MUST be version-controlled alongside code artifacts

**Rationale**: Capturing architectural patterns as reusable skills prevents reinventing solutions, ensures consistency across features, and accelerates development. Subagent governance ensures all development—human or AI-driven—follows established best practices.

## Technology Stack

**Language**: Python 3.13+

**Dependency Management**: UV (fast Python package installer and resolver)

**Development Tools**:
- Type checking: `mypy` or `pyright`
- Linting: `ruff` or `pylint`
- Formatting: `black` or `ruff format`

**Testing** (when applicable):
- Framework: `pytest`
- Coverage: `pytest-cov`

## Quality Standards

### Code Quality
- All code passes `ruff check` (or equivalent linter) with zero warnings
- All code passes type checking with `mypy --strict` (or equivalent)
- All code formatted with `black` (or equivalent)
- No commented-out code in final commits
- No debug print statements in production code

### Documentation Quality
- Every module has a module-level docstring
- Every class has a class-level docstring
- Every public function has a complete docstring
- Complex algorithms include inline comments explaining logic

### Testing Quality
- All business logic has corresponding test cases
- Edge cases are explicitly tested
- Error paths are tested
- Test output clearly indicates pass/fail

## Success Criteria

Phase I is considered complete when ALL of the following are met:

1. **Feature Completeness**: All Basic Level features are implemented:
   - Add todo item
   - Delete todo item
   - Update todo item
   - View all todo items
   - Mark todo item as complete

2. **Code Quality**:
   - 100% compliance with PEP 8
   - 100% type hint coverage
   - 100% docstring coverage
   - Zero linting errors

3. **Functional Correctness**:
   - All features work as specified
   - Edge cases handled gracefully
   - No runtime errors during normal operation

4. **Verification**:
   - All functionality demonstrable via terminal
   - Clear output for all operations
   - Intuitive command-line interface

5. **Documentation**:
   - Specification document complete and approved
   - Implementation plan complete and approved
   - Task list complete with all tasks checked off
   - Code is self-documenting via docstrings

6. **Skill Extraction**: At least 3 Agent Skills formalized and stored in the project library:
   - Skills MUST document recurring patterns from Phase I
   - Each skill MUST include purpose, usage, constraints, and examples
   - Skills MUST be validated against actual implementation

## Governance

**Authority**: This constitution supersedes all other development practices and preferences for this project.

**Compliance**:
- All code reviews MUST verify constitution compliance
- Any complexity or deviation MUST be explicitly justified in planning documents
- Violations MUST be corrected before merge

**Amendment Process**:
1. Proposed amendment MUST be documented with rationale
2. Amendment MUST be reviewed and approved
3. Amendment MUST include migration plan for existing code if applicable
4. Version number MUST be incremented according to semantic versioning:
   - **MAJOR**: Backward-incompatible changes (principle removal/redefinition)
   - **MINOR**: New principles or sections added
   - **PATCH**: Clarifications, wording improvements, typo fixes

**Review Schedule**: Constitution MUST be reviewed at phase boundaries (Phase I → Phase II transition, etc.), including the audit of extracted Skills to ensure they remain relevant and are being utilized.

**Version**: 1.1.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-09
