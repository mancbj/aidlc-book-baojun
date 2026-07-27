# Chapter 5 · Bolts: Choosing the Right Track for Fast Execution

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-05 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D19-T03 · Complete chapter review and evidence alignment |
| Draft Completeness | Formal ten-chapter production-line readable draft; D19-T03 five-category review complete |
| Primary Question | How do you choose Bolt scope, type, and stage gates from domain complexity, risk, and reversibility so speed rises without errors cascading? |
| Reader Outcome | Able to split hour-to-day Bolts and make a justified choice between DDD Construction and Simple Construction |
| Related Experiments | `EXP-05-01`、`EXP-05-02`、`EXP-05-03` |

## 01 · Question: Why Fast Execution Still Needs a Track

Chapter 3 covered Inception: decomposing Intent into Requirements, Units, Stories, and a Bolt Plan. Chapter 4 covered context engineering: letting a new session recover current facts from the Memory Bank and Standards. In Chapter 5 the question becomes: **after context is restored correctly, how do you slice work into execution batches that are fast enough yet keep mistakes from cascading?**

AI-DLC calls these execution batches **Bolts**. A Bolt is not a generic task and not a shrunken traditional Sprint. Generic tasks often say only “what to do”; Sprints often carry one-to-two-week planning, coordination, and scheduling; a Bolt is closer to an hour-to-several-day engineering track. It must have clear scope, inputs, outputs, stage gates, acceptance criteria, and completion evidence.

If a Bolt is cut too large, AI accumulates assumptions across a long execution chain and errors spread from design into implementation, tests, and docs. By the time humans see the wrong direction, the fix is not one code change—it is unwinding a chain of interdependent artifacts. If a Bolt is cut too small, the system devolves into fragmented prompts: more context switching, design that never settles, and verification cost that rises instead of falls.

So this chapter’s core question is: **how do you choose Bolt scope, type, and stage gates from domain complexity, risk, and reversibility so speed rises without errors cascading?**

After this chapter, readers should be able to do three things:

1. Split a Story into hour-to-day Bolts.
2. Judge whether it fits Simple Construction or DDD Construction better.
3. Design minimal stage gates so AI can move fast but cannot cross risk points without evidence.

### Gate

- [x] There is only one core question: how to choose Bolt scope, type, and stage gates.
- [x] Reader outcomes are observable: able to split hour-to-day Bolts and choose between DDD and Simple with justification.
- [x] This chapter does not expand full execution logs or Walkthrough; that is Chapter 6’s focus.
- [x] This chapter does not describe Bolts as traditional Sprints, generic tasks, or unbounded autonomous Agents.

## 02 · Framework: Four Design Knobs for a Bolt

This chapter describes a Bolt with four design knobs:

```text
Scope
  How much Story surface, files, and risk should one Bolt cover?

Type
  Simple Construction or DDD Construction?

Gates
  Which stages must stop for verification, recording, or human confirmation?

Evidence
  What artifacts prove the Bolt can close and hand off to the next stage?
```

### 2.1 Scope: Slice Until Errors Are Reversible

Bolt scope is not “as small as possible.” It should be small enough that errors are reversible and large enough to form a deliverable increment. A good Bolt usually has three boundaries:

- **Input boundary:** which Stories, Requirements, Standards, or fact sources it starts from.
- **Change boundary:** which files, directories, interfaces, or content it may modify.
- **Done boundary:** which evidence means stop—not “while we’re here, optimize.”

These boundaries give AI speed a container. Without a container, speed becomes diffusion; with one, speed becomes progress.

### 2.2 Type: Choosing Simple vs DDD

Not every Bolt needs full DDD. For low domain complexity, low uncertainty, low risk, and fast rollback, **Simple Construction** is enough: Plan → Implement → Test. Updating progress projections, adding a page drill-down, or generating a chapter skeleton usually does not need heavy design.

When work touches domain models, cross-module dependencies, irreversible migrations, security boundaries, complex state machines, or long-term maintenance cost, consider **DDD Construction**. It typically runs Model → Design → ADR → Implement → Test, front-loading key concepts, relationships, and trade-offs.

A plain decision line:

