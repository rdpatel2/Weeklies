# 📋 Project 2 Self-Assessed Repo Rubric

This document contains the self-assessed repository rubric for **Weeklies** (CSC 510, Fall 2026), evaluated against the project requirements.

**Scoring Scale**: `0` = None, `1` = A little, `2` = Somewhat, `3` = A lot.  
Every score is backed by direct clickable evidence links in the repository.

---

### 👥 Teamwork, Visible in GitHub

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **Many commits**: hundreds by the end is normal for teams that commit small | [GitHub Commits](https://github.com/rdpatel2/Weeklies/commits/development) | **2** | 300+ total commits across project history; active ongoing commits across development iterations. |
| **Commits come from different people** | [GitHub Contributors](https://github.com/rdpatel2/Weeklies/graphs/contributors) | **3** | Commits submitted from all 4 current team members: Rohan Patel, Srikar Desemsetti, Alex Tanton, and Kushal Upreti. |
| **Workload is spread over the whole team** | [GitHub Insights & Contributors](https://github.com/rdpatel2/Weeklies/graphs/contributors) | **3** | Balanced contribution across all team members covering backend routes, testing, simulation, styling, and documentation. |
| **Team members work across many parts of the code, not one silo each** | [PR History](https://github.com/rdpatel2/Weeklies/pulls?q=is%3Apr+is%3Aclosed) | **3** | Team members collaboratively contributed across `proj2/Flask_app.py`, `scripts/`, `proj2/tests/`, Cypress E2E specs, and documentation. |
| **Short release cycles**: frequent small commits, merged promptly | [Closed Pull Requests](https://github.com/rdpatel2/Weeklies/pulls?q=is%3Apr+is%3Aclosed) | **2** | 15 modular feature pull requests created and merged into `development` with atomic commit histories. |
| **Whole team uses the same tools**: config files in repo, updated by many different people | [`pyproject.toml`](./pyproject.toml), [`pytest.ini`](./pytest.ini), [`cypress.config.js`](./proj2/cypress.config.js), [`.coderabbit.yaml`](./.coderabbit.yaml) | **3** | Centralized configuration for Black, Ruff, pytest, Cypress, and CodeRabbit shared by all contributors. |
| **Whole team can run the system**: anyone can share screen and demo on machine | [`INSTALL.md`](./INSTALL.md) | **3** | Documented step-by-step setup enabling clean local runs (`flask run`) verified on Windows, macOS, and Linux. |

---

### 💬 Issues and Discussion

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **Issue reports: there are many** | [GitHub Discussions](https://github.com/rdpatel2/Weeklies/discussions) & [Pull Requests](https://github.com/rdpatel2/Weeklies/pulls?q=is%3Apr) | **1** | Team tracked discussions via GitHub Discussions and PRs; GitHub Issues was disabled on fork settings and is being re-enabled for final tracking. |
| **Issues are being closed** | [Merged Pull Requests](https://github.com/rdpatel2/Weeklies/pulls?q=is%3Apr+is%3Amerged) | **1** | All feature branches and bug fixes have been tracked and closed via merged PRs with detailed resolution descriptions. |
| **Issues are discussed before they are closed** | [PR Review Comments](https://github.com/rdpatel2/Weeklies/pulls?q=is%3Apr+is%3Aclosed) | **1** | Code reviews and implementation details were discussed in PR review threads and team Discord chat. |
| **A large share of issues relate to handling failing cases** | [PR #6 (CI gist token)](https://github.com/rdpatel2/Weeklies/pull/6), [PR #14 (Swap revert)](https://github.com/rdpatel2/Weeklies/pull/14), [PR #1 (UC22)](https://github.com/rdpatel2/Weeklies/pull/1) | **2** | Multiple PRs and commits specifically address edge cases, failing CI tokens, test collection issues, and reverting/refactoring broken states. |
| **Chat channel / discussion forum exists and is active** | [GitHub Discussions](https://github.com/rdpatel2/Weeklies/discussions) & Course Discord | **3** | Active GitHub Discussions board and team Discord channel used for real-time collaboration and planning. |

---

### 🧪 Tests

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **Tests exist: 50 is good, 100 is better; expected and failure cases** | [`proj2/tests/`](./proj2/tests/), [`scripts/tests/`](./scripts/tests/) | **3** | **466+ test functions** (449 pytest + 17 scripts unittest) covering expected workflows and negative/boundary conditions. |
| **Tests are a serious share of the code base** | [`proj2/tests/`](./proj2/tests/), [`proj2/cypress/e2e/`](./proj2/cypress/e2e/) | **3** | 46 Python test files plus 17 Cypress E2E specs constitute over 35% of the total application codebase. |
| **Tests run automatically on every commit (CI)** | [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) | **3** | GitHub Actions CI automatically triggers pytest, coverage reporting, Cypress E2E, and M0 evaluations on all pushes and PRs. |
| **Coverage is measured; the badge shows the number** | [CI Workflow](https://github.com/rdpatel2/Weeklies/actions/workflows/ci.yml) & [`README.md`](./README.md) | **2** | Test coverage measured via `pytest-cov`, uploaded to Codecov in CI, and displayed via the badge on README. |

---

### 📖 Documentation

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **Docs are generated, and the format is not ugly** | [`.github/workflows/docs.yml`](./.github/workflows/docs.yml), [`pdoc.toml`](./pdoc.toml) | **2** | Automated API documentation generated via `pdoc` and published to GitHub Pages from `proj2/`. |
| **Docs, the WHAT: point descriptions of each class/function** | [`proj2/Flask_app.py`](./proj2/Flask_app.py), [`proj2/sqlQueries.py`](./proj2/sqlQueries.py) | **3** | All public routes, database helpers, and modules feature comprehensive PEP 257 docstrings with parameter and return descriptions. |
| **Docs, the HOW: mini-tutorials with worked examples** | [`use-cases.md`](./use-cases.md), [`INSTALL.md`](./INSTALL.md) | **3** | Detailed end-to-end worked examples for 29 distinct use cases (UC01–UC29) and step-by-step developer tutorials. |
| **Docs, the WHY: docs tell a story — motivate the whole thing** | [`README.md`](./README.md), [`docs/m0.md`](./docs/m0.md), [`docs/milestones.md`](./docs/milestones.md) | **3** | Thorough project narrative motivating intelligent food planning, budget savings, and system architecture. |
| **Teaser video (12–30 s), prominent at TOP of README** | [`README.md`](./README.md#L20), [`docs/media/README.md`](./docs/media/README.md) | **2** | Teaser video link featured prominently below top badges; recording shot list and assets organized in `docs/media/`. |
| **Feature walk-through video (2–5 min), linked in README** | [`README.md`](./README.md#L170), [`docs/media/README.md`](./docs/media/README.md) | **2** | Full feature walkthrough video linked in README under dedicated demonstration section. |

---

### 🛡️ Standard Files and Bling

| Item | Evidence Link | Score (0–3) | Justification |
|---|---|:---:|---|
| **README.md: all badges working when clicked** | [`README.md`](./README.md) | **3** | Top badge bar features CI, tests, coverage, Python version, license, Black, Ruff, and commit tracking with valid clickable links. |
| **.gitignore: lists what must not enter the repo** | [`.gitignore`](./.gitignore) | **3** | Comprehensive gitignore excluding virtual environments, SQLite binary DBs, cache files, node_modules, and Cypress artifacts. |
| **INSTALL.md: how to install** | [`INSTALL.md`](./INSTALL.md) | **3** | Cross-platform installation instructions for Windows (PowerShell) and macOS/Linux (Bash) with test run commands. |
| **LICENSE.md: rules of use** | [`LICENSE.md`](./LICENSE.md) | **3** | MIT License file in standard location with updated copyright. |
| **CODE-OF-CONDUCT.md: rules of behavior** | [`CODE-OF-CONDUCT.md`](./CODE-OF-CONDUCT.md) | **3** | Contributor Covenant Code of Conduct with explicit project contact information. |
| **CONTRIBUTING.md: coding standards & tips to extend** | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | **3** | Detailed contribution workflow covering branch conventions, test execution, formatting standards, and PR templates. |
| **Style checker, formatter, syntax checker config + badges** | [`pyproject.toml`](./pyproject.toml), [`README.md`](./README.md) | **3** | Configured Black code formatter and Ruff linter with active badges in README linked to config files. |
| **DOI badge from Zenodo** | [`README.md`](./README.md), [Zenodo](https://zenodo.org) | **1** | Zenodo registration configured and pending final release tagging. |
| **THIRD_PARTY_LIBRARIES.md: every dependency with license** | [`THIRD_PARTY_LIBRARIES.md`](./THIRD_PARTY_LIBRARIES.md) | **3** | Complete table of all Python, development, and Node.js dependencies with versions, licenses, and compatibility summary. |
| **AI use is visible and disclosed** | [`AI_DISCLOSURE.md`](./AI_DISCLOSURE.md), [`.coderabbit.yaml`](./.coderabbit.yaml) | **3** | Comprehensive disclosure detailing tools used (Antigravity, Claude, Copilot, CodeRabbit), bot configs, and human verification evidence. |

---

### 📊 Summary Score

| Category | Maximum Points | Self-Assessed Score |
|---|:---:|:---:|
| **Teamwork** (7 items) | 21 | **18** |
| **Issues & Discussion** (5 items) | 15 | **8** |
| **Tests** (4 items) | 12 | **11** |
| **Documentation** (6 items) | 18 | **15** |
| **Standard Files & Bling** (10 items) | 30 | **28** |
| **Total** | **96** | **80 / 96 (83.3%)** |
