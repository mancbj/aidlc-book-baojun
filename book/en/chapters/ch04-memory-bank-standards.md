# Chapter 4 · Context Engineering: Memory Bank and Standards

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-04 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D18-T03 · Complete chapter review and evidence alignment |
| Draft Completeness | Formal ten-chapter production-line readable draft; D18-T03 five-category review complete |
| Primary Question | How can versioned sources of truth and explicit Standards let every fresh Agent session recover the right context and keep obeying engineering constraints? |
| Reader Outcome | Able to design a minimal Memory Bank, Standards directory, artifact references, and change-sync rules |
| Related Experiments | `EXP-04-01`、`EXP-04-02`、`EXP-04-03` |

## 01 · Question: Why AI Needs Recoverable Context

Chapter 3 answered how to break Intent into an executable plan. Once writing or development starts in earnest, a second problem appears immediately: AI sessions are fluid, but engineering facts must stay continuous.

When a human engineer returns to a project the next day, they recover context from the repo, docs, issues, tests, and recent decision records. A new Agent session needs the same entry points. The difference is that Agents have strong language capability but more fragile memory boundaries: they easily fill gaps from fragments in chat history, and they easily treat old assumptions as current facts. If a project relies only on conversational memory, it becomes harder over time to answer three basic questions.

First, what is the current goal? Continue toward v0.1 release, or has work already moved into v0.2? Without a versioned source of truth, an Agent may keep executing tasks that are already done, or skip blockers that just appeared.

Second, which files belong in the public repo and which are local working material only? In this book project, `specs.md-portal/`, `github_repo_reference_ai-agent-book-main/`, and scattered study materials are explicitly excluded from subsequent GitHub uploads. If that boundary lives only in chat, the next session may wrongly fold local reference material into public deliverables.

Third, which rules must not be “helpfully optimized away”? For example, this book’s core terminology must stay `𝓔 = Engineering with Exsecutio`; `Exsecutio` must not be auto-corrected to `Execution`. That is not spelling—it is author-defined specialized terminology. Rules like this must live in Standards, not in hope that the model guesses author intent every time.

So the core problem of context engineering is not “how to make AI remember more.” Remembering more often only amplifies noise. The real question is: **how to compress the facts, standards, and decisions the next session must inherit into engineering artifacts that can be read, validated, and updated.**

In AI-DLC, Memory Bank and Standards are the minimal answer to that question.

```text
Chat history        → unreliable recall
Versioned facts     → recoverable current state
Standards           → inheritable engineering constraints
Events & snapshots  → auditable change path
```

This chapter answers only how context is recovered and how it constrains the next execution. It does not expand how Bolts run internally, nor production deployment and monitoring; those belong to Chapters 5, 6, and 8. After this chapter, readers should be able to write a minimal Memory Bank for their own project: at least goal, state, standards, current task, evidence links, and recent decisions—and explain why those artifacts are enough for a new session to continue work.

### 1.1 Three Typical Context-Loss Failures

**Failure one: goal drift.**  
When an Agent receives “continue to the next task” without reading the source of truth, it can only guess the next step from recent chat. Guessing may suffice on short tasks, but in a two-week continuous writing system it distorts quickly. After v0.1 ships, the correct next step moves from `D14-T03` to v0.2 cycle task `C02-T01`; that must be proven by `progress/cycles.json` and `progress/generated/current.json`, not by tone of conversation.

**Failure two: boundary amnesia.**  
Real projects accumulate boundaries: which directories do not upload, which assets are reference-only, which outputs may ship, which credentials must leave traces. If boundaries are not versioned rules, AI’s “organizing power” becomes risk—it may unify, move, or publish files that merely look related.

**Failure three: standards drift.**  
Writing projects have engineering standards too. Figure style, the chapter six-phase pipeline, release Definition of Done, GitHub template fields, and “no `foreignObject` in SVG” are all standards. Standards drift is not one obvious mistake—it is a series of small “that could work too” shifts. Once those accumulate across a book or a system, readers feel stylistic chaos and maintainers lose a basis for judgment.

### 1.2 Memory Bank Is Not a Document Warehouse

