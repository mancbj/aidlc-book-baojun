# Chapter 2 · Human Judgment and Reverse Conversation

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-02 |
| Status Source | `progress/chapters.json` |
| Draft Completeness | D16-T02 readable draft; awaiting D16-T03 review and evidence alignment |
| Primary Question | When AI proactively proposes, decomposes, and executes, how should humans set the destination, retain accountability, and choose verification checkpoints? |
| Reader Outcome | Able to define Intent, boundary, non-delegable judgment, human checkpoint, and final accountable party |
| Related Experiments | `EXP-02-01`、`EXP-02-02`、`EXP-02-03` |

## 01 · Question: When AI Takes the Initiative, What Are Humans Still Responsible For?

Chapter 1 established an entry judgment: AI lowers generation cost but does not automatically bring deterministic delivery. Chapter 2 pushes one step further. Suppose the team already accepts that AI is not just an autocomplete tool—that it can proactively propose, break down tasks, generate options, fix errors, and update records. The question becomes immediate: **the more proactive AI is, where should human judgment stand?**

This question is easily pulled off course by two misunderstandings.

The first is “humans can keep prompting step by step.” In that mode, AI is only a faster execution tool. Humans think through each step, then ask AI to write code, add tests, edit docs. It is safe, familiar, and fits low-risk local work; but when AI can already propose decomposition, surface ambiguity, and compare options, pure step-by-step prompting wastes AI’s proposing power.

The second misunderstanding is more dangerous: since AI can take initiative, let AI decide goals, boundaries, and trade-offs. On the surface the system looks more automatic; in reality human accountability is diluted. Models can suggest, but models are not the final accountable party. They do not know what risk the organization will accept, which readers take priority, whether an experiment conclusion is enough to enter the main text, or who answers for a release outcome.

So this chapter’s core view is: **the more proactive AI is, the less human judgment can leave the field; human work is not watching AI’s every move, but setting destination, boundary, non-delegable judgment, human checkpoints, and final accountability.**

In AI-DLC, that relationship compresses to one line:

```text
AI proposes.
Human validates.
Engineering records the decision.
```

AI proposing lets the system see alternative paths earlier; human validation keeps goal, boundary, and accountability from drifting; engineering recording lets the next session, the next collaborator, and the next release recover this judgment. All three are necessary. Only AI proposes → model monologue; only Human validates → manual process; only Engineering records → human judgment truly enters the lifecycle.

After this chapter, readers should be able to do one concrete thing: given an AI task, first write Intent, Boundary, Non-delegable Judgment, Human Checkpoint, and Accountability, then decide where AI may start taking initiative.

### Gate

- [x] There is only one core question: after AI takes initiative, how humans set destination, retain accountability, and choose checkpoints.
- [x] Reader outcomes are observable: able to define Intent, boundary, non-delegable judgment, human checkpoint, and final accountable party.

## 02 · Framework: The Five-Piece Human Judgment Set

This chapter uses a five-piece framework to answer “what are humans still responsible for?”:

```text
Intent
  - Destination: what result are we trying to achieve?
Boundary
  - Boundary: what will we not do, must not do, or defer?
Non-delegable Judgment
  - Non-delegable judgment: which trade-offs must not be finally decided by AI?
Human Checkpoint
  - Human checkpoint: at which stages must humans stop and confirm?
Accountability
  - Accountability: who owns the final choice and its consequences?
```

These five correspond to “human judgment” in the book’s formula. They are not the opposite of AI capability—they are preconditions for scaling AI capability safely.

### 2.1 Intent: Destination Is Not a Prompt

Intent is not a casual prompt or “help me build a feature.” Intent is human judgment about outcome: why we do it, how far we go, who uses it, how we know we succeeded.

“Help me build a feedback entry” is a wish, not a qualified Intent. It at least lacks four pieces: who feedback is for, what feedback to collect, what not to collect, and what success looks like. AI can ask these questions or propose defaults, but defaults must be confirmed by humans.

