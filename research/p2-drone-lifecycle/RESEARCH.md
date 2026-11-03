# Drone aura and arrival scope

Pinned character/skill raw table hashes match. `skill_table.skchr_whitw2_3.levels[9]` proves surrounding-drone aura and global target chase, not universal aura coverage. `attack@times=1.3` is present but has no semantic label or script binding; it cannot prove a fixed1.3s arrival. Static original animation library records only operator body events; all runtime binding flags are false.

The present code's S3 aura uses `floor(duration)`: base_attack1000 gives40 pulses of2160 =86400 even when target_disappears_seconds0. Empty owner target_windows also leaves86400, but owner range does not establish global drone absence, so do not fix that by clipping aura against the owner window. Preserve source per-pulse reference and guard actual coverage/tick totals as unknown.

Default first emitted drone is at1.7s with630 per-hit (1800 x0.35), because0.4s owner event was suppressed by the unverified1.3 threshold yet advanced enumerate i. Trait proves growth from actual repeated hits against same target, not suppressed owner attempts. Keep independent drone attack/arrival/warmup unknown rather than changing1.3 or attaching a made-up arrival stream.

These are two separate scopes: aura target coverage/periodic lifecycle; autonomous attack acquisition/arrival and same-target hit counters. Missing scripts are a precise unknown. No tracked edits; no new native verification.
