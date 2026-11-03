# Independent Source review — Saved108 final v2

Verdict: no remaining Source blocker in the frozen v2 packet. This is a
non-author Source review, not an executed Saved audit, product PASS, visual
inspection, completed section or additional Window attempt. Root alone binds
actual artifacts and runs the reader/native decoder/project/Qt/Wine/tests/Git.
The reviewer did not import or execute any generated module, helper/native codec,
project API, calculator, formatter, test, Qt/Wine or Git; no tracked file changed.
Only stdlib Source/JSON reads, hashing, AST and in-memory compile occurred.

## Exact reviewed artifacts and checks

Directory: /workspace/.continuation/section108-saved-readback-source-v2

- audit108.py:55189 bytes, SHA256
  f46f0fea6456020c50830ed30ab420bebf53c2f89c0993316aeb944c638c1ef8.
- SOURCE_MANIFEST.json:3877 bytes, SHA256
  dc6bf3dbe89505b21e5026fe9918aa1424aa78436157e3324d9272812308bfa0.
- README.md:19021 bytes, SHA256
  c562582d4758fd7c8b7628182167df0f82be2ebcc7503214294775c5bd69acfd.
- AUTHOR_SOURCE_CHECK.json:1693 bytes, SHA256
  e3e573c8a75c2855110336d660de1b6a14dd2565ad3f1f446d7ca5ce8a877b2d.
- INACTIVE_BINDINGS_TEMPLATE.json:2479 bytes, SHA256
  4ad43e663860ae40b682668999dace7cbcfe9394f18e61cf3ffbd145b6ca9067.
- native_evidence.py:6468 bytes, unchanged f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a.
- window108.py:43662 bytes, frozen c4404868fec6c81d09eea18a33603b0ed1ca3c2dcabcab6f183f039494a08bc5.
- WINDOW_INDEPENDENT_SOURCE_REVIEW.md:7798 bytes,
  e51565c93b0fc523ba9009b0b1a38515f416f81cc854af0fb870f733d9278884.

All18 manifest payloads independently matched exact byte lengths/SHA; no payload
was modified. AST parses and compile-only checks for reader/helper/window passed.
All196 reader Assert AST nodes/order match the original inactive v1 exactly; all
16 FunctionDef nodes are present. Five fixture functions(profile,difficulty,zone,
fixture,cases) are byte-exact Source segments of c440. The reader's Window/review/
facts/transport constants match real supplied files. All seven known template pin
objects matched actual files; ten actual-artifact fields remainNULL and readyFalse.
No future actual native-call or record count is supplied.

## Confirmed v1 Source blocker and minimal resolution

The original55093-byte draft858848f9dab625441b3a47d103092b24bcd400fa99346532f3aaf7711d625251
was not executed. The reviewer read its entire wire and found one Saved-only
geometry predicate mismatch at original line644. Its Python floor expression
x+(width-1)//2 could differ from the actual Qt midpoint. Reviewer notes remain
in section108-saved-readback-source-v1/INDEPENDENT_SOURCE_BLOCKER_NOTES_V1.json,
2556 bytes, SHA98c6cd3521cf5b632163612fd443835ac6c1af03a25f8c36daf380367c66d193.

Official Source was retrieved from:
https://raw.githubusercontent.com/qt/qtbase/v6.9.3/src/corelib/tools/qrect.h

The saved official header is29574 bytes,
SHA0417e3398d546f9e7f3d9fb79b2f5353941eaead3d84362483030b7309019b4c.
Lines233–234 are:

    constexpr inline QPoint QRect::center() const noexcept
    { return QPoint(int((qint64(x1)+x2)/2), int((qint64(y1)+y2)/2)); } // cast avoids overflow on addition

Signed C++ integral division truncates toward zero. With right=x+width-1, the
center is trunc_zero((2*x+width-1)/2). The static counterexample x=-1,width2
has actual midpoint0 but the old floor formula produces-1. A viewport starting0
would contain the former. This is arithmetic/Source evidence only: no actual
PNG is asserted to have negative coordinates, no Qt API ran, and no product or
Window failure is inferred.

