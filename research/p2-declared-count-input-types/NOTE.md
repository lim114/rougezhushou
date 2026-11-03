# Section 57 external draft: declared count bool qualification

The draft is source-closed and ready for integration after root completes its
prior sections. No tracked file was edited. Its real frozen calculation/test
baseline is section 51, `fba536e118906f58ed2bcef359480f76e0ae4d67` (clean),
with 2,171 copied public files. Root later committed sections52,53 and54;
`integration-observation.json` separately records observed54 `195b3dae` with
root's pending55 changes. This frozen
matrix is not represented as a post-53/54/55 integrated-head validation.

## Public defect and narrow guard

These four declaration fields accept raw JSON booleans as integer 0/1:

| Active public skill / field | Before, `True` at base_attack=1000, rank10 | Existing numeric domain |
| --- | --- | --- |
| `mechanist` S2 `shield_break_count` | Same full result as count1; section51 conditional damage5000 | finite nonnegative integer-valued count |
| `mechanist` S3 `charge_count` | Same full result as count1; conditional collision damage11400 | finite nonnegative integer-valued count |
| `silverash` S2 `activation_count` | Same full result as count1; own damage3800 | finite nonnegative integer-valued count |
| `silverash` S2 `deployment_stacks` | Same full result as stack1; beneficiary damage7600 at companion_attack=2000, plus own3800 | finite nonnegative integer-valued count, at most2 |

`public-counterexamples.json` retains every active bool example in both timing
modes, its complete baseline result, paired integer-control equality and the
new explicit error. `False` is likewise accepted as 0 in all four fields.

Call chain: public `calculate_damage` → `_prepare_damage` first copies the input
and validates skill/rank/cultivation/unlock → relic/run preparation → legacy
`_skill_damage_base`, which copies the prepared request and converts all four
legacy count fields with `float`, `is_integer` and `int` → skill branch and
`build_estimate` → charge finisher (and shield finisher once53 is integrated)
→ report. The helper's local normalization does not normalize the separate
prepared scenario used by finishers. `float(True)` and `int(True)` both produce1,
so later integer validation cannot identify the original bool.

The six added lines in public `_prepare_damage` inspect the raw value before
relic/engine conversion and reject bool only for the exact active skill/field
mapping. They reuse the existing field-specific error text:

> `{field} 需要非负整数；部署触发叠层最多为 2。`

No global integer helper or legacy conversion loop is changed. Inactive fields
keep their existing behavior in both engines, including legacy's existing
global non-bool validation and extended's ignored unrelated fields. Genuine
checkbox booleans retain their behavior. The guard preserves existing
skill/rank/cultivation/unlock error priority; when an active bool accompanies
another downstream invalid value, the new count type error can precede that
downstream error. It does not promise unchanged precedence for every request
containing several invalid fields.

## Sources, fields and limits

Pinned ArknightsGameData commit:
`a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`.
Both still-present original character/skill files were freshly rehashed;
`source-receipt.json` preserves exact bindings and all30 rank records:

- `character_table.char_4230_mcnist.skills[1]` → `skchr_mcnist_2`;
  `skill_table.skchr_mcnist_2.levels[0..9]` describes barrier destruction,
  conditional AoE magical damage and ammunition. Rank10 `atk=1.5`,
  `atk_scale=2`, `trigger_time=8`.
- `character_table.char_4230_mcnist.skills[2]` → `skchr_mcnist_3`;
  `skill_table.skchr_mcnist_3.levels[0..9]` describes structural-principle charge
  collision and stopping. Rank10 own attack+280%, collision scale3.
- `character_table.char_1045_svash2.skills[1]` → `skchr_svash2_2`;
  `skill_table.skchr_svash2_2.levels[0..9]` distinguishes own skill and beneficiary
  deployment trigger using the beneficiary's attack; description explicitly
  says at most two stacks and `max_stack_cnt=2`. Rank10 `atk_scale=3.8`.

Committed `research/p2-charge-clock/source-receipt.json` and
`research/p2-empty-enemy-scope/source-receipt.json` are rehashed and retained as
evidence for the established independent-source scope. The section53
`research/p2-shield-break-reference/{NOTE.md,source-receipt.json}` is rehashed
from its external section51-based draft and explicitly identified as such.
No new native event clock or source attachment rule follows from this type fix.

