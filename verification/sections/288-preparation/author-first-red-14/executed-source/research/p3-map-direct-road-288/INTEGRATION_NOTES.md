# Unpublished direct-center candidate for a later288 section

The first strict comparison completed successfully as a cache process, not a
production release:23 frozen point pairs,12 accepted and11 rejected at the
existing per-point Euclidean distance <=4 original-pixel gate. There was no
averaging, point adjustment, inverse mapping or regular-fit promotion.

Accepted zero-based cells:

- ro6_t_1: (1,2),(1,4),(3,4),(3,5),(3,6),(4,5),(4,6),(4,7).
- ro6_t_3 / ro6_e_t_3: (1,6),(1,8),(4,6),(4,8).

All11 failed pairs remain in comparison.json and are absent from the candidate
delta. This includes near failures4.1231056256 and4.4721359550; no round-down is
used for admission. Two source-only human reads agreeing is a conservative
reference check, not proof of exact physical centers or subpixel accuracy.
The two original full-plane fits remain rejected with their original matrices,
holdouts and errors unchanged.

## Actual integration seam: not directly loadable in the old parser

The existing fixed_landmark_mapping.direct_reference_for only accepts
tile_floor / LOWLAND. Ten of the12 newly agreeing centers are tile_road /
LOWLAND, and two are tile_floor / LOWLAND. A later functional section must
explicitly extend and verify the direct-reference admission to observed road
centers; merely appending this candidate to old data would reject its whole
reference group. Existing regular ground-fit evidence already distinguishes
LOWLAND roads from highland walls, but that does not silently change the direct
parser contract. Preserve all prior28 direct points and12 regular planes.

Necessary integration checks include:

1. Exactly the12 source-bound pairs enter the delta, with unmodified author
   observed_pixel and root independent_pixel. Never use their average.
2. Bind original image SHA/size/blob/filename, original level bytes and map/tiles,
   grid digest and each alias separately. Source changes invalidate mapping.
3. Verify each accepted road/floor center through the actual public resolver;
   every rejected or unlisted integer/fractional/out-of-grid cell remains
   unknown. Keep cell_at=None and supports_segment_reference=False.
4. Reject mutated highland/wall/unknown tile types. Do not turn this lowland-road
   admission into generic arbitrary points or infer a neighboring center.
5. Verify selected cell/ordinal refresh and original-map resizing in temporary
   UI state. The fixed logical grid, candidate counts and all private run state
   remain independent. Current287 does not acquire these capabilities.

If integrated later, this could add2 direct-reference images /3 stage IDs /
12 centers, moving direct totals from6/11/28 to8/14/40. The regular full-plane
gap remains81 stage IDs /59 images. These are proposed arithmetic totals only;
no new count is a current delivered scope or passed production/UI check.
