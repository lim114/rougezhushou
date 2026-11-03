"""Root-only dependency-repaired legacy retry; reuse unchanged other scopes."""
from pathlib import Path
import hashlib,json,sys,tempfile,uuid
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.cache/full285-preparation';sys.path.insert(0,str(BASE))
from full285_runtime_common import native,git,validate_freeze,bound_bundles,sha,write_new,FREEZE
from run_full285_orchestration import commands,execute_observed,terminal_job_record,now

def main():
    native();parent=git('rev-parse','HEAD');assert parent=='f2f8ac41ee59d92e4f0851172a9a81076c461181'
    frozen=validate_freeze(parent);bundles=bound_bundles(parent)
    # Parent failed before Qt solely because original proof_files were absent.
    old=Path(r'C:\Users\李娜\AppData\Local\Temp\rouge-full285-ec254bf0c8a64493986a510420c37811')
    previous=json.loads((old/'orchestration.json').read_bytes());assert previous['status']=='all_four_terminal'
    failure=json.loads((old/'legacy/actual/native275-launcher-closure.json').read_bytes())
    assert failure['fixture_exception']['message']=='Escaped/nonregular artifact pin'
    assert not failure['actual_current_native_windows_window_verified']
    # The original pinned expected-map independently binds all seven proofs.
    mapping=json.loads((BASE/'legacy/expected-map125.json').read_bytes())
    proofs=mapping['proof_files'];assert len(proofs)==7
    for pin in proofs.values():
        name=pin.get('path',pin.get('file'));path=BASE/'legacy'/name
        assert path.resolve().is_relative_to((BASE/'legacy').resolve()) and path.is_file()
        assert sha(path)==pin['sha256']
        if 'bytes' in pin:assert path.stat().st_size==pin['bytes']
    out=Path(tempfile.gettempdir())/('rouge-full285-legacy2-'+uuid.uuid4().hex);out.mkdir()
    write_new(out/'owned-legacy-retry.json',{'kind':'ROOT285_DEPENDENCY_REPAIRED_LEGACY_RETRY','parent_commit':parent,
        'root':str(ROOT),'created_at':now(),'controller_sha256':sha(Path(__file__)),
        'source_freeze_sha256':sha(FREEZE),'source_count':len(frozen['source_sha256']),'selector_count':len(frozen['selectors']),
        'first_attempt_container':str(old),'repair':'Only original seven expected-map proof byte files supplied; no pinned code or assertions modified.',
        'proof_files':proofs,'original_activation_tool_members_changed':False,'other_scopes_reused_not_rerun':['offline','current30','current29']})
    print(json.dumps({'legacy_retry_namespace':str(out)},ensure_ascii=False),flush=True)
    folder=out/'legacy';folder.mkdir();name,argv=commands(out)[1];assert name=='legacy'
    observed=execute_observed(argv,folder);terminal,details=terminal_job_record(folder,observed)
    validate_freeze(parent);bound_bundles(parent)
    record={'kind':'ROOT285_ACTUAL_DEPENDENCY_REPAIRED_LEGACY_TERMINAL','at':now(),'parent_commit':parent,
            'source_freeze_sha256':sha(FREEZE),'argv':argv,'observed':observed,**details,'terminal':terminal,
            'passed_claimed':False,'frozen_production_and_original_tool_bytes_unchanged':True}
    write_new(out/'legacy-retry-terminal.json',record)
    print(json.dumps({'legacy_terminal':terminal,'actual_exit':observed.get('actual_observed_popen_exit'),'container':str(out),'passed_claimed':False},ensure_ascii=False),flush=True)
    return observed.get('actual_observed_popen_exit') if terminal else 1

if __name__=='__main__':raise SystemExit(main())
