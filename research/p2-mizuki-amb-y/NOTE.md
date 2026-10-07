# P2 draft 037 · 水月 AMB-Y 原版天赋条件参考与隐藏能力边界

Draft only. Base checkout: `codex/p2-development` at `a51c1560e1dc0685b5149534899da410a13ccf77`. Changes and checks are confined to `/tmp/p2-draft37`; this is not a committed section, native validation, or a completed batch receipt.

## Evidence reviewed

- Existing section017 and `tests/test_mizuki_talent_identity.py`: `uniequip_004_mizuki` has a same-identity `TALENT_DATA_ONLY` overlay with null name and the original damage parameter. Its fallback does not establish AMB-Y semantics.
- `/tmp/p2-audit/remaining-independent/summons/mizuki-amb-y-source-receipt.json`: pinned original character, skill and module data at `Kengxxiao/ArknightsGameData` commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`. All three current file SHA256 values were independently rechecked before the draft.
- Original character selector `character_table.char_437_mizuki.talents[0].candidates`: visible `创伤性癔症` uses prefab `1`; E2 `attack@mizuki_t_1.atk_scale=.5`, maximum target `1`.
- Original module selector `battle_equip_table.uniequip_003_mizuki.phases[1/2].parts`: E2 level60 hidden unnamed `TALENT` index0 uses **different prefab `10`**, with only `hp_ratio=.05/.1`, and resource keys `mizuki_equip_2_2_p1` / `mizuki_equip_2_3_p1`. This is not the same-identity index0 data overlay from section017.
- Separately, named visible `反移情` index1/prefab2 `TALENT_DATA_ONLY` raises the below-half attack bonus to `.15/.20`, or `.17/.22` at potential5+. Its description states recovery of 5%/10% maximum HP for each kill; it does not prove the hidden prefab's attachment, callback, or timing.
- Skill1 M3 selector `skill_table.skchr_mizuki_1.levels[9]`: the first-talent multiplier is `3`. Existing public reproduction contains 18 skill/stage/unlock cases and shows the original reference being lost at level60 stages2/3.
- Existing targeted GitHub public repository search receipts were read. The initially known ArkDamage repository did not exist; successful repository searches did not provide the missing native attachment source. This draft did not repeat that search without a new lead or use PRTS/private state.

Source hashes:

| Original table | SHA256 |
| --- | --- |
| character_table | `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697` |
| skill_table | `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca` |
| battle_equip_table | `006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460` |

## Supported draft scope

Only the reviewed `char_437_mizuki` / `uniequip_003_mizuki` pair, hidden `TALENT` index0/prefab10/name-null, and an existing named `.5` first talent receive the fallback. The existing visible talent is copied and marked `reference_only`; its original identity and blackboard stay separate from the hidden module ability fields. No hidden talent values are merged and no new talent attachment is declared. Other operators/modules, visible second-talent overlays, potential gates, and module cultivation gates retain their current behavior.

The preserved reference is not actual module damage. With manual attack1000, skill_rank10 and no below-half bonus:

| Source | Conditional first-talent per-hit damage before mitigation |
| --- | ---: |
| S1 | 1500 (`1000 × .5 × 3`) |
| S2 | 650 (`1300 × .5`) |
| S3 | 1250 (`2500 × .5`) |
| Normal/recharge attack | 500 (`1000 × .5`) |

The previous audit's `raw_expected_per_hit=500` for S2/S3 is an unbuffed normal-attack reference; it is not the M3 skill per-hit value. Skill references apply the existing skill attack bonus and normal damage mitigation.

Affected conditional arts have no scheduled timestamps. Possible arts are marked with unknown actual totals in every full/window/normal plan. Existing `mask_pending_damage` retains physical source subtotals and masks combined cast/phase/window/cycle damage, DPS and talent actual hit counts. Zero-hit arts stay zero. S1's existing actual-end, recharge and cycle unknowns remain unchanged.

No Mizuki kill-count or kill-clock input exists. The exact native `TALENT` add/override CFG, prefab10 implementation and current hotupdate were not migrated. Therefore hidden attachment, retention of the visible first talent in an actual AMB-Y combat instance, kill attribution, callback timing and the amount of actual extra recovery remain unknown. The draft does not schedule recovery or convert the hidden `hp_ratio` into a numerical healing component. The prior modeled healing zero is retained only in `known_healing_subtotals`; actual aggregate healing for a positive observation/cast/cycle is unknown. A zero observation establishes zero observed recovery. Empty owner/current-target windows, current-target lifetime0 or main-body interruption do not exclude kills of other enemies, so they do not establish zero extra recovery.

The report labels the original talent as a conditional reference, names the unknown extra recovery, and explains why the physical/healing subtotals cannot be used as complete output. No actual talent stacking, game sampling, native Windows check, chat action or private-state check is claimed.

The existing final relic scaler multiplied top-level `total_healing` without a `None` guard. The new unknown recovery exposed a public crash with 活玫瑰. The draft adds the same `None` guard already used for estimate healing fields; 活玫瑰/苍白花冠/涌动之餐 retain unknown recovery and still preserve numerical observed zero for a zero observation.

## Sandbox validation

`/workspace/rougezhushou/.venv/bin/python -m unittest tests.test_mizuki_amb_y_reference tests.test_mizuki_talent_identity tests.test_mizuki_s1_reference tests.test_damage tests.test_report tests.test_timing tests.test_relic_events_022 tests.test_drone_traits tests.test_relics tests.test_relic_extension tests.test_relic_mechanisms_053`

Final run from `/tmp/p2-draft37`: 170 tests, 160 passed, 10 existing skips, no failure/error. The new suite contains 14 tests including the 18-case public matrix, normal/recharge500 reference, stage/potential second talent gates, combined damage masking, separate hidden metadata, recovery unknowns even for absent current target, zero observation, unchanged controls, strict guard exclusion, input/catalog immutability, all three global healing multipliers, and public formatted report. Linux sandbox calculation only; no native game or UI validation. Sandbox checks do not establish current-client timing or full native regression.

The first sandbox run exposed an invalid test fixture (elite1 with skill_rank10). The fixture was corrected to the valid elite1 skill_rank7 control, giving the existing `1000 × .3 × 2.3 = 690` conditional S1 reference. No production behavior was altered to satisfy the fixture.
