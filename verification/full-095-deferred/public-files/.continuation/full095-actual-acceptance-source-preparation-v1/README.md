This is SOURCE preparation only. assemble_actual_acceptance095.py has not been
run. No project, API, Wine, Git, codec, image viewer or target validator was
executed. It creates no visual-review receipt and no future PASS fixture.

ROOT should read this source and run it only after all eight actual primary
executions have returned integer zero, each physical raw status and trusted
ROOT observation have been recorded, the saved validator has truly passed,
and ROOT has used view_image on all four actual PNGs:

    PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python /workspace/.continuation/full095-actual-acceptance-source-preparation-v1/assemble_actual_acceptance095.py --visual-review /workspace/.continuation/root-full095-visual-review.json

The helper pins the actual recovery FINAL binding at SHA256
af943d5f3b0c5996c83fb5d1ee82f793c96a7937e7ed493604fa126a4bbf73f3.
It preserves the eight existing observation objects verbatim, checks their exact
argv/cwd/runner/entry/status sinks and original-epoch timestamps, checks the two
new Wine adapters began after the actual recovery, and preserves the four frozen
successful observations. The original failed Wine result is not read as a pass.

Saved common bindings are exact full references at /actual_runtime_receipt and
/actual_final_runner. The required archived source guard is bound through
/checked_file_refs/<RFC6901-escaped archived absolute path>. The external guard
at /actual_source_guard cannot substitute for it, because the final acceptance
also checks a present path even under bytes_sha256 projection. Before the real
saved execution, the v2 control helper must register the actual archived guard.

Saved artifact bindings use actual checked_file_refs full references. Artifact
coverage consists of the six fixed saved outputs plus every actual regular file
in the fresh native namespace, compared with the actual UI native file receipt.
No fixed chunk count is assumed. Symlinks, nonregular entries, aliases, missing
files, stale references and extra/uncovered native files are rejected.

ROOT must independently create its visual-review receipt after actual viewing.
The required existing shape is:

    passed: true
    actual_root_view_image: true
    actual_runtime_receipt: {path, bytes, sha256} of current wine-ui-095.json
    actual_PNGs_viewed: 4
    native_Windows_game_chat_verified: false
    screenshots: four rows, each with file: {path, bytes, sha256},
                 actual_root_view_image: true, and nonempty observed text

The helper only checks these existing genuine ROOT assertions; it cannot verify
tool usage itself and never manufactures those flags or pixel observations.
Visible facts and screenshot viewport limits belong in ROOT's observations.
Saved numeric/native/file assertions do not follow from pixels.

All input checks and rechecks precede the two exclusive metadata writes:
root-full095-primary-exits.json and root-full095-ui-extra-acceptance.json.
The witness is physically written and reread before its real reference is
placed into the acceptance file. Existing outputs are preserved. If a later
write fails, any already-written evidence remains available for diagnosis.

These files are inputs to the separately reviewed recovery context finish.
Successful metadata assembly is not a completed full095 regression, section,
native Windows/game/chat check, commit or push.
