# Read-only engine closure: caster Amiya S1 finite-positive lifetime / range

Requested baseline `ab1a2f4`; first inspection matched this HEAD and had a clean worktree. Root advanced the shared HEAD to `5b5c61fd54c18bc5d7b6f35d22ef7eb23cdefdbc` during this audit. `git diff ab1a2f4 HEAD -- rouge/timing.py rouge/operator_engine.py rouge/uncertain_sources.py rouge/reporting.py` was empty. This agent changed no tracked files. No network, private state, game or chat was used. Gnosis 48 / Haruka 49 were not redone.

Final scope is only `char_002_amiya`, skill 1, continuous enemy-directed interval damage / mixed natural-and-attack-SP cycle. The requested term `enemy_life_s` corresponds here to public `timing.target_disappears_seconds`; there is no exact `enemy_life_s` API field in the current repository.

## Reproduction

Run from `/workspace/rougezhushou`:

```
.venv/bin/python /workspace/.continuation/p2-after-050/finite-positive-source/engine-audit-reproduce.py
```

Public input uses base ATK 1000, DEF/RES 0, window 10, continuous mode, no relics/module or manual animation overrides. Baseline, lifetime 0.1, lifetime 1 and `target_windows=[[0,1]]` all return:

- Window damage 11000 / 11 interval-reference hits; cast and phase damage 35000.
- Initial 7; declared duration 30; recharge 14; cycle 44; cycle damage 43000; cycle DPS 977.272727.
- Both `complete` and `estimate.complete` are true; `timing.complete` is false.
- Continuous timing `streams` and `recharge_streams` are empty and neither `phase_clock_unbound` nor `resource_and_damage_shared_clock` is present.

Zero lifetime is an existing explicit absence control: damage 0, recharge 30, cycle 60, initial still 7. Empty range `[]` is also ignored by this generic continuous path and gives the baseline numbers; this is separate existing evidence, not a proposed zero-range reinterpretation.

`engine-audit-public.json` includes the full scoped outputs, public report metrics, current HEAD and relevant source SHA256 values.

## Exact implementation points

1. `rouge/timing.py:178-196`: target windows are validated and converted to frame ranges; `selectable()` combines range availability with lifetime.
2. `rouge/timing.py:232-259`: continuous mode instead computes `floor((duration-ready)/interval)` and assigns `ready+(i+1)*interval`. Only lifetime exactly 0 clears enemy events at lines 246-247. Positive lifetime, target windows, movement/interrupt availability, and projectile phase are not applied. Normal-cycle availability offset is likewise not applied by a lifetime check in this branch.
3. `rouge/timing.py:301,324,356-360`: the frames branch checks acquisition and then impact lifetime, with strict half-open disappearance boundary. Explicitly placed frame impacts are therefore clipped, unlike the continuous interval estimate.
4. `rouge/operator_engine.py:279-294,431-432`: caster Amiya regular attacks receive synthetic continuous `times_seconds` via `attack_times()`; attaching those times does not supply a verified native acquisition/impact phase.
5. `rouge/operator_engine.py:1270-1288`: caster Amiya mixed SP `time_to_charge()` increments by normal interval plus natural recovery and talent SP. It contains no positive-lifetime/range check. Only continuous lifetime exactly 0 takes the existing natural-only reference at lines 1282-1284. Frames uses `mixed_charge_seconds` instead.
6. `rouge/timing.py:133-138`: initial-charge helper deliberately removes skill-relative availability/lifetime; the after-cast finite lifetime is not evidence to alter initial 7.
7. `rouge/timing.py:372-384`: `phase_totals()` clips components only when `times_seconds` exists, and only against its caller's boundary; unplaced totals are retained. Probe boundary 5: placed `[1,5,9]` / total30 yields10, unplaced total30 yields30. No min-life rule exists here.
8. `rouge/operator_engine.py:1408-1426`: cycle is duration+recharge, normal phase is then planned from recharge, and totals are added; only frames applies cycle-boundary clipping.
9. `rouge/operator_engine.py:1451-1479`: complete booleans and recharge/cycle/damage/DPS/HPS scalar fields are assembled; no restricted-continuous mixed-SP guard currently exists.
10. `rouge/timing.py:389-395`: continuous annotation returns after target-scope notes, before the shared-resource/damage clock flag used for frames.
11. `rouge/reporting.py:263-267,355-369`: public timing report directly renders recharge/cycle; damage report directly renders cast, phase, window and cycle DPS from those fields. Unknown actual cycle must reach these consumers, not only a metadata note.
12. `rouge/uncertain_sources.py:5-40`: existing damage aggregate masker only reacts to component `actual_total=None`; a recharge-only uncertainty does not trigger it. Setting a descriptive timing flag alone also does not change cycle output.

## Narrow guard recommendation for parent

No edits are proposed by this read-only child. Preserve established numbers only in a clearly identified conditional interval reference. For the restricted caster Amiya S1 continuous enemy-directed interval mixed-SP cycle, mark actual post-skill recharge and actual cycle unknown, then propagate to cycle damage, cycle DPS and other cycle-dependent totals/rates. Preserve initial 7, nominal duration30, cultivation parameters and exact zero-life control; do not replace with natural30 as a native actual, and do not clip with `min(life,window)` or invent a first hit/target reacquisition phase.

Set explicit scoped metadata (`phase_clock_unbound=true`, `resource_and_damage_shared_clock=false`, complete false, and the precise missing native acquisition/release/cycle-clock evidence). Do not install a global rule that changes friendly healing, other skills, instant damage, Gnosis 48 / Haruka 49, or separately supported event sources. If a model consumes explicitly classified timestamp callbacks through `sp_events`, those establish only their callback evidence; they are not a reason to fabricate regular enemy-directed attacks or to broaden this guard.

If cast/window numbers remain exposed, label them as conditional interval amounts; never relabel synthesized `(i+1)*interval` timestamps as actual. Whether to mask those cast/window fields is a separate product scope decision; the concrete minimum closure is unknown recharge/cycle plus all dependent cycle aggregates and metadata. Do not call a positive-life/range scenario fully supported merely because the legacy interval quantities are preserved.

## Validation

` .venv/bin/python -m unittest tests.test_timing tests.test_empty_enemy_scope tests.test_friendly_scope_report ` ran 31 tests, all passed. The public reproduction ran six scoped cases and a placed/unplaced boundary helper probe. These checks verify current behavior, not native timing. Source data parameters do not establish missing activation order, first-hit phase or lifetime behavior; source audit remains with the parent.
