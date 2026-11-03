# 282 scope and evidence-first design

Remaining P2 work: actual14/30 SP attributes, natural timer initialization/change
sources and full cycle. Existing273 supports onlyHP13/19;274 accepts supplied
14/30 values and supplied new rate;276 accepts supplied eligibility/second rate;
279 initializes four slots but does not link slot0 to a natural timer multiplier.
278/280/281 concern cost write arguments and must not be mistaken for recovery.

The new useful group links three already-related native operations: slot0 from
SpData into raw14 with refresh, independently declared14/30 cache/recompute into
new rate, and dirty14/30 source qualification into the separate274 timer engine.
It must actually compute/query those declared references. Source collection and
this design alone do not count as completed282. Real event timing, attached buff
inventory, protected roundtrip and current hotfix remain unknown.

Evidence: source-candidate-proof-282.json selects16method/entry records,
1647unique instructions and1833fresh byte spans on the two pinned disk originals.
Some methods/proofs were already bound in273/274/276/279; do not count them as
16new methods or a new complete audit of those earlier proofs. Entity.Init is
explicitly truncated to5328–54a3. Entity.OnAttributeDirty has a computed switch;
the original9table entries are bound, only SP14/30 selected branch is closed,
not the entire method. The extra raw7465 extraction is not part of this proof.

## Source findings and limits

- Entity.Init gets slot0 via identity index helper, converts Single toFP, calls
  OverwriteRawData(14,value,refresh=true), then builds/combines/subscribes a dirty
  delegate. Existing delegates need not be empty; no actual target is inferred.
- Both14 jump-table entry at1806f79d8 and direct30 branch reach1806f7701. It
  captures controller before rate read and NULL-checks controller after that read.
- Getter reads attributes twice, GetValue14 then GetValue30, and multipliesFP.
  New-rate and later canRecover reads remain separate snapshots.
- OverwriteRawData captures raw array before encoder, checks it after encoder,
  stores40bytes then calls MarkDirty and refresh GetValue. A partial normal
  prefix remains visible if a later callee fails. No decoder equality assumed.
- MarkDirty localBTS is before first delegate-presence read; dirty mask store is
  after that read, before branch and second delegate capture/invocation. The
  proposal models its complete normal-return fact opaquely rather than guessing
  delegate layout/inventory or exception-prefix mask state.

## Corrections preserved

The first282 coordination message called OverwriteRawData's third argument
"force". Metadata64269 proves its name is **refresh**, which is used throughout
the fixed contract. The stack zero at caller is MethodInfo, not a callback flag.
An early summary loosely said "dirty write before callback read"; actual source
649ad5 localBTS ->649ad9 firstpresenceCMP ->649ae1 dirty store ->649ae5 branch ->
649af9 second delegate capture. Invocation stays after the dirty write.
An initial candidate selector accidentally requested GetValue64289; actual
metadata index is64276. The first10-method byte proof/receipt is preserved with
`-before-getvalue-selection`; the current16-method proof binds the corrected
getter and five already-published formula/range helpers. No production code or
public evidence was changed by these preparation corrections.

## Necessary acceptance

1.14/30 default/dynamic/reversed ranges, ordered four-bucketFP wrap, dirty/clean,
   incomplete inventory, zero/negative modifiers; no13/19 recipe transferred.
2.slot0 conversion exact safe domain/unknown/negative; captured attributesNULL
   still permits conversion first; raw encoder beforeNULL/bounds; raw store
   remains if MarkDirty/refresh fails; independent refresh decode differs.
3.14/30 notification same body; controller captured before getter and guarded
   after; two attribute objects/read IDs normal independently; new-rate and
   canRecover never borrow snapshots; valid drain/invalid skip; no realSP/cycle.
4.strict input/source/helper-byte guards, no public evaluator/source injection,
   source failure suppresses references, original273/274 public API unchanged.

Prototype only in this owned cache, then independent literal/prefix tests and
limited source/code review. Root alone decides promotion/UI/full completion.
