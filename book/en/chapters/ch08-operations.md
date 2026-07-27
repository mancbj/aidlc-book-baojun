# Chapter 8 · Operations: From Delivery Candidate to Sustainable Runtime

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-08 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D22-T03 · Complete chapter review and evidence alignment |
| Draft Completeness | Formal ten-chapter production-line readable draft; D22-T03 five-category review complete |
| Primary Question | How do Build, Deploy, Runtime Verify, Monitor, and recovery mechanisms turn a tested candidate into a runnable, observable, rollback-ready system? |
| Reader Outcome | Able to define build credentials, environment gates, deploy strategy, smoke verification, monitoring signals, and rollback runbooks |
| Related Experiments | `EXP-08-01`, `EXP-08-02`, `EXP-08-03` |

## 01 · Question: Why “Tests Passed” Is Not Runtime Success

Chapter 7 answered verification: how to combine deterministic checks, independent tests, model review, and human judgment so AI-assisted delivery candidates are not model self-assessment hallucinations. Chapter 8 moves forward: **after a candidate passes verification, how do you make it a runnable, observable, rollback-ready system?**

That is the scope of Operations.

In AI-DLC, Operations is not “ship it at the end” or copying test-passed files somewhere. It is a set of runtime responsibilities: builds must be traceable, deploys must have environment gates, verification must match real runtime conditions, monitoring must detect drift, and recovery must be prepared before incidents.

Without Operations, teams err in two places.

First, they mistake delivery candidates for running systems. A candidate may pass CI, link audit, and human review—but it is not yet packaged, deployed, smoke-verified, and monitored. Second, they mistake release success for sustained success. Pages open, services start, versions exist—that only means a moment in time; sustained runtime still depends on monitoring, alerts, rollback, and recovery.

With AI, the problem sharpens. AI can quickly draft release notes, generate deploy config, and fix failed scripts—and just as quickly widen blast radius of a bad release. Without Operations boundaries, AI speed makes “go live” feel trivial; a real running system is not the phrase “released”—it is a traceable, observable, recoverable accountability chain.

So this chapter’s core question is: **how do Build, Deploy, Runtime Verify, Monitor, and recovery mechanisms turn a tested candidate into a runnable, observable, rollback-ready system?**

After this chapter, readers should be able to do three things:

1. Define source manifest, build credentials, and file hashes for a release candidate.
2. Define environment gates, deploy strategy, smoke verification, and monitoring signals for deployment.
3. Prepare rollback runbooks for failure scenarios and write recovery into reviewable records.

### Gate

- [x] One core question only: how to move verified candidates into sustainable runtime.
- [x] Reader outcome is observable: define build credentials, environment gates, deploy strategy, smoke verification, monitoring signals, and rollback runbooks.
- [x] This chapter does not re-debate verification strength; that is CH-07.
- [x] This chapter does not portray current Operations tooling as mature production capability; reference implementations in-repo remain alpha / planned boundaries.

## 02 · Framework: Five-Stage Operations Chain

This chapter describes Operations as five stages:

```text
Build
  From verified sources, produce traceable, reproducible, hash-tagged candidate assets

Deploy
  Publish candidate assets to a defined environment; record environment, permissions, version, and strategy

Runtime Verify
  In target environment: smoke checks, entry validation, release manifest cross-check, regression gates

Monitor
  Watch key metrics, error signals, user entry points, alerts, and drift

Recover
  On failure, follow runbooks to rollback, degrade, restore data, or pause release
```

This chain differs from CH-07’s verification chain. CH-07 asks **whether the candidate may be approved**; CH-08 asks **whether an approved candidate can enter runtime and be observed and recovered there**. Verification supplies correctness evidence; Operations supplies runtime accountability.

One-line distinction:

```text
CH-07 Verify: Should this candidate be approved?
CH-08 Operations: Can this approved candidate run, be observed, and be recovered?
```

That distinction matters. Many AI-assisted teams treat green CI as “already live successfully” or GitHub Release creation as “users can use it.” The first conflates verification and runtime; the second conflates deploy action and runtime state. Operations separates both confusions.

### 2.1 Build: Build Must Answer “Where From?”

Build’s first duty is traceable sources. A releasable asset should record at least: source commit, fact-source identity, build time, input files, output file hashes, and whether unreviewed state was mixed in.