```text
If failure is mostly local implementation error, use Simple.
If failure comes from conceptual modeling, boundary choice, or cross-object collaboration, use DDD.
```

### 2.3 Gates: Stage Gates Contain Cascading Errors

Bolt gates are not there to slow AI down; they expose errors locally. A Simple Bolt needs at least three visible stages—Plan, Implement, Test; a DDD Bolt must surface domain model and architecture trade-offs earlier. What matters is not stage names but inspectable evidence at each stage.

Example: a Bolt to “implement task status progression.” Without a Test gate, AI may jump status from `backlog` to `done` without generating events, snapshots, or cockpit updates. If the gate requires “fact-source validation passes, events emitted, drill-down pages updated, CI green,” errors surface before delivery.

### 2.4 Evidence: Closing a Bolt Must Leave a Trail

“Done” cannot be a chat sentence alone. At minimum, four evidence classes:

- **Plan evidence:** why this slice, dependencies, and scope boundaries.
- **Implementation evidence:** which files changed and why.
- **Verification evidence:** tests, link checks, builds, failure samples, or human review.
- **Handoff evidence:** what is next, which risks were accepted, which gaps remain for later Bolts.

Evidence lets a Bolt be closed and recovered. Completion without evidence is optimistic narration.

### 2.5 Bolt vs Sprint: AWS Official Naming (Summary)

AWS AI-DLC renames the traditional Scrum **Sprint** as **Bolt**, emphasizing hour-to-day, high-intensity, parallelizable iteration units rather than four-to-six-week cycles (see [Method Definition whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com)). A Unit may complete in one or more Bolts, sequential or parallel; AI plans Bolts; developers and the PO validate. This book uses the same terms; Chapter 6 describes **Exsecutio** as the execution loop inside a Bolt—**Bolt is the scope and gate unit; Exsecutio is execution dynamics.**

Chapter-to-workflow mapping for Bolts appears in [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md) (Part III · Artefacts).

## 03 · Three-Part Argument: Why Bolt Is the Engineering Unit of Speed

### Part one: AI speed needs batch boundaries

AI can generate many options, files, and tests quickly, but real delivery cannot mix all outputs in one execution stream. Larger scope means more hidden assumptions; longer chains mean later error discovery. Hour-to-day Bolts confine fast execution to a range that is understandable, verifiable, and rollback-friendly.

**Conclusion:** Bolt’s first value is packaging AI generation speed into error-reversible engineering batches.

### Part two: Different risks need different execution types

“Build a feature” can mean a local page or copy change, or a shift in domain model, data consistency, and long-term architecture. If everything runs Simple, complexity is underestimated; if everything runs DDD, small work is over-engineered. Choosing Bolt type matches execution flow to risk shape.

**Conclusion:** Bolt’s second value is picking the right execution track from complexity, risk, and reversibility.

### Part three: Gates and evidence make Bolts handoff-ready

AI-DLC continuity comes from handoff. Without stage records, test results, failure fixes, and completion receipts, the next session can only trust the last narrative. Gates and evidence make a Bolt auditable: why it started, how it progressed, why it may end, where the next Bolt attaches.

**Conclusion:** Bolt’s third value is turning execution from a one-off session into a recoverable, auditable, continuable delivery unit.

## 04 · Example: Four Bolts in This Book Project

We use four completed Bolts from this book project. All belong to Unit `001-github-writing-system-ui`, but each differs in scope, dependencies, and risk surface.

```text
Bolt 001
  Repository fact source, task model, chapter templates, experiment governance

Bolt 002
  Progress aggregation, event log, snapshots, cockpit rendering

Bolt 003
  GitHub templates, PR checks, Pages, Release, Projects

Bolt 004
  Sample-chapter review, trial-read feedback, v0.1 release, next-cycle entry
```

All four chose **Simple Construction**—not because the project is unimportant, but because domain complexity per Bolt was controlled, inputs and outputs were clear, failure was rollback-friendly, and most risk could surface via fact-source validation, link checks, build, and CI.

One giant Bolt mixing all four would look efficient but cascade risk: cockpit numbers lack a trusted source while the task model is unstable; GitHub Actions and Pages may publish around wrong facts before the local system is verified; release gates become formalities before sample chapters are reviewed.

