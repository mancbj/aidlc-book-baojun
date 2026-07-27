# Chapter 7 · Verification: Turning Human Checkpoints into Effective Loss Functions

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-07 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D21-T03 · Complete chapter review and evidence alignment |
| Draft Completeness | Formal ten-chapter production-line readable draft; D21-T03 five-category review complete |
| Primary Question | How do you combine deterministic checks, independent tests, model review, and human judgment to prove AI-assisted results are correct—instead of treating model self-assessment as evidence? |
| Reader Outcome | Able to choose verification strength by complexity, reversibility, safety impact, and data risk, and build a layered evidence chain |
| Related Experiments | `EXP-07-01`, `EXP-07-02`, `EXP-07-03` |

## 01 · Question: Why Model Self-Assessment Is Not Delivery Evidence

Chapter 6 covered Exsecutio: how to carry AI proposals through Plan, Execute, Verify, Repair, and Walkthrough into delivery candidates. Chapter 7 drills further: **after a delivery candidate exists, how do you prove it is actually correct—not merely that the model says it is?**

That is the verification layer in AI-DLC.

In traditional development, verification is often reduced to “run tests.” After AI joins the work, that definition is too narrow. AI may produce implementations that pass local tests but violate business intent; it may also produce confident tone, complete structure, and polished explanations while key facts, edge cases, or risk calls are wrong. Model self-assessment is especially dangerous because it shares the same cognitive source as the output: one model acts as both author and judge, so “looks reasonable” is easily mistaken for “already verified.”

This risk is not code-only. In writing, AI may turn planned experiments into verified conclusions; in design, it may produce beautiful but unbuildable flowcharts; in product work, it may flatten real user constraints into template requirements. The shared problem is not “AI is useless”—it is a missing verification layer: output never enters an independent evidence chain.

So this chapter’s core question is: **how do you combine deterministic checks, independent tests, model review, and human judgment to prove AI-assisted results are correct—instead of treating model self-assessment as evidence?**

After this chapter, readers should be able to do three things:

1. Choose appropriate verification strength from complexity, reversibility, safety impact, and data risk.
2. Distinguish what deterministic checks, independent tests, model review, and human judgment each can prove.
3. Build a layered evidence chain for an AI-assisted delivery candidate—not rely on model self-assessment alone.

### Gate

- [x] One core question only: how to prove AI-assisted results are correct.
- [x] Reader outcome is observable: choose verification strength and build a layered delivery evidence chain.
- [x] This chapter does not cover deploy, monitor, and rollback; that is CH-08.
- [x] This chapter does not dismiss model review as useless; it can be auxiliary signal but cannot alone be completion evidence.

## 02 · Framework: Four-Layer Verification Evidence Chain

This chapter describes verification as four evidence layers:

```text
Deterministic Checks
  Repeatable, automatable checks with explicit exit codes

Independent Tests
  Examples, assertions, fault injection, and end-to-end checks relatively independent of the generation path

Model Review
  Structured review, risk scans, counterexample generation, and consistency checks using models

Human Judgment
  People confirm goals, risk acceptance, semantic correctness, release gates, and accountability
```

More layers are not automatically better—you match strength to risk. A low-risk, rollback-friendly Markdown fix might need fact checks, link audit, and a quick human skim; a change touching permissions, payments, healthcare, legal, or production data cannot stop at “tests passed”—it needs independent review, human approval, and post-release observation.

The keyword here is **evidence chain**. A single check answers one local question; the chain answers whether **this delivery candidate may be approved**. One check is an instrument; the chain is a pre-flight checklist. Every instrument matters, but the pilot ultimately needs to know whether the whole aircraft may take off.

### 2.1 Deterministic Checks: Let Machines Catch Definite Errors First

Deterministic checks are the first layer. They are cheap, stable, repeatable, and CI-friendly. Format lint, schema validation, type checks, unit tests, link audit, build commands, static analysis, and repo rules belong here.

They catch three error classes.

First, structural errors: invalid JSON schema, broken Markdown links, missing YAML fields, directory layout violating conventions. Second, executable errors: failing tests, failed builds, non-zero script exit codes. Third, engineering-rule errors: PR template missing fields, GitHub workflow missing gates, generator dry-run creating unexpected events.

