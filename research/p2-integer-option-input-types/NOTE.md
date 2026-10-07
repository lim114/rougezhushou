# Section 61: raw Boolean values are not integer counts or state codes

This public-only draft is frozen against HEAD 58
`4543b9b91ac7b61fc019bb96a3d6d5ac2593a6bc`. It changes only the integer input
qualification in `Combat.option`; the parent will integrate after sections
59/60 and the required full-60 archive. Root integration and native Windows
validation are separate from this external HEAD58 evidence.

The existing engine has 28 literal `integer=True` call sites and 27 unique
fields. Three were already handled at section 54's public capability seams.
Of the remaining 24, enemy_weight already rejects raw bool in the upstream
manual-weight resolver, leaving 23 new fields. Those 24 fields correspond to
25 int-default Qt controls because drone_warmup_hits has two operators. All
use the actual QSpinBox producer. The separate 23 bool-default control records
use QCheckBox and do not intersect the integer call set. No new game mechanic
or UI maximum is inferred from that distinction.

The final local guard reads the raw value before `float` conversion and
rejects bool only when `integer=True` is actually queried. Healing_targets is
excluded from the local guard because Combat.plan queries it for every
operator while the already implemented public capability gate rejects bool
only on real healing paths. Keeping that seam preserves inactive fields.
The two other section-54 fields and enemy_weight retain their existing
upstream errors; they are not counted as new fixes. Counts that are not
queried stay ignored. In particular ghost_casts remains ignored when
ghost_count is zero; normal-plan/skill gates remain in place. Noninteger
options, actual checkbox fields, accepted strings, ranges, defaults and all
independent old errors keep their previous contracts. Future integer=True
queries inherit this input-type contract; adding a new mechanism still needs
its own source evidence. No global enum/count
prevalidator, string normalization or numerical/timing model is added.

Source closure first verified the immutable public snapshot, then rehashed the
cached pinned character and skill originals. All 510 selected skill/rank
blackboards match normalized parameters for the 25 control records. Per-key
records include current UI/call-site contracts and exact original rank-10
selectors. The Amiya guard form is absent from the current character_table
original and its lost char_patch raw is not claimed freshly verified; its
committed exact-selector source receipt is reused explicitly as historical
binding evidence. Ten additional existing research receipts are copied from
the same immutable HEAD. No unknown attachment, stacking, probability,
actual hit count, first tick or event clock is filled in.

The completed baseline corpus and draft execute 1,354 pairs / 2,708 public
calls. All 192 newly queried raw bool cases change to the original integer
error. The other 1,162 strict complete public JSON outcomes are identical,
including 150 inactive/query-gate cases, 184 real-checkbox calls and the old
enemy_weight and token string errors. In particular this section does not
repair the independent old summon_count string TypeError. Related tests run
51 methods, all passing; eight new methods produce 289 expected failed
baseline subtests without errors, which are defect evidence rather than
failed implementation attempts. The section-54 test migrates only four newly
guarded active fields; inactive legacy charge/activation fields stay covered.

An initial comparison helper compared fresh Python tuples with stored JSON
lists and reported 374 artifact differences. The full completed baseline and
draft JSON files proved that those preserved outcomes were unchanged. The
failed receipt/log remain in the archive and strict canonical complete JSON
comparison now passes without production edits or repeated calculation. This
is one resolved verification-preparation issue, not an invented mechanism or
an unexplained ignored failure. Exact raw source checks, caller/cache
invariants and the final independent review remain separately recorded.

Deterministic gzip artifacts preserve every completed public input and
output; receipts record both raw/gzip SHA256, sizes and decompression checks.
Do not archive the entire frozen/draft copies, active run, private settings or
personal images. No private state, game operations, chat messages, native
Windows success or current-hotfix attachment proof is claimed.

Patch SHA256:
`b12e5ca02ca6587661e82651a2b586b0c563a78a18480250a9bbde490c44e27c`.
