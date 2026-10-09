# Account093 saved-only verifier draft

This draft was source/AST reviewed only. It has not been executed; root alone runs it after the exact FINAL Wine process finishes. It imports only the Python standard library and never imports or runs the product, Qt, Wine, original runner or original codec. Existing FINAL packets and tracked files are unchanged.

Use the directory containing the exact three adjacent files that root executed for `--final-dir`; preserve their original names. The runner writes its receipt, gzip archive and three PNGs to `/workspace/.compat`. Use a new external report path so old evidence remains intact.

```bash
python /workspace/.continuation/ui-093-account-cache-saved-validator-draft/verify_saved_account093.py \
  --outputs-dir /workspace/.compat \
  --final-dir /workspace/.continuation/ui-093-account-cache-final \
  --repo /workspace/rougezhushou \
  --formal-review /workspace/.continuation/ui-093-account-cache-final-independent-review/source-only-final-review093.json \
  --report /workspace/.continuation/root-saved-account093-review.json
```

If root executed copied files under `/workspace/.compat`, set `--final-dir /workspace/.compat`. The verifier refuses an existing report path, writes only the new report, and exits 0 only after all saved checks pass; it exits 1 for failed/incomplete runner receipts, wrong bindings, missing artifacts or failed consistency checks. It preserves failed-prefix counts in its report and does not promote them to success.

The confirmed input names are `wine-account-window-093.json`, `wine-account-window-093-records.json.gz`, `wine-account-window-093-final.py`, `wine-account-window-093-source.json`, `wine-account-window-093-plan.json`, the exact formal source-review receipt, and the three PNG filenames attached to their planned states. It reads current public maintained source files listed in the 732-file guard; temporary account/run directories have already been removed, so their bytes are verified from saved `raw_hex` evidence instead of accessing old Windows paths.

Output JSON root fields:

- `format_version: 1`, `passed`: true only for complete saved verification, `status`: `PASS_SAVED_ONLY_ACCOUNT093` or `FAIL_SAVED_ONLY_ACCOUNT093`, and `project_calls: 0`.
- `input_bindings`: actual absolute input path → `{bytes, sha256}` for every successfully read runner/guard/plan/formal receipt/runtime receipt/archive/PNG. A failed report may contain a partial binding set.
- `input_receipt`, `saved_prefix`, `completed_saved_state_checks`, and `snapshots_verified_before_completion_or_failure` preserve the actual evidence scope.
- On success, `actual` contains measured state/window/numerical/error/early-return/button/text/API/call/snapshot/source counts; none are preset numerical-success counts. `numerical_API_bindings` records each numeric state's actual API sequence and originating step, marking inherited results explicitly. `PNGs` records bound state, filename, bytes, SHA256 and PNG dimensions.
- On failure, `error: {type, check, message}` identifies the failed condition. Missing prerequisites do not become skipped passes.
- `native_windows_verified: false`, `root_visual_review_required: true`, and `scope_limits` keep saved consistency separate from native Windows or visual acceptance.

The independent codec uses explicit stacks for graph inversion and canonical re-encoding. It verifies exact scalar/key/container types, graph aliases/order/float hex, full JSON projections and every saved snapshot. It checks the 132 states against plan order, calls/API record identity and same-step counts, mandatory caller pairs, full RunState memory/disk preservation, original public account bytes and write protection, deep500 B1 chains, B2 masked incoming-only recovery, current 732-source hashes, and three PNG hashes/CRC/IHDR metadata.

Numeric states that do not recalculate (for example rejected older observations or the shallow-view probe) may inherit the latest matching API result from an earlier step in the same case; this is recorded rather than inventing a same-step API call. Caught helper exception events are allowed. Qt slot exceptions and unfinished targeted calls are rejected.

The runner receipt does not save a runner self hash or plan SHA. Root's actual process record must establish that the bound runner/plan produced these outputs. Saved JSON cannot independently prove a Python object's RunState class identity, technical-view display transitions or screenshot pixel visibility. Those remain source-bound runner assertions and root's inspection of all three actual PNGs. The frozen Wine matrix covers masked B2 only; no standalone Wine unmasked-inert99 case is claimed.
