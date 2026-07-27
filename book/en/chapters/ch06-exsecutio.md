# Chapter 6 · Exsecutio: From Proposal to Delivery Candidate

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-06 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D20-T03 · Complete chapter review and evidence alignment |
| Draft Completeness | Formal ten-chapter production-line readable draft; D20-T03 five-category review complete |
| Primary Question | How can AI keep advancing through plan, execution, verification, repair, and Walkthrough until artifacts satisfy the definition of done and can be accepted by the next phase? |
| Reader Outcome | Able to run a full Bolt and retain phase decisions, file changes, test results, failure fixes, and completion evidence |
| Related Experiments | `EXP-06-01`, `EXP-06-02`, `EXP-06-03` |

## 01 · Question: Why Execution Is Not “Let AI Keep Going”

Chapter 5 answered how to choose a Bolt: by domain complexity, risk, and reversibility, slice work into Simple Construction or DDD Construction execution tracks. Chapter 6 moves one step forward: **after the Bolt is chosen, how can AI keep advancing through plan, execution, verification, repair, and Walkthrough until artifacts satisfy the definition of done and can be accepted by the next phase?**

That is what this book’s dedicated term `Exsecutio` expresses.

`Exsecutio` is not execution in the everyday sense, and it is not letting AI run autonomously without end. In AI-DLC, it means an engineered form of follow-through: goals come from Inception, boundaries from Memory Bank and Standards, scope from the Bolt, and work must keep returning to plan, tests, failure repair, evidence, and handoff.

You can also read the core formula on this book’s cover as a working principle:

```text
AI-DLC = 𝓔 (human judgment + AI capability)
𝓔 = Engineering with Exsecutio
```

Here `Exsecutio` is a defined term: the process of **carrying a proposal through to a delivery candidate**. AI capability makes proposals, drafts, and edits cheap; human judgment owns direction, boundaries, risk acceptance, and definition of done; engineered execution connects the two so results do not stop in the chat window but enter a versioned, verifiable, handoff-ready artifact system.

If you only let AI keep generating, three problems appear most often.

First, plan and reality diverge. AI may implement “convenient optimizations” outside the plan, or miss key deliverables inside it. Second, failures are not preserved. Test failures, fix attempts, and re-test outcomes that live only in chat leave the next session unable to tell whether the issue is truly closed. Third, definition of done softens. AI tends to declare completion when results look reasonable, but engineering delivery needs auditable evidence.

So this chapter’s core question is: **how can AI keep advancing through plan, execution, verification, repair, and Walkthrough until artifacts satisfy the definition of done and can be accepted by the next phase?**

After this chapter, readers should be able to do three things:

1. Write an executable Implementation Plan for a Bolt.
2. During execution, preserve file changes, failures, fixes, and re-test evidence.
3. Use Walkthrough so an unfamiliar reviewer can confirm Bolt completion from artifacts alone.

### Gate

- [x] One core question only: how to carry a Bolt from plan to a deliverable candidate.
- [x] Reader outcome is observable: run a full Bolt and retain phase decisions, file changes, test results, failure fixes, and completion evidence.
- [x] This chapter does not re-debate Bolt type selection; that is CH-05.
- [x] This chapter does not treat model self-assessment as completion evidence; verification mechanisms are developed in CH-07.

## 02 · Framework: The Five-Stage Exsecutio Loop

This chapter describes Exsecutio as a five-stage loop:

```text
Plan
  State what to do, why, where to change, and how to accept

Execute
  Generate, modify, supplement, and organize deliverables within scope

Verify
  Run deterministic checks, tests, builds, links, or review gates

Repair
  Preserve failures, fix issues, verify again

Walkthrough
  Explain actual changes, evidence, deviations, risks, and handoff conditions
```

These five stages are not a waterfall sequence—they are an execution loop with feedback. Plan supplies the reference; Execute produces change; Verify exposes facts; Repair closes failures; Walkthrough makes results recoverable and receivable. AI-DLC cares less whether AI “finishes in one breath” and more whether, after each push, the system is closer to an evidenced delivery candidate.