In this book project, `python3 scripts/ci_check.py` is a deterministic gate combinator. It aggregates fact-source validation, continuity checks, GitHub config checks, unit tests, progress generation dry-run, and internal link audit. It cannot prove a chapter’s thesis is true—but it can prove a batch of engineering constraints was not broken.

**Conclusion:** Deterministic checks eliminate errors that can be judged mechanically.

### 2.2 Independent Tests: Break Self-Proof with Independent Examples

Independent tests gain value from **independence**. If AI writes an implementation and also writes tests that only cover the happy path, passing tests does not mean risk was fully exposed. Stronger practice introduces independent examples, edge cases, fault injection, regression cases, end-to-end scenarios, or counterexamples from another role or model.

Independent tests ask not “does the code run?” but “does the candidate withstand scrutiny it did not design for itself?” For writing, independence might be glossary cross-check, reader task reproduction, external fact-source alignment, or unfamiliar-reviewer Walkthrough; for software, black-box tests, contract tests, exception paths, concurrency, or migration rollback.

Independent does not require another team. It can come from different data, scripts, models, reader roles, or failure assumptions. The point is not to let the candidate face only its own preset checks.

**Conclusion:** Independent tests reduce self-proof and sample bias.

### 2.3 Model Review: Make the Model a Reviewer, Not the Chief Judge

Model review is not worthless. It can quickly scan structural gaps, terminology drift, edge cases, counterexamples, risk lists, and duplication. In writing, design, and architecture discussion, it often surfaces gaps humans have not yet noticed.

The limits are clear too: hallucination, sycophancy, overconfidence, or repeating the generator’s blind spots. Model review fits as **risk finder** and **second opinion**, not sole judge. It should output checkable issues, evidence links, and disagreement points—not a single “I think it’s fine.”

Good model review is constrained to structured output, for example:

- Technical correctness: obvious false facts or logic?
- Structural coherence: does the chapter or implementation answer one core question?
- Terminology consistency: do key terms drift?
- Evidence links: can each conclusion point to files, tests, experiments, or human records?
- Over-promising: are planned, ready, done, and released conflated?

That output is not a certificate—it is review leads. People and machines can follow the leads.

**Conclusion:** Model review widens the risk search surface but cannot replace deterministic evidence and human accountability.

### 2.4 Human Judgment: Human Checkpoints Are Accountability Boundaries

Human judgment is not for show—“human in the loop”—but because some things tests and models cannot fully own: whether the goal is still right, whether risk is acceptable, whether user semantics are met, whether release timing is appropriate, whether trade-offs match organizational accountability.

In AI-DLC, human checkpoints should be concrete. A weak checkpoint is “please confirm”; a strong one is “confirm these three risks are acceptable,” “approve upgrade from RC to v0.1,” or “decide whether this chapter may go to trial readers.” The more concrete the checkpoint, the better AI can prepare upstream evidence and the more humans focus on what truly needs judgment.

Human judgment should leave records too. Approve, reject, defer, or request rework—all should trace back to the evidence chain. Otherwise “human confirmed” becomes another unreviewable black box.

**Conclusion:** Human judgment owns goals, risk acceptance, and accountability.

## 03 · Verification Strength: Choose Strength by Risk

Verification strength is not a fixed menu—it is a function of risk. In AI-DLC, four quick questions help:

```text
Complexity
  Does the change involve complex domain concepts, cross-module coordination, or long reasoning chains?

Reversibility
  If wrong, can you roll back quickly? Is rollback cost low?

Safety / Impact
  Could errors affect real users, security, permissions, finance, law, or reputation?

Data / State
  Does it modify durable data, production state, release config, or artifacts hard to rebuild?
```

Together these yield a verification strength ladder.

| Risk level | Typical task | Minimum verification chain |
|---|---|---|
| Low | Copy tweaks, local Markdown, stateless page fixes | Deterministic checks + quick human skim |
| Medium | Chapter readable drafts, static sites, generator scripts, config changes | Deterministic checks + independent samples/links/build + structured model review |
| High | Release automation, permissions, payments, data migration, production changes | Full-path tests + fault injection/rollback verification + human approval |
| Critical | Healthcare, legal, security, finance, or irreversible decisions | Multi-party independent verification + audit records + named approver |