Build is not “zip some files.” It answers three questions.

- **Source:** Which commit, fact set, and readiness produced these assets?
- **Process:** Which script, environment, and workflow constructed them?
- **Output:** Which files were produced, with what hash and size?

In this book project, `scripts/prepare_release.py` and `scripts/prepare_pages.py` embody this. Pages publish trees record source facts, commit, generated_at, workflow_run, and file hashes; Release candidates emit `release-manifest.json` with HTML zip, PDF status, release notes, and readiness provenance.

This is unromantic but important. When something goes wrong, teams need not guess: “Which commit is this page from?” “Which readiness backed this Release?” “Is the PDF a real PDF or a renamed placeholder?” Build credentials answer early.

**Conclusion:** Build is not packaging—it is **provenance proof**.

### 2.2 Deploy: Deploy Must Answer “Where To?”

Deploy is not pressing publish—it is defining target environment and strategy. GitHub Pages, GitHub Release, staging, and production carry different risk. Target environment, permissions, concurrency, overwrite policy, draft vs live, and human approval should be recorded.

This project’s `.github/workflows/pages.yml` and `.github/workflows/release.yml` encode two deploy semantics: Pages as continuous reader entry; Release as version candidate and draft publish entry. The former cares that pages are reachable; the latter that version assets are not confused.

Deploy fails most when environment is treated as wallpaper. Environment changes risk. A page deploy to local `.artifacts/` has small blast radius; to GitHub Pages it affects reader entry; a draft Release stays inside human review; a formal Release enters public version history.

Deploy strategy should state at least:

- **Environment:** local, preview, staging, production, or draft release?
- **Permission:** who triggers, who approves, which tokens or GitHub permissions?
- **Concurrency:** how concurrent publishes are handled; cancel in-flight jobs?
- **Overwrite:** may existing versions or unmarked directories be overwritten?
- **Roll-forward / Rollback:** on failure, fix forward or rollback to last stable?

**Conclusion:** Deploy is not copying files—it is placing the candidate in a **bounded environment**.

### 2.3 Runtime Verify: Target Environment Needs Another Pass

CH-07 verification happens before the candidate enters Operations; Operations **Runtime Verify** happens after deploy. Do not conflate them. Passing tests locally does not rule out config, path, permission, cache, or asset gaps in target environment.

Runtime Verify should hit real entry points. For Pages: entry page, cockpit, drilldown links, publish manifest; for Release: version, asset hashes, release notes, readiness source, draft state.

Keep runtime verification small and sharp—not re-run the full test suite—but confirm **after deploy to this environment, do the critical entry points actually work?**

```text
Pages
  index.html reachable
  site/index.html reachable
  publish-manifest.json exists
  source commit matches expectation

Release
  release-manifest.json exists
  release notes non-empty
  HTML zip hash matches manifest
  if PDF exists, real PDF—not placeholder file
```

**Conclusion:** Runtime Verify proves the candidate is **usable in target environment**.

### 2.4 Monitor: After Release, See Drift

Release success is an instant. In runtime, problems may appear late: broken paths, assets not loading, readers cannot find entry, misleading release notes, metric anomalies, rising errors, ignored feedback intake.

Monitor is not “collect everything”—pick signals that represent runtime health. For this book project, start light: Pages workflow success, Release artifact presence, progress cockpit updates, feedback entry availability, new trial-reader blockers.

For typical software: error rate, latency, throughput, resource use, business conversion, anomaly logs, alert firing, user feedback. Metrics matter when they answer **is the system still running toward the release goal?**

A practical Monitor design has three layers:

- **Technical signals:** build, deploy, HTTP, errors, latency, resources.
- **Product signals:** entry traffic, key-path completion, user feedback.
- **Governance signals:** blockers, human approvals, rollback records, known gaps.

**Conclusion:** Monitor turns release from one action into **ongoing observation**.

### 2.5 Recover: Write Recovery Before Failure

Recover is not improvisation after an incident. Runbooks should exist before release: how to rollback version, pull wrong pages, regenerate candidates, restore last snapshot, notify readers, mark known gaps, pause further spread.

