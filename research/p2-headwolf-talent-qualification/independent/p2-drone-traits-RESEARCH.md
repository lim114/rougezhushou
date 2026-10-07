# P2 drone trait audit (read-only)

Fresh evidence is in drone-traits-source-receipt.json. battle_equip_table.json and uniequip_table.json were fetched through inherited HTTPS proxy/CA trust, HTTP 200, TLS verification retained. Both bytes and SHA-256 match the pinned catalog source. Character table was reused from the earlier fresh cloud fetch and its full SHA-256 rechecked. All six relevant module parts exactly match the production catalog, not merely matching descriptions.

Game commit: a550f5e048bb94e7cdefc6eb97a4091f0c4c7add
battle_equip_table SHA-256: 006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460 (5710707 bytes)
uniequip_table SHA-256: b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9 (3365012 bytes)

## Established facts

- uniequip_table.equipDict.uniequip_002_cammou binds char_328_cammou, PHASE_2 level40. battle_equip_table.uniequip_002_cammou.phases[0..2].parts[0] target is TRAIT_DATA_ONLY, isToken false, both map/game tags null. Candidate0 blackboard: init_atk_scale .2, delta_atk_scale .15, max_atk_scale1.2, max_stack_cnt7. Text explicitly states maximum120%.
- uniequip_table.equipDict.uniequip_002_whitw2 binds char_1038_whitw2, PHASE_2 level60. battle_equip_table.uniequip_002_whitw2.phases[0..2].parts[0] has the same direct-data flags. Candidate0 blackboard: init_atk_scale .35, delta_atk_scale .15, max_atk_scale1.1, max_stack_cnt5. Text explicitly says initial drone damage increases, maximum110%.
- All six candidates require potential rank0 and match module unlock phase/level. Levels2/3 additionally contain TALENT_DATA_ONLY parts; the new trait helper must not suppress their existing selected_talents behavior.
- Base character_table.char_328_cammou.trait.candidates[0] and char_1038_whitw2.trait.candidates[0] both use init.2,delta.15,max1.1,max_stack_cnt6.
- Existing operator_engine drone loop already applies these parameter names to its per-hit warmup reference, but only reads base p['trait']; module override is ignored.

## Smallest safe implementation seam

Reuse Combat.module_parts returned by selected_talents, whose existing module selection already checks identity, module stage, elite and level (public calculation validates stage beforehand). Introduce a drone-specific trait selector taking profile, scenario and these parts. Select an eligible base trait candidate, then eligible non-token TRAIT_DATA_ONLY override candidates. The two reviewed bundles contain all four warmup fields, so replacing the selected parameter bundle is sufficient; no new addition/multiplier/layer formula is necessary. Avoid applying DISPLAY, scripted TRAIT, token parts or unknown scoped bundles. Both reviewed bundles have null tags.

Extract selected_talents' existing candidate eligibility predicate into one private helper, reused by talents and drone trait selection, or narrowly duplicate its phase/level/potential checks if a wider refactor would add risk. The existing predicate handles both normalized talent fields (phase/level/potential_rank) and raw candidates (unlockCondition/requiredPotentialRank). Leave module talent overrides and numerical warmup formula otherwise unchanged. Do not make module complete=true as a result.

## Useful worked checks

Use manual base_attack1000 to isolate changed trait parameters from module ATK additions.
- Cammou S1 window2,drone_warmup_hits7,modulelevel1 currently remains1980 per drone hit (1800*1.1), same as no module. Selected trait reference should become2160 (1800*1.2).
- Whitw2 S1 window2,modulelevel1 currently first drone per-hit270 (1350*.2), two units total540; next per-hit472.5. Selected trait should start472.5 (1350*.35), two units total945, then675 per-hit (1350*.5).
- Cover all stages1..3, both skills for Cammou/three for Whitw2, default level, just below/at40 or60, E1 with legal skill ranks, potentials1..6, warmup0 and high values, time/talent ceiling changes, and no-module result unchanged.
- A stage or operator mismatch must never allow the other's trait to leak. Public calculation already rejects an unrelated module ID.

## Remaining unknowns

This is a parameter correction inside the existing offline warmup reference. It does not verify actual independent drone timing, locked-target distribution, own attack versus drone callback ordering, reset on retargeting, skins, hot updates or real game panels. No new HP composition, deployment-limit or script-level mechanism is established. The native DLL is absent; no new DLL byte verification is claimed.
