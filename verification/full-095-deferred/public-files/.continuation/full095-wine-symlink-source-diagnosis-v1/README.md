# Full 095 Wine symlink prerequisite diagnosis — SOURCE only

The two failed `AccountCache093Tests` methods failed before constructing
`AccountCache`: the dangling control was not a link, and the damaged control had
no readable link path. The installed Wine 10.0~repack-6 `CreateSymbolicLinkW`
binary and exact Debian source implement a success-returning stub. CPython
3.12.10 trusts that return code. This is source-supported attribution of the
fixture prerequisite failure, not a passing product test or a native Windows
result.

`source-diagnosis-wine095-symlink.json` binds the original failed full-suite
receipt and raw primary exit `1`, the unchanged product/test files, exact
installed binaries and downloaded official source documents. Each official file
was downloaded through the inherited proxy with normal TLS verification.
`installed-kernelbase-CreateSymbolicLinkW-disassembly.txt` was produced by
read-only `objdump`; the DLL was not loaded or executed. The ntdll export listing
identifies a possible narrow Wine runtime predicate; this agent did not call it.

The recommended next step requires a separate real root capability probe on the
same Wine runtime and temporary filesystem. Only after that evidence exists may
an explicitly reviewed external execution adapter declare the two exact
symlink-fixture tests unavailable. It must preserve the original failure, retain
every other test, and leave `complete_repository_validation` false. A different
argv or binding requires a new reviewed runtime contract. No original receipt or
immutable context may be edited into a pass.

The existing tests remain fully exercised on Linux. Native Windows returning
success without creating a real link remains a failed prerequisite; existing
OSError/NotImplementedError skips for unavailable API or creation privileges are
unchanged. There is no permission to skip arbitrary Windows/Wine tests, relabel a
product assertion after execution, mock link semantics, or weaken damaged-file
preservation.

CPython's official `can_symlink()` is included as contrary evidence: it checks
only a non-raising creation call before removing the supposed path and therefore
does not solve this Wine success-stub case. Do not copy it without verifying the
actual path through `lstat`, `is_symlink`, and `readlink`.

This packet performs no target/helper/project/API/test/Qt/Wine execution and no
tracked edits or Git writes. It completes no new section. SOURCE attribution is
complete; runtime capability and any proposed adaptation remain unverified.

STOPWRITE after the manifest and handoff are created. Preserve this original
packet; later probe evidence belongs in a separately sealed packet.
