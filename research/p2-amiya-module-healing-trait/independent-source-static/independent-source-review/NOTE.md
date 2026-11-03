# Section 80 independent source and narrow design review

Conclusion: the original medical Amiya form explicitly has a 50% damage-to-healing trait, and its reviewed INC-X module replaces that same trait ratio with 60% in each of its three stages. The full description template is identical. The base parameter is not 40%. This is sufficient evidence for selecting the original replacement parameter in the existing offline reference; it does not verify a native script, treatment acquisition or real phase clock.

The fixed product baseline is section 77 commit `4b1e4d1f0bd9c60bc87523d6ac05c61f77f2a52b`. Four complete raw tables are freshly hashed against pinned commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`. Form selectors bind `infos.char_002_amiya.tmplIds` to the original `patchChars.char_1037_amiya3` MEDIC/incantationmedic object and the medical detail entry. Module metadata binds base character `char_002_amiya` with template `char_1037_amiya3`, not the ordinary caster object.

The base unique candidate is E0 Lv1/P1 and `scale=0.5`. Each original INC-X stage contains exactly one `TRAIT_DATA_ONLY` part, one override candidate, E2 Lv50/P1 and `scale=0.6`. Each override uses exactly the base full `overrideDescripton` template; `additionalDescription` is null. Complete parts and attributes match the catalog. The two medical skills' twenty level descriptions and blackboards also match the original source.

The parent draft's nine added selection lines and four coefficient use sites are confined to the existing medical owner block. Reversing those exact lines reconstructs the complete baseline engine byte for byte. Catalog and damage preparation files are unchanged. Module parts come from the existing module elite/level gate, and module identity/stage validation precedes the engine. No API was called to verify the invalid-stage execution; that remains the author's numerical validation responsibility.

Section 45 already makes medical S2 opening-derived healing and follow-up damage conditional references. This review preserves that scope. Native opening/buff/healing order, actual follow-up and end, friendly acquisition/range/adjacency, effective received healing, additional friendly HP and relic stacking remain unverified. The two separate parameters—S1 attack-scaled extra area treatment and the own regeneration talent—must retain their prior models. A null resource/prefab field is not universal attachment evidence.

The ordinary 34-module lead audit establishes static source equality but did not establish this ratio's consumption. Section 79 addresses regeneration qualification separately. Prior readonly research inputs are recorded by exact hashes in the source receipt; no prior completed numerical test or source search was repeated as new work.

No tracked files, product API, tests, Qt, Wine, native Windows, game, capture, private state or chat were used or modified by this reviewer. Initial broad-search and detail-schema preparation errors are retained in `preparation-diagnostics.json` and the source receipt; no conclusion relies on the failed probes.

Reproduction uses standard-library source reads only:

```sh
python source_review080.py
python static_design_review080.py
```

Receipt creation uses exclusive file creation; reproducing in place after sealing intentionally requires a fresh output directory. The numerical author may proceed within the parameter-reference boundary above.
