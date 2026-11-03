# Fixed 283 parent component contract

Only the root integrates production. This preparation is not section completion.
There is no standalone product query. All source identities are fixed by fresh
file SHA guards; callers cannot supply a manifest, source data or evaluator.

## Main API

`panel_native_finalization(payload)` accepts exactly `{fields: [...]}`. The list
contains 0–80 records, with unique `id`. Every record has exactly:

`id, field, phase, model_value, basis_kind, basis_single_bits, basis_fp_raw,
addition_raw, multiplier_delta_raw, final_addition_raw, final_scaler_raw`.

- `id` is a 1–80 character printable string. `field` is one of `hp, attack,
  defense, resistance, attack_speed`; subsets are allowed. `phase` is one of
  `cultivation, rune, normal, skill`. Skill accepts attack/attack_speed only,
  matching the existing first-three skill-panel scope.
- `model_value` is a finite JSON number or null; bool is not a number.
- `basis_kind` is `nominal_single` or `nominal_fp`. The selected basis value
  is unsigned32 Single bits or signed64 FP respectively, or null. The unused
  basis value must be null. These are explicitly **nominal model snapshots**,
  never actual protected reads and never an inferred encoder/decode equality.
- All four bucket values are signed64 FP or null. Cultivation uses neutral
  buckets `0,0,0,4294967296`. Rune has no final-addition bucket and requires
  `final_addition_raw=0`.

The source-qualified mathematical interpretation is:

- cultivation: nominal Single-to-FP basis or explicitly supplied nominal FP;
  no finalizer, typed writer, cache or getter is invented;
- rune: `(basis+ADD)*(ONE+MULT)*FS`, fixed metadata range, FP.AsFloat all-four
  signed64 conversion RC results, then the field's typed writer reference;
- normal/skill: `((basis+ADD)*max(0,ONE+MULT)+FINALADD)*FS`, fixed metadata
  range. Return the conditional ordinary recomputation/getter FP result, with
  no typed writer or Float roundtrip inserted into these phases.

FP add/multiply are the previously source-bound signed64 rules. Range clamp is
`max(min(v,upper),lower)`. Bounds are HP[1,FPMax], ATK/DEF[0,FPMax], MR[0,100],
AS[20,FPMax]. AS does not acquire the separate timing cap600. A conditional
metadata-range recomputation does not assert dirty cache state, absence of a
runtime range override, complete inventory or actual hotfix/normal execution.

Return exact top keys `source_valid, fields, complete_native_panel, actual_panel,
limitations`. Each output record retains `id,field,phase,model_value` and adds
`basis, storage_type, metadata_range, references, conditional_complete,
actual_decoded_value, actual_getter_raw, complete_native_value, limitations`.
`basis` is always `nominal_model_snapshot`. `references` has fixed keys:

`input_fp_raw, after_add_raw, multiplier_raw, after_multiplier_raw,
after_final_add_raw, after_final_scaler_raw, clamped_raw, getter_result_raw,
as_float, writer`.

`writer` is null outside rune. For rune it has `storage_type,
integer_reference, single_bits_candidates, encoder_argument_reference,
encoder_argument_bits_reference, copied_byte_count_reference`. Integer
protections have20 bytes; float protections24. All-four RC integer enumeration
can be complete yet lack a consensus; only a complete nonnull consensus closes
the integer encoder parameter. Floats close only when all bits agree.
`conditional_complete` means the relevant conditional mathematical result is
closed; `complete_native_value` and `complete_native_panel` remain false.
All actual decoded/getter/panel fields remain null.

Invalid source files suppress all derived references on the same invocation,
even if a dependency had earlier cached valid source data. Validation still
rejects malformed input. `source_data()` returns the bound public provenance.

## Separate strict flow references

The component will additionally expose internal strict references for the
native ReadAttributesField, typed writer and manager iteration. These consume
independent normality/pointer/type/decoded read facts. They are not filled with
invented true facts by the main model. A complete opaque callee-normal fact
can establish continuation while its unknown numeric result stays unknown.
The main API above is fixed for the root's integration. The following separate
flow keys are also fixed for necessary tests. Each function rejects extra keys.

Required semantics: Read(null)=Single0; type routing from literal metadata;
FP writer AsFloat precedes FieldInfo-null check; unsupported type returns false
normally without SetValue; manager rangeMeta-null skips before FieldInfo guard;
two metadata-item reads are independent; manager ordinary three buckets have no
max(0,MULT); writer normal false/unknown Boolean still continues the loop.
Unknown control predicates make future calls null rather than false. Call
failure keeps already-proved argument/write prefixes and does not create
actual state. Reflection setter normality never proves future protected decode.

### `read_field_reference(payload)`

Exact keys: `value_exists,object_type_normal,int_type_normal,int_assignable,
float_type_normal,float_assignable,unbox_normal,decode_normal,decoded_int32,
decoded_single_bits,fallback_normal,fallback_bits`. All qualifications are
tri-state. The two `*_assignable` objects have exactly `{normal,value}`, both
tri-state; call normality and its Boolean result are distinct. The independent
decoded integer is signed32/null; decoded/fallback Single bits unsigned32/null.
Unused read values do not become aliases or actual state.

