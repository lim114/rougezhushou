# Section 285 B · draft only

Production is unchanged. This proposal adds useful access to the 284 primitive
capture: the existing panel/pair/skills worksheets can address the current
extended operator instead of rejecting the imported context. It is not a new
query, numerical model, source-mechanism verification or native-panel claim.

## Files and exact current source guards

- `rouge/calibration.py` original `72fa76dcb8592b7eb539ddc4d9440cb84e92449d30795b3de9bf9b81f0006691`.
- `rouge/offline_tools_view.py` original `05de5293607b57114b20f9a228882ec2a771cd0b1606e4d215518c4680e2d3e4`.
- Drafts are under `draft/rouge/`; exact hashes are in `draft-manifest.json`.
- Candidate test file `test_extended_calibration_285.py`: 12 test methods,
  SHA `8255036dc63b02db7a658b186072bfe406574c6b018cf46989c0880694987d1f`.

Only source parsing/compilation has run. No candidate functional tests have run,
no prototype PASS receipt exists, no production file has been promoted, and no
game, private run directory, chat or original application window was accessed.

## Fixed contract

1. `_scenario` still defaults to the first three. Only `panel_layers` and
   `skill_matrix` explicitly allow the fixed 32-operator catalogue;
   `compare_panel` uses `panel_layers`. Other worksheet scope stays unchanged.
2. The public basic skills example still produces the legacy nine skills.
   An extended base defaults to itself. An explicit selector may retain the
   historical first-three subset, or it must select only the current operator.
   It may not copy extended conditions across owners.
3. The matrix adds selected-owner identity, per-row key/id/skill identity,
   names for locked skills, explicit unlock reasons, and `unlocked`.
   Locked rows never call `calculate_damage` and have no native result.
4. Available rows deep-copy that skill's existing main native result and
   declared components. They do not invoke another native evaluator. Legacy
   nonzero full totals and all extended full totals remain unknown; existing
   declared special components remain visible separately.
5. The current-context import only widens panel/pair/skills. Skills import
   always writes `operators=[current]`, including first-three imports. Pair
   import preserves the independently entered observation and context token.
6. Existing query count stays 27 calibration + 10 battle. The skills title
   becomes `全部技能与条件分项`; guidance explains legacy nine defaults.
   Each unlocked row shows only the two copied native skill fields and reasons.

## Necessary candidate test plan

The test's production default is `rouge.calibration` / `rouge.offline_tools_view`;
it never searches cache automatically. Explicit prototype command, only after
root authorizes execution:

```powershell
.venv\Scripts\python.exe -X utf8 .cache/section285-preparation/test_extended_calibration_285.py --draft-root .cache/section285-preparation/draft -v
```

- Synthetic routing markers cover all 29 extended owners / 78 skills and the
  unchanged first-three nine. These prove adapter routing and deep-copy
  ownership only; they are not 87 new numerical or mechanism verifications.
- Actual narrow main controls: Myrtle four-layer/current-context pair,
  Deepcolor's two skills with unknown ATK/special components preserved, Shu's
  locked row names/reasons and the Chinese native/conditional output.
- The first-three subset keeps the previous foreign-module/special-key cleanup.
- Cross-owner selectors, invalid ranks/internal fields and widening other
  worksheets are rejected.
- Two isolated Qt tests instantiate only `OfflineToolsPanel`, never show a
  window, never instantiate `MainWindow`, and check explicit imports, original
  buffers/observations and restrictions. They use no private state.

Keep first actual test source/output/exit snapshots even if a premise or code
fails. The root owns promotion, final public receipts, actual Windows window,
the final 285 full regression and publication.