### 2.1 Plan: The Plan Is a Reference, Not a Ritual

The value of an Implementation Plan is not to make the process look formal—it is to give later deviation audits something to compare against. A plan should at least clarify four things: goal, scope, deliverables, acceptance. Without a plan, every new file AI adds can be interpreted as reasonable; with a plan, execution can answer what was done, missed, or drifted.

An executable plan need not be long, but it must answer:

- **Objective:** What state should this Bolt push which concern to?
- **Scope:** Which objects may be read or modified? Which are out of scope?
- **Deliverables:** Which files, pages, data, tests, or docs should exist when done?
- **Acceptance:** What evidence closes the Bolt?
- **Constraints:** Which dependencies, cost, permission, style, or security boundaries must not be crossed?

For AI, the plan is a constraint; for humans, it is an audit entry. It lets Walkthrough become not merely “I did these things” but “I planned these, delivered these, deviations are here, evidence is here.”

### 2.2 Execute: Execution Must Stay Within Scope

The Execute phase can let AI generate and edit quickly, but it must not expand without bound. Every change should return to the Bolt’s input boundary, modification boundary, and completion boundary. A good execution is not “no change”—it is change that is explainable, reviewable, and reversible.

In a writing project, Execute might mean expanding chapters, generating SVGs, updating task facts, rendering the cockpit, or adding review records. In software, it might mean creating modules, changing interfaces, adding tests, migrating data, or updating docs. Whatever the object, Execute should keep two habits:

1. Know why before changing.
2. Be able to say what changed after changing.

These habits sound plain, but they block the most common AI collaboration failure mode: artifacts pile up while nobody knows which parts are target, which are incidental, and which are model enthusiasm.

### 2.3 Verify: Verification Proves You May Continue, Not That You Are Perfect

Verify’s goal is not to prove the system is forever correct—it is to prove the current Bolt may enter the next phase. For this writing system, verification might be `validate_project.py`, `generate_progress.py`, `ci_check.py`, link checks, book builds, or chapter review. For software, unit tests, integration tests, type checks, smoke tests, or human gates.

Verification should be as deterministic as possible. Model self-assessment can hint; it cannot be completion evidence. Real verification produces reviewable results: command output, test reports, build artifacts, link audits, review checklists, screenshots, snapshots, or recorded human approval.

An important boundary: verification is not perfectionism. A Bolt’s verification should cover the risks it promised. Updating a chapter skeleton does not need full end-to-end production load tests; release automation cannot be satisfied by “Markdown exists.” Verify matches gates to risk.

### 2.4 Repair: Failures Are Evidence, Not Noise

Failure logs, fix actions, and re-test results must be saved. Without failure records, teams assume first-pass delivery; without re-test records, they cannot tell whether a fix worked. AI-DLC does not require a failure-free process—it requires failures to be visible, corrected, and proven closed.

Repair suffers two illusions most.

First, pretending failure never happened: change until tests pass without recording cause, and the same class of bug returns. Second, treating fix as pass: change one line of code or copy and declare closed without re-running the check that failed.

Good repair records include at least:

- **Failed Check:** Which check failed?
- **Cause:** Why—confirmed or hypothesized?
- **Change:** What was changed to fix it?
- **Re-test:** Which check passed on re-run?
- **Residual Risk:** What risk was not covered this round?

This recording is not punishment—it is how teams learn. In AI-DLC, failure is fuel for process accuracy, not a stain to hide.

### 2.5 Walkthrough: Let a Stranger Review

Walkthrough is the Bolt’s handoff surface. It should answer: what was planned, what actually changed, what was tested, how failures were handled, what deviated, what risk remains, and how the next phase takes over. A new session or unfamiliar reviewer should not rely on AI saying “done”—they should follow Walkthrough through the evidence chain.

This is where AI-DLC differs from ordinary conversational collaboration. Ordinary collaboration often assumes “context still lives in chat”; AI-DLC assumes context will break, compress, change hands, or enter CI and release systems. Completion must satisfy tomorrow’s you, another AI session, a collaborator, or a reviewer—not only today’s dialogue.