With AI in Operations, recovery boundaries matter especially. AI can fix fast—and widen errors fast. Recover adds order and limits so teams under pressure still take definite actions.

Minimum runbook table:

| Item | Question to answer |
|---|---|
| Trigger | What signal requires recovery? |
| Owner | Who decides and executes? |
| Scope | Roll back page, Release, config, data, or all? |
| Steps | Exact commands, entry points, or manual actions? |
| Verification | How to prove state healthy after recovery? |
| Communication | Who to notify; how to record? |

**Conclusion:** Recover turns failure from panic into **executable process**.

## 03 · Three-Part Argument: Why Operations Closes Delivery

### Part one: Verified candidates lack runtime identity

Tests passed, review passed, CI passed—the candidate may enter the next phase—but it has no **runtime identity** yet. Identity comes from build manifest, target environment, deploy record, publish entry, and traceable assets.

Without runtime identity, teams struggle to answer: **what is actually running online now?** In AI collaboration, multiple sessions may produce multiple candidates, pages, and Release drafts. Without manifest and source identity, candidates look like similar shadows.

**Conclusion:** Operations’ first value is giving delivery candidates **traceable runtime identity**.

### Part two: Runtime risk differs from pre-build risk

Pre-build risk is mostly content, code, config, and evidence chain; runtime risk comes from environment, permissions, network, cache, user paths, version overwrite, monitoring blind spots, and missing recovery. Mixing the two makes teams use wrong tools.

CI cannot prove GitHub Pages is enabled; unit tests cannot prove Release was not overwritten twice; local link checks cannot prove reader entry paths are clear; model review cannot prove monitoring will alert after errors. Runtime risk needs runtime tooling.

**Conclusion:** Operations’ second value is **governing runtime risk separately from development verification**.

### Part three: Recovery ability decides whether release is sustainable

Non-rollback release makes teams conservative; release without monitoring lets errors spread silently; recovery without runbooks depends on improvisation. Sustainable release is not never failing—it is **detect, locate, rollback, and learn** when failure happens.

That is an Operations maturity signal. Junior teams ask “can we ship?” Mature teams ask “if we ship wrong, how fast do we notice, how do we withdraw, who owns it, where is evidence?” AI-DLC trains the latter question.

**Conclusion:** Operations’ third value is giving the delivery loop **post-failure recovery ability**.

## 04 · Example: This Book’s Pages and Release Paths

This project already has two minimal Operations paths: GitHub Pages publish and GitHub Release candidate. They are not full production systems—but enough as CH-08 cases: one book project moving from verified to auditable runtime entry.

### 4.1 Pages: continuous entry runtime chain

Pages is described by `.github/workflows/pages.yml`. Four key jobs: `validate`, `build`, `record`, `deploy`.

```text
validate
  python3 scripts/ci_check.py --budget-seconds 60

build
  generate_progress.py
  prepare_pages.py
  upload-pages-artifact

record
  generate_progress.py
  commit or upload recoverable progress-record

deploy
  deploy-pages
```

Operations meaning: not raw `site/` publish—validate first, build publish tree, upload Pages artifact, then deploy. `prepare_pages.py` builds an output directory with `.aidlc-generated` marker and `publish-manifest.json`. Entry pages show source commit, source facts, generated_at, and workflow_run.

Readers see not an isolated page but a **runtime entry with provenance**.

### 4.2 Release: version candidate runtime chain

Release is in `.github/workflows/release.yml`. Core job order: `validate` → `readiness` → `build` → `publish` (YAML order may differ; follow `needs`).

```text
validate
  version syntax
  ci_check.py

readiness
  needs: validate
  check_release_readiness.py
  render_release_notes.py
  upload v0.1-readiness

build
  needs: [validate, readiness]
  download exact readiness evidence
  prepare_release.py
  upload release-candidate

publish
  needs: [validate, readiness, build]
  refuse overwrite
  gh release create ... --draft
```

Notable: Release build depends on readiness. `prepare_release.py` refuses non-ready readiness and refuses readiness whose source does not match current facts—avoiding a common accident: packaging commit B’s assets with commit A’s readiness.

PDF handling is honest: without a validated PDF via `--pdf`, manifest records `pdf.status = skipped`—not a fake PDF. AI-DLC stance: unknown is unknown; unverified is unverified; placeholders are not assets.