Many teams first hear Memory Bank and treat it as “put all the materials in.” That is the mistake. A warehouse optimizes for collection; Memory Bank optimizes for recovery. A warehouse can be huge; Memory Bank should stay as small as possible. A warehouse answers “what did we ever have?” Memory Bank answers “how should the next session continue?”

An effective Memory Bank meets at least four conditions.

1. **Currency**: It describes current project state, not historical wishes. Done, blocked, next action, and release sources must be readable directly from fact files.
2. **Traceability**: Every state change links back to files, events, snapshots, or release receipts—avoiding “I remember we already did that.”
3. **Executability**: It records background and tells the next session what it may safely do and what it must not overstep.
4. **Convergability**: Scripts can validate it. Format, state enums, dependencies, links, and evidence paths do not depend on long-term human eyeballing.

This book project’s current minimal context is built from a few file classes: `progress/tasks.json` records fourteen-day task facts, `progress/cycles.json` records the v0.2 continuous-update cycle, `progress/chapters.json` records the ten-chapter six-phase production line, `progress/events/events.jsonl` records key changes, and `memory-bank/standards/` holds project standards. Together they form the context in which “a new session can pick up work.”

### 1.3 Standards Are Solidified Human Judgment

Standards are valuable not because they look formal, but because they put human judgment on the track early. Human judgment cannot be re-explained every time; once explanation relies on verbal add-ons, the faster AI executes, the faster deviation spreads.

This book already has several hard constraints, for example:

- The core formula must keep `𝓔 = Engineering with Exsecutio`.
- Figures default to technical-monograph grade, Swiss grid, IBM Carbon–lean restrained style.
- The public GitHub repo must not include locally crawled materials, reference repos, or working-book working material.
- Every critical update must enter events, snapshots, cockpit, or release receipts.
- Chapter progress must advance through the six phases `question / framework / example / experiment / figure / review`.

These rules look scattered, but they answer one question: when no human is watching every token, how does AI still move along human judgment?

### 1.4 Completion Criteria for This Section

After this section, readers should be able to restate three sentences:

1. Memory Bank is not “make AI remember all materials”—it lets a new session recover current state, boundaries, and next action.
2. Standards are not document decoration—they solidify human judgment into execution constraints AI must inherit.
3. The goal of context engineering is not longer context, but sources of truth that are more reliable, more checkable, and sustainably updatable.

If readers carry those three sentences into the rest of Chapter 4, they have passed the easiest misunderstanding gate in context engineering: AI-DLC does not try to lengthen chat—it hardens engineering facts.

## 02 · Framework: Minimal Recoverable Context Stack

CH-04’s framework is not “feed all materials to AI,” but design a small, hard, verifiable set of context artifacts so a brand-new session can recover current state and keep obeying human judgment and engineering standards.

This chapter uses a five-layer context stack:

```text
Current State
  Current cycle, next action, done/blocked status

Intent & Scope
  Goals, boundaries, explicit non-goals, public vs local material boundaries

Standards
  Stack, coding rules, terminology, visual style, release gates

Evidence Links
  Tasks, chapters, experiments, events, snapshots, build manifests, review records

Update Protocol
  When to update, who updates, how to validate, how to generate visible records
```

These five layers jointly answer five recovery questions for a new session:

1. Which cycle am I in, and what is the next step?
2. Which Intent does this task serve, and where are the boundaries?
3. Which rules must not be “helpfully optimized”?
4. Which evidence entries should my judgments and changes land in?
5. After I finish, how does the next session recover too?

In this framework, Memory Bank holds recoverable facts, Standards hold inheritable constraints, and events and snapshots hold the change path. Together they implement `𝓔 = Engineering with Exsecutio` at the context layer: human judgment is not only spoken—it is fixed into tracks the next AI execution must inherit.

### Gate

- [x] There is only one core question: how a new session recovers correct context and keeps obeying engineering constraints.
- [x] Reader outcomes are observable: able to design minimal Memory Bank, Standards directory, artifact references, and change-sync rules.
- [x] This chapter does not describe Memory Bank as “longer chat history” or “universal long-term memory.”
- [x] This chapter does not expand Bolt internal execution, release monitoring, or multi-Agent organizational governance.

### Question–Doc–Approval and Never Vibe Code (summary)

