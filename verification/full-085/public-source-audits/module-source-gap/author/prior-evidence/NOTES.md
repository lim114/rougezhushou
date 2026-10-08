# Section 55 external draft: module qualification in reports

Frozen baseline: `fba536e118906f58ed2bcef359480f76e0ae4d67` (section 51),
2,170 public files. The checkout was clean at freeze. All implementation and
verification work in this directory is external; no tracked file was edited.

## Concrete defect and narrow change

Public input:

```json
{"operator":"mechanist","elite":2,"level":59,"skill":1,"skill_rank":7,"timing_mode":"frames","module_id":"uniequip_002_mcnist","module_level":3}
```

`calculate_damage` first calls `catalog.operator_attributes`, which validates
the module identity and stage, then excludes its attributes below the existing
elite/level gate. The legacy engine reaches `estimate.build_estimate`; that
function previously appended “当前模组基础属性已参与估算” whenever a module ID
was requested. The above E2 Lv59 input therefore has the same attributes and
calculation as the no-module input while `format_report` claims participation.
E1 Lv80 and E0 Lv50 also reproduce the defect. Stages 1, 2 and 3 are affected.

The draft changes only report notes in `rouge/estimate.py` and
`rouge/operator_engine.py`. Legacy appends its exact existing participation note
only when the same established elite/level gate passes. Both engines explain
an unqualified request using:

> 所选模组未满足当前精英阶段或等级门槛，本次未计模组基础属性与能力覆盖。

Extended already avoids its participation note when no module parts are
selected; its change adds the consistent inactive explanation. Eligibility is
checked using catalog metadata, independently of whether an eligible stage
has parts. The requested `estimate.training.module_id` and `module_level` are
preserved. Arithmetic, module/talent selectors, errors, `complete` semantics,
result schema, skill-rank policy and default cultivation are unchanged.

## Source closure

Pinned game-data commit:
`a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`.

| Product form / exact original selector | Original elite gate | Original level gate | Public boundary checked |
| --- | --- | --- | --- |
| `mechanist` → `char_4230_mcnist`; `uniequip_table.equipDict.uniequip_002_mcnist` | `PHASE_2` | 60 | E1 Lv80, E2 Lv59, E2 Lv60, E2 Lv90 |
| `char_298_susuro`; `uniequip_table.equipDict.uniequip_002_susuro` | `PHASE_2` | 40 | E1 Lv60, E2 Lv39, E2 Lv40, E2 Lv70 |

The exact original uniequip records are retained in committed research:

- `research/p2-token-duration/source-receipt.json` SHA256
  `fc4c88b5af96f3041ea8d5679951ef2e148176796ebb9c8832687c697a72ad10`.
- `research/p2-susuro-recipient-factor/source-receipt.json` SHA256
  `f965081890f3942de2e3c447193f76709c8f7f4e62e22aec1b3471e603e34c8c`.
- Both receipts identify original uniequip table SHA256
  `b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9`.

`source-receipt.json` rehashes those committed receipt files and preserves the
exact selectors plus current normalized module records. The original uniequip
file was lost during the machine restart, so its historical table SHA is reused
as a historical receipt; it is explicitly not represented as a fresh raw-file
rehash. The normalized elite/level fields were freshly checked against these
retained exact records. No hidden module part is needed to establish this gate.

The still-present `character_table.json` was freshly rehashed:
14,975,251 bytes, SHA256
`68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`.
All 155 normalized, named base-talent candidates in 30 non-patch forms have
phase/level/potential qualification fields exactly matching their own original
candidate selectors. Across E0/E1/E2, min/cap levels and P1–P6, 1,080 selected
talent cases respect those fields. Existing catalog omission of 16 null-name
raw candidates is recorded, with no new conclusion about their native
attachment. This verifies selected candidate qualification, rather than
claiming exhaustive coverage of every hardcoded ability or native script.

## Fresh public verification

The matrix covers all 34 catalog modules in 29 product forms, all stages 1–3,
E0/E1, E2 one level below the gate, exactly at the gate, and at the phase cap;
both `frames` and `continuous` use `calculate_damage` and `format_report`.
Each of 1,020 requested-module scenarios is paired with the no-module scenario,
for 2,040 public calls per frozen package and 4,080 matrix public calls across
baseline plus draft.

- 612 unqualified cases: requested and absent-module attributes, selected
  talents/parts, all numerical output and clocks agree. Requested training is
  retained; no module parts are selected.
- Baseline has 18 incorrect legacy participation claims. Draft has zero.
- Baseline and draft match in every result field except `notes` for all 1,020
  pairs. All 408 eligible full results and all 1,020 no-module full results are
  identical. The shared non-note result-hash sequence SHA256 is
  `a14dbe4f4b4207f138c5972ea0b81f5406f178e479d85f24b8a6da5a7ec06529`.
- Fresh related baseline run: 97 tests pass. The six new regression methods
  produce 26 expected failing subcases against baseline. Draft runs those six
  plus all related tests: 103 tests pass. Logs and command receipts are retained.

The broader matrix uses the established current catalog gates; the exact
original source closure above establishes the concrete defect and guards
against a universal Lv60 assumption. This audit does not introduce a new gate
or certify hidden parts as attached abilities.

## Files and reproduction

- `section55.patch`: only the two report branches and
  `tests/test_module_qualification_notes.py`; `git apply --check` passed against
  the unchanged current checkout at section 51.
- `public-counterexample.json`: complete before/after/no-module result and
  formatted report for the concrete E2 Lv59 example.
- `baseline-matrix.json`, `draft-matrix.json`, `matrix-comparison.json`: all
  public inputs, result hashes, preserved cultivation and comparisons.
- `baseline-examples.json`, `draft-examples.json`: complete example results and
  reports for mechanist, Susuro and Mizuki.
- `source-receipt.json`, `baseline-freeze.json`, `draft-receipt.json`,
  `test-receipt.json`: source records, file hashes and new-run provenance.

From this directory, using the existing project venv:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python public_repro.py ./baseline
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python public_repro.py ./draft
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python run_tests.py
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python public_matrix.py ./baseline baseline-matrix.json baseline-examples.json
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python public_matrix.py ./draft draft-matrix.json draft-examples.json
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python compare_matrix.py
```

The original matrix artifacts record absolute package paths; reproduction
with relative paths changes the outer package-path field/file SHA, while the
scenario results and shared non-note result hashes remain the same. Use the
absolute paths in `test-receipt.json` and the matrix package-path fields for
identical artifact paths.

No Windows UI, game, desktop chat or native attachment validation was performed
for this external draft. Root owns integration and required batch checks. E0
rank 5–7 use eligibility remains unknown; this work does not infer a use cap
from skill-training promotion requirements.
