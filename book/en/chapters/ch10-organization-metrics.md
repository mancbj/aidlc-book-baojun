# Chapter 10 · Organization and Metrics: From Agent Roles to an R&D Operating System

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-10 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D24-T03 · Complete chapter review and evidence alignment |
| Draft Completeness | Formal ten-chapter production-line readable draft; D24-T03 five-category review complete |
| Primary Question | How do you reshape people, Agents, collaboration cadence, and metrics—and judge which AI-DLC practices deserve org-scale adoption? |
| Reader Outcome | Able to design responsibility maps for Master/Inception/Construction/Operations and people, Mob collaboration cadence, and a business value scorecard |
| Related Experiments | `EXP-10-01`, `EXP-10-02`, `EXP-10-03` |

## 01 · Question: Why Flow Is Not Enough—Organization and Metrics

Chapter 9 answered method adaptation: how to choose governance intensity among Simple, FIRE, and AI-DLC by risk. Chapter 10 asks a more organizational question: **even with the right Flow, how should people and Agents divide work, collaborate, and measure—so you can tell which practices deserve scaling?**

That is the scope of “from Agent roles to an R&D operating system.”

AI-DLC is not a personal speed trick list. When multiple Agents, sessions, and roles work in parallel, unclear responsibility lets AI speed amplify buck-passing; unclear cadence evaporates context at handoffs; metrics that only count “how much was generated” reward noise over value.

Individual Exsecutio can carry a proposal to a delivery candidate; at org scale you still need a repeatable operating system: who owns what, when to sync, how to know whether a pilot should expand or stop. Here `Exsecutio` remains the defined term for follow-through—not ordinary execution.

So this chapter’s core question is: **how do you reshape people, Agents, collaboration cadence, and metrics—and judge which AI-DLC practices deserve org-scale adoption?**

After this chapter, readers should be able to do three things:

1. Draw responsibility boundaries for Master / Inception / Construction / Operations and human key decisions.
2. Design a minimal Mob collaboration cadence so elaboration and construction hand off cleanly.
3. Use a business value scorecard to judge whether a pilot deserves expansion—not output volume alone.

### Gate

- [x] One core question only: how to reshape division of labor, cadence, and metrics to support scaling.
- [x] Reader outcome is observable: design responsibility map, Mob cadence, and value scorecard.
- [x] This chapter does not re-open internal implementation of a single Flow; that is CH-03–CH-09.
- [x] All three EXP-10 experiments are currently planned; do not write them as verified conclusions.

## 02 · Framework: Responsibility, Cadence, and Value—Three Layers

This chapter describes organizational AI-DLC in three layers:

```text
Responsibility
  Decision, execution, approval, and inform boundaries for people and four Agent types

Cadence
  Mob Elaboration, Mob Construction, async review, and handoff rhythm

Value Scorecard
  Cycle time, quality, cost, reproducibility, human attention, business outcomes
```

Without the responsibility layer, Agents are only faster fingers; without cadence, the responsibility map is wall art; without a scorecard, scaling is feel-good expansion.

### 2.1 Responsibility: Four Agents and People

The four Agent types in the specs.md reference implementation provide a division skeleton:

```text
Master Agent
  Routing, context judgment, phase navigation

Inception Agent
  Turn intent into executable plan

Construction Agent
  Advance along Bolts to delivery candidate

Operations Agent
  Release, run, observe, recover
```

Agent division does not erase human responsibility. This chapter uses RACI thinking: for key activities mark Responsible, Accountable, Consulted, Informed.

| Activity | Agent may be Responsible | Human must be Accountable for |
|---|---|---|
| Route to next phase | Master may propose | Accept phase switch and priority |
| Decompose Intent / Unit / Story | Inception may draft | Goals, boundaries, definition of done |
| Execute Bolt / fix failures | Construction may advance | Risk acceptance, stop conditions |
| Release and rollback | Operations may prepare | Release consequences and recovery authorization |

One-line principle: **AI may be Responsible; humans must keep Accountable.** Models may propose; they cannot automatically be the final accountable party.

**Layer conclusion: org step one—every key decision has exactly one ultimate accountable person.**

### 2.2 Cadence: Mob and Artifact-Driven Collaboration Rhythm