If Intent is unclear, AI can still generate a lot. The danger is exactly there: it will quickly and earnestly do something that was never correctly defined.

### 2.2 Boundary: Boundaries Keep Speed from Overstepping

Boundary answers “what we will not do.” Boundary is not passive limitation—it is active protection. It tells AI which paths look reasonable but must not enter current work.

In this book project, boundaries have saved the process repeatedly. For example `specs.md-portal/` is locally crawled official-site material and is not uploaded as a subsequent GitHub repo object; `github_repo_reference_ai-agent-book-main/` is a local reference repo and does not enter the public repo; `working-book/` is author working material and is also not a publish target. If these boundaries live only in chat memory, AI’s organizing power can become risk: it may treat “related” as “should be included.”

Boundaries keep AI’s speed from overstepping and let the next session recover without re-guessing author intent.

### 2.3 Non-delegable Judgment

Non-delegable judgments are items where AI may advise but humans must finally decide. They usually involve value, risk, accountability, and real-world constraints.

In a writing project, non-delegable judgments include:

- Who this book is for and which reader problems take priority.
- Whether a term must be kept, e.g. `𝓔 = Engineering with Exsecutio`.
- Whether an experiment is enough to support a main-text conclusion.
- Which directories do not enter the public repo.
- Whether v0.1 meets the release bar.
- Whether to delay release for stronger evidence.

In software projects, non-delegable judgments are similar: whether business risk is acceptable, where compliance boundaries lie, whether data may be accessed by models, recovery objectives, who approves the final release window.

AI can list options, explain cost, point out gaps, generate comparison tables—but it cannot be the final accountable party. The key is not “AI cannot participate” but “AI cannot decide finally.”

### 2.4 Human Checkpoint: Checkpoints Are the Steering Wheel, Not the Brake

Checkpoints are often misread as “slow AI down.” More accurately, checkpoints are the steering wheel of a high-speed system. The faster you go, the more you must confirm direction at key junctions.

A good Human Checkpoint meets at least three conditions:

1. It happens before errors cascade.
2. It requires explicit evidence, not AI self-assessment alone.
3. It leaves a record so the next execution knows why to continue, pause, or reroute.

In AI-DLC, checkpoints should not appear only at final acceptance. Whether Intent is correct, boundaries clear, Stories acceptable, Bolts chosen correctly, tests independent, release rollback-ready—all can be human checkpoints. More checkpoints is not the goal; place them where errors amplify most, rework costs most, and accountability must be clearest.

### 2.5 Accountability: Accountability Cannot Be Automated

Accountability closes the five-piece set. Once results enter the real world, someone must own trade-offs. Accountability here is not “find someone to blame”—the system must know:

- Who may confirm goals.
- Who may accept risk.
- Who may approve release.
- Who starts correction when results are wrong.
- Who writes experience back into the next round of constraints.

Without accountability, AI-DLC degrades to “model suggested it, everyone assumed OK.” With accountability, AI becomes an amplifier of human capability, not a diluter of responsibility.

## 03 · Core Pattern: Reverse Conversation

Traditional human–machine interaction is often “human asks, AI answers.” That works well locally: I give an error log, AI explains; I give code, AI refactors; I give a draft, AI polishes.

In AI-DLC, the more important structure is reverse conversation: **AI first surfaces questions, risks, options, and gaps; humans then validate, revise, or reject.**

```text
Traditional prompt chain
  Human asks -> AI answers -> Human asks again

Reverse conversation chain
  Human states intent -> AI proposes questions/options/risks
  -> Human validates boundaries/checkpoints
  -> AI executes within recorded constraints
```

Reverse conversation does not let AI own the goal—it lets AI expose what needs human judgment earlier. A good Agent should not rush to finish; before execution it should ask:

- Is my understanding of the goal correct?
- Which boundaries are still undefined?
- Which judgments cannot I make for you?
- At which stages do you need to confirm?
- If I continue, what risks might appear?

This is also why the specs.md reference implementation’s division among Master Agent, Inception Agent, Construction Agent, and Operations Agent matters. Master routes and judges context; Inception turns intent into an executable plan; Construction advances along Bolts; Operations handles release and runtime. Each Agent can propose proactively, but each critical advance should leave human validation and engineering record.

### 3.1 Mob Elaboration and Question–Doc–Approval (Summary)

The AWS method definition describes **Mob Elaboration** as Inception’s core ritual: same room, shared screen, facilitator-led mob with PO, developers, QA, and other stakeholders; AI first proposes User Stories, acceptance criteria, Units, and suggested Bolts from Intent; the team then corrects under- and over-engineering and aligns NFRs, risks, and metrics. This matches this chapter’s reverse conversation: **AI exposes gaps and options first; humans validate boundaries and checkpoints.**

The community repo [aidlc-workflows · WORKING-WITH-AIDLC](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md) operationalizes similar constraints as **Question→Doc→Approval**: key conclusions must be written into md artifacts and human-approved before Construction; stage transitions should “gate” and clear irrelevant chat context so old assumptions do not pollute the next Bolt. Chapter 4 expands Memory Bank; Chapter 3 only requires Inception outputs to include approvable, linkable Story/Unit/Bolt artifacts—not “verbal agreement” in chat.

## 04 · Three-Part Argument: Why Human Judgment Must Come First

### Part one: AI initiative changes where human work sits

In AI-Assisted mode, humans usually think through each step, then ask AI to help locally. In AI-Driven or Agentic mode, AI begins to ask questions, split work, recommend routes, and execute candidates. Human position moves forward: from step-by-step orders to defining destination, boundary, and checkpoints.

If humans only review at the end, problems surface late: wrong goal understanding, boundaries never written, default plans mismatched to risk appetite, tests not covering real acceptance. The later the discovery, the more rework.

Conclusion: **the more AI can drive progress proactively, the more humans must shift from operator to judge and gate designer.**

### Part two: Reverse conversation moves clarification forward

Traditional interaction puts clarification mainly on humans: the clearer the question, the better the answer. In real projects, humans often do not know all boundaries at the start. AI’s value is not only answering—it can help discover problems.

Reverse conversation has AI list ambiguity, risk, options, and checkpoints before execution. Humans need not design prompts from a blank page—they validate AI’s judgment checklist. That moves “requirements unclear after implementation” risk to “clarify before execution.”

Conclusion: **reverse conversation does not let AI own the goal—it lets AI expose what needs human judgment earlier.**

### Part three: Human judgment must land in traceable artifacts

Human judgment that stays in chat expires quickly. The next session cannot see this choice; another collaborator does not know why a option was rejected; release audit cannot tell whether a risk was accepted.

Judgment must enter artifacts: Intent, boundary notes, acceptance items, checkpoints, decision records, task state, accountable parties, event ledger, review records. Engineering record is not paperwork—it is how human judgment continuously constrains AI execution.

Conclusion: **human judgment constrains AI execution continuously only when engineered into records—not as one-off verbal opinion.**

## 05 · Example: Two Dialogues for the Same Vague Need

Suppose the author asks:

> Help me build a trial-read feedback entry.

The need looks small. AI can immediately generate a form, submit script, and copy. But it hides many judgments: anonymous feedback? contact info? public display? GitHub Issue? file uploads? required fields? failure handling? who handles feedback? which feedback blocks release?

### Path A: Human prompts step by step

In a normal prompt chain, the human might proceed:

```text
Human: Help me build a trial-read feedback entry.
AI: Generate a form page.
Human: Add a chapter field.
AI: Added.
Human: Add an email field.
AI: Added.
Human: Write a README.
AI: Generated.
```