### 4.3 Recover: recovery hooks in existing paths

Recovery design here is still light—but hooks exist.

First, `prepare_pages.py` and `prepare_release.py` refuse overwriting directories without generation markers—avoid accidental deletion of human dirs. Second, Release workflow creates **draft** Release—not irreversible public version. Third, readiness gate blocks v0.1 DoD failures before build. Fourth, progress system keeps events, snapshots, and source identity for historical replay.

Not a full production runbook—but Operations attitude: reject mixed sources before publish, keep credentials during publish, allow trace after publish, recover when possible on failure.

## 05 · Pattern: Minimal Operations Checklist

Abstract the case into a minimal checklist.

| Stage | Minimum credential | Common failure |
|---|---|---|
| Build | source commit, facts identity, manifest, artifact hash | unreviewed changes mixed in; assets not reproducible |
| Deploy | environment, permissions, version, strategy, artifact id | wrong environment; overwrite existing version |
| Runtime Verify | entrypoint, smoke checks, manifest match, critical path | local OK, target entry broken |
| Monitor | workflow result, errors, usage/feedback, blocker signals | nobody sees errors after publish |
| Recover | trigger, owner, steps, rollback target, post-check | improvisation after incident |

Use directly on small projects; extend cells on large ones—do not delete a row.

## 06 · Experiment: Three Operations Directions

This chapter’s experiment entries:

- **`EXP-08-01 · Release candidate source manifest validator`:** Reuse readiness/manifest validation; verify candidate source, required assets, and file hashes align. Run: `python3 experiments/exp-08-01/quickstart.py --sample`.
- **`EXP-08-02 · Rollback tabletop exercise simulator`:** From deploy topology, failure scenario, monitor signals, and runbook, generate detect→decide→rollback→recover timeline. Run: `python3 experiments/exp-08-02/quickstart.py --sample`.
- **`EXP-08-03 · Operations four-stage reproduction`:** Against frozen pin guide, reproduce Build, Deploy, Runtime Verify, Monitor credentials and rollback readiness. Run: `python3 experiments/exp-08-03/quickstart.py --sample`.

`EXP-08-01` is `ALREADY / verified`: sample at `experiments/exp-08-01/output/sample.json`. On frozen readiness/manifest inputs it proves source consistency, required asset coverage, and hash format are deterministically checkable, with `source_completeness_percent` and `hash_mismatch_count`. It does not prove full production observability; ALREADY must not be rewritten as SHIP.

`EXP-08-02` is verified: sample report at `experiments/exp-08-02/output/sample.json`. It proves topology, failure, monitor signals, and runbook connect into detect→decide→rollback→recover timeline with time-to-rollback, data-loss window, and runbook gap count. Tabletop exercise ≠ production recovery capability.

`EXP-08-03` is `KEEP-EXT / verified`: sample at `experiments/exp-08-03/output/sample.json` with `stage_completion_percent` and `rollback_readiness_percent`. Runtime Verify here is CH-08 runtime verification—not CH-07 delivery-candidate verification; frozen pin ≠ mature production capability.

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-08-01` | Release candidate source, readiness, and artifact hash consistency | Not prove full production observability; ALREADY must not be rewritten as SHIP |
| `EXP-08-02` | Clarity of detect, decide, rollback, recover timeline | Not prove all failures are tabletop-coverable |
| `EXP-08-03` | Four-stage Operations credentials reproducible on frozen guide | Not portray alpha reference as mature production; KEEP-EXT must not be rewritten as SHIP |

## 07 · Figure: Operations Runtime Loop

This chapter’s figure is the Operations runtime loop:

![Figure 8-1 · Operations runtime loop](images/ch08-operations-loop.svg){.core-figure width=100%}

Source file: `book/images/ch08-operations-loop.svg`. Chain summary:

```text
Verified Candidate
  ↓
Build → Deploy → Runtime Verify → Monitor
  ↑                                ↓
  └──────── Recover / Rebuild ◀────┘
