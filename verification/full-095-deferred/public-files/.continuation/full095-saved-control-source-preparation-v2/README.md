This is SOURCE preparation only. The helper has not been run, no saved control
file or saved proof was produced, and no project, API, Wine or Git was executed.

The original v1 helper is unchanged. The v2 helper adds exactly one 1183-byte
insertion at original byte offset 6876. Removing that exact insertion restores
all 19873 original bytes and SHA256
25e0e74b508ebde453de085009ab8f660741803a6701faaa7d76533064e3f307.
The exact insertion and hashes are recorded in
exact-inverse-saved-control095-v2.json.

Recovery acceptance requires the archived section95 source guard path, whereas
the UI source binding uses the external source guard path. The v2 insertion
reads the existing archived guard from the already-pinned original binding's
final completed_working_tree_chain row. It checks that row's actual section is
95 and verifies the archived guard path, exact SHA256
41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab,
byte count and JSON against the external guard. It adds this real full reference
to ui_binding_input_refs, preserving every original field and check. The guard
JSON has no section key; the section is checked in its actual chain row.

saved.py already independently reads every ui_binding_input_refs entry. A real
successful saved review will therefore include the archived guard's real
full reference under checked_file_refs. No saved helper or proof is patched.

ROOT should inspect the insertion and run this helper only after the actual UI
primary zero and its trusted observation exist:

    PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python /workspace/.continuation/full095-saved-control-source-preparation-v2/assemble_saved_input095.py --output /workspace/.continuation/root-full095-saved-input-spec.json

The command writes the reserved control file exclusively. A previous control
file must be preserved and diagnosed; this helper does not overwrite it.
