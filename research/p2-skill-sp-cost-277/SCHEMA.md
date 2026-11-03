# 277 fixed cache draft contract v1

Draft module: `.cache/section277-draft/rouge/skill_sp_cost_reference.py`.
Public functions: `source_data()`, `public_example()`, `skill_sp_cost_reference(payload)`, `ge_reference(sp_raw, threshold)`, `debit_argument_reference(delta)`. There is **no public source/data override**; source_data loads only the SHA-bound proof/manifest pair.
Scalar helpers return dictionaries, not scalar values (null on invalid source binding). They are **source arithmetic references**, independent of actual instance qualification. `ge_reference`: `threshold_int32, threshold_raw, epsilon_raw, comparison_rhs_raw, sp_raw, result`. `debit_argument_reference`: `delta_int32, negated_int32, input_raw, magnitude_raw, delta_type_value, delta_type_name, target_type_value, target_type_name, player_side_value, player_side_name`. Integer inputs reject bool/float/out of range.

Payload exact keys: `skill_exists, state, actions`.
State exact keys: `cost_min_sp` (signed32/null), `cast_with_no_sp` (true/false/null). This is a **declared parameter state**, not an implicitly reused getter value.
Actions contain 1–50 unique IDs; read IDs are globally unique and cannot equal an action ID. Strings are public nonempty IDs, maximum120 characters. Tri-state means only true/false/null.

Read types (exact keys):

- Int32Read: `id, normal, value`; signed32/null.
- FPRead: `id, normal, raw`; signed64/null. Owner access qualification is declared separately.
- BoolRead: `id, normal, value`.
- OwnerRead: `id, normal, exists, identity`; `exists` is pointer existence tri-state, `identity` is public opaque label/null. identity=null **only means unknown label**, never null pointer. Two reads may have different identities even when normally returned.

Every action exact common keys: `id, kind, ordinary_native_path`. Ordinary=true only qualifies the selected native branch, not pointer/copy/getter/callback completion. All nonselected later stages remain `called=null` until a proven branch skips them.

Action kinds and additional exact keys:

|kind|keys / source boundary|
|---|---|
|assign_min|`blackboard_read: Int32Read, store_returns_normally:tri`. Models only the AssignData BB-result-to-m_costMinSp store prefix. The BB result remains independently declared; no whole AssignData completion or currentSP claim. The source GetIntOrDefault call default is −1, but missing input is not automatically−1.|
|modify_min|`value:signed32/null, store_returns_normally:tri`. Writes m_costMinSp at +0x9c without clamp.|
|modify_free|`value:tri, store_returns_normally:tri`. Writes m_castWithNoSp at +0xa0.|
|admission|`owner_read:OwnerRead, unity_null_read:BoolRead, first_min_read:Int32Read, free_read:BoolRead, sp_owner_read:OwnerRead, sp_read:FPRead, decoded_cost_read:Int32Read, second_min_read:Int32Read`. Unity-null comparison is independent of plain pointer existence/alive. Initial null owner may normally return false via Unity comparison. Subsequent SP getter requires independently returned existing sp_owner_read.|
|reduce|`delta:signed32/null, free_read:BoolRead, skip_virtual_read:BoolRead, newsp_owner_read:OwnerRead, newsp_ordinary_native_path:tri, newsp_returns_normally:tri, returned_modifier_identity:string/null, modifier_copy_returns_normally:tri, apply_owner_read:OwnerRead, apply_returns_normally:tri, apply_return:tri`. skip_virtual_read is independently qualified virtual result, never defaulted from base canSkipReduceSp=false. NewSp first owner may be null: merely passed as source/target. Apply second owner must independently exist before invoking ApplyModifier. Returned modifier is opaque even after normal NewSp/copy.|

Result exact top fields: `kind, source, payload, rows, final_declared_parameter_state, actual_owner_sp_after, actual_cost_paid, actual_cast_success, complete_cycle`.
`source`: `valid, status, proof_sha256, method_count, byte_span_count`.
Each row: `id, kind, called, normal, status, stages, known_prefix_state, state_after, result_reference, arithmetic_reference, modifier_constructor_arguments, opaque_modifier_identity, apply_arguments, actual_owner_sp_after, actual_cost_paid, actual_cast_success, complete_cycle`.
The last four fields at top and row are always null. `called` names the selected action entry. `normal` is its completion tri-state; a normal Boolean false remains `normal=true, result_reference=false`. Declared state only changes in parameter-store actions; admission/reduce never change it.

