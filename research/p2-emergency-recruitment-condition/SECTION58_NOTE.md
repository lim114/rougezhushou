# Section 58: unknown emergency recruitment identity stays pending

The old public calculator treated every non-None recruitment_kind other than
`emergency_hire` as a confirmed negative. For held 同行者 (`cargo_10`), invalid
text and wrong JSON types therefore produced three applied zero effects and
removed the missing-source warning. This was an input qualification defect;
it did not establish any new game mechanism.

The final patch changes only the `emergency_hire` condition branch in
`rouge.relics.context_value`. Exact built-in strings `non_emergency` and
`emergency_hire` retain the old 0/1 behavior. Absence, None, all other names,
wrong JSON types and custom Python equality objects return None, using the
existing missing-condition path. There is no new ValueError, global enum
validator, source/recipient lifecycle change, probability or timing model.
An irrelevant recruitment_kind still leaves the complete public result
unchanged when no applicable emergency-source effect queries it.

The original ValueError proposal in NOTE.md and source-receipt.json is a
historical audit recommendation. `policy-override.json` explicitly supersedes
it; section58-source-receipt.json records the implemented pending policy.
The two known strings come directly from the existing public producer and
repair guard. The pinned topic original was already downloaded with verified
TLS and its actual 17,943,244 bytes were rehashed after recovery. Cargo_10's
usage and buffs[1] close the known atk/def/max_hp=.4 parameters. Exactly three
parsed emergency_hire effects exist, all in cargo_10. No additional attachment
or native stacking fact is inferred.

All calculations use the explicitly frozen HEAD 55 copy
`15e0fa455aad05d27303428299d24d15db4c572c`. Its 121 public source files were
verified. Existing 22 baseline public reproductions were preserved and reused.
The draft changes only relics.py among those files. The parent is responsible
for fresh integration checks against its newer branch and for the next full
Linux/Wine/actual-window batch. A root HEAD 57 apply check succeeded; this is
separate from the frozen HEAD 55 evidence.

The primary matrix executes 3,096 paired cases / 6,192 public calls:
2,310 complete outcomes are identical; 786 applicable invalid cases equal the
entire original outcome of the matching frozen case with None. All 3,096 draft
calls were accepted. Input, cached mechanics and source bytes remained
unchanged. The separate reviewer executes 1,152 pairs / 2,304 calls: 704 full
outcomes remain identical and 448 invalid cases equal existing absent/pending.
Six Python-only identity controls stay pending without invoking custom
equality. Both related test runs execute 56 methods: 55 pass, one pre-existing
historical combat test skips, zero failures/errors. Eight new methods expose
33 expected failing baseline subtests; those are defect evidence, not failed
implementation attempts or passing checks.

Complete public inputs and returns remain in external JSON files; deterministic
gzip copies preserve every decompressed byte and are suitable for the public
research archive. Compression receipts record original and compressed SHA256,
sizes and successful decompression checks. Archive the gzip files, receipts,
scripts, logs, source selectors and independent review; do not copy the whole
frozen/draft package or private state. Patch SHA256 is
`16234cd506a350baed74e6b30adc613baaf5298c3fe1d7bb935fd3bb6606ca39`.

One recovery preparation command expected tests/__init__.py that does not exist
in this namespace-package repository; it stopped before copying tests and the
copy list was corrected. One patch formatting check lacked the new-file-mode
header; adding that header made apply-check pass without changing tested code.
The independent source script initially used an incorrect kind spelling and
was corrected after inspecting the actual source. These distinct preparation
issues are explicitly retained in receipts and do not count as three repeated
unresolved attempts at a mechanism. No game actions, private run reads, chat,
native Windows success, current-hotfix equivalence or attachment proof is
claimed. Those existing unknowns remain unchanged.
