# 282 fixed draft contract

Preparation only. No production files or section counter are changed.

API: `sp_recovery_attribute_reference(payload)`, `source_data()`, `public_example()`.
There is no public source/data/evaluator injection. Top input keys are exactly
`readings`, `rate_reads`, `initializations`, `notifications` (lists; up to40/20/10/10;
at least one item overall). IDs are unique across these four groups and nested
pointer/array/value reads. A nullable identity label never establishes NULL;
`exists` separately declares pointer existence. Booleans are strict true/false/null,
not integers. FP raw values are signed64/null; Single bits uint32/null.

## Independent attribute and rate reads

`readings` reuse the complete273 reading shape, restricted to attributes14 and30
and modifier `basis="independent_cache"` / `flower_load=null`. No source-bound
flower recipe is transferred to SP. Normal getter results and encoding/cache
arguments retain273 semantics. Metadata defaults for both14/30 are min0 and
FP.MaxValue9223372036854775806, **not** ratio upper1. Dynamic ranges stay independent.

`rate_reads` entries have exactly:

```
id, ordinary_native_path,
first_attributes_getter_normal, second_attributes_getter_normal,
flat_read_id, ratio_read_id, same_entity, unchanged_to_point, multiply_normally
```

The IDs select one14 and one30 independent reading. A read ID cannot serve two
different getter access points (including refresh). Sequence is first attributes
getter -> GetValue14 -> second attributes getter -> GetValue30 -> FP multiply.
The second pointer/getter is not borrowed from the first. Unknown numerical
values may still have a normal multiply return; zero times unknown may close0.
This does not assert actual rate, cache identity, attachment or a future read.

## Shared pointer / array / value reads

PointerRead: exactly `{id, normal, exists, identity}`. ArrayRead adds `length`
(nonnegative signed32/null). ValueRead: `{id, normal, bits}`. Identity is a
1–80char label/null. All nested IDs are distinct; references to an existing
reading or rate ID are intentional references, not additional read identities.

## Initial slot0 -> raw14 overwrite prefix

Each `initializations` entry has exactly:

```
id, ordinary_native_path,
attributes_read, sp_data_read, increments_read, slot0_read,
single_conversion_normally, raw_array_read,
raw_encoder_normally, raw_store_normally, mark_dirty_returns_normally,
refresh_read_id, refresh_same_attributes, refresh_unchanged_to_point
```

attributes/sp_data are PointerRead, increments/raw_array are ArrayRead, slot0 is
ValueRead. Source captures attributes, then checks captured SpData and gets its
increment array; raw index0, array NULL/unsigned-bounds check, slot0 Single read,
Single->FP conversion, **then** checks the captured attributes pointer. NULL
attributes therefore does not skip a normally returned slot0 conversion.

OverwriteRawData captures raw array **before** encoder; encoder call happens
before raw-array NULL/bounds checks; index is14 and the opaque40byte payload is
stored before MarkAttributeDirty, followed by GetValue14 because refresh=true.
`mark_dirty_returns_normally` is an independent opaque complete-callee fact. It
does not manufacture callback target/invocation or partial mask writes. On false
or unknown, preserve completed raw store but stop future refresh accordingly.
No detailed MarkDirty mask-state simulation is offered in this first group.
Refresh selects a distinct14 reading; no encoder argument is propagated into
that read's raw/cache decode. Binding false/null leaves refresh result unqualified.

Stages (all present): attributes_read, sp_data_access, increments_read,
increments_guard, slot0_read, single_conversion, attributes_guard,
raw_array_capture, raw_encode, raw_array_guard, raw_store, mark_dirty, refresh.
Successful prefix items expose `{field:"rawData[14]", byte_count:40,
payload_identity:null, decoded_value:null}`. The converter's input reference is
separate. `raw_value_after`, `cache_value_after`, `actual_*` stay null.

## Dirty14/30 -> fresh rate -> timer reconfiguration

Each `notifications` entry has exactly:

```
id, attribute, old_value_raw, ordinary_native_path, entity_exists,
controller_read, new_rate_id, can_recover_rate_id,
ordinary_controller_update_path, controller_matches_clock,
precise_timer_identity, no_intervening_timer_changes,
timer, drain
```

attribute is14/30 (known supported SP branch only), controller is PointerRead,
new_rate_id is required, can_recover_rate_id is a different rate ID/null. Timer
is exact274 `{exists,period_raw,remaining_raw}`; drain is null or its complete
strict274 tick shape. No caller-supplied actions/new-rate/can-recover snapshot
can overwrite the generated request. The ordinary Entity branch ignores
old_value_raw; it captures controller first, computes new14*30, **then** NULL
checks controller and enters the inline UpdateSpRecoveryPerSec body. The inline
hotfix/ordinary qualification is separate from Entity's qualification.

Only a qualifying identity link generates/evaluates the pure274 request with
one reconfigure action, its new-rate argument from new_rate_id, and its separate
canRecover14/30 snapshot from can_recover_rate_id. Valid old timer drains OnTick0
then independently tests canRecover; invalid old timer does not call that getter.
No request is an actual timer/callback/SP observation. Existing274 API and
snapshots are unchanged. Onlycost/other controller paths are not spliced here.

Stages: entity_access, controller_capture, new_rate, controller_guard,
controller_update. `clock_request` / `clock_reference` are separate results;
`new_rate_reference` and `can_recover_snapshot_reference` retain independent IDs.

## Results and qualification

Top: `source_valid`, `source_file`, `readings`, `rate_reads`, `rows`,
`actual_attribute_values=null`, `actual_cache_or_dirty_state=null`,
`actual_sp_after=null`, `actual_timer=null`, `complete_cycle=null`,
`events_scheduled=false`, `hotfix_equivalence_proven=false`.
Rows contain id/kind/stages/normal/status, `stored_prefix`, the applicable value
and clock fields, and the same actual-value nulls. Each stage contains exactly
`name,called,normal,reference`. Called true is an attempted stage; false means
not reached after known failure; null means reachability unknown. Normality is
separate from numerical/identity knowledge. Unknown branch values cannot set
future-called=false. Source failure suppresses all derived references and
leaves future reachability unknown. Unknown labels never imply pointer NULL.

Standalone read/rate results are independent declarations, not an event scheduler.
No private state, game memory, DLL execution, live callbacks or chat is used.
