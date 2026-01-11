---
id: 0003
title: Constitution v2.0.0 Web Evolution
stage: constitution
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 001-basic-crud
user: Mohsin Raza
command: /sp.constitution
labels: [constitution, major-version, web-architecture, security, database]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - Verified MAJOR version bump rationale (1.1.0 → 2.0.0)
  - Validated Principle III replacement (In-Memory → Persistent Relational State)
  - Validated Principle VII addition (Stateless Security JWT)
  - Verified Technology Stack complete overhaul
  - Verified Phase II Success Criteria addition
---

## Prompt

```
Update `constitution.md` to Version 2.0.0 (The Web Evolution)

Changes Required:
1. Increment version to 2.0.0 and update SYNC IMPACT REPORT to "MAJOR: Transition to Full-Stack Web Architecture".
2. Replace Principle III (In-Memory State) with "Principle III: Persistent Relational State":
   - "Technology: Use Neon Serverless PostgreSQL with SQLModel ORM."
   - "Schema: All entities must be linked to a 'user_id' for strict data isolation."
3. Add "Principle VII: Stateless Security (JWT)":
   - "Authentication: No request shall be processed without a valid JWT token verified via BETTER_AUTH_SECRET."
   - "Ownership: The backend MUST verify that the requested Resource ID belongs to the Authenticated User ID."
4. Update Technology Stack:
   - Frontend: Next.js 16+ (App Router), Tailwind CSS.
   - Backend: Python 3.13+, FastAPI.
   - Auth: Better Auth.
5. Add Phase II Success Criteria:
   - "Secure REST API with full CRUD functionality."
   - "Responsive Next.js UI using established UX Logic Anchor skills."
   - "Successful JWT handshake between Frontend and Backend."

STOP after updating the file for my review.
```

## Response snapshot

**Constitution v2.0.0 Amendment Complete** ✅

### Version Change: 1.1.0 → 2.0.0 (MAJOR)

**Bump Rationale**: This is a MAJOR version because it fundamentally changes the application architecture from in-memory console application to full-stack web application with persistent storage. Principle III was completely replaced (backward-incompatible), and the technology stack was overhauled.

### Modified Principles

**REPLACED: Principle III**
- **Old**: "In-Memory State Management" - prohibited all persistence (file I/O, databases)
- **New**: "Persistent Relational State" - mandates Neon PostgreSQL with SQLModel ORM
- **Key Requirements**:
  - Database: Neon Serverless PostgreSQL
  - ORM: SQLModel (combines SQLAlchemy + Pydantic)
  - Schema: All entities MUST include `user_id` foreign key for data isolation
  - Migrations: Use Alembic for schema versioning
  - Query Pattern: `WHERE user_id = {authenticated_user_id}` enforced

**ADDED: Principle VII - Stateless Security (JWT Authentication)**
- **Authentication Requirements**:
  - No request processed without valid JWT token (except public auth endpoints)
  - JWT verified using `BETTER_AUTH_SECRET` environment variable
  - Token payload MUST include `user_id` claim
  - Token expiration enforced (401 Unauthorized on expired)

- **Authorization Requirements**:
  - Backend MUST verify resource ownership: `WHERE id = {resource_id} AND user_id = {token_user_id}`
  - Cross-user access returns 404 Not Found (prevents ID enumeration)
  - Admin/service accounts require explicit role claim in JWT

### Technology Stack Overhaul

**Frontend** (NEW):
- Framework: Next.js 16+ (App Router)
- Styling: Tailwind CSS
- Language: TypeScript 5+
- State Management: React Context or Zustand

**Backend** (UPDATED):
- Language: Python 3.13+ (unchanged)
- Framework: FastAPI (new)
- ORM: SQLModel (new)
- Database: Neon Serverless PostgreSQL (new)
- Migrations: Alembic (new)

**Authentication** (NEW):
- Provider: Better Auth
- Mechanism: JWT tokens with `BETTER_AUTH_SECRET`
- Storage: HTTP-only cookies + Authorization header

