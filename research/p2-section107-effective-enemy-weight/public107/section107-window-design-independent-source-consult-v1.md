# Section 107 Window design — independent Source consultation

Status: Source consultation only; no frozen window runner reviewed, no runtime or product PASS. This report checks the proposed thirteen-window design against the current public implementation. Root owns all subsequent project, Qt, Wine, native decoding, tests, application, Git, and PNG work. Reviewer executed none of those and changed no tracked file. Own stdlib text/JSON/hash/AST and compile-only were used; compile did not execute a module.

## Binding

Read and compile-only check `40227c` exited 0. Current public files:

| Path under /workspace/rougezhushou | Bytes | SHA256 |
| --- | ---: | --- |
| rouge/operator_engine.py | 156626 | f50e6b992525da0cb3daedb16a3cd4cd45f80052b063007224bd63ac8de93f50 |
| rouge/enemy_environment.py | 8213 | d55a1ad900b4dd33b030114de5f5ee5bb6f2ca2f48ddea67e686dadc7f83dd4a |
| rouge/run_modifiers.py | 6678 | c0f5de967ff160ad4ad3ad4a4823a7da158386c537297c7d032248823fe4586e |
| rouge/relics.py | 40531 | 79f5f607a247fbe366651c63ee951215a518e6a597868cd65e4212d16564e5d3 |
| rouge/app.py | 99132 | f3577a3e1e40d19b4d302e2c8e5abe498fbec635497df40f81603f0dcd7dfebf |
| rouge/damage.py | 31071 | b48c86b2f02c4ea76f9b6cbd1b32a57abd925b2d8d22e8527a0cd6cb8c61be09 |
| rouge/operator_options.py | 5328 | a9d7e474920ce4747b6216361a57c9874482a2a31cfa929280189443ea0eaa83 |

Public catalog JSON SHA256 `061079249952deda98d6b391f577cec7fa2c67a018599155df1ea11d2205a01b` was decoded by stdlib only. These are pre-107 sources, not a proof of the future full source registry count or applied candidate. Root reports original API 14 cases / 74 calls / 89 native records; this consultation did not independently decode that runtime record.

## Required correction: actual normal-call reachability

`operator_engine.py:883–913` sets Angelina S1 mode to deployment. `calculate():1396–1398` clears recharge for deployment/passive and marks deployment non-repeatable. S1 therefore has cycle None and does not call normal=True at the production gate around line 1474.

Angelina S2 is explicitly `aglna_s2_unresolved` (around lines 1362 and 1392–1394): duration and recharge are None because the actual takeoff/loop and end clock are unverified. Cycle is consequently None; normal=True is not called. Its finite isolated attack-phase reference must not be presented as a measured complete cycle. The proposed all-S2/S3 non-None assertion would be a runner blocker. Correct S1/S2 assertions are zero actual normal calls and preserved existing cycle/recharge masks; S2 duration remains None and existing conditional-reference fields remain intact.

S3 has ammo mode, 33 declared rounds at rank10, natural recovery cost30, and no deployment/nonrepeat mask. In frames mode `plan():1208–1210` derives complete duration only when the real full-plan stream emitted all declared rounds. Under the proposed persistent-target, empty timing-block fixture this is a plausible actual normal path. A Source statement is not proof that a chosen UI fixture reached it: require an actual non-None cycle/recharge and a recorded normal invocation with positive valid hits. If the actual stream cannot finish, retain the original mask and diagnose; never add a normal invocation to satisfy the test.

A transparent `Combat.plan` wrapper is appropriate: invoke the original bound method exactly once with unchanged args/kwargs, return the identical result object, and rethrow its original exceptions. Record only genuine calls made by final `MainWindow.calculate`. Restore the original method in finally. Record normal=True calls, their arguments, public `self.s` / `self.a` graphs, and the complete real return graph immediately using the approved recorder. Do not serialize the Combat instance, duplicate its invocation, or compare a separately constructed plan as though it were the production cycle. Product calculate intentionally updates scenario timeline offset, first-damage state, timing resume frames, and notes, so self.s / notes immutability is not a valid invariant. Public outer caller and durable account/run/disk pre/post conservation remain meaningful.

## Manual light oracle: exact scope and preconditions

For `ro6_n_1_1 / enemy_2002_bearmi / level0`, the public record is ELITE, massLevel4, DEF200, MR50. For the same stage / `enemy_2085_skzjxd / level0`, it is ELITE, massLevel5, DEF0, MR50. The stage's only property rune in the inspected preview changes ATK/HP on FOUR_STAR, not DEF/MR; global buffs are empty. Grade4 / zone1 has no selected-BOSS reduction, and neither target is the orb with type-specific damage factors. The selected fixture must confirm this by its actual resolution: DEF/MR match the manual inputs and damage_factor=1. A future different target or grade cannot inherit this oracle without rechecking its full consumer effects.