This path starts fast but scatters key judgments across supplemental prompts. Humans add what they think of; boundaries they did not think of temporarily do not exist. The result may be a usable-looking page, not a governable feedback entry.

Path A’s risk is not that AI did nothing—it is that AI did too much not constrained by systematic judgment.

### Path B: AI proposes, human validates

In the reverse conversation chain, AI does not rush to implement—it first offers a judgment checklist:

```text
AI: Let me confirm 5 things first:
  1. Intent: Is this entry for trial-read feedback or formal reader support?
  2. Boundary: Must we avoid collecting phone numbers, company names, etc.?
  3. Non-delegable Judgment: Which feedback blocks v0.1 release?
  4. Human Checkpoint: Who confirms before the entry goes live?
  5. Accountability: Who handles and closes feedback after submission?

Human: Trial-read feedback only; no phone numbers; blocking feedback judged by author;
       I confirm before go-live; decisions written to feedback/decisions.json.

AI: After recording boundaries and acceptance, generate entry and docs.
```

Path B is not necessarily slower than Path A. It makes pre-implementation judgment explicit. AI still generates pages and docs, but generation happens after constraints. Done is no longer “page looks fine” but “entry, boundaries, acceptance, accountability, and record paths are all traceable.”

### Comparative observation

| Dimension | Human step-by-step prompts | AI proposes, human validates |
| --- | --- | --- |
| Start | Human asks for implementation directly | AI exposes judgment checklist first |
| Boundaries | Add one when remembered | Confirm centrally before execution |
| Risk | Undefined defaults guessed by AI | Undefined items enter clarification first |
| Accountability | Often implicit in chat | Written accountable parties and checkpoints |
| Record | Depends on conversation memory | Enters source of truth, tasks, events |

This example does not prove “every need needs heavy process.” It only shows: when AI can execute proactively, what is most worth automating is not human judgment—it is surfacing where human judgment is needed earlier.

## 06 · Experiment: Chapter Experiment Entry Points

This chapter links three experiments. `EXP-02-01`, `EXP-02-02`, and `EXP-02-03` are verified; `EXP-02-03` triage remains `KEEP-EXT`.

### `EXP-02-01` · Non-delegable judgment checklist generator

This experiment turns project goals, risks, constraints, and accountability roles into a “human judgment points and accountability boundary checklist.” It tracks judgment-point coverage and unassigned accountability count. Run:

```bash
python3 experiments/exp-02-01/quickstart.py --sample
```

Sample output at `experiments/exp-02-01/output/sample.json`. It shows input entries can generate judgment points and boundaries by fixed rules; coverage only means rule hit rate, not that all non-delegable judgments in the project are covered.

### `EXP-02-02` · Reverse conversation clarification benefit experiment

This experiment compares the same vague need in two frozen session groups: implement directly vs clarify then implement. Metrics include post-implementation requirement changes, critical omissions, and clarification rounds. Run: `python3 experiments/exp-02-02/quickstart.py --sample`. Sample at `experiments/exp-02-02/output/sample.json`.

It shows frozen sessions can be compared for clarification benefit; clarification does not always reduce change. It supports this chapter’s pattern: reverse conversation is to expose critical omissions earlier.

### `EXP-02-03` · Four-Agent human checkpoint session reproduction (KEEP-EXT)

This experiment checks checkpoint adherence and unsupported approval counts for routing, proposal, human approval, and handoff sessions against a frozen pin guide in the repo. Run: `python3 experiments/exp-02-03/quickstart.py --sample`. Sample at `experiments/exp-02-03/output/sample.json`.

It shows human–machine checkpoints on frozen sessions can be reproduced deterministically; it does not write external Agent docs as the only standard or replace real human approval. It supports this chapter’s boundary: multi-Agent value is handoff back to human validation and engineering record.

## 07 · Figure: Chapter Figure Entry Point

This chapter’s figure is the “human judgment gate diagram.” It is not a generic approval flow—it is the judgment structure before AI initiative enters the engineering track.

