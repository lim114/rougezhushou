# Read-only P2 candidate: 同行者 emergency-source qualification

Baseline: `codex/p2-development`, HEAD `15e0fa455aad05d27303428299d24d15db4c572c`. The audit copied 121 tracked public Python/JSON files into `frozen/`, verified every copied byte, and ran `calculate_damage` only from that copy. `freeze.json` and `post-audit-source-check.json` record no production drift or edits. No private state, game interaction or chat was used.

The independent defect is in `rouge/relics.py`'s `context_value` emergency-hire branch: absence/None yields an unknown, but every other value is reduced to `int(kind == 'emergency_hire')`. Unrecognized names therefore become an asserted non-emergency identity and remove the missing-condition warning. This does not involve target lifetime, attack-count Boolean conversion, module attachment or recognition optimization.

All 22 complete public inputs and returns are in `public-reproduction.json`; `audit.py` reproduces them against the immutable copy. The common input is:

```python
{'operator': 'silverash', 'skill': 3, 'base_attack': 1000,
 'enemy_defense': 0, 'window_seconds': 3, 'timing_mode': 'frames',
 'relic_ids': ['rogue_6_relic_cargo_10']}
```

| recruitment_kind | Current base attack | Current total_damage | Current complete | Condition result |
|---|---:|---:|---|---|
| `unknown` | 1000 | 4000 | true | Three zero-valued effects marked applied; no warning |
| `emergency` | 1000 | 4000 | true | Three zero-valued effects marked applied; no warning |
| `non_emergency` | 1000 | 4000 | true | Recognized negative control |
| `emergency_hire` | 1400 | 5600 | true | Recognized positive control |
| absent / None | 1000 | 4000 | false | missing_conditions=`['emergency_hire']` |

The `unknown` and `emergency` strings are invalid enum inputs, not new accepted unknown sentinels. The existing public producer in `rouge/recruitment_recognition.py` emits only `emergency_hire`, `non_emergency`, or no marker. `rouge/run_recognition.py` transfers that marker's kind; `rouge/app.py` transfers the known current-run field or None. `rouge/run_state.py`'s public source-repair guard also explicitly recognizes the same two values. Only public source code was read; no stored run was loaded. Absence/None is the existing pending representation.

Existing game evidence is reused, not presented as a newly discovered mechanism. The downloaded original had been lost with `/tmp` on the environment restart, so this audit normally fetched the same pinned original using inherited proxy/CA trust with TLS verification enabled. Its 17,943,244 bytes and SHA256 `f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86` were reverified against the existing `relic-mechanics.json` and `research/p2-run-eligibility/source-receipt.json` original hash.

Exact source closure:

- `roguelike_topic_table.details.rogue_6.items.rogue_6_relic_cargo_10.usage` says the HP/ATK/DEF +40% belongs to emergency operators.
- `roguelike_topic_table.details.rogue_6.relics.rogue_6_relic_cargo_10.buffs[1]` is `global_buff_normal`; `blackboard[0].valueStr='rogue_6_relic_employ'`, then `atk=.4`, `def=.4`, `max_hp=.4`.
- The existing parsed effects match that original blackboard. No new native layer, stacking or lifecycle claim is needed to reject an invalid public enum.

Narrow implementation boundary: validate the identity only when the `emergency_hire` condition is queried. Keep absent/None pending; preserve the two recognized strings and their numerical behavior; reject explicit other names/types with ValueError. Do not map arbitrary text, truthiness or context flags onto a known recruitment source. Inputs with no applicable emergency-conditioned effect should retain their existing behavior. The existing source note, recognition mechanism, source lifecycle, stored run and actual game behavior stay outside this correction.

Verification should exercise the two invalid names, recognized positive/negative cases, absent/None pending, invalid containers/types, no-held-relic controls, and unchanged public input. No speculative game script or numerical replacement is proposed. Current hotfix equivalence and actual recipient/native attachment remain separate existing unknowns; closing them requires matching native configuration or real source/recipient observations, not this input audit.

## Root policy override for section 58

The original ValueError recommendation above is retained as the old audit proposal. The root explicitly superseded it: all unrecognized or invalid recruitment-source values must use the existing pending path, rather than raise ValueError. Only exact built-in string values `non_emergency` and `emergency_hire` produce known 0/1. Absence/None and every other value return None when this condition is queried. The two legal strings, absence/None, and complete outputs of scenarios without an applicable emergency-hire effect must remain unchanged. This changes the proposed input policy only; the source facts, frozen baseline and original reproductions are unchanged.

Independent source review found exactly three `condition='emergency_hire'` effects, all under `relics.rogue_6_relic_cargo_10.effects[0..2]`; no char-buff effect has the condition. `prepare` queries `context_value(e, scenario)` before decorating a resolved rule with `relic_id`, so the existing condition branch is the narrow seam. There is no need for a global enum validator or a change to source bindings.
