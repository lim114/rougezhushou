Section 89 protects the authenticity of observed cultivation crew counts. The
real OCR producer emits int or None. Python bool previously passed two non-None
gates in RunState.apply: overwriting a retained count and treating zero/one
observed unique IDs as evidence of a complete roster. The patch filters only
bool immediately after the existing crew read. It retains positive member
observations, valid stored counts, integer 0/1 departure behavior, all other
non-bool legacy behavior, and the earlier stale/cross-run ignored returns.

The product adds one CRLF line. Removing that line recovers the fixed original
run_state.py bytes exactly. The new test file uses LF; registry registration is
a separate single-module proposal. Root alone applies tracked changes.

Source stage: the immutable original package has 38 files, with 5 distinct
source reproductions (5 new constructors, 5 seed applies, 5 subject applies).
The separate 11-file independent source lead is static only. Neither source
stage was rerun for the draft. Source records use empty member fields; the new
tests seed elite=0/level=1 and cover additional contracts.

Author draft validation ran once: 7 test methods, 12 scenario groups, all pass,
zero skips. Measured explicit constructor entries were 14 (12 new, 2 reload),
and apply entries were 24 (12 seed, 12 subject). The two stale/cross-run returns
are included as actual entries and both preserve the state and disk bytes.
There are 38 complete saved records. The profiler also measured functions in
the external RunState file; other internal helper entries were not counted.
No whole-project helper/API total is inferred. The gzip retains complete typed
trees, caller inputs, raw persisted JSON, natural UUID/time fields and history.
The saved-only checker binds native reencoding and a separate JSON projection;
it executes no project code. Reload comparisons cover the explicitly retained
keys, rather than claiming whole-state equality despite existing notice changes.

No real .local state, damage/training/app/recognition/formatter/Qt/Wine operation
was used. Float 0.0 and string '0' tests protect old compatibility only; they do
not broaden the real producer contract. This change does not repair preexisting
corrupt state or infer P1 strengthening, departure, OCR, or native game rules.
No numerical damage/training delta is claimed from this state-only validation.

Frozen source base is 0f27027; static transport to root 1ce970f proved the target
unchanged. Later root section 88 changes may require only registry transport.
Independent formal review and root fresh related/selected validation remain
pending at this author handoff; this author pass does not authorize a commit.