One sentence tests Walkthrough quality:

```text
If I forgot today’s entire chat tomorrow and only read repo artifacts, could I tell whether this Bolt is done?
```

If the answer is no, Exsecutio is not finished.

### 2.6 Construction Two-Phase and Mob Construction (summary)

AWS **Construction** advances Domain Design → Logical Design (including ADR) → Code/Unit Tests; brownfield work first lifts code into static/dynamic models before the same greenfield-shaped path. **Mob Construction** (co-located collaboration, exchanged integration specs, Bolts delivered per Unit) pairs with Inception’s Mob Elaboration (summary in the [Amplify whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com)).

[aidlc-workflows](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md) operationalizes Construction as **two phases**: first produce a checkbox **Implementation Plan** md; after Question→Doc→Approval, start codegen. Report-style outputs (e.g. validation reports) stay separate from `aidlc-docs/` plans to avoid confusing Memory Bank fact sources. This chapter’s five-stage loop (Plan→Execute→Verify→Repair→Walkthrough) is compatible: the first Plan phase is the approvable plan; Execute starts only after approval. Chapter-to-workflow mapping is in [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md).

## 03 · Three-Part Argument: Why Exsecutio Is AI-DLC’s Follow-Through Layer

### Part one: AI proposals must land in artifacts

AI is strong at proposing, drafting, and explaining errors. A delivery candidate is not the proposal itself—it is artifacts written to the repo, passing verification, leaving evidence, and receivable by the next phase. Exsecutio turns “AI can do this” into “the system has received this.”

This step is critical. Without Exsecutio, AI output stays at the “sounds reasonable” layer: polished plans, clear paths, even runnable snippets—while repo facts, test results, release state, and team consensus do not really move. That collaboration is a high-quality discussion, not delivery.

Exsecutio requires proposals to land on versioned objects: Markdown, JSON, code, tests, config, review records, release notes, event logs, or snapshots. Only then do proposals gain engineering life.

**Conclusion:** Exsecutio’s first value is carrying model proposals into versioned, verifiable, handoff-ready artifacts.

### Part two: Verification and repair belong in one execution loop

Many failures are not because AI cannot write, but because verification and repair were never on the same track. Unsaved test failures strip fixes of context; fixes without re-test make completion an optimistic guess. Exsecutio requires execute, failure, repair, and re-test to form one loop.

This loop demotes “written” to an intermediate state and upgrades “provably safe to continue” to the completion bar. AI can ship a first version fast; the engineering system asks: did it pass agreed checks? is failure handling recorded? are plan deviations explained? is next-step handoff clear?

Without this loop, AI collaboration produces many half-finished states: surface done, detail drift, lost failures, review cost pushed late. Exsecutio front-loads those hidden costs so failure surfaces where it is still cheap to fix.

**Conclusion:** Exsecutio’s second value is turning failure–fix–re-test into delivery evidence, not chat noise.

### Part three: Walkthrough makes execution recoverable

AI-DLC continuous delivery depends on recoverability. A Bolt with only final files and no plan, deviation, test, or handoff notes forces the next session to guess again. Walkthrough makes execution results usable, reviewable, maintainable, and continuable.

That matters especially for long-horizon writing. A technical book is not ten chapters in one day—it is dozens of sessions, hundreds of edits, multiple reviews and releases while direction stays aligned. Every Exsecutio pass should clarify state, not deepen context debt.

Recoverability is also structural restraint on AI hallucination. AI can forget, misread, or grow overconfident—but artifacts do not argue by mood. Plan, diffs, tests, and Walkthrough form external constraints that replace “I feel done” with “evidence shows these conditions are met.”

**Conclusion:** Exsecutio’s third value is turning execution from a one-off session into recoverable engineering record.

## 04 · Example: The Book Progress Cockpit Bolt

