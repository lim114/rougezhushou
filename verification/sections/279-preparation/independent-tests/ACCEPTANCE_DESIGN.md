# 279 independent initializer acceptance design

Initial preparation design; root's frozen section 278 is untouched. The source gate and schema were absent for the initial draft and later fixed before executable controls were written. The final 49-method cache test is aligned to the fixed four-kind contract and its first real candidate invocation passed. Exact hashes, artifacts and remaining product scope are in `HANDOFF.md`.

## Current independent evidence

`../section279-independent-source/source-readback-279.json` freshly checks the two current original-file evidence inputs `increments-source-279.json` and `increments-consumers-279.json`: 16 methods, 632 unique instruction addresses, 695 instruction/RIP spans. Actual audit exit was 0. DLL SHA256 is `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`; metadata SHA256 is `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`. It was a read-only file audit, not DLL execution, process-memory inspection or live game validation.

The ordinary Single GE callee 220359 (`0x1866e4b90`) subtracts Single EPS bits `3727c5ac` from rhs, compares with COMISS and returns SETAE: ordered greater-or-equal **including equality** after the SUBSS result. EPS is exactly `2748779 / 274877906944`; when rhs is zero, the threshold is exactly bits `b727c5ac`. This is separate from section 277's strict FP comparison and EPS 42950. General inexact subtraction or exceptional comparison still needs independent environment/normality qualification.

## Do not conflate observations

- `get_inited` on the ordinary route means only that the existing array pointer is nonnull. It does not establish length, initialization completion or four usable values. A separate hotfix result cannot establish the array observation.
- SpData.Init captures its Blackboard **pointer argument** in `rbp`. Every loop iteration tests that same captured pointer. Each TryGetFloat result/dictionary lookup is independent; the pointer is not reread from a mutable field per slot. Contradictory per-slot pointer existence must not be accepted as observations of one ordinary invocation.
- Every slot independently rereads current mask and array field. Slot identities can differ after callbacks. Allocating and installing a requested length-4 array does not prove all later writes go to that array.
- Inactive mask bits select Single **1.0**, then leave those bits inactive. The default does not enable recovery channels. Slot indices 0–3 are fixed; bit 8 has no SpType enum name, and SpTypeIndex slot 3 NEVER_USE is an index label, not a new enabled channel.
- Successful Blackboard lookup writes BTS-updated mask before the current array null/length check. Preserve that mutation even if the array guard/store subsequently fails.
- SkillData.InitIfNot writes its init flag before its Single GE/Blackboard assignment/SpData initialization. Later failure does not undo the flag. Duration and Blackboard reads used by assignment and nested initialization are independent later reads.

## Necessary controls: Single GE and SkillData prefix

1. rhs=0, lhs at threshold bits `b727c5ac` -> true; one negative ULP below (`b727c5ad`) -> false; one ULP above (`b727c5ab`) -> true. Zero and positive/negative zero are above the threshold. Nonfinite, inexact-general-RHS and unresolved normality remain outside a closed default.
2. Compare the equality control with section 277's FP strict boundary without reusing its result or numeric EPS.
3. Existing init flag true returns before first duration read, flag write, GE, assignment or nested Init, on a separately qualified ordinary route. An unresolved hotfix cannot be replaced with ordinary behavior.
4. Initial flag false: first duration is read, flag=true write retained, then GE. GE failure/unknown keeps the flag prefix; later possible stages must be false after proven failure, null after unresolved control/normality.
5. GE false skips the assignment path but still reaches the independently read SpData and later Blackboard parameter if their reads are qualified. Do not skip nested Init or use a proposed second duration.
6. GE true rereads a later duration and a later Blackboard for assignment; values/identities can differ from the first duration/captured object. Nested SpData.Init receives another independently read Blackboard.
7. Known null assignment Blackboard fails after the flag write, before nested Init. A known null SpData likewise retains earlier flag and any assignment prefix.
8. Unknown numerical values must be distinguished from unknown branch choices: a separately qualified normal **direct** assignment may record an unknown value and still continue when no branch depends on that value. Do not repeat section 278's initial over-gating of a normal direct type store. A GE result or existence guard that is unknown does affect reachability.

