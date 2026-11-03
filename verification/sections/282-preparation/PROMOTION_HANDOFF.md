# 282 cache-only handoff

Candidate API is `sp_recovery_attribute_reference(payload)`; root's planned
query `sp-attributes` / payload `sp_attributes` fits the fixed contract. The core
and runtime packet are frozen at the actual on-disk hashes in draft-build-282.json.
Author34 and later independent receipts are separate; none alone completes282.

New files to promote after independent review:

- rouge/sp_recovery_attribute_reference.py
- research/p2-sp-recovery-attributes-282/source-proof.json
- research/p2-sp-recovery-attributes-282/source_manifest.json
- research/p2-sp-recovery-attributes-282/SCHEMA.md
- research/p2-sp-recovery-attributes-282/DESIGN.md
- research/p2-sp-recovery-attributes-282/public-example.json

All other files below the isolated cache package are byte-identical existing
public dependencies and should be reused, not copied over changed production
files blindly. The manifest lists29 guarded files. Verify current production
matches those pins before promotion. Source_data is uncached and verifies the
273/274 core/data/runtime source_artifacts and279 core/manifest/proof/support,
so stale innerLRU validity cannot bypass an invalidated outer binding. No public
data/source/evaluator injection is supported. No production monkeypatch is used.

The 273 private _reading implementation is reused only with a fixed internal
14/30 metadata-range dictionary and independently declared four-bucket caches;
the public273 API remains restricted to13/19 and is unchanged. This does not
borrow HP flower recipes. The279 public Single helper supplies only an encoder
argument reference; no protected roundtrip is inferred. The274 public clock
engine consumes a newly generated separate request with constant action identity
sp282.reconfigure; no existing request/snapshot is overwritten.

No onAttributeMarkedDirty subscription implementation is claimed. Source proves
that Entity.Init's new subscription follows raw14 overwrite, so existing
delegates remain possible. MarkDirty is represented by an opaque complete-callee
normality declaration; no internal callback target, mask-write failure state or
bulk-delegate traversal is claimed by this new product surface.

Result summary from actual public smoke:

- slot0 Single1.5 -> encoder argument6442450944; opaque raw14 store40bytes;
  later independent refresh getter7Q is30064771072.
- independent new-rate14*30 is2Q; later canRecover snapshot is1Q.
- oldP1Q/R0.75Q with declared disabled drain -> newP0.5Q/R0.25Q.
- ratio30 default upper isFP.MaxValue, so3Q survives; negative raw14 clamps0.

All actual attribute/cache/timer/SP/full-cycle outputs remain unknown. No game,
chat, private data, runtime memory or gameDLL execution was used.
