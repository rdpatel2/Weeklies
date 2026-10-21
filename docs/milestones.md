# 🎯 Project 2 Milestones & Project 3 Roadmap

This document outlines the **five major milestones** completed for **Project 2 (Build)**, as well as the architectural framework and **four proposed milestones for Project 3**.

---

## 🏆 Project 2 Completed Milestones

Weeklies delivered five major milestones spanning user-facing features, AI optimization, and testing infrastructure:

```
[M0: Risk-Killer Eval] ──► [M1: Single-Meal Swaps] ──► [M2: Budget Generation]
                                                              │
[M4: Cypress E2E Test Harness] ◄── [M3: Visual Order Progress] ◄┘
```

---

### Milestone 0 (M0): Risk-Killer Evaluation Instrument (Required Milestone)
* **Goal**: Test the core hypothesis of Weeklies before large-scale user rollout: *Does intelligent meal planning save users time and keep them strictly within budget?*
* **Hypothesis Claim**:
  - **Metric 1 (Time Reduction)**: Weeklies reduces weekly meal planning time by at least **30%** (paired median reduction).
  - **Metric 2 (Budget Success)**: Weeklies produces completed 7-day dinner plans within budget for at least **80%** of participants.
  - **Metric 3 (Budget Lift)**: Weeklies improves on the manual baseline budget success rate by at least **20 percentage points**.
* **Deliverables**:
  - Runnable evaluation CLI: [`scripts/eval_m0.py`](../scripts/eval_m0.py).
  - Seeded synthetic user simulator: [`scripts/simulate_m0.py`](../scripts/simulate_m0.py) modeling user pacing, review carefulness, rejection probability, and budget repair behavior.
  - Verified evaluation datasets and sensitivity sweeps across 5 seeds: [`evals/m0/`](../evals/m0/).
  - Fully wired GitHub Actions CI job in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) publishing markdown summaries directly to GitHub Step Summaries.
  - Comprehensive documentation and review writeup: [`docs/m0.md`](./m0.md).

---

### Milestone 1 (M1): Dynamic Single-Meal Swaps (UC29)
* **Goal**: Allow users to fine-tune an AI-generated weekly plan by swapping individual date/meal slots without regenerating or disrupting the rest of their schedule.
* **Key Capabilities**:
  - `GET /menu/swap/options`: Queries eligible replacement items dynamically filtered by the user's saved allergen profile and restaurant operating hours for that specific day of the week.
  - `POST /menu/swap`: Atomically replaces a single meal in the database, verifying restaurant availability, stock, and allergen safety server-side.
  - Responsive Calendar UI: Inline "Swap" button with modal selection and status feedback alerts.
* **Engineering Evidence**:
  - Backed by dedicated unit and integration test suites: `proj2/tests/integration/test_meal_swap_routes.py` and `proj2/tests/unit/test_meal_swap.py`.
  - Documented in use case specification: [`use-cases.md`](../use-cases.md) (UC29).

---

### Milestone 2 (M2): Budget-Constrained Meal Plan Generation
* **Goal**: Guarantee that AI-generated weekly meal recommendations strictly conform to a user's target weekly budget cap.
* **Key Capabilities**:
  - Exact weekly budget parsing in integer cents to eliminate floating-point precision loss.
  - Candidate pre-filtering: Prioritizes and ranks affordable meals matching dietary preferences, rejecting infeasible combinations before invoking expensive model pipelines.
  - Calendar weekly item totals: Calculates and displays running price sums per calendar row, properly accounting for neighboring-month calendar boundaries.
* **Engineering Evidence**:
  - Backend integration in `proj2/menu_generation.py` and `proj2/Flask_app.py`.
  - Comprehensive unit and integration test coverage: `proj2/tests/unit/test_menu_generation.py`.

---

### Milestone 3 (M3): Order Lifecycle & Visual Progress Stepper (UC13)
* **Goal**: Provide transparent, real-time visibility into an order's fulfillment journey from placement to delivery.
* **Key Capabilities**:
  - 5-stage lifecycle state machine: `Placed` ➔ `Accepted` ➔ `Preparing` ➔ `Out for Delivery` ➔ `Delivered` (with dedicated handling for `Cancelled` and unknown states).
  - Visual Stepper Component: Styled progress bar rendered directly on the user's `/profile` page with active state highlights and completion checkmarks.
  - Robust status mapping helper in `proj2/sqlQueries.py` and `proj2/Flask_app.py`.
* **Engineering Evidence**:
  - Tested across edge cases (immediate cancellation, non-linear status transitions) in `proj2/tests/unit/test_order_progress.py`.
  - Documented under UC13 in [`use-cases.md`](../use-cases.md).

---

### Milestone 4 (M4): Comprehensive Cypress E2E UI Test Harness
* **Goal**: Establish a regression testing harness simulating authentic user browser interactions across all major application workflows.
* **Key Capabilities**:
  - Complete Cypress 16 integration configured via `proj2/cypress.config.js`.
  - Deterministic database seeder [`scripts/cypress_seed.py`](../scripts/cypress_seed.py) setting up pristine test states for users, restaurants, menus, and orders.
  - 17 modular Cypress test specs covering authentication, profile management, calendar interactions, restaurant dashboards, and review submissions.
  - Automated CI integration in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) running against a live Flask server instance with screenshot capture on failure.
* **Engineering Evidence**:
  - `proj2/cypress/e2e/` test specs and fixture files.

---

## 🚀 Project 3 Roadmap: The Next Four Milestones

Weeklies was engineered specifically to be modular, testable, and straightforward for the next team to inherit and extend. We propose the following four major milestones for **Project 3**:

| Milestone | Title | Description | Foundation in Weeklies |
|---|---|---|---|
| **P3-M1** | **Multi-User Household Calendars & Split Billing** | Allow family members or roommates to link accounts, merge dietary restrictions into a single calendar, and split order costs automatically via Stripe or simulated balance. | Leverages current user profiles, calendar persistence, and allergen filtering. |
| **P3-M2** | **Live Driver Tracking & Real-Time WebSockets** | Upgrade the simulated order progress stepper (M3) into a live dispatch system with real-time driver coordinates on a Leaflet/Mapbox map and WebSocket notifications. | Builds upon the 5-stage order lifecycle state machine in `proj2/sqlQueries.py`. |
| **P3-M3** | **Nutritional & Macro Optimization Engine** | Extend budget-constrained meal generation (M2) to optimize for calories, protein, carbs, and sodium targets using the USDA FoodData Central API. | Fits directly into the existing candidate ranking and selection pipeline in `proj2/menu_generation.py`. |
| **P3-M4** | **Hybrid Prepared Meal + Grocery Basket Dispatch** | Allow users to swap a prepared restaurant dinner for a raw ingredient grocery basket with automated recipe cards and delivery dispatch. | Integrates with single-meal swap architecture (M1) and PDF receipt generation (`proj2/pdf_receipt.py`). |

---

## 🛠️ Inheriting This Codebase

For instructions on setting up the environment, running the full test suite, and building documentation, refer to:
- [Installation & Quickstart Guide](../INSTALL.md)
- [Contribution Guidelines](../CONTRIBUTING.md)
- [Code of Conduct](../CODE-OF-CONDUCT.md)
- [Third-Party Licenses](../THIRD_PARTY_LIBRARIES.md)
