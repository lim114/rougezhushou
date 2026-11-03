#!/bin/bash
set -uC
test "$(cat /workspace/.continuation/root-window-094.exit-code)" = 0 || exit 1
python /workspace/.continuation/ui-094-saved-validator-draft/verify_saved_inputs094.py \
  --outputs-dir /workspace/.compat \
  --final-dir /workspace/.continuation/ui-094-offline-input-refresh-final-v2 \
  --repo /workspace/rougezhushou \
  --expected-final-runner-sha256 cdc58d5efa9dd88512be87035b786c87ab58606646266258846854f379c498be \
  --expected-guard-sha256 259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211 \
  --formal-review /workspace/.continuation/ui-094-final-independent-review/source-only-final-review094.json \
  --expected-formal-review-sha256 940f7842a11f5b23b71af5f47c51ed405395d151b3fe3da2837c58bbac1b8578 \
  --review-success-pointer /source_gate_passed \
  --review-runtime-pass-pointer /runtime_pass \
  --review-runner-sha-pointer /runner_sha256 \
  --review-guard-sha-pointer /source_guard_sha256 \
  --review-plan-sha-pointer /plan_sha256 \
  --report /workspace/.continuation/root-saved-focused094-review.json \
  > /workspace/.continuation/root-saved-focused094-review.log 2>&1
p2_saved_status=$?
printf '%s\n' "$p2_saved_status" > /workspace/.continuation/root-saved-focused094-review.exit-code
exit "$p2_saved_status"