Clearing actual target UI and removing the single legacy56 relic then setting manual2 for the former, manual3 for the latter, while keeping all cultivation, module, level, trust, potential, rank, skill, base attack, window, frame mode, selected animation reference, continuous-attacks and timing fields fixed gives a defensible independent old-Gold light-branch oracle. Manual3 also exercises the <=3 branch for fixed4→2, but manual2 is the tighter same-effective-weight control. Manual DEF/MR setters must preserve their intended public numbers; record actual post-set UI values and actual calculate caller. Source UI ranges accept the known numbers: defense has zero decimal places, resistance one.

Do not compare the two different enemies to each other as a threshold pair. They have different DEF. Do not compare fixed-target full `run_resolution` or `relic_resolution` against manual oracle: fixed identity, provenance, held relic, missing-target notes and context are legitimately different. Compare those complete graphs to their own same-fact original fixed Gold. Components, the complete `estimate.skill`, actual normal return output and recharge_streams can be compared to the matching manual-light Gold when the above numerical and timing conditions are met. Complete original normal-plan output is suitable because its return consists of the computed fields, component graph and actual timeline, rather than the fixed target-resolution graph. Record and retain the full outputs even if a specifically justified comparison projection is needed later.

The `_relic_enemy_effects.weight_delta` is prepared once by relics.prepare and is -2 only for the eligible single held legacy56 with an active fixed target. No target leaves this rule missing/inactive: manual weight cannot establish a fixed identity. The proposed product consumes that prepared delta only in the existing weight talent comparison. No report or caller scenario rewrite is required. Fixed scenarios with manual weight0 and100 should produce identical outputs because resolve_enemy discards this manual declaration and supplies public fixed weight; both probes must be genuinely sent through the actual UI/caller. They do not test relic-count values0/100.

## Thirteen-window classification and useful assertions

Six fixed4/5 × skills1..3 plus the E1P1 and E2P3 fixed4 S1 controls give eight positive threshold crossings. E0 S1 is a no-talent control: the zero-hit/zero-total talent placeholder remains, with no new numerical contribution. Public talents select E1P1 .20/.13, E2P1 .35/.25, and E2P3 .45/.30 for light/heavy, with phase/level/potential gates in selected_talents. Use a rank genuinely open at the chosen elite (E0's chosen valid rank and E1 rank<=7); record actual training selection. Do not silently carry rank10 into E0/E1.

Fixed0/1 are already on the light side; final metadata -2/-1 is retained but does not justify a negative manual input, clamp, floor, lift or displacement rule. Compare actual numerical components/estimate to the same plain original fixture and compare candidate's signed report metadata to its gravity Gold. The legacy56 stacking rule remains unverified and is not part of this single-relic test.

Mechanist S3 should be an actual nonzero unrelated-consumer control: choose a positive window and explicit charge_count>0, verify at least one real bombardment hit and a positive independently declared charge component. Zero horizon with positive charges is rejected by damage.py:171; no actual positional or charge timeline is inferred. Changing only gravity weight must not change its components/estimate. This control is not an Angelina Combat.plan normal-path proof.

The no-target manual Angelina S1 case needs its own sequence: manual4 andmanual3 differ numerically as intended; adding legacy56 without a target leaves its weight rule missing/inactive. Compare gravity-without-target damage to that same manual weight's plain damage and preserve the missing-identity warning. It cannot follow the fixed-case invariant that manual0/100 are ignored, since manual declarations are active when target is absent.

For every fixed case, the proposed plain restoration should restore the actual target selection, held relics, manual UI weight declaration and all original numerical/timing fields before its final snapshot. Setting widgets causes genuine intermediate calculations; only enable call recording for the explicit final calculation if those intermediate calls are not part of the measurement, and state this scope. A snapshot recorder must not imply that it has certified every intermediate UI transition unless it actually captures and checks each one.

Full Candidate equality against original fixed Gold is appropriate for unchanged plain, manual and no-crossing numerical stages. Changed gravity threshold stages should retain complete native Gold and Candidate results but must use the matching independent light oracle for changed talent-dependent fields, rather than asserting equality to the known original heavy-branch bug. Non-talent components, unchanged relic/run resolutions, raw state/account/disk and unrelated public reference outputs should retain their separate same-fact Gold checks. Three actual current UI formatted texts should be saved for all stages; corrected talent-dependent texts are expected to change and are not old-Gold equality assertions.

## Remaining review/runtime gates

This consultation does not approve a runner that has not yet been written. Its future source binding must be to the actual Root749 Gold / applied750 Candidate, complete exact product transport, the same runner bytes, raw0 receipt and fresh public temporary paths. Thirteen real windows, four genuine PNGs, successful close/source guard and bounded450s remain future assertions, not measured outcomes. Native Windows/gameplay clock, S2 takeoff, displacement, negative-weight flooring, stacking, natural OCR/capture and persistent target life are not newly established.