Cadence answers when to sync, when to async, and what to hand off.

```text
Mob Elaboration
  Jointly clarify intent, boundaries, plan

Mob Construction
  Jointly advance or review at key gates

Artifact-driven async review
  Async review around repo artifacts, not chat logs

Handoff log
  Open issues, evidence locations, next executable step
```

Sync meetings belong only at high-leverage points: clarify intent, accept risk, approve release, post-incident review. Otherwise collaboration should orbit versioned artifacts: chapter drafts, tasks.json, review records, CI results, progress events, dashboard.

Dashboard (progress cockpit, Bird’s-Eye view, events and snapshots) is cadence’s observation surface—it does not replace responsibility but makes drift visible. If the cockpit shows ready tasks, chapter stages, and recent events, the next shift need not rebuild chat context.

**Layer conclusion: cadence’s product is handoff-ready state—not longer meetings.**

### 2.3 Value Scorecard: What Proves Scaling Is Worth It

Scaling cannot rely on “we used AI-DLC.” A minimal scorecard covers at least:

| Dimension | Signals to watch | Common false signals |
|---|---|---|
| Cycle time | Intent to reviewable candidate / publishable entry | Word count or commit count only |
| Quality | Defect escape, rework, fix loop after verification failure | CI green without content or runtime risk |
| Cost / Attention | Human review load, ceremony tax, blocked time | Treating all meetings and checks as “quality investment” |
| Reproducibility | Cross-session recovery, complete evidence, traceable sources | “I remember” in a personal notebook |
| Business result | Reader / user / business goal improvement | Internal satisfaction slogans |

Scorecard use is not new KPI theater—it supports three decisions: expand, shrink, stop. If you cannot say those three, you are not ready to scale.

**Layer conclusion: only practices that explain speed, quality, and attention cost together deserve expansion.**

### 2.4 Adopting AI-DLC: Official Guidance and This Book’s Boundary (Summary)

The AWS whitepaper **Adopting AI-DLC** describes two paths (summary; see [Amplify whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com) and [AWS DevOps blog](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/)):

1. **Learning by Practicing** — Coach in real scenarios with rituals such as Mob Elaboration and Mob Construction (AWS field offering: AI-DLC Unicorn Gym), not documentation training alone.
2. **Embedding in Developer Experience Tooling** — Embed AI-DLC in cross-SDLC orchestration so developers practice in unified DX.

This chapter’s Agent division, Mob cadence, and scorecard align with those directions, but **this book does not claim** this repo or specs.md is a mature “R&D operating system”; 30/30 experiment and KEEP-EXT boundaries still apply. Teams starting from [aidlc-workflows](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md) should land Question→Doc→Approval together with the org scorecard—not copy Agent names only. Chapter-to-workflow mapping is in [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md) (Part VI · Adopting AI-DLC · CH-10 §2.4).

## 03 · Three-Part Argument: Why the Org Layer Decides Scaling Success

### Part one: Automation without ownership creates systemic buck-passing

AI can propose, generate, and patch—it cannot automatically bear organizational consequences. If Master / Inception / Construction / Operations activities have no human Accountable, after incidents teams find “everyone participated, no one owned it.”

The higher the speed, the costlier buck-passing—errors traverse more steps faster, and responsibility gaps surface together afterward.

**Part conclusion: organizational AI-DLC’s first value embeds Agent capability in clear human accountability.**

### Part two: Without handoff cadence, context engineering fails in org seams

Memory Bank, task fact sources, and review records solve artifact-layer memory; Mob cadence solves human and cross-session seams. Miss either and the org cold-starts repeatedly—every new session re-explains “where we are, why we stopped, what’s next.”

**Part conclusion: organizational AI-DLC’s second value lets collaboration rhythm protect context—not hero memory.**

### Part three: Without a value scorecard, scaling copies waste

Promoting a locally effective prompt or process template may copy its ceremony tax and blind spots. The scorecard forces answers: did cycle shorten, quality hold, attention waste, business outcome improve?

Promotion without a scorecard is personal habit written as org policy.

**Part conclusion: organizational AI-DLC’s third value uses comparable signals to expand, shrink, or stop.**

