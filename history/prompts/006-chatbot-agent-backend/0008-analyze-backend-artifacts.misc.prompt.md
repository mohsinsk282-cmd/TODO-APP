---
id: 0008
title: Analyze backend artifacts
stage: misc
date: 2026-02-05
surface: agent
model: gemini
feature: 006-chatbot-agent-backend
branch: 006-chatbot-agent-backend
user: {{USER}}
command: /sp.analyze
labels: [analysis, consistency]
links:
  spec: ../../../../specs/006-chatbot-agent-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /mnt/d/github.com/TODO-APP/specs/006-chatbot-agent-backend/spec.md
  - /mnt/d/github.com/TODO-APP/specs/006-chatbot-agent-backend/plan.md
  - /mnt/d/github.com/TODO-APP/specs/006-chatbot-agent-backend/tasks.md
  - /mnt/d/github.com/TODO-APP/.specify/memory/constitution.md
tests:
  null
---

## Prompt

---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This command MUST run only after `/sp.tasks` has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The project constitution (`.specify/memory/constitution.md`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `/sp.analyze`.

## Execution Steps

### 1. Initialize Analysis Context

Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` once from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS. Derive absolute paths:

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md

Abort with an error message if any required file is missing (instruct the user to run missing prerequisite command). For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**

- Overview/Context
- Functional Requirements
- Non-Functional Requirements
- User Stories
- Edge Cases (if present)

**From plan.md:**

- Architecture/stack choices
- Data Model references
- Phases
- Technical constraints

**From tasks.md:**

- Task IDs
- Descriptions
- Phase grouping
- Parallel markers [P]
- Referenced file paths

**From constitution:**

- Load `.specify/memory/constitution.md` for principle validation

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" → `user-can-upload-file`)
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Task coverage mapping**: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases)
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements

### 4. Detection Passes (Token-Efficient Analysis)

Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.

#### A. Duplication Detection

- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection

- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.)

#### C. Underspecification

- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Tasks referencing files or components not defined in spec/plan

#### D. Constitution Alignment

- Any requirement or plan element conflicting with a MUST principle
- Missing mandated sections or quality gates from constitution

#### E. Coverage Gaps

- Requirements with zero associated tasks
- Tasks with no mapped requirement/story
- Non-functional requirements not reflected in tasks (e.g., performance, security)

#### F. Inconsistency

- Terminology drift (same concept named differently across files)
- Data entities referenced in plan but absent in spec (or vice versa)
- Task ordering contradictions (e.g., integration tasks before foundational setup tasks without dependency note)
- Conflicting requirements (e.g., one requires Next.js while other specifies Vue)

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates constitution MUST, missing core spec artifact, or requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Compact Analysis Report

Output a Markdown report (no file writes) with the following structure:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

(Add one row per finding; generate stable IDs prefixed by category initial.)

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**

- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `/sp.implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /sp.specify with refinement", "Run /sp.plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'"

### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Token-efficient output**: Limit findings table to 50 rows; summarize overflow
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

### Analysis Guidelines

- **NEVER modify files** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero issues gracefully** (emit success report with coverage statistics)

## Context

@backend

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.

## Response snapshot

I have analyzed the provided `spec.md`, `plan.md`, `tasks.md`, and `constitution.md` files for the `chatbot-backend` feature. Here is the report:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Inconsistency | CRITICAL | `tasks.md` | The `tasks.md` file shows most tasks as completed (`[x]`). According to the constitution's SDD-RI principle, analysis should occur *before* implementation. This indicates a severe process violation where `/sp.analyze` is being run after work has already been done. | Halt further implementation. Review the development workflow to ensure compliance with the SDD-RI principle. The `tasks.md` file should be a plan, not a log of completed work, at this stage. |
| B1 | Ambiguity | HIGH | `plan.md` | Non-functional requirements in the "Performance Goals" section are ambiguous. Terms like "without degradation" and "without performance issues" are not defined with measurable metrics, making them untestable. | Refine the performance goals in `plan.md` to include specific, measurable thresholds for degradation and performance (e.g., p95 latency, CPU utilization). |
| C1 | Coverage Gaps | MEDIUM | `spec.md`, `tasks.md` | There is no explicit traceability matrix mapping the 41 Functional Requirements (FRs) from `spec.md` to the specific tasks in `tasks.md`. While tasks are linked to user stories, direct mapping to FRs is missing, making it difficult to verify full requirement coverage. | Add explicit references to the FRs each task is intended to satisfy within `tasks.md`. For example: `T024 [US1, FR-026, FR-027] Add POST /api/chatkit endpoint...` |
| D1 | Duplication | LOW | `spec.md` | Functional requirements FR-006 and FR-027 are nearly identical. Both relate to using `StreamingResult`. FR-027 is slightly more specific. | Consolidate FR-006 and FR-027 into a single, more precise requirement in `spec.md` to improve clarity and reduce redundancy. |

### Coverage Summary Table

| Requirement Category | Total | Covered by Tasks (Inferred) | Notes |
|----------------------|-------|-----------------------------|-------|
| Functional Reqs (FR) | 41 | 41 | Coverage is inferred from user story tasks, but not explicitly mapped (See finding C1). |
| Success Criteria (SC) | 10 | 10 | Coverage is inferred. |
| User Stories | 3 | 3 | All user stories have dedicated task phases. |

### Constitution Alignment Issues

- **CRITICAL**: The current state of `tasks.md` violates **Principle I: SDD-RI Methodology**. The workflow should be Spec -> Plan -> Tasks -> **Analyze** -> Implement. The completed tasks suggest implementation has already begun.

### Unmapped Tasks

- All tasks in `tasks.md` are mapped to a User Story and Phase. There are no unmapped tasks.

### Metrics

- **Total Requirements**: 41
- **Total Tasks**: 58
- **Coverage %**: 100% (inferred)
- **Ambiguity Count**: 1
- **Duplication Count**: 1
- **Critical Issues Count**: 1

---

### Next Actions

1.  **CRITICAL**: Immediately address the process violation identified in finding **A1**. You should clarify what stage of development you are in. If you are pre-implementation, the `tasks.md` file should be reset to a list of pending tasks.
2.  **HIGH**: Refine the ambiguous performance goals in `plan.md` as suggested in finding **B1** to make them testable.
3.  **MEDIUM**: Improve traceability by mapping tasks in `tasks.md` directly to the Functional Requirements they cover, as suggested in finding **C1**.

I recommend resolving the CRITICAL issue before proceeding with any implementation.

Would you like me to suggest concrete remediation edits for the top issues?

## Outcome

- ✅ Impact: Identified critical process violation and other issues.
- 🧪 Tests: N/A
- 📁 Files: Read 4 files.
- 🔁 Next prompts: User might ask for remediation.
- 🧠 Reflection: The check-prerequisites.sh script output was misleading.

## Evaluation notes (flywheel)

- Failure modes observed: Misinterpretation of script arguments.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Try to get the feature name from git branch.