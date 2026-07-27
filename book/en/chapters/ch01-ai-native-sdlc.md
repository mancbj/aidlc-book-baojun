# Chapter 1 · AI-Native SDLC: From Probabilistic Intelligence to Deterministic Delivery

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-01 |
| Status Source | `progress/chapters.json` |
| Draft Completeness | D15-T02 readable draft; awaiting D15-T03 review and evidence alignment |
| Primary Question | When the cost of code generation drops sharply while output remains probabilistic, why must we redesign the SDLC rather than merely adding AI to the old process? |
| Reader Outcome | Able to distinguish AI-Assisted, AI-Driven, and Agentic paradigms, and explain the necessity and boundaries of AI-DLC using the core formula |
| Related Experiments | `EXP-01-01`、`EXP-01-02`、`EXP-01-03` |

## 01 · Question: Why the Old SDLC Cannot Contain AI

Imagine a very ordinary product need: add a “trial-read feedback entry” to an internal tool. In the era before AI, the team would clarify requirements, write tasks, schedule work, implement, test, and release. Code mattered, but what often consumed the cycle was not typing—it was aligning on goals, understanding context, handling edge cases, verifying correctness, fixing gaps, and placing the result in a maintainable system.

Now bring AI in. Developers can get routing, forms, backend APIs, test samples, draft documentation, even a Pull Request description that looks complete—all in minutes. Generation suddenly speeds up, fast enough to create a natural illusion: if code and docs can be produced this quickly, will software delivery automatically speed up too?

The answer is not that light. AI can lower generation cost, but it does not automatically lower delivery risk. It can produce a reasonable implementation and miss a permission boundary; it can add tests and bake wrong assumptions into those tests; it can generate polished explanations and state unverified conclusions with great certainty. Teams then hit a new counterintuitive phenomenon: **writing gets easier, and confirming that something should actually be delivered becomes more important.**

This chapter answers one question only: **when the cost of code generation drops sharply while output remains probabilistic, why must we redesign the SDLC rather than merely adding AI to the old process?**

“Redesign” here does not mean throwing away all existing engineering practice. Requirements, design, testing, release, rollback, and review still matter. What must change is how they are organized: the old process assumes people are the primary producers and tools are helpers; an AI-native process must acknowledge that AI has entered the center of proposing, decomposing, generating, fixing, and recording. If the process does not change with that, imbalance appears:

```text
AI makes generation faster
        ↓
More candidate designs, code, and changes
        ↓
Pressure rises on verification, trade-offs, traceability, and recovery
        ↓
If the SDLC is not restructured, speed amplifies uncertainty along with output
```

So the core job of an AI-native SDLC is not to have AI “write a bit more,” but to fold AI’s probabilistic capabilities into a system that can continuously constrain, verify, correct, and deliver.

After this chapter, readers should be able to do two things. First, judge whether a team practice is merely AI-Assisted or has entered AI-Driven or Agentic territory. Second, use this book’s core formula to explain why AI-DLC is not “AI replacing the process,” but putting human judgment and AI capability on an engineered execution track toward deterministic delivery.

### Gate

- [x] There is only one core question: why the SDLC must be redesigned.
- [x] Reader outcomes are observable: able to distinguish the three paradigms and explain necessity and boundaries with the core formula.

## 02 · Framework: Three Paradigms and One Delivery Chain

When discussing AI and the SDLC, three things are easiest to conflate: tool assistance, process driving, and agent collaboration. All may use large models and generate code, but they impose completely different requirements on human roles, sources of truth, verification, and delivery accountability.

### 2.1 AI-Assisted: People Use AI Inside the Old Process

The default structure of AI-Assisted is “human-led, AI-assisted.” People still manually drive requirements, design, implementation, testing, and release; AI is embedded in local steps: completing code, explaining errors, generating tests, polishing docs, turning a command into a script.

This mode is valuable. Learning cost is low, organizational shock is small, and it fits individual developers and low-risk tasks well. An engineer asking AI for a utility function in the IDE, or asking AI to explain a unit test from a failure log, usually does not require restructuring the whole R&D system.