This chapter uses `memory-bank/bolts/002-github-writing-system-ui/` as the sample. That Bolt’s goal: on top of three versioned fact sources, build a deterministic, fail-safe, auditable generation chain that renders task, chapter, and experiment facts into a bird’s-eye cockpit, object drilldown pages, event log, snapshots, and current summary.

It is a Simple Construction Bolt, but not trivial. It touches data aggregation, event deduplication, snapshot reuse, page rendering, link audit, responsive layout, and fail-safe behavior. It stays Simple because domain concepts are clear, reversibility is high, change targets are explicit, and risk can be exposed through tests and link checks.

This example shows the full five-stage Exsecutio loop.

### 4.1 Plan: Split “Progress Visualization” into Acceptable Deliverables

The Implementation Plan did not say merely “build a cockpit.” It split the goal into six delivery classes:

```text
Shared Progress Engine
  Load facts, normalize, compute metrics, next action, blockers, chapter and experiment rollups

Replaceable Current Projection
  current.json / current.md / last-successful-facts.json / site/data/progress.json

Append-Only Key Event Ledger
  events.jsonl for task, chapter phase, and experiment status changes

Immutable Snapshots and Changelog
  snapshots/ and CHANGELOG.md

Bird's-Eye Static Dashboard
  site/index.html, CSS, JS, and no-JavaScript fallback

Drilldown and Accessibility
  details.html, object anchors, keyboard, semantics, 360px responsive
```

This plan enables line-by-line audit during execution. AI cannot hand over a pretty page alone—the plan also demands event ledger, immutable snapshots, fail-safe behavior, drilldown, and accessibility. It cannot expand without bound—the plan explicitly excludes GitHub Actions, Pages, Projects, and formal release for later Bolts.

Plan plays two roles: a clear task boundary for AI and an acceptance checklist for humans.

### 4.2 Execute: Land the Plan on the File System

The implementation Walkthrough shows three core capability groups delivered.

First, the data engine: `scripts/progress_core.py` for metrics, status, current Day, next action, blockers, chapter matrix, experiment distribution, source identity, and event diffs.

Second, transactional generation: `scripts/generate_progress.py` runs validate → aggregate → diff → events → snapshot → summary → pages, using temp files and atomic replace to protect last-good state.

Third, human-readable projections: `progress/generated/current.md`, `progress/CHANGELOG.md`, `site/index.html`, and `site/details.html` let authors see progress, recent events, next action, and drilldown without reading JSON.

These files are not random. Together they implement one chain from the plan: authoritative facts stay in `progress/tasks.json`, `progress/chapters.json`, `progress/experiments.json`; generated outputs are projections and history; page numbers are not maintained by hand.

### 4.3 Verify: Automation and Real Browser Prove Continue

The test Walkthrough records three verification layers.

Layer one—automated tests: Validator, Progress Core, and Generator Integration—32 tests covering fact validity, metric math, next-action ordering, event deduplication, snapshot reuse, fail-safe behavior, and no-JavaScript page contracts.

Layer two—real repo checks: `validate_project.py` and `generate_progress.py --dry-run` prove current fact sources valid and repeat runs do not spawn spurious events or snapshots.

Layer three—page and browser checks: link audit confirms clickable links; desktop 1280×720 and mobile 360×800 confirm no page-level horizontal overflow and that core metrics, navigation, drilldown, focus, and console state meet requirements.

Verify is not “I checked”—it is a set of reviewable results. Browser verification moves from “HTML exists” to “real pages work at key viewports.”

### 4.4 Repair: Failures Enter Delivery History

The test Walkthrough also records two found-and-fixed issues.

First, a wrong weighted-progress assertion in tests. Initial run was 31/32 pass; one expected value was wrong: sample completion weight 5, total weight 9, correct weighted progress is 55.6%, not 62.5%. The fix was correcting the test expectation—not changing implementation to match a bad assert.

Second, dead links to planned-but-not-yet-created artifacts. Initial HTML audit found 32 planned deliverables rendered as clickable links. After fix: existing artifacts get links; not-yet-created paths show path plus “pending creation” label—no dead links.

