# Section 102 window runner v2: independent Source review

Status: **Source reviewed; no blocking Source defect found for the stated 6-window Gold and 14-window candidate workflow. No runtime execution by this reviewer.** This report does not certify a project, Qt, Wine, numeric, screenshot, or Windows result. Root owns the actual runs and their raw exit codes.

The author is Root. The reviewer is `/root/section100_training_cache_audit`. This review read text, parsed AST/JSON, hashed bytes, and compiled source in memory only. It did not import or execute the project, runner, helper, codec, tests, Qt, or Wine; it did not use Git or modify tracked repository files. The earlier v1 is an inactive Source proposal; no v1 attempt is being counted as a product failure or successful check.

## Frozen inputs and checks

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `window102.py` | 17747 | `3a808939a0604d3f40a421d4e8e06d3e2408a8cd6885746e0e6b9ff63d49b2e3` |
| `native_evidence.py` | 6468 | `f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a` |

These are the files in this directory. The manifest agrees with both actual hashes. Reviewer `fa9e59/0` parsed and compiled the runner and helper without executing them. `6b6d47/0` repeated the frozen hash/AST/compile check and read the Source manifest. Compile success is only a syntax check.

Actual repository text read for consumer/fixture alignment:

| Source | Bytes | SHA-256 |
| --- | ---: | --- |
| `rouge/app.py` | 98887 | `f4f80b2cbc4f0865cd880b757cf991801577ea49e2b2d7cbf68dff81680d2a9d` |
| `rouge/run_state.py` | 53187 | `91c8a463037f0691677e1b3fd2b6b44f5543a608807d2e10be508512c71b45a1` |
| `rouge/run_config.py` | 5738 | `e35262ce5fc74db31ea80704f5689bb05619fd9dc9798a334f8cac3455b4ac99` |
| `rouge/relic_recognition.py` | 18803 | `8f2087341b1d99e1bd442775bef367b5f7a1352cfc27e617bff77bd42ceb1256` |
| `rouge/desktop_backend.py` | 4456 | `faf0c399bec6d1d0a9a9927bc48896a2c061a559f3fcb63a55ba2d5bad3defb9` |
| `rouge/data/run-config.json` | 81421 | `d35b08029a4dee14b7955136d127c0af22529858ffb559d652ac77e4e7f2c19e` |
| `tests/test_relic_grade_sync_032.py` | 12557 | `d3f3347c6d834b5fc150f4a6e178ba16c4016d70806ebaf85e672e875bfce5ef` |

This is the actual section-101 Source basis, not a claim that the current tree remains the older 743-source baseline. The runner itself requires 745 Gold sources and 746 candidate sources from Root's supplied guards. This reviewer did not execute `source_map` or pre-authorize an unobserved candidate transport.

## Review conclusions

1. **The Gold wrapper mismatch is resolved.** Native records contain `kind` and `case`; candidate v2 validates those wrapper fields and then compares the three real payload keys `view`, `durable`, and `disks`. It does not compare a wrapper-bearing Gold record with an unwrapped candidate payload. Each of the six expected healthy case IDs must be found in the six-row successful Gold receipt.

2. **Gold evidence and Source identity are bound before candidate import.** Candidate requires the external Gold exit file to contain `0`, Gold `passed` and `workflow_complete` to be true, phase `gold`, the same runner hash, six rows, unchanged Source/CORE hashes, no Qt errors, and explicit `native_windows_verified=False`. It requires the exact old-to-new Source difference: one new `tests/test_inventory_confirmation_102.py`, no removed source, and only `rouge/run_state.py`, `scripts/verify_full_available.py`, and `scripts/verify_cloud.py` changed. Source and additional CORE files are checked before import, before success, and again in `finally`; detected drift clears success. Raw exit and Source binding still need Root's actual observation.

3. **Temporary isolation uses actual public consumers.** Each case owns a new temporary run/account/settings directory; the account and full run JSON fixtures have public catalog identities and mandatory containers. Root paths are assigned before constructing the real `MainWindow`. The actual DesktopBackend class is retained and only its storage path is redirected to the public fixture folder. Its constructor does not start Node; idle checks require no process or pending request, sampling unchecked/timer stopped, no busy chat/sample operation, and no captured Qt callback errors. The Source calls neither game connection nor sampling nor chat requests. Constructor/window behavior remains an actual-runtime question.

