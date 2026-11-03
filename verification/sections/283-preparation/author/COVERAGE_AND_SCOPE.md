# 283 evidence-first scope decision (preparation only)

## Existing work must not be counted again

The primary five panels are not missing a cultivation/rune/talent/skill model.
catalog.operator_attributes provides elite/level/trust/potential/module basis;
relic_attributes splits real source-key rune channels before the ordinary battle
layer; estimate.build_estimate and operator_engine.Combat calculate the base
panels; calibration.panel_layers and relic_panel_diagnostics already expose
four-layer values and source counterfactuals. Section056 researched120 source
entries and its layer correction;065 established attack-speed attribute20 versus
timing600.264 supplies level/model comparisons. Repeating those as five new
getter diagnostic queries would be duplicate work and should not count283.

273's reusable native getter/cache/calculation module only admits13/19, and282
adds14/30 plus its real slot0/init/dirty-to-timer chain. Neither currently binds
the five primary Entity getter channels to a native panel-calculation finalizer.
This is an actual gap in source-qualified numerical/typed-field coverage, but it
does not prove any current small supported model input is numerically wrong.

## Fresh primary candidates and established facts

Pure-file extraction, currentDLL583b04ff... and metadatad3fede17...; no game code
executed. common-panel-native-candidate.json contains9selected methods, plus
panel-writer-helper-candidate.json with FP.AsFloat and an unnamed round helper.
No whole callgraph closure is asserted: reflection, dynamic dispatch, encoders,
current metadata objects, decode state and several helper callees remain opaque.

| Primary method | Index / VA | Source fact |
|---|---|---|
| Entity.maxHp |66454 /1807073a0|Ordinary attributes getter then GetValue0, no integer rounding getter |
| Entity.atk |66458 /180701b30|Ordinary attributes getter then GetValue1 |
| Entity.def |66459 /180702f20|Ordinary attributes getter then GetValue2 |
| Entity.magicResistance |66460 /180706f20|Ordinary attributes getter then GetValue3 |
| Entity.attackSpeed |66468 /180701bd0|Ordinary attributes getter then GetValue7 |
| RoguelikeBattleManager._ApplyFinalAttributes |85517 /180d06190|Independent field metadata/reflection read; Single->FP; (raw+add)*(ONE+mult)*scaler; metadata rangeClamp; typed writer |
| AttributesData.WriteAttributesField(FP) |30792 /18231b050|FP.AsFloat then calls Single overload; not direct Int32 FP truncation |
| AttributesData.WriteAttributesField(Single) |30791 /18231ad20|Runtime type choice; ObscuredInt path uses Single->Double, unnamed half-even helper, CVTTSD2SI, encoding and reflection assignment |
| FP.AsFloat |VA1866fae20|CVTSI2SS signed64 raw -> MULSS2^-32, no fixed actualMXCSR established |

The constructor-bound field attributes decoded in common-panel-field-attributes-283.json
give maxHp(min1), atk(min0), def(min0), MR(min0,max100), AS(min20). The existing
30777 constructor and range helper were already proved in273/274;30778 must be
bound for the explicit MR upper. No AS600 attribute upper is present. Layout
metadata has HP/ATK/DEF as ObscuredInt and MR/AS as ObscuredFloat. Reuse273's
ordinary four-bucket formula, including max(0,MULT), only at the ordinary layer;
the rune finalizer above does not contain that multiplier clamp before its final
range clamp. Do not splice ordinary and rune formulas together.

The raw round helper at18000cec0 has no named metadata identity in the selected
map; it must not be called Unity.Mathf.RoundToInt merely by similar behavior.
Its floor/ceil/fraction callees can reuse280 primary byte/Intel facts after exact
join validation. Safe small Single half-even arguments are an established route;
the preceding Int64->Single conversion is not exact for every FP raw value.

## Recommended meaningful group, only if integrated into the main model

