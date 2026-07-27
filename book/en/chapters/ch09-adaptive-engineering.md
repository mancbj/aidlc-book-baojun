# Chapter 9 · Adaptive Engineering: Choosing the Right Flow and Governance Intensity

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-09 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D23-T03 · Complete chapter review and evidence alignment |
| Draft Completeness | Formal ten-chapter production-line readable draft; D23-T03 five-category review complete |
| Primary Question | How do you choose among Simple, FIRE, and AI-DLC based on task complexity, codebase state, regulatory requirements, and team scale—without over- or under-engineering? |
| Reader Outcome | Able to use the risk–ceremony matrix to choose Flow, checkpoint count, and runtime scope, and explain the cost of the choice |
| Related Experiments | `EXP-09-01`, `EXP-09-02`, `EXP-09-03` |

## 01 · Question: Why the “Right Method” Depends on Risk, Not Slogans

Chapter 8 answered the operations question: how verified candidates enter observable, rollback-capable Operations. Chapter 9 pulls the lens one level back: **when tasks, codebases, regulatory constraints, and team scale differ, how should teams choose governance intensity instead of defaulting to one process for everything?**

That is the scope of adaptive engineering.

In AI-DLC, method is not decoration—it is risk hedging. Simple Flow trades fewer rituals for faster start; FIRE uses adaptive checkpoints and dynamic Runs for brownfield and uncertain boundaries; full AI-DLC Flow trades Intent, Unit, Bolt, Memory Bank, verification, and Operations for traceability and recoverability. All three have value; all three have cost.

Without adaptive choice, teams fail in two directions.

First, over-engineering. A reversible small change is forced through full Intent decomposition, multi-layer Bolts, and a complete Operations runbook—ceremony cost exceeds the risk, and AI speed is swallowed by process. Second, under-engineering. A high-impact, low-reversibility, regulated, or multi-handoff task relies only on chat-style generation and ad hoc judgment—errors cascade, evidence disappears, rollback is hard.

AI makes this sharper. AI makes drafts, code, and docs cheap, so teams more easily assume “process can be casual,” or conversely assume “since AI is fast, pile on every ritual.” Both reactions are wrong. Proposals are cheap; error cost and human attention are not. Adaptive engineering protects those two scarce resources.

So this chapter’s core question is: **how do you choose among Simple, FIRE, and AI-DLC based on task complexity, codebase state, regulatory requirements, and team scale—without over- or under-engineering?**

After this chapter, readers should be able to do three things:

1. Assess task risk and governance need using a set of observable dimensions.
2. Make a justified Flow choice among Simple, FIRE, and AI-DLC, and write explicit non-applicability conditions.
3. Explain checkpoint count, runtime scope, and review cost for that choice—not only “it feels right.”

### Gate

- [x] One core question only: how to choose Flow and governance intensity by risk.
- [x] Reader outcome is observable: use the risk–ceremony matrix to choose Flow, checkpoint count, and runtime scope and explain cost.
- [x] This chapter does not re-open the single Operations run chain; that is CH-08’s focus.
- [x] This chapter does not pre-empt org roles and value metrics; that is CH-10’s focus.
- [x] All three EXP-09 experiments are currently planned; do not write them as verified conclusions.

## 02 · Framework: Risk–Ceremony Matrix

This chapter uses the “risk–ceremony matrix” as the Flow selection framework: judge risk and constraints first, match ceremony intensity second, explicitly accept cost third.

```text
Risk Dimensions
  Complexity · Codebase State · Compliance · Team Scale · Reversibility

Ceremony Budget
  Checkpoints · Artifacts · Approvals · Traceability · Runtime Scope

Flow Options
  Simple Flow
  FIRE Flow
  AI-DLC Flow
```

The left side of the matrix is not preference—it is constraint. The right side is not honor—it is cost. Choosing a Flow is an explainable trade between “cost of being wrong” and “cost of ceremony.”

### 2.1 Five Risk Dimensions

Before choosing, assess at least five dimensions:

| Dimension | Question to ask | High-signal indicators |
|---|---|---|
| Complexity | Does the task span multiple domain concepts, interfaces, or drifting requirements? | Multiple Units, many boundaries, requirements still moving |
| Codebase State | Greenfield, brownfield, or monorepo / legacy coupling? | High coupling, missing tests, unclear blast radius for local changes |
| Compliance | Audit, security, regulatory, or customer contract requirements? | Changes must leave traces, approvals, replay |
| Team Scale | Solo push, or cross-role, cross-session, cross-shift handoff? | Parallel people, context easily lost |
| Reversibility | Can you roll back quickly; are data or user impacts recoverable? | Low reversibility; touches production entry or immutable history |