[WORKING-WITH-AIDLC](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md) summarizes context discipline as **Question→Doc→Approval** (clarifications written into versioned artifacts → human approval → then execute) and **Never Vibe Code** (without an approved plan or Story, codegen should not start). Stage gating also recommends **actively clearing** chat context unrelated to current artifacts at the start of a new Bolt or new phase, forcing the Agent to cold-start from Memory Bank, Standards, and `aidlc-docs/` (or this book’s `progress/`, `memory-bank/`) instead of guessing state from long conversation.

That aligns with this chapter’s five-layer stack: Memory Bank answers “what the next session inherits,” Standards answer “what must not be casually changed,” Update Protocol answers “how to write back to the source of truth after approval.” This book does not copy the workflow’s full directory layout; teams using aidlc-workflows should keep the same evidence boundary as this chapter—chat is not a delivery credential. Chapter-to-workflow mapping is in [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md).

## 03 · Three-Part Argument: Why Context Engineering Enables Continuous Delivery

### First part: chat history cannot carry engineering facts

Chat history suits conversation, not a continuous-delivery source of truth. It lacks stable structure, resists script validation, and does not naturally separate “completed facts,” “old plans,” “temporary ideas,” and “author’s final judgment.” If an Agent keeps going from chat impression alone, goal drift, boundary amnesia, and state misreads appear most easily.

Conclusion for this part: **the first value of context engineering is to pull must-inherit current facts out of chat history into versioned, checkable, traceable artifacts.**

### Second part: Standards turn human judgment into inheritable constraints

Human judgment that stays in one conversation round decays in the next execution round. Terminology must not change, directories must not upload, figure style must not drift, release status must not be manually forged—these are not preferences a model reliably “infers from smarts”; they are engineering constraints that must be written explicitly into Standards.

Conclusion for this part: **the second value of context engineering is to solidify human judgment into standards a new session must read and obey.**

### Third part: update protocol keeps context hardening, not rotting

If Memory Bank and Standards only grow without discipline, they soon become noise libraries. AI-DLC must engineer the update action itself: state changes enter fact sources, key changes enter the event ledger, phase results generate snapshots, the cockpit projects from facts, review records return to chapter evidence chains. Context does not get heavier with every delivery—it becomes more recoverable.

Conclusion for this part: **the third value of context engineering is to keep context recoverable, auditable, and executable through continuous updates.**

## 04 · Example: This Book Project’s Minimal Memory Bank

We use this book project as the example. Suppose a brand-new Agent session receives only: “Continue to the next task.” If it relies on chat impression, it may read “next task” as the most recently mentioned task, the tail of v0.1 release, or even repeat work already finished. For stable handoff, the project must translate “continue” into readable facts.

The current minimal Memory Bank splits into five entry classes:

```text
Current State
  progress/generated/current.json
  progress/tasks.json
  progress/cycles.json

Intent & Scope
  memory-bank/intents/001-github-writing-system/requirements.md
  memory-bank/story-index.md

Standards
  memory-bank/standards/coding-standards.md
  memory-bank/standards/tech-stack.md
  working-book/SVG_STYLE_GUIDE.md

Evidence Links
  progress/events/events.jsonl
  progress/snapshots/
  planning/reviews/
  .artifacts/book/build-manifest.json

Update Protocol
  validate_project.py
  generate_progress.py
  ci_check.py
```

The first class is Current State. `progress/tasks.json` tells the Agent which tasks are done, which are ready, and whether dependencies are satisfied; `progress/chapters.json` tells six-phase production-line status per chapter; `progress/generated/current.json` is the aggregate projection for cockpit and next action. Without such facts, “continue” is only guessing.

The second class is Intent & Scope. `memory-bank/intents/001-github-writing-system/requirements.md` and `memory-bank/story-index.md` tell the Agent what goal the system originally served: not merely writing a few chapters, but building a system for sustained writing on GitHub with automatic recording, visual tracking, and release. Scope also includes explicit non-goals: `specs.md-portal/`, `github_repo_reference_ai-agent-book-main/`, and `working-book/` are not uploaded as subsequent GitHub repo objects.

