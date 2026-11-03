# Proposed283 integration seam and source gates

This is a design, not a started/completed section or permission to edit production.
Root accepted investigation of the integrated five-panel group; production and
282 publication stay with root. No new scalar-only diagnostic query is proposed.

## Product change and exact existing seams

The product gains a source-qualified native finalization/precision result attached
to its **existing** primary panel generation and four-layer calibration. The old
nominal model values, supported inputs, context token, source selectors and
unknown actual states are preserved. A nominal model value is not silently
renamed actual/native verified, and the native result cannot overwrite the model
from an unproved RC, protected roundtrip or modifier activation assumption.

Proposed shared module: `rouge/panel_native_finalization.py`. One evaluator covers
HP/ATK/DEF/MR/AS, their typed storage, conditional conversion results, metadata
ranges and independent ordinary getter reads. This must be called from the main
path, not only from a standalone query/manifest display.

Concrete call sites to adapt as one group:

1. `relic_attributes.apply_attribute_runes` / `prepare_attribute_runes`: keep
   their public model return shape, and add a private sibling path returning the
   same model attributes plus native rune-finalizer references from the actual
   already-resolved source list. Main `_prepare_damage` uses that private path
   once, so no source selector/tally is independently reimplemented. Carry a
   private reference record in the prepared scenario; public underscore/source
   injection remains rejected by the existing public calibration adapter.
2. `estimate.build_estimate`: at construction of `stats`, pass its actual model
   hp_bonus/defense_bonus/defense_flat/total effects primitives and rune basis
   to the common evaluator. Do not reverse-engineer modifier inputs by dividing
   output by basis, subtracting adjacent panels or assuming list registration.
   SilverAsh's defense_flat is a final addition in the model, not part of a rune
   multiplier. Real activation/order remains unknown unless separately bound.
3. `operator_engine.Combat.__init__` and its skill-phase result construction:
   same seam for the extended engine; do not create a second unrelated numerical
   implementation. At minimum the first-three path must be complete. Other
   operators' special sources must be qualified individually or remain unknown.
4. `damage._skill_damage_base` and `estimate` skill snapshot: carry their actual
   model ATK multiplier and AS additions into the same reference. The first
   three9skills' frozen last-level data were inspected: they do not establish
   a missing new universal skill HP/DEF boost. Do not fabricate such boosts.
5. `calibration.panel_layers`: add the main result's per-field native references
   beside the **existing four rows**, explaining their input/encoder/independent
   decode boundaries. It must reuse the main calculation reference, not call an
   independent arithmetic sheet and claim those are the main result's values.
   Existing `compare_panel`/264 matching context still cannot certify game values.

## Value and completeness contracts to settle before implementation

- `model_value` is the preserved current output. It can remain useful under its
  already documented nominal input/environment assumptions.
- `conditional_reference` is source arithmetic over explicitly identified model
  input bits/FP values. If a JSON decimal is encoded as the model's float32 input,
  call that a **nominal bit interpretation**, not a read of the actual Blackboard
  value. Installed field/layout/range facts do not prove current buff inventory.
- `encoder_argument_reference` is before protected encoding, never a future
  AttributesData/Entity getter decoded value. Actual runtime values stay null.
- Ordinary recalculation consumes independently declared getter/raw values or
  a clearly labeled nominal model link. No hidden crypto equality link. A clean
  cached result is not re-clamped merely because default range metadata exists.
- The shared evaluator may close finite normal results which agree over all
  allowed RC candidates; multiple candidates/overflow keep the full native
  reference unknown while proven arithmetic pieces remain visible. It must not
  turn model compatibility into actual RC/inventory/callback evidence.
- Preserve `model_complete` semantics and existing supported model outputs. Add
  distinct native qualification/completeness fields rather than silently marking
  old nominal inputs unsupported or reducing their support without a counterexample.

This is useful only if the main panel exposes the typed/range/precision-qualified
result and uncertain boundaries for each existing phase. If all native values
are left unknown with no useful numeric pieces, or only five copies of273 are
created, the proposal is not a meaningful283 and should be deferred.

