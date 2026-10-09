# Source-only audit: current environment configuration consumers

Prepared by `/root/section099_run_persistence/io_semantics_source_review`,2026-10-09, for Root's selection of original reproductions. **No project/helper/codec/Qt/Wine/tests/Git was executed; no product or test candidate was prepared and no tracked file was written.** Findings below are Source candidates, not runtime reproductions, game-mechanism proofs or completed sections.

## Inspected current Source

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| rouge/app.py | 98887 | `f4f80b2cbc4f0865cd880b757cf991801577ea49e2b2d7cbf68dff81680d2a9d` |
| rouge/run_state.py | 54325 | `6571da263737f14fa7e07c086771f3374691f1c7af56ce7d17580988a952b2fa` |
| rouge/run_config.py | 5789 | `1b2d5287d6b6ec273e5d0b236a200906b96e27d87ed28fe067dc6d9fb3e4042d` |
| rouge/run_modifiers.py | 6678 | `c0f5de967ff160ad4ad3ad4a4823a7da158386c537297c7d032248823fe4586e` |
| rouge/battle_preview.py | 15499 | `316af4334fb33c0657dc79f2e6433bab76b900e3f4d7ca3a8149de431e172fdb` |
| rouge/enemy_environment.py | 8078 | `49a8937d46718ca5ba35a4e41244441a49afb746a4b93f52dc840609163b8439` |
| rouge/data/run-config.json | 81421 | `d35b08029a4dee14b7955136d127c0af22529858ffb559d652ac77e4e7f2c19e` |
| tests/test_run_config_validation.py | 6092 | `082ba6ee0a96d99f9c69585a429ace811ffc70cc7bbd97ebe83f8f6908a2ccfe` |

Source was read in `a9b4f2/0`,`e25614/0`,`fda59b/0`,`27713e/0`,`7471eb/0`,`cfa935/0`,`e1e2bc/0`; bounded public JSON/pins in `7c8032/0`. Searches with guessed screen_reader/node_content module paths returned2; actual readers are recognition/run_recognition/visual_recognition, and no missing guessed filename is used as evidence. No native saved record or compressed research artifact was decoded.

## Primary coherent candidate: mode eligibility, automatic confirmation and recovery

`_validate_saved_containers` requires config/difficulty records to be dictionaries and a nonempty difficulty record to contain value. It does not qualify value type, mode aliases or source leaf types. This preserves accepted raw evidence, as documented in the existing section98 contract.

Current `difficulty_value` requires exact integer grade in the pinned0–15 NORMAL map and checks only `modeDifficulty` when supplied. `prepare_run` checks **both** explicit `modeDifficulty` and `mode`, rejecting either non-NORMAL before enemy scaling. That direct API rejection is already covered by `test_run_config_validation` and is correct existing behavior.

Consequently, this JSON-native record is a Source candidate for inconsistent consumer eligibility:

```json
{"value":2,"mode":"MONTH_TEAM","captured_at":1000,"source":"public-env106"}
```

It can be embedded in a saved config with operators/relics/resources/tactical_tools/maps empty dictionaries, history empty, run id a nonempty string, started_at0,last_read1000 and relic_icon_memory null. Those complete outer fields avoid unsupported shapes; the candidate is the consumed difficulty leaf, not an invented Python object. Use `mode="NORMAL"` and omitted mode as otherwise identical healthy controls. MONTH_TEAM is the existing negative-test string, not a claim that a new game mode is supported; arbitrary HARD likewise means unsupported input.

Source chain:

1. Load keeps the record. Fresh RunState.apply also admits it because it calls `difficulty_value`, which ignores mode. No numerical rule is invented or silently applied at that admission point.
2. `recognition_context` deep-copies it; `confirmed_config` reuses it because grade2 qualifies and captured_at is nonnull.
3. `read_run` merges known/fresh; `read_config` suppresses the badge-grade path when difficulty is already a known member. Explicit full info-panel grade recognition remains available and can replace the record, so this is a potentially blocked badge-only recovery path, not proof all recovery is impossible.
4. `MainWindow.sync_run_config` disables its grade combo whenever the record is not None, uses the automatic-confirmation tooltip whenever the dict is truthy, and tries to select its raw value. `RunState.summary` prints raw grade2 without mode eligibility qualification. This is inconsistent with the numerical consumer's explicit unsupported-mode contract.
5. `MainWindow.calculate` passes raw config to the original numeric API. `prepare_run` raises its existing mode ValueError; MainWindow catches Exception, clears damage_result and displays the error. `enemy_preview` catches ValueError/KeyError and returns environment=None/context_pending. These are existing rejection/pending paths, **not** an unhandled startup crash or a demonstrated wrong enemy number.

Fresh producer-shaped difficulty `{"value":2,"source":"public-normal"}` at a later timestamp overwrites the raw old record when directly applied; the same grade does not add a config identity-change history event. Source does not establish that a real image will reach that producer after known reuse, so Root must separately check normal read/recovery reachability. Null captured_at prevents reuse already and must remain a short-circuit control.