This table is not fear-mongering—it avoids two common mistakes.

One is over-verifying low-risk work. Running heavy review for every typo makes teams abandon the process. The other is under-verifying high-risk work. A change affecting permissions or production data supported only by model self-assessment and a few passing unit tests is like sealing a dam crack with a sticky note—it looks covered; water does not care.

The goal is attention matched to risk: low-risk passes fast, high-risk slows down, critical risks must be visible.

## 04 · Three-Part Argument: Why Verification Must Be Layered

### Part one: AI confidence amplifies unverified errors

AI output often has high fluency and structure. Unverified results look finished—especially in long prose, code, config, and process descriptions. The smoother the answer, the easier it is to skip verification.

This is not only “model hallucination”—it is collaboration psychology. Humans lower guard against complete formatting, clear headings, reasonable tone. When AI says “I already checked,” it sounds like evidence; without external checks, it is just more generated text.

**Conclusion:** Layered verification’s first value is downgrading “looks reasonable” to **hypothesis pending proof**.

### Part two: Different errors need different layers

Format, link, and schema errors suit deterministic checks; edge cases and regression risk suit independent tests; conceptual gaps and counterexamples suit model-assisted discovery; risk acceptance, semantic correctness, and release accountability require humans. No single layer covers all errors.

If everything goes to automated tests, semantics and accountability escape. If everything goes to human review, humans drown in trivial errors. If everything goes to model review, the model repackages its blind spots as new confidence.

**Conclusion:** Layered verification’s second value is **matching check mechanisms to error types**.

### Part three: Evidence chains make candidates approvable

A delivery candidate entering release or the next phase cannot rest on “tests passed” alone. It must answer: which machine checks passed? which independent cases covered? what did model review find? which risks did humans accept? which risks remain? Those answers form the chain.

The chain is not bureaucracy—it clarifies approval. When evidence scatters across chat, terminals, files, and memory, it is hard to decide release; when evidence is organized as a chain, approve, rework, or escalate is easier.

**Conclusion:** Layered verification’s third value is moving completion judgment from model self-assessment to an **approvable evidence chain**.

## 05 · Example: This Book’s CI Gate

This project already has a reusable deterministic gate combinator: `scripts/ci_check.py`. It is the existing implementation of `EXP-07-01 · Repository deterministic gate combinator`; experiment status is `ALREADY / verified` (triage remains ALREADY, not rewritten as SHIP).

The script is plain: run a fixed sequence of Must checks; any sub-check failure fails the whole run with non-zero exit. Its value is not “smart”—it is stable, repeatable, and fits PR and local delivery. `EXP-07-01` contract-tests static parsing of the gate combination; it does not re-run full CI inside the experiment.

### 5.1 What is the candidate?

Here the candidate is not one file—it is the current repo working tree: chapters, task facts, chapter facts, experiment facts, generators, site pages, GitHub config, tests, and links. After each Dxx task, the candidate must answer:

```text
Can these changes serve as trusted input for the next writing/release step?
```

That is more accurate than “no errors.” No errors is the floor; trusted input also requires consistent fact sources, working drilldown, no duplicate events, buildable chapters, and intact links.

### 5.2 Seven deterministic gate classes in `ci_check.py`

By default `ci_check.py` runs seven check classes.

| Check | Command | What it proves |
|---|---|---|
| facts | `scripts/validate_project.py` | Task, chapter, and experiment fact sources valid; dependency, status, and required-artifact rules intact |
| continuity | `scripts/validate_feedback.py` | Trial feedback and release continuity records match current conventions |
| github-config | `scripts/validate_github_config.py` | Issue, PR, Projects, Pages, Release GitHub config structures valid |
| tests | `python -m unittest discover -s tests` | Core behavior for build, generation, validation, GitHub config still meets test assertions |
| verified-experiments | `scripts/run_verified_experiments.py` | SHIP / ALREADY / KEEP-EXT experiments that are verified with contract paths reproduce |
| generation-dry-run | `scripts/generate_progress.py --dry-run --actor ci-check` | Current facts project to progress without dry-run writing disk or new history noise |
| internal-links | `scripts/check_internal_links.py` | In-repo Markdown/HTML links and fragment anchors are not broken |