![Figure 2-1 · Human judgment gate](images/ch02-human-judgment-gate.svg){.core-figure width=100%}

Source file: `book/images/ch02-human-judgment-gate.svg`. When reading, follow this main chain:

```text
Intent
  -> Boundary
  -> AI Proposal
  -> Human Checkpoint
  -> Accepted Work
  -> Evidence Record
  -> Feedback to Intent / Boundary
```

Two emphases:

1. AI Proposal sits after Boundary. AI may take initiative, but initiative must happen inside boundaries.
2. Evidence Record feeds back to Intent and Boundary. Evidence from each execution updates the next round of human judgment.

## 08 · Boundary: What This Chapter Does Not Cover

To keep Chapter 2 focused, this chapter deliberately does not cover:

- Repeating Chapter 1’s overall case for AI-native SDLC necessity.
- Full decomposition from Intent to Requirement, Unit, Story, Bolt Plan—that is Chapter 3.
- Cross-session Memory Bank and Standards structure—that is Chapter 4.
- Bolt stage gate detail—that is Chapters 5 and 6.
- Verification method comparison—that is Chapter 7.

This chapter answers only: **when AI proposes and executes proactively, how human judgment becomes destination, boundary, checkpoint, and accountability.**

## 09 · Reader Exercise

Pick a task you are considering handing to AI and spend 10–30 minutes filling this minimal judgment card.

```text
Task:
Intent:
Boundary:
Non-delegable Judgment:
Human Checkpoint:
Accountability:
Evidence Record:
```

Follow three rules when filling:

1. Intent must state outcome, not action. “Collect trial-read feedback and form a revision entry” beats “build a form.”
2. Boundary: at least three items, one must be “what we are not doing now.”
3. Non-delegable Judgment: at least two items, each with final confirmer noted.

Then ask AI to propose an implementation plan from this card. If the plan does not reference these constraints, do not implement—have it rewrite the plan first.

## 10 · Review Notes for D16-T03

D16-T03 review should focus on five items:

- Technical boundary: do not write human judgment as “human approves everything,” or AI initiative as “AI owns everything.”
- Terminology consistency: keep `𝓔 = Engineering with Exsecutio` and place this chapter clearly under “human judgment” in the formula.
- Evidence boundary: `EXP-02-01` / `EXP-02-02` / `EXP-02-03` are verified but each only proves rule-based checklist, frozen session comparison, and human–machine checkpoint reproduction; `EXP-02-03` must not be rewritten as SHIP or as mature Agentic approval.
- Structural coherence: question, five-piece set, reverse conversation, case, experiments, figure, and exercise must serve the same core question.
- Adjacent chapter boundaries: this chapter does not expand Chapter 3 Intent decomposition artifacts—only how humans confirm goals and boundaries.

## References

- `book/toc.md`: CH-02 core question, reader outcome, reference implementation, experiment direction.
- `book/manifesto.md`: “human judgment” duties in the core formula.
- `../../chapters/ch01-ai-native-sdlc.md`: previous chapter’s AI-Assisted, AI-Driven, and Agentic distinction (Chinese source).
- `./ch01-ai-native-sdlc.md`: English translation of Chapter 1.
- `progress/chapters.json`: chapter source of truth and six-phase status.
- `progress/experiments.json`: experiment governance for `EXP-02-01`, `EXP-02-02`, `EXP-02-03`.
- `progress/tasks.json`: writing task cards D16-T01, D16-T02, D16-T03.
- `specs.md-portal/pages/agents/overview.md`: local snapshot of four-Agent responsibilities.
- `specs.md-portal/pages/faq.md`: local snapshot related to AI proposes, human validates and Mob Elaboration.
- [aidlc-workflows · WORKING-WITH-AIDLC](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md), `docs/WORKING-WITH-AIDLC-MAP.md`: Question→Doc→Approval operational mapping.