There is a related exact-frame cache identity issue: recognition.ScreenReader filters confirmed-config fields to value,modeDifficulty,id,name,level,usage,effect_verified,source, **omitting mode**. Two currently reused records differing only in mode can have the same image-cache context key even though numerical eligibility differs. A shared supported-mode qualifier may naturally separate the unsupported record from the known context; alternatively the cache identity must include all fields that still affect accepted consumer semantics. This is a Source risk, not a performed OCR/cache experiment.

Minimum coherent direction after Root's original reproduction: qualify automatic-confirmation and known-config use against the already existing supported value/both-mode contract, retain the original stored record unchanged on read, expose unusable/pending status honestly, and allow a later legitimate normal observation to recover. Do not convert invalid values into zero, invent non-NORMAL rules, or relax explicit numerical errors. No specific product design is authored in this report.

## Second concrete environment consumer candidate: difficulty source formatting

This otherwise eligible JSON record is also accepted and reused:

```json
{"value":2,"captured_at":1000,"source":null}
```

Missing source, empty string and ordinary string are safe Source controls. Nonstring null/list/dict/int/bool source leaves are preserved by the saved loader and not rejected by `prepare_run`. The numeric API can carry them into `run_resolution.difficulty`; `reporting.py`'s run-environment note directly concatenates `difficulty.get('source',fallback)` with strings. An explicit nonstring source therefore reaches a Source TypeError at report construction, while a missing key uses the fallback. MainWindow's render_damage is inside its calculation Exception handler, so it clears damage_result and displays that error; this is a blocked report/result workflow, not process-crash proof or a newly wrong mathematical rule. Root should separately reproduce numeric success and default/technical/estimate-format behavior, retaining caller/raw disk facts.

Source metadata is not a universal game-evidence schema. A rendering capability fix must preserve valid grades, missing/empty/string behavior and opaque stored leaves without fabricating a human source or treating arbitrary nonempty metadata as a mechanism confirmation. Normal new producer records have string source and can replace the bad raw record; known membership currently suppresses badge-only reads in the same way noted above. This candidate can fit the supported-environment confirmation/display/recovery group, subject to Root's actual evidence and scope choice.

## Squad flags, level and source: limits and already fixed controls

Known string ID/exact name/timestamp qualifies squad reuse. Cached unhashable/unknown IDs and corrupt old verified-record protection were already addressed in103, so do not repeat them as new fixes. Actual previous booleanTrue/known fixed name protection still prevents a legitimate stronger trade record being weakened by a same-name incomplete badge.

Explicit nonboolean effect_verified is already rejected by prepare_run before attribute rules, and False/omitted flags preserve pending squad stats; existing tests cover this. Importantly, current103 test `test_unusable_old_verification_flag_stays_raw_until_new_valid_badge_replaces_it` deliberately requires known-identity records with flags string/1/null/list/dict to remain raw through confirmed_config and unused reads, then recover through a real valid later badge. A new all-purpose strict squad-reuse filter would break that contract. Any106 change needs a deliberate consumer-specific boundary and retained raw/unused semantics, not blanket schema enforcement.

Squad level is not used to select numerical buffs: fixed ID data plus effect_verified determine those rules. Summary alone currently labels any nonnull level equal to1 as strengthened, everything else as base. A boolTrue or unrelated value can therefore mislabel raw stage information; however, it does not establish a numerical buff bug. Source producer uses fixed bandLevel for verified tooltips and None for unverified shared-icon badges. A stage-display refinement must preserve unverified None and must not infer verified stage from the shared base icon or invent a stage schema. This is a bounded display candidate, lower priority than the concrete mode/source chain.

Squad source is not consumed by the located numerical rules or this difficulty-source concatenation. Arbitrary squad source metadata alone is not a crash or buff eligibility finding. Unknown source strings should not be treated as automatically verified. Preserve existing source leaf/unused behavior unless a real consumer needs a qualification.

## Exclusions and next evidence

- Noninteger/out-of-range difficulty and explicit non-NORMAL modeDifficulty are already excluded by difficulty_value from fresh admission/reuse; numeric API also rejects unsupported values. Their loaded raw UI lock/summary can still be inconsistent, but do not claim numerical acceptance.
- Empty difficulty dict is already absent for numeric/reuse gates; sync_run_config nevertheless disables on non-None while showing its unconfirmed tooltip. It is a display/control consistency case, not a claimed crash or confirmation of grade0.
- No unsupported-mode enemy scaling was observed; battlepreview's existing caught-error path is safe. Enemy target bool handling belongs to the sibling audit; Root already noted later enemy_skill_reference guards mean preview bool is not newly accepted. Do not duplicate that false positive.
- Raw difficulty is also copied to map metadata/generation consumers. This is a related Source qualification risk, not a proven actual map/UI failure or permission to expand106 into a new game rule.
- No new native timing/summon/environment clock evidence was found or invented. E0 rank, extra DEPLOY and unknown technical buff mechanisms remain outside this candidate.

Root should first archive original Source-bound JSON/API/UI reproductions with same-condition healthy/missing/unused controls. Only actual evidence can choose the coherent106 product scope. This read-only audit contributes zero completed sections and contains no candidate code or tests.