Fresh v2 uses sx=2*x+width-1; sy=2*y+height-1, then sx//2 for nonnegative sx or
-((-sx)//2) for negative sx(and likewise y). It uses only exact signed integers,
with stored cursor/viewport field types and positive widths/heights already
checked. This matches the Qt Source without float conversion or weakened
viewport inclusion. The single one-occurrence local transport952d9a86 has exact
forward and byte inverse back to858848. Every other reader byte is unchanged;
all196 assertions remain identical. Official header/evidence/manifest copies
are byte-identical to the public Source取证 package. c440 and helper are unchanged.
No extra actual Window run is requested or justified by this Saved-only repair.

## Native decoding and artifact admission

Root's future reader operation uses unchanged f040 read_record: safe single
relative filename, no symlink, exact compressed and decoded bytes/hash, protocol4,
no globals/persistent references/trailing data, exact builtin graph qualification.
The comparator preserves types, float bits, dictionary insertion order and
bidirectional internal container aliases. Those functions were read, not run.
The graph equality scope is each recorded comparison domain; independently
frozen graphs do not certify former live alias links across events.

Actual bindings must have the exact supplied bytes/hash, actual_runtime_ready
exactlyTrue, pinned reader/window/review/facts/transport/original sources, and real
raw0 primary files. Both Window receipts must be same-c440, passed/workflowTrue,
correct phases and full Source/CORE pre/post maps with no drift/Qt errors. Gold is
real750; candidate is real751, exactly two changed old paths(env/cloud) and one
new108test. Corrected107 test2c5e remains exact; full helper is unchanged and cloud
prepend is independently checked by module AST. Source maps and CORE are checked
before and after Saved readback and drift revokes success. Output is a fresh
exclusive file outside repository; inputs/evidence/images are not rewritten.

The unchanged original plain JSON was independently read at640662 bytes/SHAcaadc9ecfd748e1172820abe460735b0563210e1c25312482e0d2a541ac5a790.
It has47 cases/eight previews,178 explicit calls/225 native records. The reader
will decode every entry, require consecutive sequence filenames and exact
record-directory set equality, and bind all55 ordered public definitions to real
API calls/whole-case graphs. Every original caller before/after remains strict;
actual callee returns, errors, texts, args/technicalkwargs and blocked phases must
match their own native wire and metadata. Original22 errors remain original
observations, not candidate PASS. JSON metadata is deliberately compared through
its JSON producer view and never presented as native alias preservation.

## Window records and explicit cross-interface boundary

The whole code was read against c440 producers. Every actual result/exception
calculator record preserves full args/kwargs. Explicit43 snapshot rows refer to
actual observed callee returns/errors and complete raw caller/config. Extra
signal-driven calls are retained and counted from actual receipts rather than a
prepared number. Every UI pure group checks its joint durable/all-file graph.
Three-formatter groups check joint complete result/durable/files around all three
real calls and retain complete estimate/default/technical texts. Independent
preview whole callers and formatter inputs/outputs are linked to real snapshots.
These are common group before/after proofs, not individual three-formatter events.

The dedicated actual_cross_API_identity_order_boundary is required for precisely
the healthy targeted case set; the one healthy no-target contrast does not invent
a preview/boundary. Each joint before graph has exact ordered original numeric
and preview environments, complete damage_result,durable,disks. The numeric env
is the identical nested object of damage_result.result.run_resolution.enemy
within that one frozen graph; before/after fullnative equality holds. Both original
environments and complete damage_result/state/files bind to actual snapshots and
callee returns without normalization.

Exact dict types, numerical prefix(enemy_id,level,stage_id), independent prefix
(stage_id,enemy_id,level), identical remaining key order and all three exact scalar
identity values/types are required. Separate shallow comparison copies use the
entire numerical key sequence and all original values. Saved copies match those
complete mappings and fullnative comparison checks all nested types/order/float
bits/internal aliases. Only that declared cross-API prefix is adapted. Original
raw environments/callers/results/text/state and full same-input Gold domains are
never reordered or projected. Root's prior diagnostic0e73 JSON is exact copied
provenance, not a native decode performed by this reviewer.

All33 healthy snapshot view/durable/disks graphs must equal complete corresponding
same-input Gold graphs, including result/scenario/three texts/preview/callers and
raw disk bytes. All10 changed errors must preserve complete raw caller/durable/
disks/loaded summary while showing the correct original AE/TE versus new explicit
ValueError and pending environmentNone. The reader does not turn unknown input
into cleared or confirmed values and does not compare intended changes to the
old defective output. The narrow prefix adapter never applies to Gold equality.

## Memory, authorized save and reload domains

All40 raw matrix inputs are explicitly admitted into an already healthy real
window's public memory only; only config changes and all account/cache/tmp data
must remain exact. No saved-schema or natural OCR admission is claimed, and raw
cases may not save. Every independent case starts from the full already-loaded
baseline. The accepted known4_1 cache retains its raw main=[6] rather than rewriting
it; known-ID numerical precedence is the existing rule.

Two genuine apply_run_observation phases use legal known4_1 at1001 and ambiguous
portal at1002. Caller input retains stale6 while the existing accepted zone retains
previous main4. The complete actual new durable/disk phase reaches its calculation
snapshot, actual timestamp/last_read/main4 types are checked, account graph/files
remain unchanged and authorized atomic run save consumes the tmp sentinel. These
writes are not mislabeled disk-unchanged experiments or invented portal depth.

Both actual close/directRunState reloads bind their real records. Read-only matrix
restores then compares the complete original already-loaded graph(defaults/notice/
order), not rawJSON missing defaults. Fresh-save restart compares the full actual
persisted JSON graph and actual restarted graph, never former live aliases. No
second MainWindow reopening is performed or implied. JSON aliases and unrelated
leaf schemas are not generalized from these fixtures.

## Four visual anchors and honest limits

The candidate real panel binds original unknown raw context, actual target tuple,
full independent pending text and displayed text. Original panel success isFalse;
set_context render plus explicit render are distinct actual call sites.

Four required PNGs bind exact case/tab/anchor rows, complete real report text and
selection, actual stored cursor/viewport rectangles or actual QLabel summary.
The corrected midpoint reconstructs the exact Qt inclusion predicate on those
stored integers. Every original PNG row/anchor native reference must match the
Root visual ledger; Root must record actually_viewedTrue with a nonempty observation
and independently verify exact bytes/SHA/PNG signature. Source runner's
Root_visual_verifiedFalse remains intact; the reader never fabricates viewing.
This reviewer did not decode or view any actual image.

Scope flags remainFalse for native Windows, naturalOCR, malformedSavedcache
admission, individual three-formatter before/after, cross-freeze live aliases,
JSON live aliases and second MainWindow reopen. The author packet's10 futureNULL/
readyFalse activation is honest. Root's reported third Gold success is subsequent
runtime evidence, not produced by this Source review; actual Gold/candidate/visual
paths and hashes must still satisfy separate Root bindings. Both failed earlier
Gold attempts remain immutable and cannot satisfy same-c440/raw0/passed gates.
There is no fourth attempt or weakened oracle implied by this packet.

The final reader Source has no remaining blocker in the reviewed scope. Actual
restricted decoding, saved equality, candidate runtime, screenshot visibility and
publication remain Root work; Source approval alone proves none of those outcomes.