```

Left: Verified Candidate; center: Build / Deploy / Runtime Verify / Monitor; bottom low-weight loop: Recover / Rebuild; right: Sustainable Runtime. Runtime Verify is runtime verification—not CH-07 delivery-candidate verification.

The figure should show three things:

1. Operations starts from verified candidates—not ad-hoc publish.
2. Build, Deploy, Runtime Verify, and Monitor each produce traceable credentials.
3. Recover / Rebuild is part of the loop—not a post-failure patch.

Do not draw Monitor as terminal. Monitor triggers Recover, Rebuild, or the next improvement cycle.

## 08 · Boundary: What This Chapter Does Not Solve

First, this chapter does not redefine verification strength. CH-07 already covers deterministic checks, independent tests, model review, and human judgment. CH-08 only handles the post-approval runtime chain.

Second, this chapter does not cover organizational scale governance. How teams, product lines, and risk tiers choose different Flows is CH-09.

Third, this chapter does not claim `memory-bank/operations/` already exists as a mature directory. This repo has no formal operations directory yet; the chapter treats it as method landing zone and future implementation direction.

Fourth, this chapter does not promise `EXP-08-02` proves production recovery; `EXP-08-03` verified only proves frozen four-stage credentials reproduce—not mature observability or recovery.

Fifth, this chapter does not treat release automation as production maturity. Automation is reliable action; maturity also needs environment gates, monitoring, recovery, audit, and accountability.

Sixth, `EXP-08-01` verified only proves candidate source and manifest consistency checks reproduce; it ≠ Runtime Verify passed and ≠ mature monitoring/recovery.

### Operations phase and official method (summary)

AWS AI-DLC **Operations** emphasizes AI analyzing metrics/logs/traces, proposing scale/tune/isolate actions aligned to runbooks, and executing **after human approval**; Deployment Units include images/Serverless/IaC and generate functional, security, and load tests (summary in the [whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com)). This book’s Chapter 8 expresses the same loop as Build→Deploy→Runtime Verify→Monitor→Recover and **explicitly marks specs.md Operations Agent / `memory-bank/operations/` as alpha reference**—do not write “tools are production mature” because the official whitepaper describes them. This repo’s Pages/Release automation is teaching-grade Operations sample—not a substitute AWS Deployment Unit implementation. See [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md) for workflow boundaries (Operations Agent maturity).

## Reader Exercise

Pick a candidate you plan to release and write a minimal Operations runbook in 30 minutes.

1. Candidate provenance: commit, fact source, build script, readiness?
2. Build credentials: manifest, file hashes, build time, output assets?
3. Deploy strategy: target environment, trigger, permissions, draft or not, overwrite allowed?
4. Runtime Verify: three real entry points to check after publish?
5. Monitor: which signals in first 24 hours; who watches?
6. Recover: if entry breaks, assets wrong, or release notes wrong—rollback or rebuild how?
7. One judgment: Release, Rollback, Rebuild, Pause, or Escalate.

If you can answer **when this candidate fails, how we know, how we withdraw, how we rebuild**, you have moved from publish action to Operations thinking.

## References

- `scripts/check_release_readiness.py`: v0.1 readiness and release blocker report.
- `scripts/prepare_release.py`: traceable Release candidate asset construction.
- `scripts/prepare_pages.py`: GitHub Pages publish tree and publish manifest.
- `.github/workflows/pages.yml`: Pages build, upload, deploy, and progress record chain.
- `.github/workflows/release.yml`: Release readiness, candidate build, and draft publish chain.
- `planning/releases/v0.1-policy.json`: machine-readable v0.1 Definition of Done gates.
- `experiments/exp-08-01/output/sample.json`: release candidate source manifest validation sample.
- `progress/experiments.json`: governance status for `EXP-08-01`, `EXP-08-02`, `EXP-08-03`.
- `book/toc.md`: CH-08 core question, reader outcome, and experiment directions.
- [AWS AI-DLC Method Definition (Amplify)](https://prod.d13rzhkk8cj2z0.amplifyapp.com): Operations phase summary (not mature-tool claim).
- [WORKING-WITH-AIDLC-MAP.md](../../../docs/WORKING-WITH-AIDLC-MAP.md): chapter-to-AI-DLC workflow map (Part III · Phases & Rituals; Operations Agent boundaries).
- `book/images/ch08-operations-loop.svg`: Operations runtime loop figure.
- `../../chapters/ch08-operations.md`: Chinese source chapter.