## 04 · Example: This Book’s Writing System as Pilot

This repo’s GitHub writing system is a small, complete org pilot: division, cadence, observation surface, and explicit done / release gates. It is not an enterprise RACI manual, but enough to show how the three layers land.

### 4.1 Responsibility map: who owns what

| Activity | Responsible (may include Agent) | Accountable (human) | Key artifacts |
|---|---|---|---|
| Route next Dxx card | Master-like routing / state analysis | Author / Maintainer | `progress/tasks.json` |
| Lock chapter skeleton / readable draft | Construction-like writing | Author | `book/chapters/*.md` |
| Five-category review | Review executor / Agent assist | Author | `planning/reviews/*` |
| Validation and progress generation | Scripts and CI | Author / Maintainer | `scripts/*`, `progress/generated/` |
| Pages / Release | Operations-like workflow | Maintainer | workflows, manifest, release |

Key constraint: Agents may help write, change scripts, run checks—but closing tasks, accepting review conclusions, and releasing stay human Accountable.

### 4.2 Cadence: sprint cards, PRs, and cockpit

Minimal pilot cadence:

```text
1. Start from a ready task (single focus)
2. Complete work on an isolated branch
3. Run links / build / validate / generate_progress / ci_check
4. Submit PR for review—no auto-merge
5. Let events, snapshots, dashboard record state changes
6. Next session read fact sources first, then continue
```

This maps to Mob Elaboration (task and boundaries), Mob Construction (joint or continuous review at gates), and artifact-driven async review (PR + review + CI). Handoff log need not be a separate doc—`tasks.json`, review records, and progress events share handoff duty.

### 4.3 Scorecard seeds: whether the pilot deserves continuation

| Dimension | Observable signals in this pilot |
|---|---|
| Cycle time | Dxx card ready → done close speed |
| Quality | CI, internal links, five-category review, release readiness |
| Attention | Blocked items, rework count, large fixes without evidence |
| Reproducibility | Whether events / snapshots / source identity replay |
| Business result | Readable chapters added, reader feedback, publish entry usable |

If cycle lengthens without quality or reproducibility gain, shrink ceremony; if quality gates are routinely skipped, stop expanding—fix responsibility and cadence first.

## 05 · Pattern: A Minimal Org Operating System Checklist

| Layer | Minimum artifact | Failure signal |
|---|---|---|
| Responsibility | One-page RACI / responsibility map | No Accountable found after incident |
| Cadence | Sync point list + async artifact agreement | Every session cold-starts |
| Scorecard | Five-dimension pilot scorecard | Can only say “we used AI” |
| Observation | Dashboard / events / snapshots | State lives only in chat |
| Scale decision | Expand / shrink / stop rules | Org-wide rollout without evidence |

Use this table for small-team pilots. Large orgs can extend roles and metrics but should not drop Accountable, handoff artifacts, or stop conditions.

## 06 · Experiment: Three Verification Directions

This chapter’s experiment entries:

- **`EXP-10-01 · Human–Agent responsibility RACI generator`:** From R&D activities, four Agent types, and team roles, emit responsibility, approval, collaboration, and inform matrix. Run: `python3 experiments/exp-10-01/quickstart.py --sample`.
- **`EXP-10-02 · AI-DLC value scorecard`:** From delivery baseline, run records, defects, and business outcomes, emit cycle, quality, review load, and business value dashboard. Run: `python3 experiments/exp-10-02/quickstart.py --sample`.
- **`EXP-10-03 · Mob collaboration and Agent handoff reproduction`:** Against a frozen pin guide, reproduce Mob Elaboration, Mob Construction, and handoff log. Run: `python3 experiments/exp-10-03/quickstart.py --sample`.

`EXP-10-01`, `EXP-10-02`, and `EXP-10-03` are verified. `EXP-10-01` sample at `experiments/exp-10-01/output/sample.json` shows key activities can generate RACI and surface missing Accountable and conflicts; Accountable must be human. `EXP-10-02` sample at `experiments/exp-10-02/output/sample.json` shows baseline and run records can summarize cycle, quality, review load, and business outcome change with expand / shrink / stop suggestions. Neither proves org deployment or causal business value.

