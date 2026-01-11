# Todo Full-Stack Web Application Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: 1.1.0 → 2.0.0
Type: MAJOR (Transition to Full-Stack Web Architecture)

Modified Principles:
- REPLACED: III. In-Memory State Management → III. Persistent Relational State
- ADDED: VII. Stateless Security (JWT Authentication)

Modified Sections:
- Technology Stack: Complete overhaul for web architecture
  - Frontend: Next.js 16+ (App Router), Tailwind CSS
  - Backend: Python 3.13+, FastAPI
  - Database: Neon Serverless PostgreSQL with SQLModel ORM
  - Auth: Better Auth with JWT
- Success Criteria: Added Phase II criteria for web application
- Title: Updated from "Python Console App" to "Full-Stack Web Application"

Templates Requiring Updates:
- ⚠ .specify/templates/plan-template.md (add database schema, API design, auth flow sections)
- ⚠ .specify/templates/spec-template.md (add API endpoints, auth requirements, UI wireframes)
- ⚠ .specify/templates/tasks-template.md (add frontend, backend, database, auth task categories)

Follow-up TODOs:
- Review Agent Skills (id_architect, ux_logic_anchor, error_handler) for web context applicability
- Create database migration strategy from in-memory Phase I data
- Define API versioning and endpoint naming conventions
- Establish JWT token lifecycle and refresh policies
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

### III. Persistent Relational State

**MANDATORY**: All application data MUST be stored in Neon Serverless PostgreSQL with strict data isolation.

Technology Requirements:
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel (combines SQLAlchemy and Pydantic)
- Schema: All entities MUST include a `user_id` foreign key for data isolation
- Migrations: Use Alembic for database schema versioning

Data Isolation Rules:
- Every entity table MUST have a `user_id` column (foreign key to users table)
- Query filters MUST enforce `WHERE user_id = {authenticated_user_id}`
- Cross-user data access is strictly prohibited
- Database constraints MUST prevent orphaned records

**Rationale**: Persistent storage enables multi-user web applications with data durability. User-level isolation ensures security and privacy. SQLModel provides type-safe database operations aligned with Principle II (Pythonic Excellence).

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

**REQUIREMENT**: All backend logic MUST be verifiable via terminal output or API testing tools.

Interaction model:
- Backend: REST API endpoints testable with curl, HTTPie, or Postman
- Output via structured JSON responses
- Clear HTTP status codes (200, 400, 401, 404, 500)
- Human-readable error messages

**Rationale**: API-first design ensures backend logic is decoupled from frontend presentation. Terminal/HTTP testing enables rapid verification without UI dependencies.

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

### VII. Stateless Security (JWT Authentication)

**MANDATORY**: All API requests MUST be authenticated with a valid JWT token verified against BETTER_AUTH_SECRET.

Authentication Requirements:
- No request shall be processed without a valid JWT token (except public auth endpoints)
- JWT tokens MUST be verified using the `BETTER_AUTH_SECRET` environment variable
- Token payload MUST include `user_id` claim for identity verification
- Token expiration MUST be enforced (reject expired tokens with 401 Unauthorized)

Authorization Requirements:
- Backend MUST verify that the requested resource ID belongs to the authenticated user ID
- Ownership validation pattern: `SELECT * FROM table WHERE id = {resource_id} AND user_id = {token_user_id}`
- Cross-user resource access MUST return 404 Not Found (not 403, to prevent information leakage)
- Admin/service accounts require explicit role claim in JWT payload

**Rationale**: JWT provides stateless authentication suitable for serverless backends. Ownership verification at the database layer prevents unauthorized data access. Returning 404 for forbidden resources prevents attackers from enumerating valid resource IDs.

## Technology Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Styling**: Tailwind CSS
- **Language**: TypeScript 5+
- **State Management**: React Context or Zustand (as needed)

### Backend
- **Language**: Python 3.13+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Migrations**: Alembic

### Authentication
- **Provider**: Better Auth
- **Mechanism**: JWT tokens with `BETTER_AUTH_SECRET` signature verification
- **Token Storage**: HTTP-only cookies (frontend) + Authorization header (API)