The third class is Standards. `memory-bank/standards/coding-standards.md` sets basic constraints on tasks, JSON, links, generated files, and tests; `memory-bank/standards/tech-stack.md` sets this project’s static stack; `working-book/SVG_STYLE_GUIDE.md` holds figure-style judgment. Together they stop AI from treating “I think that’s nice too” as project standard.

The fourth class is Evidence Links. Task completion cannot stop at “done” in prose. It should link to the event ledger, snapshots, review records, experiment outputs, and build manifests. For example, when D17-T03 closed CH-03, evidence landed in `planning/reviews/ch-03-writing-review.md`, `progress/events/events.jsonl`, `progress/snapshots/`, and cockpit drill-down objects. A new session need not trust the prior Agent’s self-report—it can follow evidence.

The fifth class is Update Protocol. `validate_project.py` checks fact sources, `generate_progress.py` generates events, snapshots, and pages from facts, `ci_check.py` chains validation into continuous-integration gates. Context is not a manually curated one-page “project blurb”—it is a set of artifacts that harden automatically after each task advance.

So a session with Memory Bank interprets “continue to the next task” like this:

```text
Read fact sources
  → find ready task
  → check dependencies and boundaries
  → change the corresponding chapter or artifact
  → update task/chapter fact sources
  → generate events, snapshots, cockpit
  → run validation and commit evidence
```

A session without Memory Bank may still produce fluent text, but it does not know whether it is on the right task. A session with Memory Bank is not merely “more memorable”—it has tracks for recovery, execution, and handoff.

## 05 · Experiment: Cold-Start Recovery A/B Check

This chapter’s evidence entry is `EXP-04-01 · Memory Bank cold-start recovery A/B experiment`. It compares two candidate first-turn actions:

- `with_memory_bank`: read versioned facts, cycle, chapters, standards, and exclusion boundaries, then act.
- `without_memory_bank`: act from chat impression and vague project background only.

Current sample output shows:

| Group | Context Recovery | First Action Error | Clarification Questions |
|---|---:|---:|---:|
| with_memory_bank | 100.0% | false | 0 |
| without_memory_bank | 0.0% | true | 3 |

From repo root:

```bash
python3 experiments/exp-04-01/quickstart.py --sample
```

Output is at `experiments/exp-04-01/output/sample.json`. The experiment uses Python standard library only—no network, no model calls. It checks five things: current cycle, next action, evidence paths, excluded directories, and specialized terminology recovery.

These results do not prove every project gets the same numbers, nor that AI truly understood business semantics. They support a narrower, more reliable claim: **when key context is written as versioned facts and Standards, new sessions recover correct action boundaries more easily; when context lives only in chat impression, first-action errors and terminology drift appear more easily.**

That is exactly where AI-DLC needs experiments. We do not require proof that “Memory Bank always works”—only an observable difference on the table: the same phrase “continue to the next task” can yield very different recovery quality with or without engineered context.

### `EXP-04-02` · Standards drift detector

`EXP-04-02` checks rule violations and version gaps between versioned Standards and generated artifacts. Run:

```bash
python3 experiments/exp-04-02/quickstart.py --sample
```

Output is at `experiments/exp-04-02/output/sample.json`. It only shows declared rules can be compared deterministically; it does not prove those rules apply to every repo. Without human baseline labels, false-positive rate is recorded as `null`—it must not be dressed up as already low.

### `EXP-04-03` · Official Memory Bank structure reproduction (KEEP-EXT)

`EXP-04-03` is verified, but triage remains `KEEP-EXT`: it only validates minimal Memory Bank required paths and reference validity against a frozen pin fixture in the repo—it does not fetch external specs.md pages in CI. Run:

```bash
python3 experiments/exp-04-03/quickstart.py --sample
```

Output is at `experiments/exp-04-03/output/sample.json`. The sample reports `required_file_completeness_percent` and `reference_validity_percent`; it shows frozen structure loads reproducibly, does not write specs.md as the sole standard, and does not prove arbitrary projects’ Memory Bank semantics are already correct.

## 06 · Figure: New-Session Cold-Start Recovery Stack

This chapter’s figure is the “new-session cold-start recovery stack”:

![Figure 4-1 · Memory Bank recovery stack](images/ch04-memory-bank-stack.svg){.core-figure width=100%}

