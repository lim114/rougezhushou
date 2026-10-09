# Source-only account097 consumers and preservation contract

This document describes inspected source. It proves no runtime behavior and
supplies no completed96 baseline. Root remains the sole tracked-file writer,
Wine executor and Git executor. This author did not run project/helper/codec/
tests/API/Qt/Wine/Git or read private state.

The frozen account candidate core is 11551 bytes / SHA256
`29bf05d1c7fc111b2e74977be6ca413bb0a25c50cead69fe3a04237ef5a2768e`.
Its independent review is 22994 bytes / SHA256
`93c2bf45845c36bf24440574b3d8aa300ee23140a687e9535c04389da3223635`:
20 source checks, no blockers, project runtime pending. The earlier author
handoff predates that independent review; its formal_source_pass=false is not
silently rewritten. Both retain their attribution and original hashes.

The current app source used for source-only consumer inspection is 96725 bytes /
SHA256 `589b9ac2b846206581c394d037baec0d9e43a165a7bdd5becc0982ab0e09c0fd`.
The future096 app candidate is 99159 bytes / SHA256
`0c388853b351e3869a01f32f42058fc8e0a0cb23fc67f25d6141bde13350423d`.
Neither source inspection establishes completed096. Root must resolve actual
source coordinates after096, then require exact hashes and a whole reviewed
adaptation if they differ from these candidates.

| Source flow | Practical output | Required future observation |
| --- | --- | --- |
| `MainWindow.__init__`, app:102–104 | Real AccountCache records alias and real RunState | Whole startup state and exact `.json`/distinct `.tmp` path roles; no private inputs |
| `AccountCache.observe` assigns merged record before calling save, candidate:233–239 | Valid facts survive a failed save | Caller and full record graph before/after; true return with saveFalse; separate exact original baseline exception |
| `MainWindow.apply_operator_observation`, future096 app:898 | Accepted account read follows actual UI identity and refresh path | Native account-failure continuation recorded once; original refresh/button common probes pair against baseline |
| `MainWindow.current_operator_state`, future096 app:799 | Account reference overlaid by present run-confirmed fields and run ranks | Run level1 wins account levels2–7 when checkbox enabled; disabling exposes account; full run/caller unchanged |
| `MainWindow.account_training_status`, future096 app:810 | Visible cultivation provenance plus persistence notice | Both old provenance prefix and precise new failure suffix; run_confirmed handling retained |
| `MainWindow.sample_received`, app:448–480 | Visible operator summary body plus account notice | Real constructed ordinary public delivery through this consumer; no capture/OCR claim; no native opaque pair sent into Qt raw text |
| `training_conditions` and `skill_rank_value`, app:806/814, shifted after096 | Existing explicit training into calculation | Equal accepted effective facts give complete same scenario/results/all three reports/native math vectors |
| `update_operator` / `show_observed_operator`, app:819/891, shifted after096 | Selection, preview labels, level/manual markers and provenance | Full controls and tooltips retained; same source-bound old behavior except declared notice/failure continuation |
| `calculate`, app:1019, shifted after096 | Original calculation and rendered reports | Actual button requests and original numeric calls; no count forecast, caller mutation or truncated output |

The ordinary observation route can preserve opaque text in an unknown-ID record,
an unupdated other-ID record, and unoverwritten mapping leaves of fields,
sources, field_times and skill_times. Same-ID old top-level extra may disappear
under the unchanged producer. The plan preserves that behavior and does not
invent a broader retention rule.

`_integer`, `_timestamp`, `_record_issue`, `_merged_record`, `_protect`,
`_screen_all`, `view` and `observe` are complete unchanged source functions.
The candidate changes only constructor session save_issue, notice and save.
Save retains `_screen_all` and permanent preserve_original return before the new
serialization boundary. Save failure cannot unlock a damaged load; later valid
observations cannot erase the original protection. `load_issue` remains separate
from `save_issue`. New-session recovery is demonstrated only with a healthy
preserved original and a new object, never by clearing a protected object.

The real UI failure construction is a nonempty directory at the distinct public
`account.tmp` role. It gives an actual write_text/open OSError without assuming
chmod defeats root privileges. Original target bytes and the directory sentinel
are captured whole before/after. Moving the owned fixture barrier out of the way
is a declared fixture operation that retains evidence; product cleanup, delete,
retry and replay remain absent. Other IO stages and partial writes are separately
labeled injected unittest boundaries, not permission or UI claims.

Official Python3.12 JSON documentation/RFC8259 and independent stdlib probes are
already pinned in the survey/source review. They establish a narrow CPython text
lead, not project success or interoperable Unicode. Native adjacent high→low
surrogate strings must be constructed as two Python codepoints; JSON escaped
pairs decode as a scalar and cannot serve as that fixture.

The historical five native/byte codecs remain whole in the copied source
reference. Their raw string nodes are unsuitable for direct durable evidence of
these native pairs: ensure_ascii=False cannot UTF8-write lone surrogates, while
ensure_ascii=True alone folds adjacent pairs when JSON is decoded. The only new
transport is a source-pending string-node ord-array envelope/inverse. Its decoder
accepts integer ordinals0..0x10ffff including surrogate ranges, rejects bool,
negative and out-of-range/type-invalid entries, and restores every old node field,
reference, order, native type and alias. Full native graph is authoritative;
optional JSON projections carry explicit applicability and never certify native
pair equality. Root must execute the controls and review the concrete FINAL
source; this author executed none.