These dimensions are not a scoring game. Do not pretend precision to two decimal places. What helps: for each dimension write “what is the current evidence” and “what if we are wrong.” For example, Codebase State evidence might be test coverage, module coupling, recent regression incidents; Reversibility evidence might be draft publish, rollback path, irreversible data touch.

**Layer conclusion: characterize risk before method; otherwise Flow choice is taste debate.**

### 2.2 Governance Intensity of Three Flows

Three reference Flows can be roughly ordered by ceremony intensity:

```text
Simple
  Requirements → Design → Tasks
  Fits low complexity, high reversibility, clear boundaries

FIRE
  Dynamic Run, adaptive checkpoints, brownfield / monorepo friendly
  Fits uncertain boundaries, confirm-as-you-go tasks

AI-DLC
  Intent → Units → Stories → Bolts → Memory Bank → Verify → Operations
  Fits full trace, multi-person handoff, sustained recovery
```

When matching, do not mechanically look up a table—ask “which risk is most expensive.”

- If the biggest risk is unclear requirements and drifting boundaries, FIRE’s dynamic Run and adaptive checkpoints (Autopilot / Confirm / Validate style) often fit.
- If the biggest risk is multi-person handoff, cross-session amnesia, or non-recoverable release, AI-DLC’s Memory Bank, Bolt, verification, and Operations are worth it.
- If the biggest risk is simply finishing a clear small change, Simple’s short chain is usually honest.

Simple, FIRE, and AI-DLC here are governance-intensity options, not identity labels. One product can use different Flows on different tasks; one team can upgrade or downgrade in a pilot—as long as rationale and non-applicability are written down.

**Layer conclusion: Flow is a risk-hedging tool, not a team banner.**

### 2.3 Ceremony Budget: Checkpoints, Scope, and Cost

After choosing Flow, decide ceremony budget:

- **Checkpoints:** Where must work stop for confirm, verify, or approve?
- **Artifacts:** Which objects must enter the repo source of truth?
- **Runtime scope:** Delivery candidate only, or must reach Pages / Release / monitoring?
- **Review cost:** How much human attention is expected?

Budget goal is not “more is more professional”—it is “just cover key risks.” Extra checkpoints are tax; missing checkpoints are debt.

A minimal usable record:

```text
Decision Record
  Task:
  Top risks:
  Chosen flow:
  Why not the other two:
  Checkpoint budget:
  Runtime scope:
  Upgrade / downgrade trigger:
```

**Layer conclusion: the product of adaptive engineering is an explainable ceremony budget, not just picking a label.**

## 03 · Three-Part Argument: Why Method Must Be Adaptable

### Part one: One-size process creates both waste and voids

If every task runs full AI-DLC, low-risk changes waste attention; if every task is chat-style Simple, high-risk work loses trace and recovery. Uniform process looks fair; it is unfair to risk.

AI does not auto-correct that unfairness. It only makes the wrong process faster: save ceremony where you should, erase traces where you must keep them.

**Part conclusion: adaptive engineering’s first value is avoiding one ceremony set for all risk magnitudes.**

### Part two: Codebase state changes the real cost of the same method

The same “add a release gate” costs completely different effort in a greenfield small repo vs a brownfield monorepo. Brownfield amplifies hidden dependencies, test gaps, and regression surface; FIRE’s dynamic Run and adaptive checkpoints, or AI-DLC’s stronger trace, may be cheaper than a superficially simple linear flow.

Cheap is not “less documentation”—it is “fewer unknown couplings stepped on.” If the repo is not clean, pretending to run Simple usually pushes complexity to after the incident.

**Part conclusion: adaptive engineering’s second value is counting codebase reality in Flow choice, not pretending every repo is equally clean.**

### Part three: Choice must carry cost and non-applicability

Saying “we chose AI-DLC” is not engineering content. A useful choice states which risks this ceremony covers, which tasks must not use it, what the checkpoint budget is, and how to downgrade or upgrade if judgment was wrong.

Method choice without non-applicability becomes religion. Adaptive engineering requires every choice to be reviewable by the next shift—they may disagree, but they must understand.

**Part conclusion: adaptive engineering’s third value is making Flow choice a reviewable decision, not a slogan.**

## 04 · Example: Three Task Types, Flow Comparison, and Swap Test

This book’s writing system itself is a three-way comparison sample—not a lab fiction, but real risk differences in one repo.

