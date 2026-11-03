# 283 independent numerical preparation handoff

Ready for parent integration, **not a completed283 section or final independent acceptance**. All work is confined to this cache. Production, public tests, private settings and actual game/chat state are untouched.

## Composable module and fixed contract

- Module: `.cache/section283-numeric/rouge/panel_native_precision.py`.
- Frozen executed SHA256: `878347f7f5d69d09535f1bf0aec409068c68a3cdcf54812091c7deb96be838fc`.
- Contract: `NUMERIC_SCHEMA.md`.
- Functions: `fp_single_reference(raw)`, `writer_integer_reference(raw)`, `single_integer_reference(bits)`.
- Parent source workflow author accepted the keys and the meaning of complete versus consensus.

The module computes exact Fraction/integer candidates and no host floating result. It covers all four signed64 CVTSI2SS rounding modes; multiplication by exact2^-32 is normal/zero and exact for this entire domain. No subnormal branch or actual MXCSR is fabricated. An ambiguous floating payload remains ambiguous even when the later integer closes.

`complete` means a full safe candidate enumeration. An integer is closed only when both complete is true **and** integer_consensus is nonnull. If even one candidate is outside signed32, the other valid integer subset cannot prove a complete parameter. MAX64 can scale to+2^31 and is therefore an incomplete Int32 writer reference; MIN64 scales to the valid MIN32.

The integer helper reference is restricted to the independently qualified ObscuredInt chain, not every reflection/Double-boxing branch. No encoded payload is a later decoded getter, and numerical completeness says nothing about callee normality or actual state. The parent must freshly source-bind this module before invoking it.

## Source gate3

- Official Intel fresh inspection: `intel-primary-inspection-283.json`, SHA256 `4851b53ab4711e3d7b5b7c79826521dbd3ad65a97c70e47fb1d58bf621c5aebf`.
- Pinned original Intel PDF SHA256: `bc4348020f5d5a27b0207c61e3c88d4e610eaf428658dc5d08a1cc84f98a719b`.
- Bookmarks/pages (zero based): CVTSI2SS405, CVTSS2SD407, CVTTSD2SI420, MULSS889.
- Fresh original GameAssembly byte readback: `fp-asfloat-primary-readback-283.json`, SHA256 `a0f049c6bb8d40ef1c2cae5ef50f0c270b23b2d7498df7063560ce66132b986a`.
- The readback checked19 existing AsFloat instructions and2 unique RIP spans. It binds signed64 REX.W instruction bytes `f3480f2ac3` and scale Single bits0x2f800000. Rechecked overlapping source spans are not new mechanism-count credit.

Gate4's full anonymous18000cec0-to280 exact-byte/callee join belongs to the route source peer. That peer independently confirmed the applicable source contract: Double return, half-even in the safe writer domain, with the final32-bit CVTTSD2SI only on the ObscuredInt branch. Parent integration must bind the peer's final receipt; this cache does not relabel the anonymous helper or independently claim all other gates complete.

## First actual preparation verification

- `first-real-numeric/process.json`: actual exit0; five necessary mathematical groups; module and test hashes unchanged.
- Process receipt SHA256: `bc878823fdfb64ed06fd09b363855e682ac47bb4a06982894e5c4f8b90f3ade8`.
- Test SHA256: `e8543e8e8c1fb08e643a93573c657bfe310ebab15dde0b55b7711775f121fe38`.
- Stderr SHA256: `80c6670a71ae1b4ade57e4e3e86c4988ede82f15394d36c414bfc5ab4ca892b6`.
- Original test/core/runner/stdout/stderr are preserved under `first-real-numeric/`.
- `fixed-literal-readback-283.json`:21 fixed expected cases and actual per-RC writer classifications; SHA256 `0134b0f6eb0a34e7ad364496774c1fc7810fd8bb8e3dab21d723fa677b3a9063`.
- `tiny-normal-supplement-283.json`: four additional independently supplied tiny-normal Single boundary controls, actual exit0; SHA256 `4a90ac1383d74a44b292452477c8534ed866b1d9102d73590ba446079c7a456a`.

The latter supplement closes a wording boundary: arbitrary tiny normal Single half-offset arithmetic need not be exact in Double, but all allowed normal results stay on the same side of the adjacent integer boundary and return integer0. The narrower AsFloat domain has minimum nonzero2^-32, so its offset arithmetic does fit Double exactly. Subnormal/DAZ input remains unknown.

The first PDF-inspection attempt with the project venv lacked pypdf; no package was installed. The documented bundled Python then ran the same source successfully (actual exit0). The web tool's >10MB rejection and this environment limitation are recorded in SOURCE_NOTES.md and original tool output; neither was converted into a fabricated raw successful download or inspection transcript.

No final independent test suite, native gameplay validation, main-panel integration, completed section, cloud publication or production release is claimed here. Those remain root-owned.