**Unified five-attribute native panel finalization and source-qualified panel
outputs**, not five isolated repeated getter diagnostics.

1. One shared typed evaluator for all five attributes covers the actual source
   order from rune read/FP arithmetic/range/typed write to an independently
   declared ordinary modifier/cache result and Entity getter channel. Reuse
   existing source rules rather than duplicate one module per attribute.
2. Integrate it with the existing main panel/calibration entry so the first three
   operators' cultivation, rune and covered ordinary/skill snapshots use the
   same native arithmetic/qualification path. Do not just display another source
   manifest or arithmetic worksheet. Existing model values are explicit nominal
   references; compatible native references and unresolved totals are distinct.
3. Close safe finite normal/zero conversion domains or all allowed conditional
   rounding candidates. Do not assume actualRC, handler behavior, crypto keys or
   actual field reflection target. A write encoder argument is not the later
   decoded AttributesData basis; the ordinary layer needs an independent typed
   read or an explicitly qualified model link. A field pipeline with a gap must
   keep the full native total unknown while retaining already-proven pieces.
4. Preserve existing model behavior/default API unless a concrete same-input
   counterexample plus complete native prerequisites justifies a correction.
   The current file evidence alone does not authorize replacing every old
   nominal panel value or claiming the current game panel has been calibrated.

Completion threshold: real main-panel generation gains a common numeric/typed
source path for all five fields, with independently literal-checked expected
values and visible handling of unsafe totals. If implementation only binds the
five getter names to the already273 formula or repeats264 diagnostics, **do not
count283**; retain this packet as preparation and choose another substantive task.

## Necessary acceptance design

- All5channels/2storage types; HP min1 versus ATK/DEF0; MR0..100; AS20 with
  attribute>600 retained while timing stillcaps600. Dynamic/reversed ranges are
  handled only in their actual ordinary/rune source position.
- Positive/zero/negative additions and multiplier/FScaler, signed64 FP wrap and
  incomplete inventory. Rune versus ordinary max(0,MULT) must not be conflated.
- Exact-half integers, near-half Q32 inputs, negative values and high Int32/Int64
  conversion candidates. Never infer actualRC from SSE opcode alone.
- Encoder/reflection failed or unknown; partial prior field stores survive;
  independent later decode may differ. Unknown/failure future reachability and
  static nominal model values remain distinct.
- First-three operator practical scenarios cover all skill phases/normal panels
  through the shared model entry. Retain existing cultivation/source selectors,
  no mutable base stats, no private/runtime memory, no automatic game actions.
- No generic source/evaluator/parameter activation injection; fresh guard covers
  reused helpers/public proofs. Reuse unchanged273/282 tests, do not inflate
  nativefresh count with a repeated whole proof audit.

## Alternative if the integrated panel group is too weak or not closed

Cost modifier activation/order is the stronger alternative to another diagnostic.
It needs actual conditional event routing into281, not sorting arbitrary input
actions and calling the existing scalar engine again. New candidate file reads
cost-activation-candidate.json/rune-order-candidate.json include Character
_PreprocessSkill76055, Roguelike.PreProcessCharacter85519, RuneManager
PreprocessCharacter85091, Rune.CompareTo85039, base and CSkillCdMul priority
getters and constructors. Base getter returns500 in the ordinary body; the
specialized getter and stable list construction/sorting need full branch/type
binding before a product order may be derived. The manager list traversal only
proves traversal of an already-declared current list, not creation/priority order.
Current declared list/action inputs in278/281 do not establish live activation.

Remaining source gates: actual rune registration and list sorting/priority
receiver identities, Character stage/Unity-null and source inherited class
dispatch, BasicCharBuff selection/PreprocessChar/DoPreProcess and activation
conditions, independent decoded cost at every step. No cross-step protected
roundtrip or actual full skill cycle can be supplied just by this ordering proof.
If choosing this alternative, bind those callees first; the current candidate
packet is a lead, not a closed numerical mechanism or completed283.