Splitting into dozens of fragment prompts causes another failure mode: each prompt is tiny, but the system loses batch sense. AI might add a JSON field today, edit a page tomorrow, add a test the day after—with no delivery boundary stating what the set accomplishes together. Fragments feel controlled but hand off poorly.

Order across the four Bolts controls risk propagation.

**Bolt 001** establishes repository fact source, task model, chapter templates, and experiment governance. It answers “where does all later state come from?” Without it, any progress page is manual copy.

**Bolt 002** aggregates progress, records events, snapshots, and cockpit—after the fact source is stable. It answers “how do critical updates visualize automatically?” Running it before Bolt 001 puts pages before facts.

**Bolt 003** wires GitHub templates, PR validation, Pages, Release, and Projects after the local system is verifiable. It answers “how do collaboration and release attach to the fact source?” Early GitHub wiring amplifies unstable state remotely.

**Bolt 004** closes sample-chapter review, trial-read feedback, v0.1 release, and next-cycle entry. It answers “how does the system form a public, recoverable, continuable loop?” Without the first three Bolts, release devolves into manual checklists that are hard to reproduce.

The case shows Bolt value is not listing tasks—it is slicing risk in verifiable order. The right Bolt is neither “everything at once” nor “so fragmented it loses meaning,” but a batch where AI delivers a real increment and leaves enough evidence for the next batch.

### 4.1 Why Simple Was Enough

The first four Bolts all used Simple Construction. Four dimensions justify that:

| Dimension | Situation | Conclusion |
|---|---|---|
| Domain complexity | Writing system, fact source, static pages, GitHub workflow | No full domain modeling required |
| Reversibility | Markdown, JSON, HTML, YAML recoverable via Git | Lighter process is acceptable |
| Verification | Validation scripts, link checks, build, CI cover critical paths | Test gates expose most errors |
| Cross-boundary risk | No real user data migration or production database | No ADR-level architecture gate |

If the same project later handled paid reader data, collaborator permissions, automatic Issue sync writes, release rollback, and multi-repo dependencies, the judgment would change. Errors would no longer be page or Markdown mistakes—they could touch permissions, consistency, and long-term architecture, and DDD Construction would fit better.

## 05 · Experiment: Three Verification Directions for Bolt Choice

This chapter’s experiment entry points:

- **`EXP-05-01 · Bolt size estimator`:** From Stories, complexity, risk, and dependencies, produce Bolt scope, duration estimate, and split suggestions. Run: `python3 experiments/exp-05-01/quickstart.py --sample`.
- **`EXP-05-02 · DDD vs Simple Bolt selector`:** From task description, domain complexity, risk, and reversibility, suggest Bolt type with rationale. Run: `python3 experiments/exp-05-02/quickstart.py --sample`.
- **`EXP-05-03 · Official Bolt type checkpoint reproduction`:** Against the repo’s frozen Bolt type guide fixture, reproduce DDD and Simple stage records. Run: `python3 experiments/exp-05-03/quickstart.py --sample`.

`EXP-05-01`, `EXP-05-02`, and `EXP-05-03` are **verified**. Sample for `EXP-05-01` at `experiments/exp-05-01/output/sample.json` shows Story complexity, risk, and dependencies convert to scope, estimates, and split suggestions; duration error vs baseline when present, otherwise `null`. Sample for `EXP-05-02` at `experiments/exp-05-02/output/sample.json` shows rule-based Simple/DDD suggestions with rationale and gray-zone split/gate hints; agreement and over/under-engineering counts when expert labels exist. Neither replaces human judgment.