But the boundary of AI-Assisted is clear: the process itself has not changed. Whether requirements are clear, whether boundaries are written into the source of truth, whether acceptance is reproducible, whether failure samples are kept, whether release has receipts—still depends mainly on manual upkeep. AI only accelerates certain actions in the old process.

One-line test: **if AI only improves efficiency in local human actions without changing task decomposition, state progression, evidence recording, and stage gates, it is AI-Assisted.**

### 2.2 AI-Driven: AI Participates in Decomposition, Execution, and Progression

The shift in AI-Driven is not just “AI writes more code.” AI begins to participate in work breakdown, proposing plans, executing tasks, fixing tests, updating status, and syncing progress. Human work changes too: not just feeding prompts one by one, but setting goals, boundaries, and checkpoints so AI advances along the source of truth.

The system must then answer a new set of questions:

- Where do AI’s inputs and boundaries come from?
- How are AI-generated plans accepted?
- How is drift during AI execution detected?
- How is each critical update recorded automatically?
- Where do humans make judgments that cannot be delegated?

Without engineered answers, AI-Driven easily degrades into faster, more complex chat-driven development. The team looks like it is moving fast, but the next day a new session, a different person, or another Agent may not know where current state came from, which decisions are in effect, or which evidence shows the result can enter the next stage.

One-line test: **if AI already participates in planning, execution, and state progression, and the team constrains it with sources of truth, acceptance, events, and gates, it has truly entered AI-Driven.**

### 2.3 Agentic: Multiple Agents Collaborate Along an Engineering Track

Agentic development further extends AI capability into a delegable, recoverable, continuously executable agent system. A Master Agent can route tasks; an Inception Agent can decompose Intent into Requirement, Unit, Story, and Bolt Plan; a Construction Agent can follow Bolts to produce design, implementation, tests, and Walkthrough; an Operations Agent can build and deploy candidates, run Runtime Verify, and fold in monitoring.

What is most appealing here is parallelism and continuity. Multiple Agents can collaborate around the same source of truth and split complex work into advanceable local pieces. But risk is also clearer: the more Agents, the less order can rely on chat memory and verbal agreement. Otherwise, multi-Agent work only parallelizes uncertainty.

One-line test: **if multiple Agents can divide work around the same set of versioned artifacts and keep advancing through stage gates and an evidence chain, it is Agentic; otherwise it is just multiple sessions generating at once.**

### 2.4 How the Three Paradigms Differ

| Paradigm | AI’s place | Human’s main work | Source-of-truth requirement | Typical risk |
| --- | --- | --- | --- | --- |
| AI-Assisted | Local assist tool | Write prompts, review code, manual wrap-up | Low to medium; old process can continue | Locally correct but not traceable end-to-end |
| AI-Driven | Participates in plan and execution | Set goals, boundaries, acceptance, correction | High; needs tasks, state, evidence, events | Speed amplifies hidden assumptions |
| Agentic | Multi-Agent division of labor | Design accountability, gates, recovery | Very high; must be versioned, recoverable, auditable | Parallelism amplifies context drift |

The point of this table is not to label teams, but to help them see what to add next. If you are still AI-Assisted, do not pretend you already have Agentic delivery; if AI already decomposes and executes, you must start adding sources of truth, gates, and evidence chains.

### 2.5 Method Source: AWS AI-DLC Method Definition (Summary)

