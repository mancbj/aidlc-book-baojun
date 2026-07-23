# Experiment Schema

## Base Fields

- id、name、chapter、triage、effort
- inputs、outputs、metrics
- command、acceptance
- status、updated

允许 triage：`SHIP`、`KEEP-EXT`、`ALREADY`。
允许 effort：`S`、`M`、`L`。
允许 status：`planned`、`ready`、`in-progress`、`verified`、`blocked`。

## Conditional Fields

### SHIP

- repository_path
- readme_path
- sample_input
- sample_output
- test_path

### KEEP-EXT

- external_source
- pinned_version
- configuration
- reproduction_steps
- sample_result

### ALREADY

- reused_implementation
- cross_chapter_references

只有满足对应条件字段并达到 acceptance 的实验才能标记 verified。