Return: `source_valid,normal,stages,single_bits_candidates,route,
actual_decoded_value`. Stage names in order: `argument_null_check,object_type,
int_target_type,int_assignability,float_target_type,float_assignability,
unbox_and_copy,decode,fallback_convert`. Each stage has `name,called,normal,
reference`. Known unused branches have calledfalse; an unknown predicate makes
future calls null. Normal/null source argument returns Single+0. The Int32
decoded read enumerates four CVTDQ2PS-equivalent scale-invariant RC candidates;
it is not read back from a writer argument. Fallback Convert.ToSingle is opaque,
with independent normality and result bits; no IConvertible body is invented.

### `write_field_reference(payload)`

Exact keys: `fp_raw,field_exists,as_float_normal,field_type_read,type_route_normal,round_normal,
encode_normal,copy_normal,box_normal,set_value_normal`. Raw is signed64/null;
all qualifications tri-state; field_type_read is `{normal,value}`, where value
is `ObscuredInt,ObscuredFloat,Int32,Single,unsupported` or null. Unknown identity
is not a null pointer. Input FP is independent; no caller source override exists.
`type_route_normal` independently qualifies expected-type handle resolution,
associated class initialization and comparisons; normal field-type retrieval
alone does not establish this later normal prefix. Other complete-stage normal
qualifications similarly include their adjacent unexpanded initialization or
dynamic callee work, and do not establish callback identities or real state.

Return: `source_valid,normal,stages,return_boolean,as_float_reference,
encoder_argument_reference,encoder_argument_bits_reference,boxed_type_reference,
stored_prefix,actual_decoded_value`. Ordered stages: `as_float,field_null_check,
field_type_read,type_route,round,encode,struct_copy,box,set_value`. AsFloat occurs
even if the FieldInfo pointer is known null. A recognized route normally returns
true only after SetValue normally returns. Unsupported type returns false
normally, with no box/SetValue calls. Null/failed/unknown normality preserves
previous references but cannot assert normal completion. Unknown numeric data
does not stop a qualified normal opaque encoder/copy/box/SetValue chain.

ObscuredInt rounds then CVTT32 before its encoder, copies20 bytes and boxes the
protected struct. ObscuredFloat copies24 bytes and boxes the protected struct.
Single boxes its Single bits directly. The primitive Int32 selector calls the
round helper and boxes a Double, then supplies that object to reflection; it
has no ObscuredInt encoder or CVTT32 in this branch. A numeric round reference
outside the shared safe signed32 domain remains unknown; independent normal
reflection facts may still establish continuation. `stored_prefix` explicitly
means a completed temporary protected-struct copy, not a field mutation or
verified encoded payload; later decoded values always remain null.

### `manager_flow_reference(payload)`

Top keys exactly `ordinary_native_path,initial_metas,iterations`.
`initial_metas={get_normal,exists,count_normal,count}` with tri-state qualifiers
and signed32/null count. A nonpositive count has zero iterations; a positive
count must equal the declared list length, at most40. Count is captured once.
Unknown count leaves iteration eligibility unknown. Actual hotfix execution is
not modeled by ordinary_native_pathfalse.

Each iteration has exactly `id,first_meta,second_meta,reflection_get_normal,
read_field,single_to_fp_normal,arrays,range_read,writer`.

- first_meta keys: `get_normal,exists,item_normal,item_exists,field_read_normal,
  field_exists`, all tri-state. FieldInfo is captured from this first item.
- second_meta keys: `get_normal,exists,item_normal,item_exists,range_read_normal,
  range_exists,attribute_read_normal,attribute`; attribute signed32/null, other
  values tri-state. This item/getter is independent from the first item. Range
  null skips before the captured FieldInfo-null guard, even if FieldInfo is null.
- read_field is the complete fixed Read payload above. reflection_get_normal
  is the independent opaque reflection GetValue call normality. There is no
  early attributes-instance null check that precedes this reflection call.
- arrays is exactly `{addition,multiplier,scaler}`, each with `read_normal,
  exists,length,element_normal,raw`. Length unsigned32/null; raw signed64/null;
  other fields tri-state. Each array is read independently, then its own null
  and unsigned-index bounds checks precede its element load. A negative signed
  attribute is not silently treated as a valid Python negative index.
- range_read is `{normal,lower_raw,upper_raw}`; normal tri-state and bounds
  signed64/null. This is an independent range result; it is not deduced from
  the captured FieldInfo, because the second range item can differ.
- writer is the fixed Write payload without fp_raw and field_exists: these are
  bound from the calculated/clamped FP argument and the captured first field.
  It cannot independently replace that pointer or the computed argument.

Return: `source_valid,normal,stages,rows,actual_attributes,
complete_native_panel`. Each row has `id,normal,stages,read_reference,
writer_reference,arithmetic_reference,loop_continues_reference,
actual_attributes`. The row arithmetic has `basis_raw,after_add_raw,
multiplier_raw,after_multiplier_raw,after_scaler_raw,clamped_raw`; no max-zero
or final-addition bucket is inserted. Writer Boolean is deliberately ignored
for loop continuation. The three initial stages are `initial_metas_get,
initial_metas_check,initial_count`; iteration stage names are the fixed
`MANAGER_NAMES` tuple in the implementation. All actual fields stay null;
complete_native_panel stays false regardless of conditional normal completion.