[Raja SP · AWS AI-DLC Method Definition](https://prod.d13rzhkk8cj2z0.amplifyapp.com) (also reachable from the [AWS DevOps blog post](https://aws.amazon.com/cn/blogs/devops/ai-driven-development-life-cycle/)) is highly isomorphic to this book’s Chapter 1 question, but phrased in AWS’s official whitepaper. Below is a reading summary only—it **does not replace the original**:

| Principle (excerpt) | Meaning for the SDLC |
| --- | --- |
| Reimagine rather than retrofit | Iteration shifts from weeks/months to hours/days; many traditional rituals (e.g. story-point velocity) need rethinking in terms of business value |
| Reverse the conversation | Humans give Intent (destination); AI provides decomposition and route (like turn-by-turn navigation); humans retain oversight |
| Integration of design into the core | DDD/BDD/TDD flavors are embedded in planning and decomposition, not optional white space per team |
| Align with AI capability | Adopt AI-Driven balance: AI orchestrates; humans own verification, security, and final accountability |
| Cater to complex systems | Aimed at high architectural complexity and multi-team systems; minimal/low-code scenarios are out of scope for this method |
| Retain what enhances symbiosis | Keep artifacts that help human verification, such as User Story and Risk Register, optimized for real-time use |
| Facilitate transition through familiarity | Deliberate renames such as Bolt lower the cost of learning from Agile mental models |
| Minimise stages, maximise flow | Few stages as possible, but human “loss function” style verification at key decision points |
| No hard-wired SDLC workflows | AI generates Level 1 Plan by pathway (greenfield/brownfield/defect, etc.); humans validate Level 2+ step by step |

This book’s **AI-DLC = 𝓔 (human judgment + AI capability)** is an **engineering interpretation layer** on that official methodology, not a verbatim translation of AWS documents. specs.md, aidlc-workflows, and this book’s experiments each mark evidence boundaries so whitepaper appendix prompt templates are not treated as the book’s sole operational standard.

## 03 · Core Formula: From Probabilistic Intelligence to Deterministic Delivery

This book compresses the AI-DLC watershed into one formula:

> **AI-DLC = 𝓔 (human judgment + AI capability)**  
> **𝓔 = Engineering with Exsecutio**

The formula is deliberately not “human + AI = delivery.” Human judgment and AI capability, even added together, only yield stronger generation, faster feedback, and more candidate paths. They do not automatically become shippable software.

Human judgment owns four things: goal, boundary, trade-off, and accountability. Goal answers “where are we actually going”; boundary answers “what must not be done”; trade-off answers “how to choose among options”; accountability answers “who owns judgment and correction when results are wrong.” AI can assist these judgments but cannot finally own them.

AI capability also owns four things: propose, decompose, generate, and execute. It can turn vague intent into candidate requirements, suggest architecture options, generate code and tests, and fix implementation from failures. Its strengths are speed, breadth, and stamina; its risks are probabilistic output, incomplete context, and overconfidence.

`𝓔 = Engineering with Exsecutio` turns the first two into delivery. `Exsecutio` is a book-specific term stressing execution that drives plans to a deliverable state—not generic “execution” alone. `𝓔` includes at least four observable capability classes:

| 𝓔 capability | What it constrains | Observable artifacts |
| --- | --- | --- |
| Source of truth | Current goals, tasks, state, dependencies | `progress/tasks.json`, Memory Bank, Story, Bolt |
| Stage gates | What may enter the next stage | Acceptance items, checkpoints, Definition of Done |
| Evidence chain | Why we believe the result is correct | Tests, failure samples, build manifests, review records |
| Feedback record | How change is recovered and traced | Event ledger, snapshots, CHANGELOG, release receipts |

So the shortest definition of AI-DLC remains:

> Humans set direction, AI adds acceleration, engineered execution ensures delivery.

More strictly, AI-DLC is not “AI replacing the SDLC,” but “redesigning the SDLC around AI’s capabilities and risks.” It acknowledges AI’s speed and AI’s probabilistic nature; it uses AI’s generative power but does not treat model confidence as delivery evidence.

The opening of the book already embeds `book/images/fig0-1.svg` as the core figure. This chapter can revisit it repeatedly: human judgment and AI capability do not land on delivery directly—they enter `𝓔` first. Only through constraint, verification, correction, and follow-through can probabilistic output become deterministic delivery.

## 04 · Three-Part Argument: Why the Lifecycle Must Be Restructured

### Part one: AI changed the cost structure of software development

Much of the rhythm of traditional SDLC was designed around human production cost. Clarifying requirements took meetings; design took multi-person sync; implementation took engineer scheduling; testing took manually crafted samples; release took coordinated windows. Scrum Sprints, requirement reviews, dev scheduling, and batched testing are organizational techniques formed under that cost structure.

The first thing AI changes is the cost of drafts. A requirement can spawn multiple solution sketches in minutes; an API can quickly get matching tests; an error log can get an immediate explanation; release notes can be auto-drafted. Teams feel “the bottleneck is gone.” What actually disappeared is only part of generation cost.

The new bottleneck appears in selection, verification, and integration. More options mean trade-offs matter more; faster code means tests matter more; frequent changes mean traceability matters more; longer context means sources of truth matter more. Teams that still understand AI through the old process treat AI as a faster typist and miss that the system bottleneck has moved.

Conclusion of this part: **AI’s main effect is not making every old step a little faster—it changes where the process bottleneck sits.**

### Part two: Probabilistic intelligence must pass through an engineering system

What makes AI output powerful is also what makes it dangerous. It can give coherent answers under incomplete information and plausible explanations without evidence. Humans lower their guard when reading fluent text; systems assume runnable code means reliability.

Software delivery needs not “looks reasonable” but “correct under constraints.” An implementation must trace back to requirements; requirements to intent; tests must prove key risks; release must trace to build credentials. AI can participate in these links but cannot substitute its own certainty for evidence.

That is why AI-DLC needs versioned sources of truth, stage gates, failure samples, state diff records, and review credentials. They are not documentation burden—they are the transmission that turns probabilistic intelligence into engineering outcomes. Without them, the faster you go, the harder drift is to detect.

Conclusion of this part: **without sources of truth, standards, checkpoints, and evidence chains, speed amplifies both output and risk.**

### Part three: AI-DLC is the lifecycle that turns speed into deterministic delivery

The goal of AI-DLC is not to make the process look more “AI,” but to bring AI’s speed into a loop that is verifiable, reproducible, releasable, and recoverable. Referencing specs.md’s three phases, that loop can be read as a chain from intent to runtime:

```text
Inception
  Intent → Requirements → Unit → Story → Bolt Plan
Construction
  Model / Plan → Design → Implement → Test → Walkthrough
Operations
  Build → Deploy → Runtime Verify → Monitor → Recovery
Evidence & Feedback
  Events → Snapshots → Changelog → Next Intent
```

Each segment of this chain handles the same problem: AI can generate candidates, but candidates must pass human judgment and engineering evidence to move forward. Inception is not just writing requirements—it turns goals into traceable work structure. Construction is not just writing code—it advances implementation through stage gates. Operations is not just going live—it preserves build, Runtime Verify, monitoring, and recovery credentials; Runtime Verify here is not the same as delivery-candidate verification in Chapter 7. Evidence & Feedback is not just summarizing—it writes experience back into the next round of judgment.

Conclusion of this part: **the value of AI-DLC is not “a more AI-like process,” but bringing AI’s speed into a delivery loop that is verifiable, reproducible, releasable, and recoverable.**

## 05 · Example: Two Paths for the Same Intent

To ground the framework, take a minimal example. Suppose the team wants a “trial-read feedback entry”: readers can submit chapter feedback, authors can see a feedback summary, and blocking issues become revision tasks.

### Path A: Old process plus AI

On the AI-Assisted path, the author might:

1. Ask AI to generate a feedback form page.
2. Ask AI to add a submit script or static form config.
3. Ask AI to write a few tests.
4. Manually check whether the page looks usable.
5. Merge code and add documentation later.

This path is fast, especially for exploration. But it easily leaves open: where are requirement boundaries? Must feedback be anonymous? Which fields are required? How are submit failures handled? How does feedback enter the task system? After release, how do you prove the entry actually works? If the next session continues maintenance, where do you restore context?

These are not failures of AI-Assisted—they are its boundary. It suits local acceleration; it does not natively provide lifecycle-level traceability.

### Path B: AI-DLC closed loop

On the AI-DLC path, the same Intent enters the source of truth and task track first:

```text
Intent: Prepare trial-read feedback entry
  - Boundary: collect trial-read feedback only, not marketing subscriptions
  - Acceptance: entry reachable, fields complete, feedback path documented
  - Task: D12-T03 "Prepare trial-read feedback entry"
  - Artifacts: feedback/template, README, site link
  - Events: task state changes auto-written to events.jsonl
  - Projection: cockpit and object drill-down show next action and completion evidence
```

On this path, AI can still generate pages, scripts, and copy, but every step must return to tasks, artifacts, and acceptance. Done is not “the page looks fine,” but the source of truth shows the task complete, required artifacts exist, acceptance passes, progress pages drill down, and key events are traceable.

That is the difference between AI-DLC and old process plus AI: the former does not slow AI down—it gives AI’s speed rails, brakes, and an odometer.

### Comparative observation

| Dimension | Old process + AI | AI-DLC closed loop |
| --- | --- | --- |
| Speed | Fast start, fast local generation | Slightly heavier start, but recoverable afterward |
| Accountability | Mostly human memory and catch-up | Human judgment written into boundaries, acceptance, gates |
| Evidence | Often stops at “looks usable” | Tasks, artifacts, tests, events traceable |
| Recovery | Depends on chat history or personal memory | New session continues from source of truth |
| Risk | Hidden assumptions may shift later | Assumptions surface earlier in acceptance and records |

Later experiments in this chapter will harden this contrast: the same Intent through conversational generation vs. AI-DLC loop, comparing delivery cycle, rework, defects, and evidence completeness.

## 06 · Experiment: Chapter Experiment Entry Points

`EXP-01-01`, `EXP-01-02`, and `EXP-01-03` are all verified and consume only frozen fixtures in the repository—no external models or live web fetches in CI. `EXP-01-03` triage remains `KEEP-EXT`.

### `EXP-01-01` · Same Intent multi-generation variance baseline

This experiment asks: when input is identical and multiple frozen generations differ, how large are structural difference rate and test-pass variance? Run: `python3 experiments/exp-01-01/quickstart.py --sample`. Sample at `experiments/exp-01-01/output/sample.json`.

It shows that multiple frozen results for the same Intent can be diffed deterministically; a frozen variance baseline does not prove any model is “stable enough.” It supports this chapter’s argument: the process cannot rely on a single generation alone.

### `EXP-01-02` · AI-Assisted vs AI-Driven comparison

This experiment asks: for the same small feature, how do manual round-trips, defect escape, and end-to-end time compare between frozen AI-Assisted and AI-Driven delivery records? Run: `python3 experiments/exp-01-02/quickstart.py --sample`. Sample at `experiments/exp-01-02/output/sample.json`.

It shows two frozen workflow records can be compared; it does not prove one workflow is universally better. It supports this chapter’s case: AI-DLC trades source of truth and gates for recoverable, auditable delivery.

### `EXP-01-03` · AI-DLC three-phase official flow reproduction (KEEP-EXT)

This experiment checks artifact completeness and checkpoint counts for Inception, Construction, and Operations trajectories against a frozen pin guide in the repo. Run: `python3 experiments/exp-01-03/quickstart.py --sample`. Sample at `experiments/exp-01-03/output/sample.json`.

It shows the three-phase trajectory on the frozen guide can be reproduced deterministically; it does not write specs.md as the only standard or validate a live portal. It supports this chapter’s boundary: specs.md is a reference implementation, not the methodology itself.

## 07 · Figure: Chapter Figure Entry Point

This chapter continues to reuse the book’s core figure `book/images/fig0-1.svg` (embedded at the book opening). It expresses not a generic flowchart but the causal structure of AI-DLC:

```text
Human judgment + AI capability
        ↓
𝓔 = Engineering with Exsecutio
        ↓
Deterministic delivery
        ↓
Feedback and scale
```

When reading the figure, note two places. First, human judgment and AI capability do not point directly to delivery—they must pass through `𝓔`. Second, feedback is not an appendix—it returns to human judgment and engineering constraints and decides how the next lifecycle begins.

If readers remember only one figure, remember this one: all AI-DLC chapters expand different segments of this chain. Independent chapter figures CH-02 through CH-10 are local expansions of this chain, not replacements for the core figure.

## 08 · Boundary: What This Chapter Does Not Cover

To keep Chapter 1 from becoming a small book, this chapter deliberately does not cover:

- The full model of human–machine responsibility allocation—that is Chapter 2.
- Intent-to-Bolt Plan decomposition detail—that is Chapter 3.
- Memory Bank and Standards engineering structure—that is Chapter 4.
- Bolt types, stage gates, and execution mechanics—that is Chapters 5 and 6.
- Verification methods, deployment/operations, and organizational scale—that is Chapters 7–10.

This chapter establishes one entry judgment only: **if AI’s generative power has already changed the cost structure of the development system, the SDLC must be redesigned around the engineering transformation of probabilistic intelligence.**

## 09 · Reader Exercise

Choose your team’s most recent experience using AI for programming and spend 10–30 minutes on the short exercise below.

1. Write the Intent for that work: one sentence stating the goal.
2. Judge whether it was AI-Assisted, AI-Driven, or Agentic.
3. List three non-delegable human judgments: goal, boundary, trade-off, or accountability.
4. List what AI actually did: propose, decompose, generate, test, fix, or record.
5. Check for four classes of `𝓔` artifacts: source of truth, stage gates, evidence chain, feedback record.
6. If one class is missing, add one minimal artifact—for example one acceptance item, one failure sample, one event record, or one reproducible command.

When done, you should answer in one sentence: did this AI use improve local efficiency, or start changing the delivery system?

## 10 · Review Notes for D15-T03

D15-T03 review should focus on five items:

- Technical boundary: do not write AI-DLC as the only correct process, or specs.md as this book’s framework itself.
- Terminology consistency: keep `𝓔 = Engineering with Exsecutio`; do not auto-replace with `Execution`.
- Evidence boundary: `EXP-01-01` / `EXP-01-02` / `EXP-01-03` are verified but each only proves diff, comparison, and three-phase trajectory reproduction on frozen fixtures; `EXP-01-03` must not be rewritten as SHIP or as full official flow deployment.
- Structural coherence: question, framework, case, experiments, figures, and exercise must serve the same core question.
- Adjacent chapter boundaries: Chapter 1 explains only why the lifecycle must be restructured, not the specific methods of Chapters 2–10.

## References

- `book/manifesto.md`: core formula, formula explanation, and boundaries.
- `book/part-00-overview.md`: AI-DLC bird’s-eye view, lifecycle map, and book narrative structure.
- `book/images/fig0-1.svg`: AI-DLC core formula and deterministic delivery loop.
- `book/toc.md`: CH-01 core question, reader outcome, reference implementation, and experiment direction.
- `specs.md-portal/pages/methodology/what-is-ai-dlc.md`: local snapshot of AI-DLC methodology entry.
- `specs.md-portal/pages/methodology/sdlc-reimagined.md`: local snapshot of AI-native SDLC methodology pages.
- `specs.md-portal/pages/core-concepts/bolts.md`: local snapshot of Bolts vs Sprint comparison.
- `progress/chapters.json`: chapter source of truth and six-phase status.
- `progress/experiments.json`: experiment governance for `EXP-01-01`, `EXP-01-02`, `EXP-01-03`.
- `progress/tasks.json`: writing task cards D15-T01, D15-T02, D15-T03.
- [AWS AI-DLC Method Definition (Amplify)](https://prod.d13rzhkk8cj2z0.amplifyapp.com), [AWS DevOps blog post](https://aws.amazon.com/cn/blogs/devops/ai-driven-development-life-cycle/): methodology source summary (CH-01 §2.5).
