# Section 51 rebuilt after the cloud restart

The previous temporary directory and its patch/receipts were lost on restart. This directory is a new persistent reconstruction. Every validation count below comes from new executions against a fresh public source freeze; prior /tmp runs are not claimed as current validation.

The frozen baseline is project commit `c780e0d57616d1a4c5b5f2063e1dfb42b6005344` plus the then-current uncommitted section 50 `rouge/timing.py`. `baseline-freeze.json` records the exact 2,170 public package/test files and hashes, dirty status and freeze time. After the parent committed section 50 as `ab1a2f49332e9dbb577eb3ffa1a497c0bb969fa6`, all 2,170 public files still matched the frozen baseline (`integration-head-check.json`). Private state and account data were not copied. The new patch is `section51.patch`; it changes exactly four existing guards in `rouge/catalog.py` and adds `tests/test_training_input_types.py`. All work is outside the checkout at `/workspace/.continuation/p2-qualification-051`; no tracked file was edited or committed. `git apply --check` succeeded against the current checkout.

## Public input problem and narrow change

JSON boolean values currently pass `isinstance(value, int)`: `elite:true` calculates as E1 and produces training text `精英 True`; `level:true`, `potential:true` and active `module_level:true` similarly act as integer 1. The existing skill/rank guards already reject boolean values. The patch adds the same boolean exclusion to the existing elite, level, potential and active module-stage rejection guards, preserving the existing error text.

The complete path is `damage.calculate_damage` → `_prepare_damage` → `catalog.operator_attributes` → `prepare_run`/`relics.prepare` → `_evaluate_damage` → legacy calculation or extended `Combat.calculate` → report construction. `_prepare_damage` copies the request and strictly validates skill/rank first, then passes these four cultivation values directly to `operator_attributes` **before any integer conversion**. No later step converts them into ints. Extended `Combat` stores the original values in `estimate.training`; `format_report` formats elite/level/potential directly. Core event-count/skill-rank conversions are unrelated and occur after the shared cultivation guard, so they cannot bypass it.

Fresh paired public example, retained in `public-input-baseline.json`:

```json
{"operator":"char_298_susuro","skill":1,"skill_rank":7,"elite":true,"level":40,"potential":1}
```

Both this boolean input and the matching `elite:1` request have attack 417 and total healing 5629.5 in the old baseline. Their metadata differs: the first report says `精英 True · 等级 40 · 潜能 1 · 信赖加成进度 100%`, the second says `精英 1`. In `public-input-draft.json`, the bool request receives `ValueError("精英阶段需要为 0、1 或 2。")` while the integer request keeps its result. Equivalent cases are saved for false elite/rank 1, true level/potential and active true module stage. Skill/rank bool requests retain their already-existing errors.

The module guard remains under the existing `if module_id` branch. No-module ignored stage values remain compatible, including booleans, numeric strings, floats and null. No default level, accepted integer boundary, error wording, trust/floating parameter, skill rank/use limit, public API or UI was changed. No new native game mechanism is introduced.

The standard UI already supplies integer values: level uses `QSpinBox.value()`; elite comes from integer phase indices/`range(3)` emblem keys; potential uses integer 1–6 icon keys; module stage is a profile integer stage or `int(regex_group)`. The UI read-only cultivation labels do not require booleans. This is code/protocol evidence; this subtask did not run an actual UI.

## Fresh validation