Both are pedagogically useful. One shows verification itself can be wrong and must be corrected against facts; the other shows page usability includes link semantics, not only content. Critically, neither was hidden—they entered the test Walkthrough as failure–fix–re-test evidence future reviewers can audit.

### 4.5 Walkthrough: Hand Execution to the Next Phase

The implementation Walkthrough lists deliverables, doc updates, smoke evidence, and explicit out-of-scope items. The test Walkthrough gives automated tests, link audit, browser verification, no-JS contracts, and fail-safe evidence.

A new session reading only these files can answer:

- What did this Bolt originally plan to deliver?
- Which files and capabilities were actually implemented?
- Which tests passed?
- What issues appeared along the way?
- How was closure proven after fixes?
- What was intentionally left for later Bolts?

That is Exsecutio’s finished shape: AI did the work and left in the repo why, what actually changed, how it was verified, how failures were handled, and how to take the next step.

## 05 · Pattern: A Reusable Exsecutio Record Template

Readers can abstract this case into a general template. Every Bolt need not produce long docs, but five information classes should stay visible.

| Stage | Minimum record | Reviewer must be able to judge |
|---|---|---|
| Plan | Goal, scope, deliverables, acceptance, constraints | What this Bolt should finish and must not do |
| Execute | File changes, implementation notes, key trade-offs | Whether actual change stayed in plan scope |
| Verify | Commands, tests, builds, review, or human gates | Whether completion has external evidence |
| Repair | Failure, cause, fix, re-test, residual risk | Whether issues truly closed |
| Walkthrough | Plan vs actual, evidence, deviation, handoff | Whether a stranger can recover context |

This table can go straight into a team Bolt template. It does not require essays every time—it requires key judgments not live only in chat.

A light Bolt might need only 20 lines of Walkthrough; a high-risk Bolt might need fuller design records, ADRs, test reports, and human approval. Scale can vary; structure should not disappear.

## 06 · Experiment: Three Verification Directions

This chapter’s experiment entries:

- **`EXP-06-01 · Plan–Walkthrough deviation auditor`:** Compare Implementation Plan, code changes, and Walkthrough; emit tables of planned items, actual changes, and undeclared deviations. Run: `python3 experiments/exp-06-01/quickstart.py --sample`.
- **`EXP-06-02 · Failure–fix–re-test loop recorder`:** From failure logs, fix commits, and test results, build a time-ordered repair evidence chain. Run: `python3 experiments/exp-06-02/quickstart.py --sample`.
- **`EXP-06-03 · End-to-end Bolt execution reproduction`:** Against a frozen-pin Bolt execution guide, reproduce full artifacts from plan through test report and elapsed time. Run: `python3 experiments/exp-06-03/quickstart.py --sample`.

`EXP-06-01`, `EXP-06-02`, and `EXP-06-03` are verified. `EXP-06-01` sample at `experiments/exp-06-01/output/sample.json` shows plan, actual change, and Walkthrough can be alignment-audited; undeclared changes count as deviation, not automatic error. `EXP-06-02` sample at `experiments/exp-06-02/output/sample.json` shows failures, fix commits, and re-tests form a temporal evidence chain, with repair rounds, regression pass rate, and evidence completeness; completeness does not mean optimal repair quality.

`EXP-06-03` triage remains `KEEP-EXT`: sample at `experiments/exp-06-03/output/sample.json` reports `completion_seconds` and `artifact_completeness_percent`. It only shows end-to-end artifacts reproduce on the frozen guide—it does not write external tutorials as the sole implementation or treat sample duration as production performance guarantee.

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-06-01` | Plan and Walkthrough align; undeclared changes exist or not | Not prove every deviation is wrong |
| `EXP-06-02` | Failures, fixes, and re-tests form a continuous evidence chain | Not prove one-pass is better than multi-round repair |
| `EXP-06-03` | Bolt execution artifacts on frozen pin are complete and reproducible | Not write external tutorial as this book’s only implementation; KEEP-EXT must not be rewritten as SHIP |

The first two audits and the third frozen reproduction are backed by reproducible artifacts. Whether unfamiliar reviewer cost actually drops still needs real readers and team practice—frozen samples alone must not overclaim.

## 07 · Figure: Exsecutio Execution Loop

This chapter’s figure is the Exsecutio execution loop:

![Figure 6-1 · Exsecutio execution loop](images/ch06-exsecutio-loop.svg){.core-figure width=100%}

Source file: `book/images/ch06-exsecutio-loop.svg`. Main line and feedback:

```text
Plan ──▶ Execute ──▶ Verify ──▶ Repair ──▶ Walkthrough
 ▲                         │         │            │
 │                         └─────────┘            ▼
 └──────────── Evidence / Feedback ◀────── Handoff
