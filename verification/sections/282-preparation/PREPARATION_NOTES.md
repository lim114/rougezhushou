# 282 preparation receipts and non-completion boundary

source-candidate-proof-282.json's latest packet normalizes Entity.Init's selected
92instructions/384bytes and SHA separately from original_full_method_metrics.
Its whole_method_claim=false and cfg_finished=false deliberately avoid claiming
closure of Init or the unexpanded Entity.OnAttributeDirty switch/dynamic calls.
The previous packet is retained as -before-prefix-normalization. Current selected
scope remains16entries/1647unique instructions/1833fresh bound spans.

The first build receipt hashed the generated LF string, whereas Windows
write_text materialized CRLF. The executed candidate core's on-disk SHA is
c9cf4c2e86b42556cb2b7f0b26c2b1bc083d840a9bedc6990f343447b4f57073.
The original9a159967... receipt is retained as -before-on-disk-core-hash. No core
logic was changed after its first public smoke or author34 checks. The build
script now records actual written bytes. Publication must bind the on-disk
bytes, as the author check already did.

Actual commands in the original Windows workspace:

1. `.venv/Scripts/python.exe -X utf8 .cache/section282-preparation/inspect_primary_282.py`
2. `.venv/Scripts/python.exe -X utf8 .cache/section282-preparation/bind_source_candidate_282.py`
   latest actualexit0, chunk fafad5,1833fresh spans; no game execution.
3. `.venv/Scripts/python.exe -X utf8 .cache/section282-preparation/build_draft_282.py`
   actualexit0, chunk9f9907; sourcepack/prototype only, not public implementation.
4. Public source/example smoke actualexit0 chunk4e9a98; new2Q versus eligibilityQ,
   timerP=2147483648/R=1073741824; raw slot0 FP6442450944, independent refresh7Q.
5. `.venv/Scripts/python.exe -X utf8 .cache/section282-preparation/verify_draft_282.py`
   actualexit0 chunk22cf13, author34 change-specific checks. The JSON is an actual
   receipt; raw stdout exists in the tool output, no invented stdout file.

Only this owned cache was modified. No production/tests edits, section count,
commit, push, game actions, DLL execution, memory reads, chat or private state.
Root and independent agents decide source review/necessary tests/promotion/UI.