### 4.1 Task A · Low-risk copy fix

Suppose you fix one term explanation in a chapter—no script changes, no publish chain, no Pages entry impact.

| Dimension | Judgment |
|---|---|
| Complexity | Low: local copy |
| Codebase State | Irrelevant or weak |
| Compliance | Low: no extra audit |
| Team Scale | Solo sufficient |
| Reversibility | High: easy revert |

Lean toward: **Simple**. Ceremony budget: state intent, fix copy, run internal links or related gates, submit review. Non-applicability: full Intent decomposition, multi-layer Bolts, or full Operations runbook for this task.

If Task A wears full AI-DLC, the usual result is not higher quality but ceremony tax—many artifacts prove “we are formal” without covering extra key risk.

### 4.2 Task B · Brownfield release gate change

Suppose you change `scripts/check_release_readiness.py` or the Release workflow so readiness and candidate asset sources are stricter.

| Dimension | Judgment |
|---|---|
| Complexity | Medium–high: gate logic coupled to release semantics |
| Codebase State | Brownfield: scripts, workflows, policy files interdependent |
| Compliance | Medium: affects release trust |
| Team Scale | Possible cross-session; successors must take over |
| Reversibility | Medium–low: wrong gate blocks or wrongly allows release |

Lean toward: **FIRE**, or local upgrade to **AI-DLC** on the critical path. Ceremony budget: confirm existing readiness / prepare_release boundaries, before/after comparison, failure samples, override policy, how to roll back workflow behavior. Non-applicability: one-shot big change without checkpoints, or “looks right” in chat only.

### 4.3 Task C · Multi-role writing-system sprint

Suppose you advance the ten-chapter production line, progress fact sources, cockpit, and review loop across multiple Agents / sessions.

| Dimension | Judgment |
|---|---|
| Complexity | High: chapters, tasks, experiments, events, site coupled |
| Codebase State | Evolving writing system, not a one-off script |
| Compliance | Medium–high: auditable state and release evidence |
| Team Scale | Cross-session, cross-role, cross-day |
| Reversibility | Medium: wrong state pollutes tasks / chapters / dashboard |

Lean toward: **AI-DLC**. Ceremony budget: Intent / task fact sources, chapter six stages, verification gates, progress events, Operations entry when needed. Non-applicability: state only in chat, or “model said done” as done.

### 4.4 Swap Test: Write the cost of choosing wrong

| Swap | Typical cost |
|---|---|
| Task A × AI-DLC | Ceremony tax: attention drowned in artifacts, slower delivery, risk not reduced |
| Task C × traceless Simple | Evidence void: state not handoff-ready, regressions hard to locate, release rationale unclear |
| Task B × checkpoint-free sprint | Regression debt: gate passes while sources mix or rollback path missing |

This comparison answers one key question: if the team cannot say “why this Flow, where checkpoints spend attention, when not to use it,” they have process preference—not adaptive engineering.

## 05 · Pattern: A Minimal Flow Decision Card

Readers can compress this chapter’s cases into one card:

| Field | Minimum write-up |
|---|---|
| Task | One-sentence task |
| Top 2 risks | Two most expensive risk dimensions |
| Chosen flow | Simple / FIRE / AI-DLC |
| Why this flow | Which risks it covers |
| Why not others | Explicit non-applicability |
| Checkpoint budget | Where to stop, who confirms, what |
| Runtime scope | To candidate, Pages, Release, or monitoring |
| Upgrade / downgrade | Signals to intensify or lighten ceremony |

This card can go in a PR description or task notes. It does not replace CH-07 verification intensity choice or CH-08’s run chain; it only decides “how strong a method skeleton this time.”

## 06 · Experiment: Three Verification Directions

This chapter’s experiment entries:

- **`EXP-09-01 · Simple/FIRE/AI-DLC Flow selector`:** From task complexity, codebase state, team scale, and compliance, emit Flow suggestion, rationale, and non-applicability. Run: `python3 experiments/exp-09-01/quickstart.py --sample`.
- **`EXP-09-02 · Risk-to-checkpoint budget simulator`:** From risk list, reversibility, impact scope, and autonomy preference, emit checkpoint count, placement, and cost–benefit estimate. Run: `python3 experiments/exp-09-02/quickstart.py --sample`.
- **`EXP-09-03 · Brownfield Flow selection case reproduction`:** Against a frozen pin guide, reproduce Simple, FIRE, AI-DLC three-way decision comparison. Run: `python3 experiments/exp-09-03/quickstart.py --sample`.