```

The main flow runs horizontally; the failure loop returns lightly from Verify to Repair, then Verify again; Walkthrough feeds the next-phase receive zone; feedback lines return to shared input or constraint area, not a single node only.

The figure should help readers see three things:

1. Exsecutio’s main line runs from plan to handoff—not from prompt to answer.
2. Verify and Repair are a loop, not optional extras.
3. Evidence / Feedback returns to shared inputs and constraints so the next execution round has better context.

The figure should not cram detail. Each card keeps one core sentence so readers bird’s-eye structure first, then return to the body for depth.

## 08 · Boundary: What This Chapter Does Not Solve

First, this chapter does not choose Simple vs DDD Bolts—that is Chapter 5. It assumes the Bolt is already chosen and focuses on running to a delivery candidate.

Second, automated tests are not all verification. Writing, design, product decisions, and risk acceptance may need human gates. AI-DLC requires visible verification, not that everything must automate.

Third, this chapter does not encourage unbounded AI autonomy. Exsecutio does not remove humans—it places human judgment at key points: set direction, confirm boundaries, accept risk, approve release.

Fourth, not every failure needs a long report. Light failures get light records; high-risk failures need full records. What matters is failures do not vanish and re-tests are not skipped.

Fifth, Walkthrough is not documentation theater. Its goal is lower recovery cost. If it does not help the next executor judge “can we continue now,” it is only a pretty summary.

Sixth, `EXP-06-03` verified status covers only the frozen execution guide fixture in-repo—it must not pose as live external fetch validation or generalize sample duration as universal performance.

## Reader Exercise

Pick a real small task you are advancing and run Exsecutio for 30 minutes.

1. Write a Plan of at most 8 lines: goal, scope, deliverables, acceptance.
2. Execute minimal changes—only what the plan allows.
3. Run one Verify that produces external evidence: test, build, link check, review checklist, or human approval.
4. If something fails, record cause, fix, and re-test.
5. Write a Walkthrough with plan vs actual, verification, deviation, and next step.
6. Tomorrow open the same repo without chat—artifacts only—and see if you can still recover context.

If you can continue without chat memory, you have completed Exsecutio’s minimal loop.

## References

- `memory-bank/bolts/002-github-writing-system-ui/bolt.md`: progress aggregation, events, snapshots, and cockpit Bolt.
- `memory-bank/bolts/002-github-writing-system-ui/implementation-plan.md`: Bolt plan evidence.
- `memory-bank/bolts/002-github-writing-system-ui/implementation-walkthrough.md`: implementation Walkthrough.
- `memory-bank/bolts/002-github-writing-system-ui/test-walkthrough.md`: test Walkthrough.
- `memory-bank/bolts/001-github-writing-system-ui/bolt.md`: foundational fact-source Bolt.
- `progress/experiments.json`: governance status for `EXP-06-01`, `EXP-06-02`, `EXP-06-03`.
- `book/toc.md`: CH-06 core question, reader outcome, and experiment directions.
- [AWS AI-DLC Method Definition (Amplify)](https://prod.d13rzhkk8cj2z0.amplifyapp.com), [WORKING-WITH-AIDLC](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md), [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md): Mob Construction and two-phase Construction summary.
- `book/images/ch06-exsecutio-loop.svg`: Exsecutio five-stage loop figure.
- `../../chapters/ch06-exsecutio.md`: Chinese source chapter.
