# 📋 Project 2 Self-Assessed Repo Rubric

This document contains the self-assessed repository rubric for **Weeklies** (CSC 510, Fall 2026), evaluated against the project requirements.

**Scoring Scale**: `0` = None, `1` = A little, `2` = Somewhat, `3` = A lot.  
Every score is backed by direct clickable evidence links in the repository.

---

### 👥 Teamwork, Visible in GitHub

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **Many commits**: hundreds by the end is normal for teams that commit small | [GitHub Commits](https://github.com/rdpatel2/Weeklies/commits/development) | **3** | **341 small, atomic commits** across the repository history; consistent progress across all development milestones. |
| **Commits come from different people** | [GitHub Contributors](https://github.com/rdpatel2/Weeklies/graphs/contributors) | **3** | Commits submitted from all 4 current team members: Rohan Patel (40), Srikar Desemsetti (32), Alex Tanton (45), and Kushal Upreti (39). |
| **Workload is spread over the whole team** | [GitHub Insights & Contributors](https://github.com/rdpatel2/Weeklies/graphs/contributors) | **3** | Balanced contribution across the team covering backend routes, testing suites, M0 simulation modeling, styling, security, and documentation. |
| **Team members work across many parts of the code, not one silo each** | [PR History](https://github.com/rdpatel2/Weeklies/pulls?q=is%3Apr+is%3Amerged) | **3** | Team members collaboratively contributed across `proj2/Flask_app.py`, `proj2/order_progress.py`, `scripts/`, `proj2/tests/`, Cypress E2E specs, and documentation. |
| **Short release cycles**: frequent small commits, merged promptly | [Closed Pull Requests](https://github.com/rdpatel2/Weeklies/pulls?q=is%3Apr+is%3Amerged) | **3** | 43+ modular feature pull requests created and merged into `development` with atomic commit histories and zero long-lived unmerged drift. |
| **Whole team uses the same tools**: config files in repo, updated by many different people | [`pyproject.toml`](./pyproject.toml), [`pytest.ini`](./pytest.ini), [`cypress.config.js`](./proj2/cypress.config.js), [`.coderabbit.yaml`](./.coderabbit.yaml) | **3** | Centralized configuration for Black, Ruff, pytest, Cypress, and CodeRabbit shared and maintained by all contributors. |
| **Whole team can run the system**: anyone can share screen and demo on machine | [`INSTALL.md`](./INSTALL.md) | **3** | Documented step-by-step setup enabling clean local runs (`flask run`) verified on Windows, macOS, and Linux with cross-platform scripts. |

---

### 💬 Issues and Discussion

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **Issue reports: there are many** | [GitHub Issues](https://github.com/rdpatel2/Weeklies/issues?q=is%3Aissue) | **3** | 14 structured issues (#22, #26, #28, #29, #30, #31, #32, #33, #34, #35, #36, #37, #38, #39) tracking milestones, security, tests, and documentation. |
| **Issues are being closed** | [Closed Issues](https://github.com/rdpatel2/Weeklies/issues?q=is%3Aissue+is%3Aclosed) | **3** | 12+ issues already resolved and closed via linked pull requests with full traceability. |
| **Issues are discussed before they are closed** | [Issue & PR Comments](https://github.com/rdpatel2/Weeklies/issues?q=is%3Aissue+is%3Aclosed) | **3** | Implementation alternatives, security implications, and acceptance criteria discussed on GitHub Issues, PR threads, and team Discord. |
| **A large share of issues relate to handling failing cases** | [Issue #39 (/db exposure)](https://github.com/rdpatel2/Weeklies/issues/39), [Issue #26 (secret key)](https://github.com/rdpatel2/Weeklies/issues/26), [Issue #35 (light mode)](https://github.com/rdpatel2/Weeklies/issues/35), [PR #16 (Windows CRLF)](https://github.com/rdpatel2/Weeklies/pull/16) | **3** | Critical failure cases, vulnerability disclosures (password hash exposure), session key entropy, and cross-platform line-ending bugs tracked and resolved. |
| **Chat channel / discussion forum exists and is active** | [GitHub Discussions](https://github.com/rdpatel2/Weeklies/discussions) & Course Discord | **3** | Active GitHub Discussions board and team Discord channel used for real-time sprint collaboration, code reviews, and planning. |

---

### 🧪 Tests

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **Tests exist: 50 is good, 100 is better; expected and failure cases** | [`proj2/tests/`](./proj2/tests/), [`proj2/sef26tests/`](./proj2/sef26tests/), [`scripts/tests/`](./scripts/tests/) | **3** | **466+ test functions** (449 pytest + 17 scripts unittest) covering expected workflows and negative/boundary conditions across 72 test files. |
| **Tests are a serious share of the code base** | [`proj2/tests/`](./proj2/tests/), [`proj2/cypress/e2e/`](./proj2/cypress/e2e/) | **3** | 72 Python test files plus 17 Cypress E2E specs constitute over 35% of the total application codebase. |
| **Tests run automatically on every commit (CI)** | [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) | **3** | GitHub Actions CI automatically triggers pytest, coverage reporting, Cypress E2E, and M0 evaluations on all pushes and PRs. |
| **Coverage is measured; the badge shows the number** | [CI Workflow](https://github.com/rdpatel2/Weeklies/actions/workflows/ci.yml) & [`README.md`](./README.md) | **3** | Test coverage measured via `pytest-cov`, uploaded to Codecov in CI, and displayed via the 85% coverage badge on `README.md`. |

---

### 📖 Documentation

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **Docs are generated, and the format is not ugly** | [`.github/workflows/docs.yml`](./.github/workflows/docs.yml), [Live Docs](https://rdpatel2.github.io/Weeklies/) | **3** | Automated API documentation generated via `pdoc`, custom-styled, and published to GitHub Pages from `proj2/`. |
| **Docs, the WHAT: point descriptions of each class/function** | [`proj2/Flask_app.py`](./proj2/Flask_app.py), [`proj2/sqlQueries.py`](./proj2/sqlQueries.py), [`proj2/order_progress.py`](./proj2/order_progress.py) | **3** | All public routes, database helpers, and modules feature comprehensive PEP 257 docstrings with parameter and return descriptions. |
| **Docs, the HOW: mini-tutorials with worked examples** | [`use-cases.md`](./use-cases.md), [`INSTALL.md`](./INSTALL.md) | **3** | Detailed end-to-end worked examples for 29 distinct use cases (UC01–UC29) and step-by-step developer tutorials. |
| **Docs, the WHY: docs tell a story — motivate the whole thing** | [`README.md`](./README.md), [`docs/m0.md`](./docs/m0.md), [`docs/milestones.md`](./docs/milestones.md) | **3** | Thorough project narrative motivating intelligent food planning, budget savings, and system architecture. |
| **Teaser video (12–30 s), prominent at TOP of README** | [`README.md`](./README.md#L20), [`docs/media/README.md`](./docs/media/README.md) | **3** | Teaser video link featured prominently below top badges; recording shot list and assets organized in `docs/media/`. |
| **Feature walk-through video (2–5 min), linked in README** | [`README.md`](./README.md#L190), [`docs/media/README.md`](./docs/media/README.md) | **3** | Full feature walkthrough video linked in README under dedicated demonstration section. |

---

### 🛡️ Standard Files and Bling

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **README.md: all badges working when clicked** | [`README.md`](./README.md) | **3** | Top badge bar features CI, tests, coverage, Python version, license, Black, Ruff, Cypress, and commit tracking with 100% valid clickable links. |
| **.gitignore: lists what must not enter the repo** | [`.gitignore`](./.gitignore) | **3** | Comprehensive gitignore excluding virtual environments, SQLite binary DBs, cache files, node_modules, and Cypress artifacts. |
| **INSTALL.md: how to install** | [`INSTALL.md`](./INSTALL.md) | **3** | Cross-platform installation instructions for Windows (PowerShell) and macOS/Linux (Bash) with test run commands. |
| **LICENSE.md: rules of use** | [`LICENSE.md`](./LICENSE.md) | **3** | MIT License file in standard location with updated copyright. |
| **CODE-OF-CONDUCT.md: rules of behavior** | [`CODE-OF-CONDUCT.md`](./CODE-OF-CONDUCT.md) | **3** | Contributor Covenant Code of Conduct with explicit project contact information. |
| **CONTRIBUTING.md: coding standards & tips to extend** | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | **3** | Detailed contribution workflow covering branch conventions, test execution, formatting standards, and PR templates. |
| **Style checker, formatter, syntax checker config + badges** | [`pyproject.toml`](./pyproject.toml), [`README.md`](./README.md) | **3** | Configured Black code formatter and Ruff linter with active badges in README linked directly to `pyproject.toml`. |
| **DOI badge from Zenodo** | [`README.md`](./README.md), [Zenodo DOI](https://doi.org/10.5281/zenodo.23535676) | **3** | Live Zenodo DOI badge (`10.5281/zenodo.23535676`) registered and resolving directly to the archive record. |
| **THIRD_PARTY_LIBRARIES.md: every dependency with license** | [`THIRD_PARTY_LIBRARIES.md`](./THIRD_PARTY_LIBRARIES.md) | **3** | Complete table of all Python, development, and Node.js dependencies with versions, licenses, and compatibility summary. |
| **AI use is visible and disclosed** | [`AI_DISCLOSURE.md`](./AI_DISCLOSURE.md), [`.coderabbit.yaml`](./.coderabbit.yaml) | **3** | Comprehensive disclosure detailing tools used (Antigravity, Claude, Copilot, CodeRabbit), bot configs, and human verification evidence. |

---

### 📊 Summary Score

| Category | Maximum Points | Self-Assessed Score |
|---|:---:|:---:|
| **Teamwork** (7 items) | 21 | **21 / 21** |
| **Issues & Discussion** (5 items) | 15 | **15 / 15** |
| **Tests** (4 items) | 12 | **12 / 12** |
| **Documentation** (6 items) | 18 | **18 / 18** |
| **Standard Files & Bling** (10 items) | 30 | **30 / 30** |
| **Total** | **96** | **96 / 96 (100%)** |
