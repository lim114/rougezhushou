# 282 independent necessary acceptance design

Status after author freeze: the first actual independent invocation passed 40 test methods, exit 0. See `HANDOFF.md` and `first-real-40/process.json` for the executed inputs, unchanged SHA256 bindings and original output. Only this independent cache changed; formal integration remains root-owned.

The following design was prepared before the frozen executable was tested; its necessary scope is retained for audit.

The fixed draft is `.cache/section282-preparation/SCHEMA.md`; source facts are in its DESIGN and candidate proof/readback. The current candidate contains 16 selected method/entry records, 1647 unique instructions and 1833 original byte spans. These include reused source; do not call them sixteen new methods or repeat/sum earlier full source audits.

## Agreed product boundary

The initialization trace has thirteen stages and ends at refresh. Later subscription is an original-source ordering fact, not an implemented subscription/callback inventory or observed binding. MarkDirty is a declared complete opaque callee; no first/second-delegate or partial dirty-mask state is fabricated. Source order is local BTS -> first delegate-presence read -> dirty store -> branch -> second delegate capture/invocation. Normal MarkDirty does not identify a target or prove a live callback occurred. Notifications are separately qualified declarations; no initialization or dirty write automatically schedules one.

## 14/30 cache and four-bucket controls

- Both default ranges are [0, FP.MaxValue=9223372036854775806], not ratio upper ONE and not signed64 MAX. A dirty attribute30 with raw3*ONE and no modifiers returns3*ONE.
- A clean getter uses its independently decoded cache directly, including a declared negative value. It does not perform a new clamp or use a proposed raw value/recompute. It cannot inherit a previous encoder/cache-write argument.
- Full formula is `((raw + ADD) * max(0, ONE + sum(MULT_DELTA)) + FINALADD) * product(FINALSCALER)`, followed by `max(min(value,upper),lower)` with source signed64 FP wrap at each operation. Do not multiply modifier deltas or add final scalers.
- Literal combined example raw2*ONE, ADD1*ONE, MULT_DELTA=ONE/2, FINALADD=ONE/2, FINALSCALER=2*ONE ->10*ONE. Two independent modifiers each MULT_DELTA=ONE/2 and FINALSCALER=2*ONE with rawONE ->8*ONE, not9*ONE.
- Negative MULT aggregate clamps to0 before final addition; a positive final addition can survive. Final scaler is not replaced with a positive/default value. Signed wrap occurs before range clamp.
- Dynamic reversed range lower5*ONE/upper2*ONE closes to5*ONE under normal reads, including otherwise unknown arithmetic; no sorting/rejecting bounds. Unknown read normality must not be skipped just because a range might determine a constant.
- Preserve clear-dirty prefix after successful enumeration if raw/range/cache-store later fails. Failure before enumeration completion does not prove clear-dirty. Incomplete inventory keeps complete value unknown except independently closed range constants; listed buckets/preClamp are not totals or bounds.
- `basis=independent_cache` and flower_load=null only. A 13/19 flower recipe cannot transfer to14/30. Strict normal/exists/included qualifiers and IDs remain independent.

## Rate read controls

- Test first attributes getter -> GetValue14 -> second independent getter -> GetValue30 -> FP multiply. A later getter failure preserves the earlier read fact, not a computed rate. Unknown identity is not a null pointer.
- Flat4*ONE and ratioONE/2 ->2*ONE. Ratio values aboveONE are not clamped. A normal zero operand can close product0 even if the other FP value is unknown; nonzero times unknown stays unknown.
- `same_entity` and `unchanged_to_point` qualify a linked rate independently of numerically equal values. Never reuse the first attributes pointer/normality for the second getter.
- Every actual accessor point gets distinct reading IDs, including refresh, newRate and canRecover. A single ID cannot prove two getter calls. Duplicate/reused references must be rejected according to the final contract.

## Slot0 and raw14 prefix controls

- Captured attributes known null does not skip SpData access, array slot0 read or a normally completed Single->FP conversion. Its guard occurs afterward; no raw overwrite occurs after known failure.
- increments array null/length0 fails before slot0 read; slot0 has no invented spType enable guard. Inactive default1 from another initializer is not automatically propagated here.
- Literal bits1.5 ->raw6442450944, bits-1 ->-4294967296, signed zero ->0. Protected encoding does not imply a later decoder value, min0 clamp, mask/channel enable or actual SP.
- Numerical unsupported/unknown slot0 can still have independently normal conversion/encoder/store facts and an opaque40byte store. Failed/unknown conversion normality instead makes later calls false/null as appropriate.
- raw-array capture precedes encoder. Known null/short raw array still permits encoder before its guard. Index14 requires length at least15; length14 fails after encode. Unknown guard reachability is not false.
- raw store failure has no completed40byte prefix. Successful raw store followed by MarkDirty failure/unknown retains that prefix and stops refresh false/null; it does not invent partial dirty/callback state.
- Refresh uses a distinct14 read with its own decode, same-attributes and unchanged qualifiers. For instance an encoder input1.5*ONE can coexist with refresh decoded3*ONE; neither replaces the other. False/unknown alias qualification cannot silently qualify the refresh value.
- Shared flags, negative zeros, unknown labels and pointer existence are independent. Test exact thirteen-stage ordering and no extra callback/subscription claims.

## Dirty notification and 274 boundary controls

- Attributes14 and30 take the same supported source branch; other attributes are rejected by this selected-scope API. old_value_raw is ignored by the source branch and cannot replace newRate.
- Capture controller before newRate, guard it after newRate. A known null controller still allows the normally completed new getter; no controller update follows its later guard.
- Entity ordinary qualification and controller inline ordinary qualification are separate. Nonordinary/unknown routes cannot invent normal computation or an attached controller/timer.
- NewRate is a reference to its own pair of getter readings. canRecover uses another independent pair/rate ID and source strict rate>EPS; newRate must not overwrite that snapshot or vice versa.
- With old valid timer, request OnTick(0) before independent canRecover. A no-expiry drain can use oldP=ONE, oldR=3*ONE/4. NewRate2*ONE gives newP=ONE/2; independent canRecover true gives kept-past newR=ONE/4. Independent canRecover rate0 instead invalidates, despite positive newRate.
- With old invalid timer, directly Reset(ONE/newRate,true); canRecover is not called and may have no ID. Do not require its values or reuse newRate as its read.
- Keep drain failure/unknown prefix and normality semantics of unchanged274. Do not rerun that complete old suite; compare the newly generated strict request against its fixed public API where appropriate, with small literal period/R cases.
- Identity of Precise timer, matching controller and no intervening changes are independent. Missing links suppress a qualified request/reference; equal numbers alone are insufficient.
- Generated request must retain exactly one reconfigure action and independent references. Reject caller actions/newRate/canRecover overrides. Preserve old274 input/snapshots/API bytes and actual values null; events_scheduled=false.

## Source and strict-input controls

After the module is frozen, enumerate every actual declared core/model/proof/support pin. Clone only the complete public dependency tree into a bounded cache temp directory; assert validity before each one-byte change and each missing-file test. Exercise stale-after-valid module/cache guards and all public output groups. Original bytes and private data stay untouched; no public evaluator/source injection or fallback.

Preserve the first actual stdout/stderr, exit, core/test bytes and command. A test-contract correction must be distinguished from a product defect; no original failure is erased. Necessary new tests cover this group's additional integration; the already passing273/274/279/280/281 suites and author preparation checks are not counted again. Actual cache/dirty/callback/timer/SP/complete cycle remain unknown regardless of conditional prefix completeness.
