# WEEKLIES — Your meals. Your schedule. Your budget.
**CSC 510 / Project 1b / Proposal**  
**Group 11 | Srikar Desemsetti, Rohan Patel, Alex Tanton, Kushal Upretti**
## Project overview
Choosing meals every day takes time, and more often than not, a weekly plan can be costly and get old quickly. We propose extending Weeklies into a budget-aware meal planner that lets customers set a weekly limit, understand selections, and replace meals without rebuilding their calendar. Restaurant owners and kitchen staff gain clearer order updates and a view of upcoming demand: less daily planning, more spending control, and better coordination.
## Who benefits?
**Customers** — Busy people who need to balance time, cost, and preferences.  
**Restaurant owners** — See upcoming demand and manage fulfillment.  
**Kitchen staff** — Follow an explicit preparation queue.  
**Maintainers** — Build on reproducible use-case tests.
## Our next version
**Budget — Weekly spending limits.** Compare meal prices across vendors and allocate a weekly budget for meals.  
**Meal selection — Individual meal replacement.** Swap a single calendar entry for the week without disrupting future plans.  
**Order status — Order progress timeline.** See recorded order transitions on a timeline that refreshes as the restaurant progresses through fulfillment.
## Development plan
### Before · Project 1a baseline
**Map real user goals.** 28 documented use cases. Trace routes and record success and exception paths for accounts, planning, orders, reviews, and analytics.  
**Establish regression evidence.** 172 test functions in 28 modules. Use Flask clients and temporary SQLite fixtures; attach a verified run summary.  
**Understand planning limits.** Trace UC06–07 and tests: generation checks hours, stock, and declared allergies while retaining existing slots.
### Now · Project 2 proposed work
**Budget-aware generation.** Add a weekly cap and item total; filter and rank eligible candidates. Test exact-limit and impossible-budget cases.  
**Single-meal swaps.** Replace one date/meal slot after server-side availability and allergen checks. Test that other slots stay intact.  
**Visible order progress.** Persist transition timestamps; refresh a customer timeline. Test ownership, legal transitions, and terminal states.
### Future · Project 3 candidate work
**Reusable weekly templates.** Save and copy a week to new dates; recheck prices, hours, and stock. Require review before creating orders.  
**Explainable suggestions.** Allow users to get suggestions based on previous preferences, available budget, and current availability.  
**Restaurant demand preview.** Aggregate plans by date and meal. Separate tentative selections from orders; omit customer identities.
## Evidence and system views
**28 documented use cases · 28 Project 1a test modules · 172 test functions**  
Counts checked in `use-cases.md` and `proj2/sef26tests/`. Source inventory only; execution, pass/fail totals, and coverage still need verification.
**Insert real screenshot:** Customer meal calendar — show existing generated entries.  
**Insert real screenshot:** Restaurant order dashboard — show fulfillment controls.  
**Insert test-run capture:** Project 1a suite summary — include date and commit.
## Proposed stack
**Python / Flask** — Extend existing planning and order routes.  
**SQLite** — Store budgets, meals, and transition history.  
**HTML / CSS / JavaScript** — Calendar actions and timeline refresh.  
**LLM + fallback** — Rank candidates; enforce constraints in code.  
**pytest / Actions** — Check regressions as features evolve.
## Project links
**Repository:** https://github.com/rdpatel2/Weeklies  
**Discussion forum:** [FORUM URL]  
**Feature walkthrough:** [VIDEO URL] (2–5 minutes)  
Print each complete URL underneath its matching QR code. Give CSC 510 tutors and lecturers access to the forum.
## Finalization checklist
Replace bracketed links and add three functioning QR codes, real screenshots, verified test-run evidence, and official technology icons. Confirm the group details, forum permissions, walkthrough duration, and one-page PDF export. Proposed features are not claims of completed implementation.
