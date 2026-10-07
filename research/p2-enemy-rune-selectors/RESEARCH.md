# P2 environment audit, candidates for sections 22–25

Read-only audit on `codex/p2-development`, 2026-10-07. No tracked edits, branch/commit actions, test-suite or state mutations. Public calculation reproductions use ordinary in-memory scenarios and PYTHONDONTWRITEBYTECODE=1.

## Strong candidate: enemy-specific stage rune scope

`rouge/enemy_environment.py` lines 38–45 accepts the `enemy_attribute_mul` key and global profession/buildable masks, then extracts only numeric attribute names. It drops an explicit `enemy` blackboard selector, merely adds a pending message and **still multiplies the extracted factors onto every selected enemy**. Reporting an unknown does not undo this wrong numerical application.

Pinned originals are from commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`; fresh HTTP 200 downloads preserved proxy and TLS, and their full byte counts/SHA256 match the existing `previews.json` source manifest. See `source-receipt.json` and downloaded level JSON.

1. `level_rogue6_3-3.json.runes[1]`: FOUR_STAR, `enemy_attribute_mul`, `atk=1.5`, `enemy.valueStr="enemy_1076_bsthmr"`. The preceding `runes[0]` is global ATK ×1.2, HP ×1.5.
   * Matching explosion specialist: 2000 ×1.2 ×1.5 = **3600 ATK**, currently correct and should remain.
   * Unrelated Ursus beast `enemy_1108_uterer` at `ro6_e_3_3`, grade 4: reference ATK 380; currently **684**, whereas global-only is **456**. HP 5250 is unaffected by the scoped ATK rune.
   * Same unrelated enemy in `ro6_n_3_3`: ATK 380, no FOUR_STAR rune applied; preserve.
2. `level_rogue6_4-1.json.runes[3]`: FOUR_STAR, `enemy_attribute_mul`, `max_hp=1.5`, `enemy.valueStr="enemy_10151_nspace_2"`. `runes[2]` is global ATK/DEF/HP ×1.2.
   * Matching specialist: 18000 ×1.2 ×1.5 = **32400 HP**, currently correct and should remain.
   * Unrelated proto hound `enemy_2137_shsdgo` at `ro6_e_4_1`, grade 4: currently **32400 HP**, whereas global-only is **21600**.
   * Same proto in `ro6_n_4_1`: HP 18000; preserve.

All eight public scenarios and resolved `steps`/`pending` are in `reproductions.json`. A grade 4 context is deliberate: no exclusive low-grade decrease, grade 5+ HP increase, elite ATK threshold or region-growth factor obscures the worked values. Targeted scope errors can change enemy ATK/HP even where current sustained-target damage happens to be unchanged.

Suggested bounded implementation: check the explicit enemy selector before any numerical attribute multiplication. For the two proven literal selectors above, skip unrelated target IDs and preserve matching targets. Reject/defer unsupported or malformed selector structure without applying its factors broadly. Distinguish selector metadata from an unknown numerical attribute only after evidence supports it. Attach the raw rune index/source to the step if changing source reporting.

The `SIX_STAR` enemy-list/`rune_alias` records in `level_rogue6_c-7.json.runes[2]` and `[4]` are cataloged as NORMAL stage variants (`ro6_t_15` / `ro6_c_7`), so they are currently excluded. Do **not** activate them or infer pipe-list/alias runtime behavior simply to expand this section. Their original file was freshly hash checked only to bound scope. One failed locator (`level_rogue6_t-15.json` does not exist in the manifest) was resolved using the actual shared catalog levelId, not a mechanism failure or three-attempt defer.

Meaningful verification: public target-match/unrelated-target cases for both emergency stages; preserve normal variants; preserve global stage multiplier and difficulty stacking; do not apply unsupported selector records. No screenshots/recognition work needed. This is one coherent section, not multiple quotas split by enemy.

## Other inspection conclusions

Pinned normal grade rules 5 (HP +30%), 8 (elite/boss ATK +15%), 11 (boss damage -20%) agree with current static implementation. Squads contain only two already-supported direct all-friendly 15% variants; their gift/resource/recruit rules remain intentionally outside current inventory inference. No further concrete numerical mechanism change is justified from these data alone.

Specific grade 0–3 and 13–15 multipliers originate in the existing documented community mechanism receipt. Public PRTS was already denied by the proxy; this audit did not repeat that denied route. Native scripts and current live observations are absent, so unverified phase/trigger details stay unknown.

P2 is not complete. Existing env_system_new/global buff, long-term tech, and independent enemy behavior gaps remain.

## Second confirmed independent scope: Aglna2 manual target weight

See `metadata-NOTE.md`, `metadata-source-receipt.json`, and 21 read-only cases in `metadata-reproductions.json`. A real UI control submits a declared target weight, but resolve_enemy deletes it even when no fixed enemy is selected; light/heavy manual declarations therefore return the same public result. The original character talent and existing numerical helper establish the ≤3 / >3 threshold. Narrow correction can preserve the manual operator option without changing selected-enemy identity precedence or the gravity relic's separately enforced pinned-target prerequisite. This is one independent section; stale underscore factors are only an internal seam observation and are not a product scope.