`EXP-09-01`, `EXP-09-02`, and `EXP-09-03` are verified. `EXP-09-01` sample at `experiments/exp-09-01/output/sample.json` shows rule-based Flow suggestions can carry rationale and non-applicability. `EXP-09-02` sample at `experiments/exp-09-02/output/sample.json` shows a risk list can translate to checkpoint count, placement, and review cost; key-risk coverage and unnecessary checkpoints can be measured. Neither proves all risks are exhausted or expert-level agreement.

`EXP-09-03` triage remains `KEEP-EXT`: sample at `experiments/exp-09-03/output/sample.json` reports `decision_rationale_coverage_percent` and `estimated_process_overhead_score`. It only shows three-way decisions reproduce on the frozen brownfield case—it does not write external guides as the sole standard or replace human Flow choice.

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-09-01` | Flow suggestion carries rationale and non-applicability | Not prove suggestion matches expert consensus |
| `EXP-09-02` | Checkpoint budget covers key risks without excess | Not prove every risk fits a budget formula |
| `EXP-09-03` | Brownfield scene can compare three Flows for decision | Not rewrite external guide reproduction as production validation; KEEP-EXT must not become SHIP |

## 07 · Figure: Risk–Ceremony Matrix

This chapter’s figure is the risk–ceremony matrix:

![Figure 9-1 · Risk–ceremony matrix](images/ch09-risk-ceremony-matrix.svg){.core-figure width=100%}

Source file: `book/images/ch09-risk-ceremony-matrix.svg`. How to read the matrix:

```text
                Low Ceremony -------- High Ceremony
High Risk       FIRE / AI-DLC         AI-DLC
Medium Risk     FIRE                  FIRE / AI-DLC
Low Risk        Simple                Simple / FIRE
```

The side lists five risk dimensions: Complexity, Codebase State, Compliance, Team Scale, Reversibility. Matrix cells are typical lean—not mandatory law; each placement should answer: why, why not, what is the checkpoint budget. The right side keeps non-applicability and upgrade / downgrade triggers.

## 08 · Boundary: What This Chapter Does Not Solve

First, this chapter does not re-open the Operations five-stage run chain. Build, Deploy, Runtime Verify, Monitor, Recover detail belongs to CH-08; here you only decide whether a task enters full runtime scope.

Second, this chapter does not discuss org role redesign, Mob cadence, or value scorecards—that is CH-10.

Third, this chapter does not frame Simple, FIRE, and AI-DLC as camps that eliminate each other. They are different governance intensities and can coexist on different tasks in one product.

Fourth, this chapter does not promise `EXP-09-01` / `EXP-09-02` prove selection or budget at expert level; `EXP-09-03` verified status only proves frozen-case decision reproduction—not replacement for human Flow choice.

Fifth, this chapter offers no auto-selection black box that replaces human judgment. The matrix organizes the question; accountability stays with people.

## Reader Exercise

Pick a real task you are doing or about to do; spend 30 minutes filling a Flow decision card.

1. One-sentence task; mark the two most expensive risk dimensions.
2. Choose one Flow among Simple, FIRE, AI-DLC; say why.
3. One sentence each: why not the other two.
4. List checkpoint budget: at least two mandatory stops, who confirms what.
5. Write runtime scope: candidate, verification, release, or monitoring.
6. Write upgrade / downgrade triggers: signals to intensify or lighten ceremony.
7. Mini Swap Test: if you chose wrong, what cost is most likely?

If you can answer “why this task gets this Flow, and when it should not,” you have moved from method preference to adaptive engineering.

## References

- `book/toc.md`: CH-09 core question, reader outcome, reference implementations, experiment directions.
- `book/part-00-overview.md`: scale-layer questions and AI-DLC Flow reference path.
- `book/chapters/ch08-operations.md`: run-chain boundary; this chapter only decides full runtime scope.
- `scripts/check_release_readiness.py`: in-repo reference for Task B–class release gate changes.
- `.github/workflows/release.yml`: release semantics and draft / override rejection reference.
- `progress/experiments.json`: governance status for `EXP-09-01`, `EXP-09-02`, `EXP-09-03`.
- `progress/chapters.json`: CH-09 six-stage production-line status.
- [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md): green/brown-field and Flow selection mapping (Part IV–V · CH-09).
- `https://specs.md/architecture/choose-flow`: external decision guide entry for `EXP-09-03`; local portal copy not in repo.
- `../../chapters/ch09-adaptive-engineering.md`: Chinese source chapter.