`EXP-10-03` triage remains `KEEP-EXT`: sample at `experiments/exp-10-03/output/sample.json` reports `handoff_information_loss_percent`, `decision_agreement_percent`, and `collaboration_seconds`. It only shows Mob collaboration and handoff reproduce on a frozen session—it does not write external comparison as sole standard or prove mature real-org collaboration.

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-10-01` | Key activities have Accountable and conflicts visible | Not prove generated RACI fits every org |
| `EXP-10-02` | Scorecard covers cycle, quality, attention, business outcome together | Not prove pilot business value causally |
| `EXP-10-03` | Mob and handoff log reduce information loss | Not rewrite external comparison as production validation; KEEP-EXT must not become SHIP |

## 07 · Figure: R&D Operating System Three Layers

This chapter’s figure is the R&D operating system three-layer diagram:

![Figure 10-1 · R&D operating system three layers](images/ch10-org-operating-system.svg){.core-figure width=100%}

Source file: `book/images/ch10-org-operating-system.svg`. Three layers:

```text
People & Agents  →  Responsibility (RACI)
        ↓
Collaboration    →  Cadence (Mob + async review)
        ↓
Evidence & Value →  Scorecard + Dashboard
```

The figure must show: Accountable belongs to people; Agents may be Responsible; Dashboard is observation—not responsibility; scorecard output is expand / shrink / stop—not vanity metrics. The right side keeps Scale Decision.

## 08 · Boundary: What This Chapter Does Not Solve

First, this chapter does not re-open internal implementation of a single Flow. Simple / FIRE / AI-DLC selection is CH-09; Inception, Bolt, Exsecutio, verification, and Operations mechanisms are earlier chapters.

Second, this chapter is not a full enterprise change program—only the minimal responsibility map, cadence, and scorecard set for small-team pilots.

Third, this chapter does not mythologize Dashboard as a management console. The cockpit makes state visible; it does not auto-produce correct decisions.

Fourth, this chapter does not promise `EXP-10-01` / `EXP-10-02` prove org deployment or business causality; `EXP-10-03` verified status only proves frozen Mob/handoff session reproduction—not mature real-org collaboration.

Fifth, this chapter does not outsource final accountability to the model. AI proposes; human remains accountable.

## Reader Exercise

Spend 30 minutes designing a minimal AI-DLC org operating system for your team.

1. List five key activities (e.g. topic pick, decomposition, implementation, review, release).
2. Fill R / A / C / I for each; check exactly one Accountable.
3. Design one-week rhythm: which points require Mob, which require async artifact review.
4. Write handoff minimum: which files let the next shift continue.
5. Fill five-dimension scorecard current baseline (estimates OK if labeled).
6. Write three scaling rules: when expand, shrink, stop.
7. One sentence: is this pilot Expand, Hold, Shrink, or Stop?

If you can say “who owns it, how we hand off, what justifies scaling,” you have moved from using Agents to organizational AI-DLC.

## References

- `book/toc.md`: CH-10 core question, reader outcome, reference implementations.
- `book/part-00-overview.md`: scale layer and reading path.
- `book/chapters/ch02-human-judgment.md`: four Agents and human–machine responsibility prelude.
- `book/chapters/ch06-exsecutio.md`: defined term `Exsecutio` and follow-through layer.
- `book/chapters/ch09-adaptive-engineering.md`: Flow selection boundary; this chapter does not rewrite the selection matrix.
- `progress/tasks.json` / `progress/chapters.json` / `progress/events/events.jsonl`: fact-source cadence in the org pilot.
- `site/`: progress cockpit as observation surface reference.
- `progress/experiments.json`: `EXP-10-01`, `EXP-10-02`, `EXP-10-03`.
- [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md): org-level Mob and metrics reading order; Part VI · CH-10.
- `https://specs.md/methodology/ai-dlc-vs-agile`: external comparison entry for `EXP-10-03`; local portal copy not in repo.
- [AWS AI-DLC Method Definition (Amplify)](https://prod.d13rzhkk8cj2z0.amplifyapp.com), [AWS DevOps blog](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/), [WORKING-WITH-AIDLC](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md): adoption and Mob summary.
- `../../chapters/ch10-organization-metrics.md`: Chinese source chapter.