Together these cover what AI edits break most often here: fact sources, auto records, page drilldown, book build, collaboration config, verified experiment contracts, and link graph. Dry-run, verified-experiments, and link audit especially catch “surface content OK but generation or evidence system broken” failures.

### 5.3 What it cannot prove

`ci_check.py` has clear boundaries.

It cannot prove a chapter’s argument is true. It cannot judge whether readers find the explanation clear. It cannot confirm cover aesthetics. It cannot replace trial-reader feedback. It cannot guarantee future GitHub network, Pages deploy, or PDF render environments forever.

So `ci_check.py` is layer one of the chain—not the whole chain. It proves **engineering constraints intact**, not **content value validated by readers**. If CI is deified, teams treat green as correct; if CI is ignored, trivial errors keep escaping.

### 5.4 How this chapter draft walks the chain

After this chapter draft, verification runs:

```text
CH-07 draft
  ↓
validate_project.py
  ↓
generate_progress.py
  ↓
ci_check.py
  ↓
events / snapshot / dashboard
```

That path matches this chapter’s claim: machines catch definite errors first; completion status lands in fact sources and the visualization cockpit. Review records then add structured model/human review to the chain.

## 06 · Model Review and Human Judgment Together

Model review and human judgment are often collapsed into “please review.” In AI-DLC, split them.

Model review suits broad early scans. It can ask many “what if” questions: terminology drift? duplicate across chapters? over-promising? missing evidence links? unstated boundaries? counterexamples?

Human judgment suits final trade-offs. It answers “do we accept”: this risk? this chapter for trial read? v0.1 release? defer this gap to v0.2?

The best relationship:

```text
Model Review finds candidates for concern.
Human Judgment accepts, rejects, escalates, or defers them.
```

Models widen search; humans own accountability. The more structured model review, the less costly human judgment; the more concrete human checkpoints, the better models prepare useful evidence.

## 07 · Experiment: Three Verification Directions

This chapter’s experiment entries:

- **`EXP-07-01 · Repository deterministic gate combinator`:** Reuse `scripts/ci_check.py`; statically parse and contract the Must gate combination. Run: `python3 experiments/exp-07-01/quickstart.py --sample`.
- **`EXP-07-02 · Independent review disagreement matrix`:** Compare delivery candidate, test evidence, independent model review, and human rubric; emit multi-party judgments and disagreement attribution matrix. Run: `python3 experiments/exp-07-02/quickstart.py --sample`.
- **`EXP-07-03 · Layered verification checkpoint reproduction`:** Against a frozen pin guide, inject defects into a sample candidate; record first discovery layer and escape counts. Run: `python3 experiments/exp-07-03/quickstart.py --sample`.

`EXP-07-01` is `ALREADY / verified`: sample at `experiments/exp-07-01/output/sample.json`. It proves `ci_check.py` Must gates can be statically parsed and stably reproduced (including passed/failed/configured counts and missing/extra comparison). Contract tests must not call `--live` or re-run full CI inside the experiment. It does not prove content quality or reader understanding is fully validated.

`EXP-07-02` is verified: sample at `experiments/exp-07-02/output/sample.json`. It proves frozen model review and human rubrics yield a disagreement attribution matrix with agreement rate, new risk count, and human override rate; model review cannot replace human judgment.

`EXP-07-03` is `KEEP-EXT / verified`: sample at `experiments/exp-07-03/output/sample.json` with `escaped_defect_count`, `first_discovery_stage`, and `verification_seconds`. Verification layers are deterministic_checks / independent_tests / model_review / human_judgment. Verify here is CH-07 delivery-candidate verification—not CH-08 Runtime Verify; frozen pin is not the only standard.

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-07-01` | Fixed gates stably aggregate repo Must checks | Not prove content quality or reader understanding fully validated; ALREADY must not be rewritten as SHIP |
| `EXP-07-02` | Where model review, test evidence, and human rubric disagree | Not prove model review replaces human judgment |
| `EXP-07-03` | First discovery layer and escapes for injected defects | Not generalize one sample to all projects’ verification cost; KEEP-EXT must not be rewritten as SHIP |

## 08 · Figure: Layered Verification Evidence Chain

This chapter’s figure is the layered verification evidence chain:

![Figure 7-1 · Layered verification evidence chain](images/ch07-verification-evidence-chain.svg){.core-figure width=100%}

Source file: `book/images/ch07-verification-evidence-chain.svg`. Structure summary:

```text
Candidate
  ↓