4. **The numeric and formatting path stays original.** The wrapper delegates to the saved real `calculate_damage` function, checks the actual positional/keyword caller before and after, and records the returned native result. The window invokes its real `calculate` method. A non-None damage result is required. The snapshot stores the complete actual damage result, actual status/summary/held/tool projections, durable state, and public disk bytes. It calls original estimate, default-report, and technical-report formatters, verifies their input remains unchanged, verifies estimate equals the default report, and verifies the actual text widget matches the default report with only the existing NBSP display normalization. The six healthy candidate snapshots use the native comparator, which preserves exact built-in types, float bits, ordering, and container reference structure. Separate calculator caller records are retained and checked within each phase; they are not separately paired across Gold.

5. **Healthy edge fixtures preserve the existing numeric contract.** Gold has true, false, and null flags; count values include integer zero, float zero, negative float zero, and float total three with two real relics and one real tactical tool. This is aligned with the section-102 consumer proposal preserving original bool/int/float/None flag behavior and existing count behavior. The runner does not claim that its six GUI cases cover every legacy numeric flag; the runnable section-102 tests cover additional compatibility controls separately.

6. **Historical restoration is sourced from the existing public API.** The ambiguous `rogue_6_relic_legacy_24` bar is created through real `RunState.apply` at count one, with the existing four candidates and a complete-bar observation. The Source difficulty table gives those identities grades 0, 3, 6, and 9; real grade 10 resolves the existing `_c` identity, consistent with the original resolver and `test_relic_grade_sync_032.py`. The candidate injects only the malformed raw confirmation flag into that genuinely generated historical state. The invalidation control first applies positive count two without icons, which the existing reconciliation path uses to invalidate the previous full-bar memory. Grade-only replay therefore must not confirm that case. It does not invent a new relic rule or infer a missing counter value.

7. **New proof is distinguished from a partial observation.** Full current-bar proof includes two fixed relic IDs and one tactical tool, and expects total three / relic expected count two. Explicit current zero expects no held relics or tools. Both and valid history must produce actual boolean confirmation. Partial/no-history and invalidated-history must remain incomplete; the partial case also must retain the original malformed raw flag. The fresh observation is checked for caller preservation, followed by the real application/save path. The direct RunState restart then checks exact confirmation flag/status and unchanged saved disk phase.

8. **Screenshots and success gates are reachable and scoped.** Actual tab zero is `采样测试`, where the real `run_summary` label is constructed; tab one is `伤害测试`. Four candidate cases switch to tab zero through the same read-only state/disk check, then save actual `window.grab()` PNGs. Every case must complete construction, explicit calculation, snapshot checks, and close checks before its row is appended. Success requires all six/fourteen rows, no Qt errors, the exact PNG count, and stable Source/CORE hashes. A failure or timeout cannot become a normal successful workflow receipt. Actual PNG rendering/content must still be inspected by Root; a positive `save` return is not a visual review.

## Evidence limits and precise wording for Root

The v2 Source contains **six Gold constructions and fourteen candidate constructions**, not fourteen real reopen cycles. Five candidate cases with an action use a real observation, authorized save, and direct `RunState` reload. The three malformed no-action cases (`bad-text`, `bad-list`, `bad-dict`) have real construction/calculation/views/close raw-state checks but no reload. None of these v2 cases constructs a second real MainWindow after closing. Root should describe that exact scope, not all windows as reopened. A minimal extra RunState reload before closing the no-action cases could extend that narrow coverage, but it is not necessary to run the currently declared v2 workflow and would require a fresh Source version and pin.

Disk evidence retains complete public run/account bytes and temporary-file presence flags. Every initial fixture requires both temp files to be absent. It does not test survival of a pre-existing `.tmp` file or preserve such a file's bytes, and should not be reported as doing so. Read/view/selection/close phases keep the current raw bytes; an authorized new observation uses its own legitimate saved disk phase.

The calculator wrapper records successful original results and caller preservation. It does not independently capture a raised numeric exception before the app catches it. This runner's intended catalog-valid cases require a non-None result and therefore cannot silently turn such an exception into window success, but it is not a dedicated unknown-numeric rejection probe.

No Root runtime receipt has been interpreted as passing by this review. The four screenshots, actual Gold raw exit, actual candidate raw exit, saved-native audit, source drift check, and any genuine Windows availability all remain Root's responsibility. This Source explicitly labels the environment as not native Windows.
