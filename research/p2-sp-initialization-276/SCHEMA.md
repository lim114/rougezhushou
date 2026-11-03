# 技力初始化声明合同（第276节）

Public functions: `source_data()`, `public_example()`, `sp_initialization_reference(payload)`, `max_sp_reference(cost, charges)`, `initial_single_reference(first_max, init_sp)`, and the separate `natural_clock_link(report, link)`.

Every object has exactly the listed keys. Boolean qualifications accept only `true`, `false`, or `null`; integers exclude booleans. Signed32 and signed64 are bounded. IDs are unique caller-supplied public labels (1–60 characters); they are not actual pointers. Nullable ID fields represent unknown opaque payloads. No helper decodes a protected cost or opaque array.

`payload`: `entity_exists`, `controller_exists`, `precise_timer_identity`, `no_intervening_state_changes` (tri); `state`; `actions` (1–50 operations).

`state`: nullable `owner_id`, signed32/null `sp_type`, nullable `cost_payload_id`, nullable `increments_payload_id`, signed32/null `max_sp`; `timer` with tri `exists` and signed64/null `period_raw`, `remaining_raw`. The increments token identifies a declared copied segment, not the allocated array identity or element values. Actual array contents remain unknown.

Every action includes `id`, `kind`, `ordinary_native_path` (tri). All read and action IDs must differ, including nested reset/update operations.

`int_read`: `id`, `normal` (tri), `value` (signed32/null).

`opaque_read`: `id`, `normal` (tri), `payload_id` (nullable public ID).

`capacity_read`: `id`, `ordinary_native_path`, `sp_data_exists` (tri); independent `cost_decode` and `charges_decode` (`int_read`); `max_encode_normally`, `getter_returns_normally` (tri); independent `max_decode_read` (`int_read`). Its signed32 product is only the pre-encoding argument. The getter returns an opaque protected value before the independent caller decode; decoded capacity comes solely from max_decode_read.value, never from the product. Normal encode/getter/decode does not prove stable crypto-key reads or roundtrip equality. Unknown decode values remain unknown even with normal=true. First and second Entity reads cannot reuse IDs or snapshots.

`data`: `exists` (tri), `sp_type_read` (`int_read`), `sp_type_store_normally` (tri), `cost_read` (`opaque_read`), `cost_copy_normally` (tri), `increments_read` (`opaque_read`), `increments_destination_exists`, `increments_length_read_normally` (tri), `increments_destination_length` (integer 0–2147483647/null), `increments_copy_normally` (tri). A failed or unknown Array.Copy never supplies partial elements. Normal copy retains only the declared source-segment token/count.

`can_recover_read`: `id`, `exists`, `normal`, `value` (tri). The value is an independently declared getter result; this API does not substitute a rate snapshot for the getter. `second_rate_read`: `id`, `exists`, `normal` (tri), `raw` (signed64/null). Distinct IDs are mandatory, even if declared numbers happen to match.

Action fields in addition to the common three:

* `construct`: `increments_allocate_normally`, `increments_assign_normally`, `timer_allocate_normally`, `timer_constructor_normally`, `timer_assign_normally`, `base_constructor_normally` (tri); `post_ctor_hotfix` with `present`, `returns_normally` (tri). The source prefix stops before optional callback effects. It writes only increments/timer references; owner/type/cost are never inferred zero. The genuine timer constructor writes 0/0.
* `reset`: nullable `owner_id`; `owner_write_normally` (tri); `data`; `can_recover_read`; `second_rate_read`; `timer_call_returns_normally` (tri).
* `reset_timer`: `timer_call_returns_normally` (tri).
* `update_data`: `only_update_sp_cost` (tri); `data`; `can_recover_read`; `second_rate_read`; `timer_call_returns_normally` (tri).
* `entity_init`: `first_max_read` (`capacity_read`); `init_sp_read` (`int_read`); `single_encoder_normally`, `sp_payload_copy_normally` (tri); `second_max_read` (`capacity_read`); `max_sp_write_normally` (tri); `controller_reset` (complete nested `reset` action). This is the qualified SP prefix, not whole Entity.Init/OnInit.
* `entity_update`: `max_read` (`capacity_read`); `max_sp_write_normally` (tri); `controller_update` (complete nested `update_data` action).

Result: `source_valid`, `declared_initial_state`, `rows`, `state_after_reference`, `normal_return_reference`, `actual_current_sp: null`, `complete_cycle: null`, and scope/unknown text. Each row has `id`, `kind`, `called_reference`, `normal_return_reference`, `status`, `stages`, `known_prefix_state_reference`, `state_after_reference`, `initial_sp_prefix`, `capacity_reads`, `conditional_branches`. Stage fields: `name`, `called_reference`, `normal_return_reference`, `argument_reference`, `value_reference`, `detail`. Unknown normality does not establish a completed write. `known_prefix_state_reference` is the last completed boundary, not an assertion about the final actual state. Rows after an unqualified chain are not declared completed.

`max_sp_reference` returns `cost`, `charges`, `signed32_product_reference`, `source_valid`; `initial_single_reference` returns `signed_min_reference`, `single_exact_reference`, `scaled_signed64_eligible_reference`, `encoder_constructor_argument_raw_reference`, `actual_initial_sp: null`, `source_valid`. Non-exact integers remain unknown without actual MXCSR; MIN32 is exactly representable and scales to MIN64. No alive gate or zero clamp is introduced.

Separate `link`: `after_action_id` (existing action ID), `controller_exists`, `precise_timer_identity`, `no_intervening_timer_changes` (tri), `actions` (original strict274 action declarations). `natural_clock_link` validates the original274 schema and returns a new qualified request only when the selected row's normally returned timer snapshot is independently qualified. It never mutates the report, original snapshots, or separate user274/275 requests. It does not execute or complete a natural/cast cycle.

Unknown normality leaves later calls unknown; a known exception leaves them uncalled. A constructor with unknown continuation leaves final timer-pointer existence unknown while retaining the last completed prefix.
