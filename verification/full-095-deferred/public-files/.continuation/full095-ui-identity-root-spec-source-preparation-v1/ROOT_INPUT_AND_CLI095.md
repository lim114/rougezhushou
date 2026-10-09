# Section95 identity Root-spec assembly: Source-only

This packet prepares a stdlib helper for Root. The author only parsed/compiled Source and verified physical Source references. No assembler main, project, tests, codecs, context, sealer, UI, Wine or Git was executed. Sections96–98 remain paused.

Root must supply the two actual independent Source-review files and their real SHA256 hashes. Each review must expose `/source_gate_passed=True`, `/runtime_pass=False`, `/runner_sha256` equal its reviewed producer or Saved runner, and `/execution_argv` equal the full launch argv. The UI review must also expose `/source_keys` equal the unchanged129-own-key list. These actual review references are not guessed here.

Root command, with actual values substituted:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python /workspace/.continuation/full095-ui-identity-root-spec-source-preparation-v1/assemble_root_identity_spec095.py \
  --ui-formal ACTUAL_ABSOLUTE_UI_REVIEW_PATH --ui-formal-sha256 ACTUAL_UI_REVIEW_SHA256 \
  --saved-formal ACTUAL_ABSOLUTE_SAVED_REVIEW_PATH --saved-formal-sha256 ACTUAL_SAVED_REVIEW_SHA256 \
  --output /workspace/.continuation/root-full095-ui-identity-retry-v1-actual-spec.json
```

If the reserved identity prelaunch already exists, preserve it and add `--prelaunch /workspace/.continuation/root-full095-ui-identity-retry-v1-prelaunch.json --prelaunch-sha256 ITS_ACTUAL_SHA256`. Otherwise the helper creates that file exclusively after every check succeeds, using its actual invocation time. Prelaunch `actual_Root_epoch_binding` is the existing b83 prior binding, avoiding a cycle with the new binding not yet sealed. A new FINAL binding is a subsequent Root sealer output.

Before writing, the helper verifies frozen Source packets, pinned physical references,907 producer AST assertions, current735 maintained hashes against41b9 and b83, loss capsule bcbf with primaryNULL/causeUNKNOWN/two incomplete attempts, and six unmodified actual primary-zero observations. Every21 identity UI/control sink and the native namespace must be absent. It derives the UI projection directly from prior `b83.root_spec.ui` and the producer contract, updating only runner/review/argv/output paths, and fills Saved runner/review references. Pending or missing values cannot assemble.

The resulting status `ROOT_BOUND_ACTUAL_FULL095_UI_IDENTITY_RETRY_SOURCE_INPUTS` is Source metadata readiness. Obtain an independent review bound to that exact completed spec and frozen context packet, run the Root-only exclusive context sealer, obtain an independent FINAL Source/spec review, then resume and run the actual third UI attempt. All finish/save/publication gates remain required. A third same-issue failure or interruption requires preserving evidence and deferring. No fourth attempt or future development is authorized here.

Root must capture real primary exit/logs for each metadata/runtime command. No old exit or receipt is created or replaced.
