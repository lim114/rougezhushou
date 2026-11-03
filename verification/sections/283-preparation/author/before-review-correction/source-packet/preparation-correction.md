# Preserved preparation correction

Before literal decoding, the preparation note tentatively inferred the third
writer type from its Double boxing class. That inference was wrong: the source
RuntimeTypeHandle literal at1887faee0 is encoded4001cd07, native type59011,
System.Int32. Its branch promotes the input Single to Double, calls the unnamed
round helper, boxes the returned Double, then invokes reflection SetValue.
Normal acceptance/conversion by that reflection call is independent. This is
not the ObscuredInt branch, whose explicit CVTTSD2SI32 precedes its encoder.

The original common-panel-native-candidate and panel-writer-helper-candidate
bytes are preserved. No production implementation or tests used the tentative
Double selector label. The fixed contract uses the freshly decoded type
identities and the independently mapped mscorlib method tokens. Shared native
address184625350 has multiple method identities, including Type.op_Equality;
the three instruction bytes implement pointer comparison. Its FP equality
alias cannot establish the argument types at the writer call site.

The first ad-hoc metadata-filter command had a Python bracket syntax error and
did not write a result. The saved read_routing_metadata_283.py then executed
normally, actual exit0. This preparation failure was a script syntax error,
not target execution or an actual native mechanism observation.