### Development Tools
- **Backend**:
  - Type checking: `mypy --strict`
  - Linting: `ruff check`
  - Formatting: `ruff format`
  - Dependency Management: UV

- **Frontend**:
  - Type checking: Built-in TypeScript compiler
  - Linting: ESLint with Next.js config
  - Formatting: Prettier

### Testing
- **Backend**: `pytest` with `pytest-cov` for coverage
- **Frontend**: Jest + React Testing Library
- **E2E**: Playwright (optional for Phase II)

## Quality Standards

### Code Quality
- All code passes linter checks with zero warnings (ruff for Python, ESLint for TypeScript)
- All code passes type checking (mypy --strict for Python, tsc --noEmit for TypeScript)
- All code formatted consistently (ruff format for Python, Prettier for TypeScript)
- No commented-out code in final commits
- No debug print/console statements in production code

### Documentation Quality
- Every module has a module-level docstring
- Every class has a class-level docstring
- Every public function has a complete docstring
- Complex algorithms include inline comments explaining logic
- API endpoints documented in OpenAPI/Swagger format (FastAPI auto-generates)

### Testing Quality
- All business logic has corresponding test cases
- Edge cases are explicitly tested
- Error paths are tested (400, 401, 404, 500 responses)
- Test output clearly indicates pass/fail
- Database integration tests use transactional rollbacks (no persistent test data)

### Security Quality
- All secrets stored in environment variables (never committed to git)
- JWT tokens validated on every protected endpoint
- SQL injection prevented via ORM parameterized queries
- CORS configured correctly (whitelist frontend origin)
- Rate limiting implemented on auth endpoints

## Success Criteria

### Phase I (COMPLETE)
Phase I is considered complete when ALL of the following are met:

1. **Feature Completeness**: All Basic Level features implemented in CLI
2. **Code Quality**: 100% PEP 8 compliance, type hints, docstrings, zero linting errors
3. **Functional Correctness**: All features work as specified, edge cases handled
4. **Verification**: All functionality demonstrable via terminal
5. **Documentation**: Specification, plan, tasks complete and approved
6. **Skill Extraction**: 3 Agent Skills formalized (id_architect, ux_logic_anchor, error_handler)

### Phase II (In Progress)
Phase II is considered complete when ALL of the following are met:

1. **Secure REST API**: Full CRUD functionality with JWT authentication
   - All endpoints require valid JWT tokens
   - User data isolation enforced at database level
   - Proper HTTP status codes (200, 400, 401, 404, 500)
   - OpenAPI documentation generated

2. **Responsive Next.js UI**: Functional web interface using established UX patterns
   - Landing page with authentication (login/signup)
   - Todo list view with status symbols ([✓] completed, [○] pending)
   - Add, edit, delete, toggle completion actions
   - Standardized success/error messages (leveraging UX Logic Anchor skill)
   - Mobile-responsive design (Tailwind CSS)

3. **Successful JWT Handshake**: Frontend and backend authentication integration
   - Login flow: credentials → Better Auth → JWT token → HTTP-only cookie
   - API requests include Authorization header or cookie
   - Backend validates JWT signature using BETTER_AUTH_SECRET
   - Token expiration handled gracefully (redirect to login on 401)

4. **Database Integration**: Neon PostgreSQL with SQLModel ORM
   - All entities have `user_id` foreign key
   - Database migrations managed with Alembic
   - Connection pooling configured for serverless environment

5. **Code Quality**: Maintains Phase I standards across frontend and backend
   - Zero linting/type errors in both Python and TypeScript
   - Comprehensive docstrings/comments
   - No hardcoded secrets (environment variables only)

6. **Testing**: Backend API tests with >80% coverage
   - Unit tests for business logic
   - Integration tests for database operations
   - Authentication/authorization tests (valid/invalid tokens, ownership checks)

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
   - **MAJOR**: Backward-incompatible changes (principle removal/redefinition, architecture shift)
   - **MINOR**: New principles or sections added
   - **PATCH**: Clarifications, wording improvements, typo fixes

**Review Schedule**: Constitution MUST be reviewed at phase boundaries (Phase I → Phase II transition, etc.), including the audit of extracted Skills to ensure they remain relevant and are being utilized.

**Version**: 2.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-11
