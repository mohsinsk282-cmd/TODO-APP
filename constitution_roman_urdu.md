# Todo Full-Stack Web Application Aain (Constitution)

<!--
SYNC IMPACT REPORT
==================
Version Change: 1.1.0 -> 2.0.0
Type: MAJOR (Transition to Full-Stack Web Architecture)

(Ye hissa technical hai aur English mein behtar samajh aata hai, isliye ise maintain kiya gaya hai.)
-->

## Bunyadi Usool (Core Principles)

### I. SDD-RI Tariga-e-Kaar (Spec-Driven Development with Rigorous Implementation)

**NON-NEGOTIABLE (Is par samjhota nahi hoga)**: Validate shuda specification aur task breakdown ke baghair koi implementation nahi hogi.

Tamam feature development ko is tarteeb ko follow karna LAZMI hai:
1. **Specification** (`/sp.specify`): User stories, acceptance criteria, aur zarooriyat (requirements) define karein.
2. **Planning** (`/sp.plan`): Architecture aur design ke faislay.
3. **Task Breakdown** (`/sp.tasks`): Chote, testable tasks.
4. **Implementation** (`/sp.implement`): Tasks ko tarteeb waar anjam dein.

**Wajah (Rationale)**: Ye scope creep ko rokta hai, coding se pehle wazahat (clarity) yaqeeni banata hai, aur requirements se lekar implementation tak traceability qaim rakhta hai. Code ki har line kisi na kisi documented requirement se judi honi chahiye.

### II. Pythonic Excellence (Python Ki Maharat)

**LAZMI (MANDATORY)**: Tamam code ko PEP 8 standards ki pabandi karni chahiye aur Python 3.13+ ke features ka faida uthana chahiye.

Code quality ki zarooriyat:
- PEP 8 style guide ko baghair kisi exception ke follow karein.
- Modern Python 3.13+ features use karein (pattern matching, type unions `|` ke sath, waghaira).
- Hoshiyari (cleverness) par parhne mein asani (readability) ko tarjeeh dein.
- Ba-maqsad (meaningful) variable aur function naam istemal karein.
- Functions ko chota aur focused rakhein (single responsibility).

**Wajah (Rationale)**: Maintainability ke liye consistency aur readability bohat ahem hain. Python 3.13+ aisay taqatwar features deta hai jo code ki safai aur type safety ko behtar banate hain.

### III. Persistent Relational State (Mustaqil Relational Halat)

**LAZMI (MANDATORY)**: Tamam application data ko Neon Serverless PostgreSQL mein sakht data isolation ke sath store kiya jana chahiye.

Technology Zarooriyat:
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel (SQLAlchemy aur Pydantic ka milap)
- Schema: Tamam entities mein data isolation ke liye `user_id` foreign key shamil honi chahiye.
- Migrations: Database schema versioning ke liye Alembic ka istemal karein.

Data Isolation Qawaneen:
- Har entity table mein `user_id` column hona chahiye (users table ke liye foreign key).
- Query filters mein `WHERE user_id = {authenticated_user_id}` lazmi lagana chahiye.
- Cross-user data access (doosre user ka data dekhna) sakhti se mana hai.
- Database constraints ko yateem records (orphaned records) se rokna chahiye.

**Wajah (Rationale)**: Persistent storage multi-user web applications ko data durability ke sath chalane ke qabil banata hai. User-level isolation security aur privacy ko yaqeeni banata hai. SQLModel type-safe database operations provide karta hai jo Principle II (Pythonic Excellence) ke mutabiq hain.

### IV. Type Safety & Documentation

**LAZMI (MANDATORY)**: Tamam functions ke paas mukammal type hints aur tafseeli docstrings honi chahiye.

Zarooriyat:
- Tamam function parameters aur return values ke liye type hints.
- Jahan munasib ho `typing` module types use karein (`list[str]`, `dict[str, Any]`, waghaira).
- Docstrings Google ya NumPy format mein hon.
- Parameters, return values, aur raise hone wali exceptions ko document karein.
- Jahan madadgar ho wahan docstrings mein usage examples shamil karein.

**Wajah (Rationale)**: Type hints development ke waqt hi errors pakad leti hain aur inline documentation ka kaam karti hain. Tafseeli docstrings code ko khud-wazahat-kuninda (self-explanatory) banati hain aur naye logon ke seekhne ka waqt kam karti hain.

### V. Terminal-Based Verification

**ZAROORAT (REQUIREMENT)**: Tamam backend logic ko terminal output ya API testing tools ke zariye verify kiya jana chahiye.

Interaction model:
- Backend: REST API endpoints jinhein curl, HTTPie, ya Postman se test kiya ja sake.
- Output structured JSON responses ke zariye.
- Wazeh HTTP status codes (200, 400, 401, 404, 500).
- Insano ke parhne ke qabil error messages.

**Wajah (Rationale)**: API-first design is baat ko yaqeeni banata hai ke backend logic frontend presentation se alag (decoupled) rahay. Terminal/HTTP testing UI dependencies ke baghair tezi se verification karne ki ijazat deti hai.

