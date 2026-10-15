# 288 author implementation handoff

Owned edits only: rouge/fixed_landmark_mapping.py,
rouge/data/fixed-landmark-references.json, scripts/extend_direct_landmark_288.py,
tests/test_direct_landmark_288.py and research/p3-map-direct-road-288/**.
No commit/push, old-test/doc/full-entry/UI-script edits, game/chat operation or
private runtime access was performed by this agent. Root's parallel checkpoint
and work-in-progress edits were left intact.

## Frozen functional source

- parser: b5b9e52f6342a81c72cac2e2410ecc1819202ff5ae1c75f9a6117f817778622b
- data: b7ef0f2165598b4b8f414b5b4f0f2601f94f114499443b6e5ee0235af5f6b8e0
- builder: 51657f1a0dc93101f3fc7eac70c99dad36b997a87b8560ee02fffe61936ec185
- test: 610e8eb811da9ffc8727611676b6ba53c592f1892600bbff0496b2d4bcf33aee

The public source-manifest original bytes retain SHA
015f18ec8a0f5f8a6360ee66e022dddf5df8a0bf56e768f1febe397bf353c958.
Its13 frozen files include all23 pairs/11 rejects and the two original failed
planes. Every required replay input is local to the public source pack; old
.cache source_file values are historical provenance, not runtime dependencies.
README explains the historical unpublished-candidate documents retained as-is.

## Actual necessary checks and first red result

The first14-method run was before promoting the parser/data:7 pass,6 fail and
1 error, exit1. It correctly found the old runtime/data had no new reference
and no explicit road admission. Original source bytes, stdout.bin, stderr.bin
and process.json are preserved under .cache/section288-first-real-14/.
Receipt SHA:43e1be215d79817e100f85656f7809e69440866c91547eae472bdc0715efdcc7.

After implementing the declared parser contract and explicitly running the
builder with --write, the unchanged14 methods all passed, actual exit0:
.cache/section288-implemented-real-14/process.json,
SHA84945bf9052e47470e3c995ab87d046ed88b780eb2f53e8a62a41f4a1cb815e6.
The test module source was not changed between those two real runs.
Both runs preserve exact source snapshots and before/after hashes. They use
isolated offscreen Qt widgets, not the original native MainWindow/game.

Checks cover real public resolver points/aliases, all unknown grid cells,
fractional/nonfinite/out-of-grid inputs, no inverse/segment, strict4-pixel
boundary, floor legacy default versus explicit road tag, malformed/mismatched
tags, height/key rejection even after digest rebinding, all image/level/file/
size/grid alias guards, every13 input pin plus manifest valid-clone/tamper/
missing control, deterministic read-only build, explicit idempotent write and
unknown-target overwrite refusal,3 sizes, actual logical-grid click/refresh,
unknown clearing and no inferred original-image click.

## Delivered scope and remaining boundaries

New12 centers: ro6_t_1 has8 and ro6_t_3/ro6_e_t_3 share4. New points explicitly
declare tile_key;10 roads and2 floors must match LOWLAND in the pinned grid.
Legacy points missing a label still mean floor only, never road or arbitrary
terrain. Totals become8 direct images/14 stage IDs/40 centers. Prior28 point
records and all12 regular-plane dictionaries remain unchanged. The full-plane
gap remains81 stage IDs/59 images; no highland top, portal footing, birth offset,
random range, actual entity position or movement time is newly certified.

Root owns the remaining related old-scope maintenance and native window check.
Known static old assertion: tests/test_map_projection_048.py's rejected-plane
test permits a later direct branch only for ro6_n_2_4; ro6_t_1 now similarly
has8 sparse centers. Keep its masked-direct original-plane failure and frozen
original-fit/4-pixel assertions. This agent did not execute or edit that test.