## Source details requiring closure

Current nine method signatures are archived in panel-method-signatures-283.json:
ReadAttributesField30790 returns Single; both Write overloads30791/30792 return
**Boolean**; manager85517 returns Void; the five Entity getters return FP.
The manager ignores the writer Boolean and continues its loop; a normal false
unsupported-type result is different from a throwing writer and must not stop
later fields as if it were an exception. Do not invent a Boolean result for the
Void manager. Writer FP overload calls AsFloat before Single overload checks
FieldInfo NULL, so the NULL FieldInfo does not skip conversion.

Required gates before prototype:

1. Bind actual runtime-type selector literal identities, expected FieldInfo/boxed
   type routing, signature parameters and the relevant constructor30778. Shared
   native addresses/target_symbols aliases are not enough to name System.Type
   equality or unbox/decode helpers. Reflection target remains independently
   qualified; do not assume a field label is an actual matching FieldInfo.
2. Reuse273 generic four-bucket/range/FP rules and bind current five default range
   attributes. The rune finalizer differs: `(raw+ADD)*(ONE+MULT)*FINAL_SCALER`,
   then its field range. No ordinary max(0,MULT) before the rune product.
3. FP.AsFloat is signed64 CVTSI2SS followed by MULSS2^-32, **not** conversion of
   a signed32 integer. Close its all-RC finite normal/zero domain with exact
   integer/rational math and the Intel primary source. No actual MXCSR assumed.
   Its smallest nonzero output is of order2^-32, so a subnormal exception must
   not be invented simply because the raw input is small. Check boundaries
   including MAX64 rounding up and later Int32 writer out-of-domain cases.
4. Join unnamed18000cec0 with the half-even helper/floor/ceil/fraction proof from
   280 by exact bytes/callees, not by a guessed public method name. This helper
   returns Double, and the ObscuredInt branch converts it with CVTTSD2SI.
5. Direct float typed write stores a passed Single/24byte protected payload;
   integer write stores an encoded Int32 candidate. Normal reflection assignment
   is independent. Neither establishes a next decoded basis for the next layer.
6. Guard all reused code and public sources freshly; do not trust helper LRU.
   The current candidate925instructions/1021spans is an investigation subset,
   not a closed full panel mechanism. Do not count these candidates as eleven
   new completed mechanisms or claim no current hotfix override.

## Necessary acceptance before counting283

- Existing first-three API/calibration rows remain and now carry the shared
  per-phase five-attribute result. Main result and calibration references agree
  exactly without recomputation/observation mutation or new user entry of base stats.
- Independent literal cases for HP min1, MR upper100, AS attribute>600 versus
  timing600, negative/zero/raw and clean-cache behavior; ordinary/rune multiplier
  distinction; final addition not multiplied by runes; source order/FP wrap.
- Exact Single half ties, near-half Q32 and signed64-to-Single edge candidates;
  integer writer closure only if all qualified candidates agree; floating writer
  exact/ambiguous bits separate from subsequent decoded value. No Python default
  nearest-mode or rounding-for-display is passed off as actual native policy.
- Boolean unsupported-type false permits later manager fields; exception/unknown
  retains earlier prefixes and leaves reachability appropriately false/null;
  encoder-before-FieldInfo-NULL and independent two metadata/range reads.
- Existing supported nominal scenarios unchanged; any deliberate same-input
  correction has its original failure/source/precise applicability and new
  literal expected value. Source-only archives or an isolated query do not close283.
- Actual current window after root integration; temporary state and preserved
  selection/scroll/input/result. Necessary checks only; next full cadence stays290.

If gates1/3/4 or the main-path seam cannot be closed without pretending crypto
roundtrip or actual modifier activation, stop at investigation. Use the alternate
cost activation/list-construction route documented in COVERAGE_AND_SCOPE.md;
do not count a diagnostic wrapper as a completed section.