### VI. Reusable Intelligence (Agent Skills)

**LAZMI (MANDATORY)**: Tamam bar bar anay walay architectural patterns ko nikal kar Agent Skills ke tor par formalize kiya jana chahiye.

Pattern Extraction Zarooriyat:
- Implementation ke doran bar bar anay walay design patterns ki shinakht karein (maslan ID management, CLI formatting, error handling).
- Patterns ko project ki skill library mein wazeh documentation ke sath shamil karein.
- Har skill mein shamil hona chahiye: maqsad, istemal ki misalein, rukawatein (constraints), aur wajah (rationale).
- Skills ko jahan mumkin ho language-agnostic hona chahiye, aur jahan zaroori ho implementation-specific.

Subagent Governance:
- Development ke doran banaya gaya koi bhi subagent is Aain (Constitution) ki pabandi kare.
- Subagents ko consistency barqarar rakhne ke liye qaim shuda Agent Skills ka istemal karna chahiye.
- Subagents ke daryaft kiye gaye naye patterns ko skill library mein shamil karne ke liye tajweez kiya jana chahiye.
- Skills ko code artifacts ke sath version-controlled hona chahiye.

**Wajah (Rationale)**: Architectural patterns ko reusable skills ke tor par mehfooz karna dobara hal dhoondne (reinventing solutions) se bachaata hai, features mein yaksaaniyat (consistency) lata hai, aur development ko tez karta hai. Subagent governance is baat ko yaqeeni banata hai ke tamam development—chahe insani ho ya AI ki—qaim shuda behtareen tareeqon (best practices) par amal kare.

### VII. Stateless Security (JWT Authentication)

**LAZMI (MANDATORY)**: Tamam API requests ko aik valid JWT token ke sath authenticate hona chahiye jo `BETTER_AUTH_SECRET` ke khilaf verify kiya gaya ho.

Authentication Zarooriyat:
- Valid JWT token ke baghair koi request process nahi ki jayegi (siwaye public auth endpoints ke).
- JWT tokens ko `BETTER_AUTH_SECRET` environment variable ka istemal karte hue verify kiya jana chahiye.
- Token payload mein identity verification ke liye `user_id` claim shamil hona chahiye.
- Token expiration ko lazmi nafiz kiya jana chahiye (expired tokens ko 401 Unauthorized ke sath reject karein).

Authorization Zarooriyat:
- Backend ko verify karna chahiye ke manga gaya resource ID authenticated user ID ki malkiyat hai.
- Malkiyat validation pattern: `SELECT * FROM table WHERE id = {resource_id} AND user_id = {token_user_id}`
- Cross-user resource access par 404 Not Found return karna chahiye (403 nahi, taake information leakage se bacha ja sake).
- Admin/service accounts ke liye JWT payload mein wazeh role claim ki zaroorat hoti hai.

**Wajah (Rationale)**: JWT serverless backends ke liye munasib stateless authentication provide karta hai. Database layer par ownership verification ghair-majaz data access ko rokti hai. Mana kiye gaye resources ke liye 404 return karna hamla-awaron (attackers) ko valid resource IDs ka andaza lagane se rokta hai.

## Technology Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Styling**: Tailwind CSS
- **Language**: TypeScript 5+
- **State Management**: React Context ya Zustand (hasb-e-zaroorat)

### Backend
- **Language**: Python 3.13+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Migrations**: Alembic

### Authentication
- **Provider**: Better Auth
- **Mechanism**: JWT tokens jin ki `BETTER_AUTH_SECRET` signature verification ho
- **Token Storage**: HTTP-only cookies (frontend) + Authorization header (API)

### Development Tools
- **Backend**:
  - Type checking: `mypy --strict`
  - Linting: `ruff check`
  - Formatting: `ruff format`
  - Dependency Management: UV

- **Frontend**:
  - Type checking: Built-in TypeScript compiler
  - Linting: ESLint Next.js config ke sath
  - Formatting: Prettier

### Testing
- **Backend**: `pytest` coverage ke liye `pytest-cov` ke sath
- **Frontend**: Jest + React Testing Library
- **E2E**: Playwright (Phase II ke liye optional)

## Quality Standards (Mayar ke Mayarat)

### Code Quality
- Tamam code linter checks pass kare baghair kisi warning ke (Python ke liye ruff, TypeScript ke liye ESLint).
- Tamam code type checking pass kare (Python ke liye mypy --strict, TypeScript ke liye tsc --noEmit).
- Tamam code yaksa taur par format ho (Python ke liye ruff format, TypeScript ke liye Prettier).
- Final commits mein koi commented-out code na ho.
- Production code mein koi debug print/console statements na hon.

### Documentation Quality
- Har module ki module-level docstring ho.
- Har class ki class-level docstring ho.
- Har public function ki mukammal docstring ho.
- Complex algorithms mein logic samjhane ke liye inline comments hon.
- API endpoints OpenAPI/Swagger format mein document hon (FastAPI khud generate karta hai).

