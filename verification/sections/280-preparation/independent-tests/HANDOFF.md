# Section 280 independent necessary acceptance

The first real candidate invocation passed all 33 necessary methods, actual exit 0. Test and candidate bytes stayed unchanged throughout. This is isolated acceptance, not section publication, a game observation, or a claim that P2 is complete. Production, frozen section 279/278 files, private state, game and chat were untouched.

## Exact test and real originals

- `test_skill_cost_rounding_consensus_independent_280.py`: SHA256 `f39d45a920c6f802b5995e9dc02579aa4f597b59b896fa8848fe6bf29546c404`.
- Candidate `.cache/section280-draft/rouge/skill_cost_rounding_consensus.py`: SHA256 `86853e05e770e17d8cdbaabe14d4fb9f13e576efea378333b5470a39ec78aa77`.
- `first-real-33/process.json` records the actual command, times, exit 0, 33 methods and identical before/after hashes.
- `first-real-33/` retains original test/core/runner bytes and raw stdout/stderr. Stderr SHA256 is `b1c174739ae2bb1e6a771ef4ee4f28e0899460118d5d824b5f71481a5a349602`.

Root can promote the exact test bytes to `tests/test_skill_cost_rounding_consensus_independent_280.py`. Default module is production only (`rouge/skill_cost_rounding_consensus.py`). `setUpClass` loads it only when subject is None; explicit `--module-file` assigns and retains the candidate subject. There is no automatic cache fallback or public source/data/RC selection.

Actual isolated invocation:

```powershell
.venv\Scripts\python.exe -X utf8 .cache/section280-independent-tests/run_candidate_280.py --module-file .cache/section280-draft/rouge/skill_cost_rounding_consensus.py --output .cache/section280-independent-tests/first-real-33
```

## Coverage

The golden matrices directly list conversion and operation RC alternatives, raw binary32 neighbors, final half-even integers and safe-domain failures. They cover 10 times actual Single 0.2 -> 2; 10 times actual Single 0.05 -> 0/1; actual Single 1.05 with cost20 -> 21 and cost30 -> 31/32; negative counterparts; inexact positive/negative Int32 conversion; mathematical zero with conservative signed-zero bits; MIN32 valid versus domain overflow; a partial single valid candidate which still cannot establish complete consensus; finite overflow; subnormal/nonfinite/unknown inputs; exact ties and large exact integers; three source kinds; normal/failed/unknown independent operation prefixes; independent next-action cost; and no encoder/store/current-state claim.

The two source-negative methods each first clone the full public package and assert it is valid, then flip one byte or remove one file among proof, manifest and all five SHA-guarded support documents. This gives fourteen source subcases without claiming a separate test-method count. Invalid source blocks scalar and all three kind references; public source injection is rejected. All original guarded hashes remain unchanged. Temporary paths are bounded within this cache/test directory before file removal.

## Important scope: all16 is a conservative contract

The test with cost16777217 and modifier bits `b2ffffff` is a **conditional mathematical counterexample to using the same-RC diagonal as the all16 result**. The modifier is `-2^-25+2^-49`. RN/RD/RZ conversion gives L=2^24: its product is exactly `-0.5+2^-25`, integer 0. RU conversion gives U=2^24+2: its product is `-0.5-2^-25+2^-48`; operation RD selects the more negative neighbor (`bf000001`) and gives -1, while RN/RU/RZ select `bf000000` and give 0. Consequently the diagnostic same-RC candidates are [0] but the all16 candidates are [-1,0], so the fixed conservative contract must keep consensus unknown.

This does not prove live cross-RC reachability, a game RC change, uniform probability or a physical requirement to model sixteen independently attainable cases. The adjacent source instructions have no explicit MXCSR write. Actual environment/exception-handler coupling is unproved here; all16 is deliberately an overapproximation. Additional source-backed unchanged-RC evidence could justify a separately reviewed successor, not silent narrowing of this section's schema.

An arithmetic underflow result cannot be fabricated from an illegal fractional cost: with an Int32 converted to normal integer/zero and a finite normal Single operand, these add/multiply forms do not produce a nonzero subnormal result in the supported input domain. The tests still cover subnormal operand rejection, the smallest normal operand, overflow and all invalid final Int32 candidates. They do not claim an impossible underflow sample was exercised.

## Remaining work belongs to root

The candidate source package is bound to the source agent's nine-method / 546-instruction / 759-span original proof; this acceptance does not replace that original byte evidence or prove the current machine's MXCSR, masks or handlers. Actual cost, SP and complete cycle remain null throughout. Product/UI integration, actual production unittest discovery, documentation/index commit and remote publication are root-owned. No route advice or battle intervention is added.