## Necessary controls: four slots and preserved writes

1. Ordinary preexisting nonnull array of length 0 -> get_inited true, early return, no requested allocation and no slot stores; four values remain unproved.
2. Declared getter-hotfix true with opaque array -> early return without an ordinary array/length observation. Known normal getter result is not an actual four-value array.
3. Captured Blackboard absent -> all lookups are skipped, but each slot still independently chooses active protected-decoder or inactive 1.0 fallback by its own current mask. No bit is newly enabled by defaults.
4. Successful lookup at slot 0 with initial mask 0 -> known mask 1 prefix, then array null -> slot store fails and future slots are skipped. The mask prefix survives.
5. Successful lookup at slot 2 with signed mask MIN32 -> updated mask `-2147483644`, demonstrating bit selection rather than `mask>0` or enum clamping.
6. Fallback with mask -1 -> active low slot bits remain active even though the signed mask is negative. A known active bit requires the independently qualified protected float decode; unknown decoder value is not replaced with 1.0.
7. A mask mutation between slots changes a later fallback branch. Do not reuse initial mask or previous observed mask as the next observation.
8. Array replacement between slot 0 and slot 1: retain per-slot destination identity; do not claim one four-value array. Unknown identities do not mean null receivers.
9. Array known null or short length after lookup/mask prefix -> preserve prior direct writes and prior completed slots, then mark future calls false. An unresolved existence/length guard keeps future reachability unknown.
10. Slot 0 known store then slot 1 unresolved callback/guard -> retain slot 0; no synthesized slot 1–3 output. All slot stages remain listed, with false versus null reachability kept distinct.
11. Per-slot lookup `found=false` ignores its out value and follows the separately read mask. `found=null` is different from false and cannot select either route by default.
12. Successful lookup `normal=true, found=true, bits=null` can have a separately qualified normal direct unknown-valued Single store; no numeric arithmetic uses those bits. Similarly, a normal active decode can return an unknown Single while a direct store is independently qualified. Whether a strict first schema supports such traces must be explicit; it must not invent a number or infer failure.
13. Successful lookup with unknown current mask does not make a value-dependent branch: BTS always sets the known slot bit; a qualified direct mask write can retain unknown full mask plus the known bit-set property. In contrast, fallback with unknown mask affects the decoder/default branch and cannot choose a value.
14. Length-4 request/installation, four known store prefixes, and four matching receiver identities are separate facts. Actual initialized object identity, live controller binding, current recovery rate/time and full cycle remain unknown unless separately supplied and source-bound.

## Consumer boundary / successor facts

OnTick's complete ordinary caller does not directly read controller array field `+0x38` or multiply by slot 0. Positive UpdateMultiple count is passed through the independently bound signed Int32-to-FP conversion (`movsxd; shl32`) after NextMultiple. This rejects treating the slot-0 default 1.0 as a direct natural-tick multiplier. It does not close timer initialization, callbacks or every possible indirect dependency.

Attack/heal and damage callers use controller array `+0x38`, not an established alias of a specific SpData array. They pass immediate 1/2 to raw index helper `0x1844dc660` and then load the returned index. The helper was unknown in the initial readback and has since been separately closed as `mov eax,ecx; ret`; the fresh independent two-instruction supplement is `../section279-independent-source/index-helper-supplement.json`. Metadata method identity remains unknown. The fixed contract therefore supports independently qualified index 1/2 requests. Damage also checks cancellation and the separately identified ignoreForSp native byte field; RecoverMp separately rereads owner and stopped state. Current source traces do not prove live event frequency, current actor SP or exact recovery times. These consumers are now source-bound request prefixes within the four-kind contract, not new battle-only relic numeric inputs or actual live recovery totals.

## Contract gate

Use fixed exact typed read points and source binding after SOURCE_GATE/SCHEMA land. No public evidence injection, automatic source fallback, assumed hotfix equivalence, key string guesses or actual actor/cycle numbers. Keep original real failures and distinguish a corrected test contract from an implementation correction. Use cache-only candidates explicitly; production-path discovery must have a setUpClass loader that leaves an explicit candidate subject untouched. This design does not count section 279 as complete.