- `related-final.log`: six new methods plus five existing relevant modules pass **95 tests**, zero failures/errors/skips. The new methods cover public `operator_attributes`, full `calculate_damage` through all three legacy aliases and extended Susuro/patch medic Amiya, both timing modes, false/true, existing field errors, valid integer boundaries, default `level=None`, active module stages, ignored no-module stages and input/catalog isolation. Kaltsit/Silverash have no active modules in this calculated catalog; active module-stage cases use the three profiles with modules. Five existing modules were freshly copied from the current public checkout; the six new methods were reconstructed in this draft.
- `integer-baseline.json` and `integer-draft.json`: **4,596 full public calculation pairs** and **678 direct public attribute pairs** are equal. Calculation records hash the complete JSON output, including metadata/report/timing. The sweep covers 32 calculated forms/87 skills, available phase/skill combinations, levels 1/cap, potentials 1/6, rank boundaries, both timing modes and module stages at unlock boundaries. These are **existing API-accepted integer calls**, not a statement that every E0 rank is native-valid. The two new artifacts share SHA256 `0df75ae914675f9e460262e6dab151ee9748a57c63851f6780526f4617f86ec4`.
- `comparison.json` compares 42 input controls: only five formerly accepted bool cases change to the existing field errors; the other 37 controls keep their exact outcome. Existing float/string/default behavior does not change.
- Each public-input artifact records a fresh **2,610 internal `_prepare_damage` integer-admission matrix**; 1,542 calls are accepted and the whole matrix is equal before/after. This matrix is an implementation-policy observation, not native legality evidence. Both cached catalogs retain their hashes and public requests remain unchanged.
- Independent read-only review checked the four-line patch, all 2,170 frozen hashes and identical integer artifacts. The reviewer ran the six tests against baseline and draft: baseline detects 69 failed boolean subcases, draft passes all six methods. That baseline result is expected defect evidence, not a passing regression. The review receipt states these as separately reported reviewer results.

Only `draft/rouge/catalog.py` differs from the baseline package. Reproduction scripts are preserved here: `freeze.py` (protects an existing freeze from overwrite), `public_sweep.py`, `reproduce_inputs.py`, `source_audit.py`. Tests run with the draft directory as working directory/PYTHONPATH and `PYTHONDONTWRITEBYTECODE=1`; no cached live package or fake dependency import was used. The reconstructing agent had no failed implementation/test execution in this new run. Earlier /tmp fixture/archive mistakes were historical preparation failures and were not reused as new runs.

## E0 skill-use limit stays unknown

Current pinned character/skill raw files were rehashed successfully and Susuro's exact `$.char_298_susuro.allSkillLvlup[0..5].unlockCond` records re-read: upgrades to ranks 2–4 require PHASE_0/level 1; upgrades to ranks 5–7 require PHASE_1/level 1. Those records contain training costs and establish account training requirements. They do not establish whether a roguelike operator restricted to E0 can use a previously trained common skill rank.

The earlier temporary topic/roguelike/patch/gamedata-constant raw files are no longer present and were **not** rehashed in this reconstruction. The committed section 48 `research/p2-gnosis-isw-a-reference/source-receipt.json` was read and its persisted `gamedata_const` receipt reused, explicitly as a historical source receipt. Its old `/tmp` local path is not evidence that the raw file now exists. This input-type fix does not need a new mechanism download. `source-receipt.json` distinguishes current raw hash checks from historical receipt reuse and missing raw files.

The actual calculation catalog still has 32 forms/87 skills, all with three phases and ten skill ranks, rarities 4/5/6. The three aliases map to `char_1052_kalts2`/`char_1045_svash2`/`char_4230_mcnist`; the other 29 public form IDs include the two patch Amiya forms. Current raw character mapping/phase caps/skill IDs/unlocks match all 30 non-patch forms; the missing patch raw source is not claimed to have been freshly revalidated. There is no calculated 1–3-star form to justify a generic lower-rarity cap.

Existing UI unknown-rank defaults E0/E1 to 7 and prior token tests use E0/rank 7; they are compatibility evidence, not new native E0 proof. E0 use eligibility remains explicit unknown until a fixed roguelike recruit/use protocol, explicit authoritative rule or independent current-run observation closes it. This draft does **not** reject E0 rank 5–7, change the rank-7 preview default or impose a maximum 4.

The parent will integrate after section 50's full validation and perform project checks/checkpoints. This subtask does not claim full regression, Wine, Windows, game/current hot-update or actual UI validation.
