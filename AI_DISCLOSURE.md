# 🤖 AI Disclosure & Verification Statement

This document details the use of Artificial Intelligence (AI) tools in the development of **Weeklies** (CSC 510, Fall 2026), outlining how AI was integrated, the bot configurations present in the repository, and the explicit human verification process applied to all AI-generated code.

---

## 1. Principles of AI Use

In accordance with course guidelines:
- **AI as an Accelerator, Not an Author**: AI systems were utilized as pair programmers to draft boilerplate, explore architectural alternatives, generate test cases, and refine documentation.
- **Human Accountability**: All architecture, business logic, security policies, and commits were reviewed, validated, and tested by team members prior to merging.
- **Transparency**: All configurations, agent prompts, and assisted areas are explicitly disclosed.

---

## 2. Tools & Systems Utilized

| Tool | Provider | Purpose | Primary Applications |
|---|---|---|---|
| **Antigravity** | Google DeepMind | Agentic pair programmer | Refactoring, bug diagnosis, cross-platform compatibility fixes, documentation authoring |
| **Claude Code** | Anthropic | Command-line coding agent | Test scaffold generation, Cypress spec drafting, M0 simulation modeling |
| **GitHub Copilot** | GitHub / OpenAI | In-editor code autocompletion | Function docstrings, repetitive unit test assertions, boilerplate routing |
| **CodeRabbit** | CodeRabbit AI | Automated PR code review bot | Continuous pull request static analysis and code review (configured in `.coderabbit.yaml`) |

---

## 3. Bot Configurations in Repository

- **CodeRabbit**: [`.coderabbit.yaml`](./.coderabbit.yaml) is checked into the repository root to govern automated PR reviews on `main` and `development`, enforcing test assertions, security policies, and Python coding standards.
- **GitHub Actions CI Bots**: Automated test, coverage, and linting runners configured in [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) and [`.github/workflows/docs.yml`](./.github/workflows/docs.yml).

---

## 4. Breakdown of AI Assistance vs. Human Engineering

| Component / Task | AI Contribution | Human Engineering & Verification |
|---|---|---|
| **M0: Risk-Killer Eval** (`scripts/`) | Suggested lognormal distribution sampling and initial CLI argument structure for `simulate_m0.py`. | Defined hypothesis metrics, designed evaluation policy (`m0-time-budget-v2`), validated seed reproducibility, fixed cross-platform CRLF line-ending bugs on Windows, and reviewed sensitivity bounds. |
| **Single-Meal Swaps** (UC29) | Generated boilerplate Flask route handlers and mock test templates. | Implemented server-side restaurant hours checking, multi-allergen string parsing, SQLite query optimization, calendar frontend UI integration, and manual end-to-end testing. |
| **Budget-Constrained Generation** | Assisted with candidate sorting algorithms and edge-case boundary test cases. | Formulated exact-cents financial modeling, designed candidate rejection heuristics before model execution, implemented neighboring-month calendar row item sums, and resolved database state issues. |
| **Order Progress Stepper** (UC13) | Suggested initial CSS flexbox layout for the stepper component. | Mapped database order status codes to business lifecycle states (`Placed` ➔ `Delivered`), added cancelled/unknown state handling, and conducted visual styling audits. |
| **Cypress E2E Testing** | Drafted initial Cypress test spec skeletons for login and orders. | Authored the database seeding script (`scripts/cypress_seed.py`), engineered test isolation, debugged timing/race conditions in headless CI runs, and configured live server spawning. |
| **Documentation & Standards** | Assisted in compiling Markdown tables and formatting rubrics. | Audited project compliance with course requirements, validated license compatibility in `THIRD_PARTY_LIBRARIES.md`, and proofread all technical specifications. |

---

## 5. Human Verification Protocol

To ensure code quality, correctness, and system security, every line of AI-assisted code was subjected to the following multi-layer human verification pipeline:

1. **Local Execution & Manual Verification**:
   - The Flask server was run locally (`flask run`) to manually verify UI responsiveness, form validation, and database state transitions.
2. **Automated Unit & Integration Tests**:
   - AI-suggested code was never accepted without accompanying tests. The test suite was executed locally via `pytest` to confirm regression-free behavior across all 449+ unit and integration tests.
3. **End-to-End Browser Validation**:
   - Full browser execution was verified using Cypress (`npx cypress run`) against a seeded SQLite database to ensure realistic user behavior.
4. **Static Analysis & Linting**:
   - Code was formatted using `black` and verified using `ruff` to ensure compliance with PEP 8 and project style guidelines.
5. **Peer Review**:
   - Team members reviewed pull requests before merging into `development`.