`rouge/app.py:639..662` uses QSpinBox integer values: charge/shield/activation
controls0..100, activation default1; deployment stacks0..2. Serialization at
1032..1034 uses `.value()` directly. UI100 is not imposed as an API or native
event limit: independent probes and the main matrix preserve accepted1000
for the first three declarations. The raw ammunition8 and charge-capacity
parameters do not establish a whole-scenario upper bound; this draft introduces
none. Existing full-cast and collision-time unknowns remain conditional
references, with no callbacks, event input, phase or placement added.

## Field-specific compatibility and separate53 regression

All four retain integer floats and ordinary integer numeric strings such as
`1.0` as a Python number and `"1"` as a string. Field-specific existing string
behavior is preserved rather than generalized:

- On section51, `shield_break_count`, `activation_count` and
  `deployment_stacks` also accept `"1.0"`; `charge_count="1.0"` already fails
  in the old charge finisher's `int(raw)` call. The latter remains unchanged.
- Independent public51-versus-external53 comparison found that53's new shield
  finisher similarly uses `int(raw)`, introducing a regression for the formerly
  legal `shield_break_count="1.0"`. Root fixed this separately within53 at
  `5362de55358cda5d856e293e89c9a99ea45e5e29`, reusing the core's already
  validated integer-valued numeric conversion. The independent reviewer then
  verified the real committed53 public result: string `"1.0"` equals int1,
  conditional5000 remains, actual damage remains unknown, and input is intact.
  `independent-root53-string-check.json` retains that distinct check. The57
  patch does not mix in that extra change, and its main matrix remains frozen51.
- `review.md` and `independent-{root51,draft53}-results.json` retain the actual
  paired public observations and their source/root provenance. They are not
  evidence that53 was already committed when those calls ran.

## Fresh verification

Main matrix: 1,876 scenario pairs. Each package runs1,876 primary public calls
plus2,784 independent integer/omitted controls, or4,660 calls per package.
Baseline plus draft therefore totals9,320 matrix `calculate_damage` calls:

- 16 active bool outcomes change from accepted integer-equivalent results to
explicit ValueError; paired valid integer controls remain identical.
- 1,860 complete results or existing errors remain identical, including1,376
inactive bool cases over all87 supported skills,184 non-bool numeric/error
cases,288 integer scope cases and12 genuine checkbox cases.
- Zero/default counts, stacks2 versus3, integer floats/strings,1000 declarations,
negative/fractional/nonfinite values, zero windows, zero enemy lifetime, ranks
1/7/10, manual-duration parameters and both timing modes are included. Caller
inputs and catalog hashes remain unchanged.
- Shared unchanged-outcome-hash sequence SHA256:
  `01d14cf3ea3d1bf616ff9f56a3f4f60175259e33d49cb475b36e138d0932ec41`.

Fresh test runner:78 related baseline tests pass; the seven new regression
methods yield17 expected failures against baseline; draft85 related+new tests
pass. The initial copied-directory discovery ran87 tests and hit two unrelated
missing prerequisites: a retired test helper and an untracked screenshot used
by a recognition test. That initial attempt is recorded in `test-receipt.json`.
The final runner selects calculation modules and four pure enemy/state methods,
without copying an untracked/private screenshot or claiming the omitted
recognition/retired-source tests passed.

Independent review checks and public observations are retained in `review.md`,
`draft-review.md` and their independent artifacts. Root owns later integrated
tests, runner registration and full available batch checks.

## Patch and reproduction

`section57.patch` contains only the six-line guard in `rouge/damage.py` and
`tests/test_declared_count_input_types.py`. Its insertion hunk uses following
`prepare` imports as context so54's preceding active-count guard can coexist;
the final patch passed `git apply --check` on observed54 with root's pending55
changes. Root should add
`tests.test_declared_count_input_types` to its verification runner at integration.

From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python run_tests.py
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python public_matrix.py /workspace/.continuation/p2-declared-count-types/baseline baseline-matrix.json
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python public_matrix.py /workspace/.continuation/p2-declared-count-types/draft draft-matrix.json
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python compare_matrix.py
```

No Wine, Windows UI, current game or desktop chat validation was run by this
external task. No private state, game action, network bypass or event input was
used.
