# 278 independent necessary acceptance design

Preparation only. This document does not implement production behavior, establish a live game state, or complete section 278. Four-slot initialization is outside this proposed cost group and can remain a successor. The cache SCHEMA v1 is now fixed, and 44 necessary executable controls are prepared in `test_skill_data_cost_independent_278.py`; they have only been syntax checked pending the prepared candidate module.

## Inputs and source qualifications

Read-only inputs:

- `.cache/research/p2-skill-data-modifiers-278/SOURCE_GATE.md`.
- `.cache/section278-independent-cost-source/cost-source-review.json`: 9 methods / 689 instructions / 705 fresh spans, all original bytes matched; actual game MXCSR is explicitly unproved.
- Raw source callers `85326-DoPreprocessChar.txt`, `85329-DoPreprocessChar.txt`, `85835-DoPreProcess.txt`, `84998-_ScaleSpCost.txt`, `84880-_ModifySpData.txt`.

The expected numerical constants in `literal-boundaries.json` are conditional reference inputs, not observations of native execution. They do not use the core implementation or section 276's protected decode product. No case assumes encoder input equals a future decoded value. Native route, reads, copied protected payload, arithmetic domain, encoder completion, and write completion require their own qualifications.

## Necessary numeric controls

Use exact finite normal/zero Single operations for positive and negative half-even controls. Cover both tie parity directions and zero results; source has no zero/one minimum clamp. Use raw Single bits, not loosely parsed decimal display values. Reject NaN, infinity, subnormal operands/results, overflow, invalid Int32 conversion, and inexact Int32-to-Single conversion when independent qualification or a closed interval cannot resolve the final integer.

An RC-independent interval extension could exercise both outcomes: `cost=10, bits=3e4ccccd` has neighboring result Singles 2 and 2.000000238418579, both round to integer 2; `cost=10, bits=3d4ccccd` has neighboring Singles 0.5 and 0.5000000596046448, yielding 0 and 1, so final integer must remain unknown. **The fixed first version has an exact-operation domain, so even the former converging integer case must remain unknown.** The executable test explicitly requires that unknown. Negative counterpart can yield -1/0 and remains unknown. `cost=16777217, bits=3f800000` also remains unknown because CVTDQ2PS may select 16777216 or 16777218. Do not use host rounding mode as evidence of the game mode. The optional interval row in `literal-boundaries.json` is mathematical design evidence, not an expectation that the first version implements it.

Every invocation rounds independently. Two conditional multiply steps `(1, 1.5)->2` and independently read `(2, 1.5)->3` must not be replaced by a combined multiply which rounds 2.25 to 2. A second step's different independent decoded input must override any previous encoder argument; no roundtrip equality follows from two normal calls.

SpScale is signed low-32-bit integer multiplication. Cover MAX32*2=-2, MIN32*-1=MIN32, MIN32*2=0, 65536*65536=0, ordinary signs, scale 0, and -1. Scale 0 still goes through encoding/copy/update requests; it is not the ReduceSp delta-zero early return. Direct replacement supports negative/zero signed32 without rounding or clamp. Bool and out-of-range integers are invalid typed inputs.

## Necessary path and prefix controls

The fixed schema must be checked against source-ordered stages, not merely a successful final result:

1. All five ordinary/hotfix paths are separately qualified. Hotfix normal completion does not prove the ordinary calculation or direct field write.
2. CdMul/CdAdd mainSkill=null is a normal return before Blackboard reading. TryGetFloat false is a normal return before spData reading/decoding. A unknown/failed lookup is distinct from false. CostMul calls GetFloat; do not add an unproved missing-key false skip.
3. A known cost decode survives a later unknown operand/arithmetic/encoder stage, while unexecuted future stages are `called=null` where completion is unknown and `called=false` after a proven failure or skip.
4. Encoded payload and 20-byte destination write are independent. A known input/normal encoder must not claim payload fields, keys, copied value, or actual updated cost.
5. SpScale's first data/spData and second data/spData are independent. Owner is read after cost copy, then second data is read even if that owner is known null; the null guard occurs after the second data read.
6. SpScale checks second data and owner raw nulls, then forwards secondData.spData to Entity.UpdateSpData with `onlyUpdateSpCost=true`. There is no local second-spData null guard at `0x180cef867`; null can be a known argument without proving the callee returned normally. Do not replace this argument with firstData.spData.
7. SpScale owner/data failure after the 20-byte write retains the completed write prefix; a request is not actual actor SP/payment/clock settlement.
8. ModifySpData checks first data existence, then calls the encoder and loads its returned 20-byte prefix before the first spData null guard (`0x180cdefac`). A first spData null does not skip the encoder. Failed/unknown encoder prevents reaching that later guard.
9. ModifySpData writes cost first. When modifyType=true, it reads second data and spData, writes the declared Int32 SpType, and changes only-cost to false. Failure here preserves the earlier cost write. When false, second data/type write are proved skipped and only-cost stays true.
10. ModifySpData reads first owner and separately calls Unity truthiness. False means normal return, retaining cost/type writes, with second owner/third data/update skipped. Existence and identity do not automatically establish truthiness.
11. Unity truthiness true is followed by a separate second-owner read and third-data read. A known null second owner does not skip third-data reading, because its raw null guard follows that read. Actual update receiver/argument must use these later observations.
12. First/second/third data identities may differ or be unknown. Unknown identity is not null existence, and known nonnull does not prove equality. Do not silently link these snapshots to a section 276 update execution.
13. A normal update request or source-local reference is not proof of updated protected cost, current SP, payment, skill activation, recovery phase, or whole-cycle values. These totals stay unknown without separate source-backed readback.

## Proposed public example

Use a small source-bound example with independent actions: CdMul `(3, bits3fc00000)->4`; CdAdd `(5, bits3f000000)->6`; CostMul `(-3, bits3fc00000)->-4`; uncertain CdMul `(10,bits3d4ccccd)->unknown`; SpScale `(MAX32,2)->-2` with first and second spData identity different and only-cost=true; direct ModifySpData `(newCost=-7,modifyType=true,newType=6)` with type written to a second receiver and update data from a third receiver; direct ModifySpData with false Unity truthiness showing cost write retained and no update request. This gives useful known prefixes without misrepresenting live values or combining unrelated sources into a complete cost.

## Contract gate

Executable cases use the fixed source/core-agent API, stages, arithmetic qualifiers, dictionary keys, and scalar representation. Default module path is production only; cache candidates require explicit `--module-file`. Keep original failed assertions and raw outputs if a case fails. A corrected test contract must be classified explicitly; do not shrink the group or restore route recommendations. Run only necessary changed-module acceptance, then provide exact exit/count/source hashes to root.