**Development Tools**:
- Backend: mypy --strict, ruff check/format, UV (unchanged from Phase I)
- Frontend: TypeScript compiler, ESLint, Prettier (new)
- Testing: pytest (backend), Jest + React Testing Library (frontend), Playwright (E2E, optional)

### Phase II Success Criteria Added

1. **Secure REST API**: Full CRUD with JWT authentication
   - All endpoints require valid tokens
   - User data isolation at database level
   - Proper HTTP status codes (200, 400, 401, 404, 500)
   - OpenAPI documentation generated

2. **Responsive Next.js UI**: Web interface with UX patterns
   - Landing page with authentication (login/signup)
   - Todo list view with status symbols ([✓] completed, [○] pending)
   - CRUD actions (add, edit, delete, toggle)
   - Standardized messages (leveraging UX Logic Anchor skill)
   - Mobile-responsive (Tailwind CSS)

3. **Successful JWT Handshake**: Frontend-backend authentication integration
   - Login flow: credentials → Better Auth → JWT → HTTP-only cookie
   - API requests include Authorization header/cookie
   - Backend validates JWT signature
   - Token expiration handled (redirect to login on 401)

4. **Database Integration**: Neon PostgreSQL with SQLModel
   - All entities have `user_id` foreign key
   - Alembic migrations
   - Connection pooling for serverless

5. **Code Quality**: Phase I standards maintained across stack
   - Zero linting/type errors (Python + TypeScript)
   - Comprehensive docstrings/comments
   - No hardcoded secrets

6. **Testing**: Backend API tests >80% coverage
   - Unit tests for business logic
   - Integration tests for database
   - Auth/authz tests (tokens, ownership)

### Security Quality Standards Added

- All secrets in environment variables (never committed)
- JWT tokens validated on every protected endpoint
- SQL injection prevented via ORM parameterized queries
- CORS configured correctly (whitelist frontend origin)
- Rate limiting on auth endpoints

### Sync Impact Report

**Templates Requiring Updates**:
- ⚠ `.specify/templates/plan-template.md` - add database schema, API design, auth flow sections
- ⚠ `.specify/templates/spec-template.md` - add API endpoints, auth requirements, UI wireframes
- ⚠ `.specify/templates/tasks-template.md` - add frontend, backend, database, auth task categories

**Follow-up TODOs**:
- Review Agent Skills (id_architect, ux_logic_anchor, error_handler) for web context applicability
- Create database migration strategy from in-memory Phase I data
- Define API versioning and endpoint naming conventions
- Establish JWT token lifecycle and refresh policies

### Document Title Updated

- **Old**: "Todo In-Memory Python Console App Constitution"
- **New**: "Todo Full-Stack Web Application Constitution"

### Governance Updated

- **Last Amended**: 2026-01-11 (today)
- **Amendment Process**: Added "architecture shift" as example of MAJOR version bump

## Outcome

- ✅ Impact: Constitution fundamentally transformed to support full-stack web architecture with persistent storage, multi-user JWT authentication, and comprehensive security requirements
- 🧪 Tests: Version bump validation PASS, Principle replacement validation PASS, Technology stack overhaul PASS, Phase II criteria addition PASS
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Review and update templates (plan, spec, tasks), Create Phase II specification (`/sp.specify`), Review Agent Skills for web applicability
- 🧠 Reflection: MAJOR version bump correctly reflects architectural paradigm shift from in-memory CLI to full-stack web application. New Principle VII establishes security-first approach with JWT authentication and ownership verification. Phase II success criteria provide clear measurable targets for web implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitutional amendment completed without errors
- Graders run and results (PASS/FAIL): Semantic versioning validation PASS, Principle completeness PASS, Technology stack coherence PASS, Success criteria clarity PASS
- Prompt variant (if applicable): Standard `/sp.constitution` workflow with explicit MAJOR version requirements
- Next experiment (smallest change to try): Validate that Phase I Agent Skills (id_architect, ux_logic_anchor, error_handler) can be applied to Phase II web architecture without modification