### Testing Quality
- Tamam business logic ke liye corresponding test cases hon.
- Edge cases ko wazeh taur par test kiya gaya ho.
- Error paths test kiye gaye hon (400, 401, 404, 500 responses).
- Test output wazeh taur par pass/fail bataye.
- Database integration tests transactional rollbacks use karein (koi persistent test data na ho).

### Security Quality
- Tamam raaz (secrets) environment variables mein store hon (kabhi bhi git mein commit na hon).
- Har protected endpoint par JWT tokens validate hon.
- ORM parameterized queries ke zariye SQL injection se bacha jaye.
- CORS sahi tareeqe se configure ho (frontend origin ko whitelist karein).
- Auth endpoints par Rate limiting nafiz ho.

## Success Criteria (Kamiyabi Ke Mayar)

### Phase I (MUKAMMAL)
Phase I tab mukammal samjha jayega jab DARJ ZAIAL TAMAM pure hon:

1. **Feature Completeness**: Tamam Basic Level features CLI mein implement hon.
2. **Code Quality**: 100% PEP 8 ki pabandi, type hints, docstrings, zero linting errors.
3. **Functional Correctness**: Tamam features specification ke mutabiq kaam karein, edge cases sambhale gaye hon.
4. **Verification**: Tamam functionality terminal ke zariye dikhayi ja sake.
5. **Documentation**: Specification, plan, tasks mukammal aur manzoor shuda hon.
6. **Skill Extraction**: 3 Agent Skills formalize ho chuke hon (id_architect, ux_logic_anchor, error_handler).

### Phase II (Jaari Hai - In Progress)
Phase II tab mukammal samjha jayega jab DARJ ZAIAL TAMAM pure hon:

1. **Secure REST API**: Full CRUD functionality JWT authentication ke sath.
   - Tamam endpoints ke liye valid JWT tokens lazmi hon.
   - Database level par User data isolation nafiz ho.
   - Munasib HTTP status codes (200, 400, 401, 404, 500).
   - OpenAPI documentation generate ho.

2. **Responsive Next.js UI**: Functional web interface jo establish shuda UX patterns use kare.
   - Landing page authentication ke sath (login/signup).
   - Todo list view status symbols ke sath ([✓] completed, [○] pending).
   - Add, edit, delete, toggle completion actions.
   - Standardized success/error messages (UX Logic Anchor skill ka faida uthate hue).
   - Mobile-responsive design (Tailwind CSS).

3. **Successful JWT Handshake**: Frontend aur backend authentication integration.
   - Login flow: credentials → Better Auth → JWT token → HTTP-only cookie.
   - API requests mein Authorization header ya cookie shamil ho.
   - Backend `BETTER_AUTH_SECRET` use karte hue JWT signature validate kare.
   - Token expiration ko shaleeqay se sambhala jaye (401 par login ki taraf redirect).

4. **Database Integration**: Neon PostgreSQL SQLModel ORM ke sath.
   - Tamam entities mein `user_id` foreign key ho.
   - Database migrations Alembic ke sath manage hon.
   - Serverless environment ke liye connection pooling configure ho.

5. **Code Quality**: Frontend aur backend dono mein Phase I standards barqarar rakhein.
   - Python aur TypeScript dono mein zero linting/type errors.
   - Tafseeli docstrings/comments.
   - Koi hardcoded secrets nahi (sirf environment variables).

6. **Testing**: Backend API tests >80% coverage ke sath.
   - Business logic ke liye Unit tests.
   - Database operations ke liye Integration tests.
   - Authentication/authorization tests (valid/invalid tokens, ownership checks).

## Governance (Nizam-e-Insuram)

**Ikhtiyar (Authority)**: Ye aain (constitution) is project ke liye tamam doosre development practices aur preferences par foqiyat rakhta hai.

**Amalwari (Compliance)**:
- Tamam code reviews mein aain ki pabandi ki tasdeeq LAZMI hai.
- Kisi bhi pecheedgi (complexity) ya inhiraf (deviation) ka planning documents mein wazeh jawaz (justification) hona chahiye.
- Khilaf warziyon ko merge karne se pehle theek karna LAZMI hai.

**Tarmeem Ka Amal (Amendment Process)**:
1. Tajweez karda tarmeem ko dalail (rationale) ke sath document kiya jana chahiye.
2. Tarmeem ko review aur manzoor kiya jana chahiye.
3. Agar laagu ho to tarmeem mein existing code ke liye migration plan shamil hona chahiye.
4. Version number ko semantic versioning ke mutabiq barhaya jana chahiye:
   - **MAJOR**: Backward-incompatible tabdeeliya (usool hatana/dobara define karna, architecture shift).
   - **MINOR**: Naye usool ya sections shamil kiye gaye.
   - **PATCH**: Wazahatein, alfaz ki behtari, typo fixes.

**Review Schedule**: Aain ko phase boundaries par review kiya jana LAZMI hai (Phase I -> Phase II transition, waghaira), jisme extracted Skills ka audit bhi shamil hai taake ye yaqeeni banaya ja sake ke wo relevant hain aur unka istemal ho raha hai.

**Version**: 2.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-11