`EXP-05-03` triage remains **`KEEP-EXT`**: sample at `experiments/exp-05-03/output/sample.json` reports `stage_completeness_percent` and `checkpoint_adherence_percent` for Simple and DDD tracks. It only proves stage/checkpoint reconciliation on the frozen guide fixture—not that external specs.md pages are the sole standard—and does not replace human Bolt type choice.

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-05-01` | Whether scope, estimates, and overflow splits reproduce | That every project estimates hours accurately |
| `EXP-05-02` | Whether Simple / DDD choice aligns with expert judgment | That the selector replaces human judgment |
| `EXP-05-03` | Whether stages/checkpoints on the frozen pin guide reproduce | External reference as this book’s only standard; KEEP-EXT must not be rewritten as SHIP |

Together these experiments serve one question: Bolts should be explainable from complexity, risk, dependencies, reversibility, and verification cost—not gut feel.

## 06 · Figure: Bolt Selection Matrix

This chapter’s figure is the **Bolt selection matrix**:

![Figure 5-1 · Bolt selection matrix](images/ch05-bolt-selection-matrix.svg){.core-figure width=100%}

Source file: `book/images/ch05-bolt-selection-matrix.svg`. How to read the matrix:

```text
Low Complexity / Low Risk / Reversible
  → Simple Construction
  → Plan → Implement → Test

High Domain Complexity / Cross-boundary Risk / Hard to Reverse
  → DDD Construction
  → Model → Design → ADR → Implement → Test
```

Horizontal axis: domain complexity. Vertical axis: risk / irreversibility. Lower-left: Simple. Upper-right: DDD. Middle band: “split the Bolt or add gates.”

The figure is for choice, not decoration. Lower-left tasks usually fit Simple; upper-right fit DDD; gray zone means do not guess—split the Bolt or add gates to a Simple Bolt.

Treat the gray band as a reminder:

```text
If you cannot choose Simple or DDD,
first ask: can the high-risk part become its own Bolt?
If not, which gate must you add?
```

Adding a cockpit metric might be Simple; changing task state model, event semantics, and release gates is no longer “just a page.” Split into two Bolts: change and validate the fact-source model, then update the UI.

## 07 · Boundary: What This Chapter Does Not Solve

First, this chapter does not teach full Bolt runtime. Chapter 6 expands **Exsecutio**: how AI advances through plan, execution, verification, correction, and Walkthrough to a delivery candidate.

Second, DDD is not “advanced” and Simple is not “junior.” They are tracks for different risk shapes. Both over-engineering and under-engineering are errors.

Third, sizing is not precise prediction. Bolt size estimation makes risk visible—it does not guarantee hour-accurate completion.

Fourth, AI must not unilaterally set every gate. AI may propose gates; humans still confirm domain complexity, risk appetite, and irreversibility.

Fifth, `EXP-05-03` verified status covers only the in-repo frozen guide fixture. Do not write KEEP-EXT reproduction as full official Bolt type deployment, or pretend it validates a live external fetch.

## Reader Exercise

Pick one of your Stories and spend 20 minutes designing two Bolt options.

1. Write the Story goal and acceptance.
2. Write one **Simple Bolt**: Plan, Implement, Test only.
3. Write one **DDD Bolt**: Model, Design, ADR, Implement, Test.
4. For each option, list Scope, Type, Gates, Evidence.
5. Mark the most likely failure points: implementation detail, domain model, cross-module dependency, data risk, or release risk.
6. Choose one option and write one sentence of rationale.

If you can explain why this Story does not need DDD—or why it must use DDD—you are turning speed choice into engineering judgment.

## References

- `memory-bank/bolts/001-github-writing-system-ui/bolt.md`: fact source and templates Bolt.
- `memory-bank/bolts/002-github-writing-system-ui/bolt.md`: progress aggregation, events, snapshots, cockpit Bolt.
- `memory-bank/bolts/003-github-writing-system-ui/bolt.md`: GitHub collaboration and release automation Bolt.
- `memory-bank/bolts/004-github-writing-system-ui/bolt.md`: sample review, feedback, v0.1 release, next-cycle Bolt.
- `progress/experiments.json`: governance for `EXP-05-01`, `EXP-05-02`, `EXP-05-03`.
- `book/toc.md`: CH-05 core question, reader outcome, experiment direction.
- `planning/reviews/ch-05-writing-review.md`: formal ten-chapter CH-05 five-category review record.
- [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md): chapter-to-AI-DLC workflow map (Part III · Artefacts / CH-05).
- [AWS AI-DLC Method Definition (Amplify)](https://prod.d13rzhkk8cj2z0.amplifyapp.com): Bolt vs Sprint official naming summary.
