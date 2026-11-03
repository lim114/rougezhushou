# Section 278 independent test handoff

Preparation/isolated acceptance is complete. This is not a claim that the product section is completed or published. Production, production tests, shared public status, another agent's cache, private state, game and chat were not modified or operated.

## Test bytes and candidate

- Current test after discovery-loading maintenance: `test_skill_data_cost_independent_278.py`, 46 necessary methods, SHA256 `103cd443d3aebbf12cfa058b40dfae34a6f2308980f0dead3f23fa2c592252f7`.
- Candidate: `.cache/section278-draft/rouge/skill_data_cost_reference.py`, SHA256 `7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a`. It was unchanged throughout every independent invocation.
- Test default is strictly `rouge/skill_data_cost_reference.py`. A preparation candidate requires an explicit `--module-file`; there is no implicit cache fallback.
- Root can promote the same test bytes to `tests/test_skill_data_cost_independent_278.py` and register its necessary selectors. This file uses the fixed exact-only cost contract and does not require RC interval-convergence extensions or four-slot initialization.

## Actual invocations and preserved failure

1. `first-real-44/process.json`: actual exit 1; 44 methods, 2 failures. Original test/core bytes and raw stdout/stderr are retained. Original test SHA256 `255a8ce076feb1a8e3c8b20e5fbfc689efc5975964e5ee6241eed4f5a58a3266`.
2. `final-real-44/process.json`: actual exit 0; the same 44 cases passed after correcting two source-contract expectations. No candidate implementation was changed to satisfy them.
3. `source-failure-extra-2/process.json`: actual exit 0; only the two added source-failure methods were executed. They cover one-byte tampering of the proof and manifest and omission of each file, helpers returning None, all five kinds retaining no numeric/store/update references, and public source overrides being rejected. Every modification was in a temporary copy; the candidate's original public proof/manifest SHA stayed unchanged.

`combined-necessary-coverage.json` records the two successful actual invocations (44 + 2). It also verifies that every original 44 method's AST body is unchanged in the final 46-method file. It explicitly does not claim a single 46-method invocation or repeat the original 44 unnecessarily.

Root found before formal execution that unittest module discovery bypasses `main()` and would leave the subject unset. The current file adds `setUpClass`: it loads the default production path only when subject is None; a subject already assigned by explicit candidate `main()` is preserved. `before-discovery-loading-maintenance-d531.py` retains the complete prior SHA `d5314002f6c2b6461c818a380c610d3e8dc0e3951fecba95a4f6ed9745887b0d` source. `discovery-loading-maintenance.json` records that all 46 test-method AST bodies are unchanged. This issue was found before a formal invocation, so no formal failure receipt is invented and cache acceptance is not repeated. Root owns the later actual production unittest discovery run.

`FIRST_FAILURE_CLASSIFICATION.json` (SHA256 `b796529195bf59c577fbbc6f087b8c9a986bd359505032a7ec7c686b3290dd0b`) explains the two erroneous test expectations. `direct-store-source-clarification.json` (SHA256 `1f167226cd3e660b8167dcb8ed7972b7d3641b2b7ce61f0760951a0edc312cb9`) freshly rechecks 7 exact original DLL instructions: a pointer comparison's normal execution is separate from its false existence result, and a normal direct Int32 type store may retain a prefix whose value is unknown without making value-independent later calls unreachable. Source agent and root independently confirmed the clarification; numerical values and actual cost/SP/cycle remain unknown.

## Coverage and exact command

Controls cover positive/negative half-even ties; exact Int32 values beyond 2^24; zero arguments without accidental skip; nonfinite/subnormal/inexact/overflow unknowns; low32 MIN/MAX/zero signed products; all five source routes; independent protected costs and receivers; encode-before-null; cost/type prefixes surviving later failures; Unity false normal return; source-ordered deferred owner guards; void update arguments; typed schema rejection; and source failure without public injection.

The cache invocation was:

```powershell
.venv\Scripts\python.exe -X utf8 .cache/section278-independent-tests/run_candidate_278.py --module-file .cache/section278-draft/rouge/skill_data_cost_reference.py --output <fresh-output-directory>
```

The added source-failure invocation also specified these exact test names:

```text
IndependentCostTests.test_source_one_byte_proof_or_manifest_tamper_blocks_all_references
IndependentCostTests.test_source_missing_proof_or_manifest_blocks_all_references
```

After promotion, a production-path invocation is `.venv\Scripts\python.exe -X utf8 tests/test_skill_data_cost_independent_278.py -v`. Runtime UI and formal source-bundle promotion remain root-owned work. These isolated receipts establish no Windows gameplay history, observed live MXCSR, protected roundtrip, actual actor payment/recovery phase, full skill cycle, or route advice.