Each stage has exact `name, called, normal, reference`. Fixed ordered stage names:

- assign_min: `blackboard_result`, `parameter_store`.
- modify_min/modify_free: `parameter_store`.
- admission: `owner_read`, `unity_null_read`, `first_min_read`, `free_read`, `sp_owner_read`, `sp_read`, `decoded_cost_read`, `second_min_read`, `ge_comparison`.
- reduce: `free_read`, `skip_virtual_read`, `newsp_owner_read`, `newsp_call`, `apply_owner_read`, `modifier_copy`, `apply_call`.

All stages are included, initially unknown. Proved skips change only future source-ineligible stages to `called=false, normal=null, reference=null`. Failure after a known prefix similarly proves later source stages unreachable. Unknown condition/normality stops the reference flow and leaves later called=null. Independent values can be null even when normal=true; this does not invent negative/false/0/default. In particular unknown free/virtual result does not prove no NewSp/Apply call.

Admission ordinary source:
1. Independent owner read (raw null allowed) and Unity-null result. Unity true → completed false, subsequent stages skipped.
2. Read first min. Negative → free getter; true → completed true/no SP/cost; false → independent SP-owner+SP then independently decoded dataCost. Nonnegative → independent SP-owner+SP then a **second** min read (may differ), with free/dataCost stages skipped.
3. Signed threshold × Q exactly, then strict `SPraw > wrap64(thresholdQ−42950)`.

Reduce ordinary source:
1. delta=0 → completed true/all stages skipped. Otherwise free getter true, or then independently qualified virtual skip true, similarly completed true/no debit request.
2. Signed32 NEG(delta), exact Int32→FP. Independent first owner is passed twice into NewSp; no dereference implies nonnull requirement here.
3. When `newsp_ordinary_native_path=true`, constructor arguments reference is SP target1, ADD1 if raw>=0 else MINUS2, abs magnitude with MIN64→MAX64−1, PlayerSide.DEFAULT0. `source_identity/target_identity` use the first owner public label/null and do not imply pointer equality with the later Apply owner. `newsp_returns_normally` separately gates returned opaque modifier copy and later owner/read/apply.
4. Independently read second Apply receiver **immediately after NewSp and before copy** (0x18095dc28), then copy136 bytes (0x18095dc3f–97). Raw-null receiver can still precede the complete copy; only its later null check determines whether Apply is callable. Force=false, no public mask argument. Normal Apply Boolean is the ReduceSp result reference, never paid-cost/currentSP evidence.

Qualification false source yields no action arithmetic. Helpers supply isolated arithmetic only, never actor completion. Hotfix/current virtual identity cannot be inferred from a selected base method or ordinary invocation.

## Exact nested row-reference keys

- Admission `arithmetic_reference`: same full dictionary as `ge_reference` (`threshold_int32, threshold_raw, epsilon_raw, comparison_rhs_raw, sp_raw, result`).
- Reduce `arithmetic_reference`: only `delta_int32, negated_int32, input_raw`. This is the NEG/Int32→FP prefix, so magnitude/enum fields are deliberately absent here.
- Reduce `modifier_constructor_arguments`: `magnitude_raw, delta_type_value, delta_type_name, target_type_value, target_type_name, player_side_value, player_side_name, source_identity, target_identity, source_exists, target_exists, returned_payload_fields, cancel_reason_mask`. The last two are always null. This dictionary requires both `newsp_ordinary_native_path=true` and `newsp_returns_normally=true`; ordinary=true alone does not certify reaching all constructor-argument preparation after possible failures.
- Reduce `apply_arguments`: `owner_identity, modifier_identity, force` with force=false. There is no return-derived actual effect or public mask field.
- Stage `newsp_call.reference` when normally returned: `value_raw, source_identity, target_identity, source_exists, target_exists` (raw value supplied to NewSp, before sign/Abs/constructor processing). Unknown NewSp ordinary path may still normally return through a different path; this reference remains the caller's supplied arguments only.
- Stage `modifier_copy.reference` when normally returned: `byte_count, modifier_identity, fields` with byte_count136 and fields=null.
- Source-qualified parameter store stage reference: `field, value`; assignment result labels in read stage retain exact declared read shape, not a reconstructed runtime read.