Deterministic Checks → Independent Tests → Model Review → Human Judgment
  ↓                         ↓                  ↓                ↓
Machine Evidence       Behavioral Evidence  Risk Findings   Approval / Rejection
```

Candidate on the left; four evidence layers horizontally; bottom converges to Release / Rework / Escalate. Verify here is delivery-candidate verification—not CH-08 Runtime Verify.

The figure should show three things:

1. Verification is a chain, not one action.
2. Automated checks, independent tests, model review, and human judgment emit different evidence types.
3. Final judgment is not only pass/fail—it may be release, rework, or escalate risk.

Do not place model review after human judgment in the figure. Model review serves human judgment—it does not stamp approval for humans.

## 09 · Boundary: What This Chapter Does Not Solve

First, this chapter does not cover Build, Deploy, Monitor, and Rollback. Those are CH-08 Operations. CH-07 ends at **whether the delivery candidate may be approved**—not **whether the system is running in production**.

Second, this chapter does not equate passing tests with correctness. Tests are part of the chain—not all of it. Semantics, risk acceptance, and accountability tests cannot cover still need other evidence.

Third, this chapter does not treat model review as model self-proof. Model review produces risk leads—not final verdicts.

Fourth, this chapter does not require maximum verification for every task. Strength should track risk: low-risk needs speed, high-risk needs stability.

Fifth, this chapter does not make human checkpoints ceremonial. If humans click approve without concrete risks, evidence, and trade-offs, “human-in-the-loop” is empty.

Sixth, `EXP-07-01` verified only proves gates aggregate and contract reproducibly; green CI does not mean chapter thesis holds or CH-08 Runtime Verify passed.

Seventh, `EXP-07-03` verified only covers defect discovery/escape on the frozen layered fixture; do not generalize one sample to all projects’ verification cost or conflate with CH-08 Runtime Verify.

## Reader Exercise

Pick a recent AI-assisted delivery candidate and design a verification evidence chain in 30 minutes.

1. Name the candidate: code, chapter, page, config, release bundle, or process decision?
2. Judge risk level: complexity, reversibility, safety impact, data/state impact?
3. Design deterministic checks: which commands, scripts, schemas, links, or builds can run automatically?
4. Design independent tests: which examples, edges, counterexamples, or unfamiliar-reviewer tasks break self-proof?
5. Design model review: structured risk list—not “looks fine.”
6. Design human judgment: who approves what, which risks accepted, how rework on reject?
7. Write one delivery judgment: Release, Rework, Escalate, or Defer.

If you can say **why this candidate may enter the next phase**—not only “AI said done”—you have this chapter’s core.

## References

- `scripts/ci_check.py`: repository deterministic gate combinator.
- `scripts/validate_project.py`: task, chapter, and experiment fact-source validation.
- `scripts/validate_feedback.py`: feedback and release continuity validation.
- `scripts/validate_github_config.py`: GitHub collaboration and release config validation.
- `scripts/check_internal_links.py`: internal link audit.
- `scripts/run_verified_experiments.py`: verified experiment contract-test entry.
- `experiments/exp-07-01/output/sample.json`: gate combination contract sample.
- `tests/test_build_book.py`: book build and source manifest assertions.
- `progress/experiments.json`: governance status for `EXP-07-01`, `EXP-07-02`, `EXP-07-03`.
- `book/toc.md`: CH-07 core question, reader outcome, and experiment directions.
- [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md): chapter-to-AI-DLC workflow map (Part III · Phases & Rituals).
- `book/images/ch07-verification-evidence-chain.svg`: layered verification evidence chain figure.
- `../../chapters/ch07-verification.md`: Chinese source chapter.
