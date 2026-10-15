# 283 fixed internal precision reference contract

The parent will bind `rouge/panel_native_precision.py` and its primary source freshly before invoking it. These internal pure functions perform rational/integer arithmetic only. No public data, source, RC or evaluator injection is accepted. Input booleans, floats and out-of-width integers are rejected; `None` is an unknown value.

`fp_single_reference(raw)` accepts signed64 or null and returns exact keys:

`input_raw, complete, single_bits_candidates, candidates, reason`.

For known raw, `candidates` contains four ordered rows `{conversion_rc,bits}` where RC0/1/2/3 are nearest-even/down/up/toward-zero and `bits` is the final Single after multiplication by exact2^-32. `complete` means all normal-result RC branches are covered, including ambiguous bits; it does not mean a unique float or actual RC. Unknown input has no candidates and complete false. Multiple bits set reason `multiple_single_candidates`.

Signed64 integer conversion has magnitude at most2^63, and the largest rounded conversion is2^63. The scaled nonzero magnitude is at least2^-32. Every scaled candidate therefore has a normal Single exponent between-32 and31, so multiplication by2^-32 is exact in every RC. There are four conversion candidates; inventing subnormal results or extra multiplication ambiguity is incorrect.

`single_integer_reference(bits)` accepts independently supplied unsigned32 Single bits or null and returns exact keys:

`input_bits, complete, integer_candidates, integer_consensus, reason`.

Only finite normal/zero Single inputs within the anonymous helper's safe signed32 writer domain are qualified. Double promotion is exact; the resulting integer is invariant across RC. For the AsFloat output domain, the helper's half-offset arithmetic fits Double exactly. An independently supplied tiny normal Single can make that offset inexact, but every candidate remains between the same adjacent integer boundaries and gives0; do not claim that all tiny-normal arithmetic is exact. After rounding, CVTTSD2SI must have a signed32 value. An invalid conversion is never reinterpreted as an ordinary integer-indefinite encoder parameter. Subnormal/DAZ and nonfinite environments remain unknown. Both signed zeros yield integer0; this says nothing about a future decoded value.

`writer_integer_reference(raw)` composes the two references and returns exact keys:

`input_raw, complete, integer_candidates, integer_consensus, single_bits_candidates, reason`.

All four branches must be safe for complete true. Multiple safe integer results are complete enumerations but have consensus null and reason `multiple_integer_candidates`. If any candidate is outside signed32, complete is false with reason `int32_out_of_domain`; the remaining qualified integer subset is retained, but cannot establish full consensus. The parent must require both complete and nonnull consensus before displaying a closed encoder argument. The per-RC float rows remain available through `fp_single_reference`, and the independent literal receipt preserves per-RC writer classifications.

None of these completeness flags establish call normality, actual MXCSR/exception masks, reflection target identity, modifier activation, encoding/decode equality, panel state or actual game values. Those qualifications belong to the source-bound parent workflow.