Source file: `book/images/ch04-memory-bank-stack.svg`. Structure summary:

```text
New Agent Session
  ↓
Read Current State + Intent + Standards + Evidence
  ↓
Derive Next Safe Action
  ↓
Execute and Update Facts
  ↓
Events / Snapshots / Dashboard
  ↺
Next Session Recovers from Updated Facts
```

The figure emphasizes a closed loop, not a folder of files. A new session first reads Current State, Intent & Scope, Standards, and Evidence Links, derives the next safe action, then after execution must write changes back through Update Protocol to fact sources and trigger Events, Snapshots, and Dashboard. The next session recovers from updated facts.

The figure should carry at least three visual weight levels:

1. Primary: main flow `New Session → Next Safe Action → Updated Facts`.
2. Secondary: four input classes—Current State, Intent & Scope, Standards, Evidence Links.
3. Tertiary: audit outputs such as Events, Snapshots, Dashboard.

Do not read Memory Bank as an ordinary document warehouse: the recovery stack’s value is “how the next session continues safely.”

## 07 · Boundary: What This Chapter Does Not Solve

To keep Memory Bank from becoming a basket for everything, this chapter draws clear boundaries.

First, this chapter does not discuss “unlimited long-term memory.” AI-DLC cares about engineering recovery, not saving every conversation, asset, and preference in the model. Long-term memory without structure, validation, and update rules only preserves old assumptions longer.

Second, this chapter does not replace Bolt execution mechanics in Chapters 5 and 6. Memory Bank tells the Agent current state and constraints; Bolt decides how an execution batch is designed, implemented, tested, and accepted. Correct context does not imply correct execution.

Third, this chapter does not replace Operations in Chapter 8. Events, snapshots, and cockpit support traceability before and after release, but deployment verification, monitoring, and recovery strategy need separate treatment.

Fourth, this chapter does not require every team to copy this book’s directories. Copy the principles: version current state, standardize human judgment, trace evidence paths, automate validation in update protocol. Concrete filenames may differ; the four commitments cannot.

Fifth, `EXP-04-03` verified status covers structure and reference checks on the frozen pin fixture only; do not write KEEP-EXT reproduction as full official spec landed in production, and do not recast it as SHIP.

## Reader Exercise

Choose one of your own projects and spend 20 minutes designing a minimal Memory Bank of at most six files.

1. Write a `current-state` file: current cycle, next action, done/blocked status.
2. Write an `intent-and-scope` file: goals, boundaries, and explicit non-goals.
3. Write a `standards` file: five rules AI must not “helpfully optimize.”
4. Write an `evidence-index` file: entries for tasks, experiments, reviews, release, or build evidence.
5. Write an `update-protocol` file: which fact sources must update after task completion.
6. Delete one unnecessary file so Memory Bank stays a recovery stack, not a warehouse.

Then test in one sentence: let a session that knows nothing about the project read only this file set and answer “What is the next safe action?” If it still needs heavy guessing, your Memory Bank is not too small—it is not hard enough yet.

## References

- `progress/cycles.json`: v0.2 active cycle and next-action source.
- `progress/generated/current.json`: current progress aggregate and cockpit data.
- `progress/chapters.json`: ten-chapter six-phase production-line fact source.
- `memory-bank/standards/coding-standards.md` and `memory-bank/standards/tech-stack.md`: current project Standards entries.
- `planning/releases/v0.2-draft.md`: v0.2 continuous-update cycle draft.
- `experiments/exp-04-01/README.md`: Memory Bank cold-start recovery A/B experiment description.
- `experiments/exp-04-01/output/sample.json`: reproducible experiment output generated for C02-T02.
- `experiments/exp-04-03/README.md`: official Memory Bank structure reproduction (KEEP-EXT / frozen pin) description.
- `experiments/exp-04-03/output/sample.json`: frozen pin structure and reference validation sample.
- `progress/experiments.json`: governance status for `EXP-04-01`, `EXP-04-02`, `EXP-04-03`.
- `planning/reviews/ch-04-writing-review.md`: formal ten-chapter production-line CH-04 five-category review record.
- [WORKING-WITH-AIDLC](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md), [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md): Question→Doc→Approval and Never Vibe Code.
