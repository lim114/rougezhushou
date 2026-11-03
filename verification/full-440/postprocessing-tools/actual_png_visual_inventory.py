"""Inventory a sealed full440 archive; reuse only exact prior PNG appearance.

No Qt, screenshots, windows, tests, source edits or private-state access. This
tool must be invoked by root only after the original full execution is archived.
"""
from pathlib import Path,PurePosixPath,PureWindowsPath
from hashlib import sha256
from datetime import datetime,timezone
from collections import Counter
import argparse,json,struct,sys

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
SCHEMA='full440_actual_png_visual_inventory_v1'
PROOF_CACHE={}


def digest(raw):return sha256(raw).hexdigest()


def regular(path,base=ROOT):
    path=Path(path)
    if not path.is_absolute():path=ROOT/path
    if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(base.resolve()):raise ValueError('Exact regular public file required: '+str(path))
    for parent in path.parents:
        if parent==base:break
        if parent.is_symlink():raise ValueError('Linked parent refused: '+str(path))
    return path


def relative(path):return path.relative_to(ROOT).as_posix()


def pinned(path,pin,expected_bytes=None):
    path=regular(path);raw=path.read_bytes()
    if digest(raw)!=pin or(expected_bytes is not None and len(raw)!=expected_bytes):raise ValueError('Current recorded bytes differ: '+relative(path))
    return raw


def public_proof(name,pin):
    path=regular(name)
    if not relative(path).startswith('verification/'):raise ValueError('Cloud-verifiable public proof required: '+str(name))
    key=(str(path),pin)
    if key not in PROOF_CACHE:PROOF_CACHE[key]=pinned(path,pin)
    return PROOF_CACHE[key]


def archive_member(archive,files,name):
    posix=PurePosixPath(name)
    if not isinstance(name,str)or posix.is_absolute()or'..'in posix.parts or'\\'in name or':'in name or posix.as_posix()!=name:raise ValueError('Unsafe archive member')
    if name not in files:raise ValueError('Archive member is not manifest bound: '+name)
    pin=files[name];return pinned(regular(archive/name,archive),pin['sha256'],pin['bytes'])


def actual_png_name(name):
    parts=PurePosixPath(name).parts
    return len(parts)==3 and parts[1]=='actual'and parts[-1].lower().endswith('.png')


def terminal_archive(archive,manifest_hash,attempt):
    expected=ROOT/'verification/full-440'/('execution-attempt'+str(attempt))
    if archive.resolve()!=expected.resolve():raise ValueError('Only the explicitly named public full440 execution archive may be inventoried')
    manifest_path=regular(archive/'archive-manifest.json',archive);manifest=json.loads(pinned(manifest_path,manifest_hash));files=manifest['files']
    if(manifest.get('section')!=440 or manifest.get('actual_validation_attempt')!=attempt
       or manifest.get('kind')!='EXACT_FULL440_ORIGINAL_EXECUTION_ARCHIVE'
       or manifest.get('all_executed_retained_Popen_and_assigned_jobs_terminal')is not True
       or manifest.get('all_original_ordered_components_retained')is not True
       or type(manifest.get('actual_root_controller_exit'))is not int):raise ValueError('Actual terminal original archive is not established')
    process=json.loads(archive_member(archive,files,'root-launch/controller-process.json'))
    actual_exit=process.get('actual_observed_exit')
    if(process.get('status')!='completed'or type(actual_exit)is not int
       or process.get('owned_popen_retained')is not True
       or process.get('exit_observed_directly_from_retained_popen')is not True
       or process.get('exit_inferred_from_output_json')is not False
       or actual_exit!=manifest['actual_root_controller_exit']):raise ValueError('Retained original root Popen terminal provenance required')
    exit_raw=archive_member(archive,files,'root-launch/process.exit')
    if int(exit_raw.decode('ascii').strip())!=actual_exit:raise ValueError('Actual root process.exit differs')
    freeze_raw=archive_member(archive,files,'source-freeze.json')
    if digest(freeze_raw)!=manifest['source_freeze_sha256']:raise ValueError('Archived source freeze differs')
    ledger=json.loads(archive_member(archive,files,'orchestration.json'))
    if ledger.get('status')!='all_required_components_terminal'or ledger.get('root_freeze_sha256')!=manifest['source_freeze_sha256']:raise ValueError('Original component ledger is not terminal or bound to this freeze')
    if[row.get('name')for row in ledger.get('steps',[])]!=ledger.get('required_components'):raise ValueError('Original required component ordering differs')
    for step in ledger['steps']:
        status=step.get('status','')
        if status=='terminal':
            if step.get('terminal_supervisor_and_job_verified')is not True:raise ValueError('Component terminal job proof missing: '+step['name'])
        elif not(status.startswith('not_run_')and step.get('name')=='legacy_typed'and ledger.get('automated_available_scope_passed')is False):raise ValueError('Unfinished or uncertain component: '+str(step.get('name')))
    return manifest,files,process,ledger


def source_identity_refs(archive,files,actual_names,namespace):
    refs={name:[]for name in actual_names};used=[];ignored=[];problems=[]
    ns=PureWindowsPath(namespace)if isinstance(namespace,str)else None
    def resolve(raw,member):
        raw=raw.replace('\\','/');win=PureWindowsPath(raw)
        if win.is_absolute():
            try:name=win.relative_to(ns).as_posix()if ns is not None else None
            except ValueError:
                try:name=Path(raw).relative_to(archive).as_posix()
                except ValueError:return None
        else:
            path=PurePosixPath(raw)
            if path.is_absolute()or'..'in path.parts:return None
            name=(PurePosixPath(member).parent/path).as_posix()if len(path.parts)==1 else path.as_posix()
            prefix=relative(archive)+'/'
            if name.startswith(prefix):name=name[len(prefix):]
        return name if name in refs else None
    def walk(value,pointer,member):
        if isinstance(value,dict):
            for key in('path','file','screenshot','png'):
                raw=value.get(key)
                if not isinstance(raw,str)or not raw.lower().endswith('.png'):continue
                name=resolve(raw,member)
                if name is None:continue
                pin=value.get('screenshot_sha256')if key=='screenshot'else value.get('sha256',value.get('png_sha256'))
                if pin is None:pin=value.get('screenshot_sha256')
                if pin!=files[name]['sha256']:
                    problems.append({'receipt':member,'json_pointer':pointer,'field':key,'png':name,'reason':'Screenshot metadata SHA is missing or differs from actual archive member','declared_sha256':pin});continue
                identities={k:value[k]for k in('name','stage','stage_id','event_id','key','hwnd','process_id','pid','native','native_window','width','height','requested_window_size','actual_widget_size','technical_view')if k in value}
                refs[name].append({'receipt':relative(archive/member),'receipt_sha256':files[member]['sha256'],'json_pointer':pointer,'original_recorded_png':raw,'recorded_png_sha256':pin,'identity_fields':identities})
            for key,item in value.items():walk(item,pointer+'/'+str(key).replace('~','~0').replace('/','~1'),member)
        elif isinstance(value,list):
            for index,item in enumerate(value):walk(item,pointer+'/'+str(index),member)
    for name in sorted(files):
        path=PurePosixPath(name)
        if len(path.parts)!=3 or path.parts[1]!='actual'or path.suffix!='.json':continue
        if path.name.endswith('-source-closure.json')or path.name in('source100-guard-input.json','native275-constructor-ledger.json','native275-launcher-closure.json'):
            ignored.append({'file':name,'reason':'Source/constructor binding ledger, not screenshot-identity receipt; every actual PNG is still inventoried'});continue
        raw=archive_member(archive,files,name)
        try:document=json.loads(raw)
        except(ValueError,UnicodeError)as error:problems.append({'receipt':name,'reason':'Public JSON could not be read: '+str(error)});continue
        used.append({'file':name,'sha256':files[name]['sha256'],'bytes':len(raw)});walk(document,'',name)
    return refs,used,ignored,problems


def previous_review(entry,current_raw,registry_name,registry_sha):
    if entry.get('sha256')!=digest(current_raw)or entry.get('bytes')!=len(current_raw):raise ValueError('Registry entry differs from actual PNG')
    origin=entry['preferred_origin'];origins=entry['review_origins'];index=origins.index(origin)
    actor=origin['actor'];kind=origin['review_method']
    if kind not in('root_direct_visual_review','subagent_direct_visual_review','inherited_contact_sheet_visual_review')or not isinstance(actor,str)or not actor:raise ValueError('Unknown actual review method/actor')
    public_proof(origin['leaf_proof'],origin['leaf_proof_sha256'])
    original=regular(origin['original_png'])
    if not relative(original).startswith('verification/')or pinned(original,entry['sha256'],entry['bytes'])!=current_raw:raise ValueError('Prior original PNG full bytes are not identical')
    contact=None
    if kind=='inherited_contact_sheet_visual_review':
        contact=origin['contact_sheet'];mapping=json.loads(public_proof(contact['proof'],contact['proof_sha256']))
        if mapping.get('root_viewed')is not True:raise ValueError('Inherited contact sheet is not marked actually viewed')
        public_proof(contact['sheet'],contact['sheet_sha256'])
        if not any(m.get('sha256')==entry['sha256']and relative(regular(m['file']))==relative(original)for m in mapping.get('members',[])):raise ValueError('Contact sheet does not map the exact prior source PNG')
    value={'reviewed':True,'method':'contact_sheet'if contact else'previous_exact_bytes','reviewed_file':relative(original),'review_receipt':origin['leaf_proof'],'review_receipt_sha256':origin['leaf_proof_sha256'],'review_actor':actor,
           'registry_proof':{'file':registry_name,'sha256':registry_sha,'entry_sha256':entry['sha256'],'origin_index':index},'inherited_review_method':kind,'status':'prior_exact_png_appearance_reused','whole_current_and_prior_PNG_bytes_compared_equal':True,'current_original_direct_view_claimed':False}
    if contact:value['contact_sheet_proof']={k:contact[k]for k in('proof','proof_sha256','sheet','sheet_sha256','member')};value['limited_review_scope']='Actual inherited contact-sheet scale only; neither new original-PNG direct viewing nor fine text/pixel validation'
    return value


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,required=True);p.add_argument('--attempt',type=int,default=1);p.add_argument('--archive-manifest-sha256',required=True)
    p.add_argument('--registry',type=Path,required=True);p.add_argument('--registry-sha256',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--fresh-sha256',action='append',default=[],help='Require real new original viewing even if prior exact pixels exist')
    p.add_argument('--actor',required=True,help='Actual invoking root/agent; this inventory performs no visual viewing')
    args=p.parse_args();archive=args.archive if args.archive.is_absolute()else ROOT/args.archive
    output=args.output if args.output.is_absolute()else ROOT/args.output
    if not output.resolve().is_relative_to((ROOT/'.cache').resolve())or output.exists():raise ValueError('A new cache-only output file is required; never overwrite evidence')
    registry_path=regular(args.registry)
    if not relative(registry_path).startswith('verification/'):raise ValueError('First archive the byte-identical public prior registry, then supply its existing public path')
    registry_raw=pinned(registry_path,args.registry_sha256);registry=json.loads(registry_raw)
    if registry.get('schema')not in('full365_prior_actual_visual_png_registry_v1','full380_prior_actual_visual_png_registry_v1','full440_prior_actual_visual_png_registry_v1')or'public_derivation'not in registry:raise ValueError('Actual public-path derived prior visual registry required')
    manifest,files,process,ledger=terminal_archive(archive,args.archive_manifest_sha256,args.attempt)
    actual_names={name for name in files if actual_png_name(name)}
    physical=set()
    for path in archive.rglob('*.png'):
        regular(path,archive);physical.add(path.relative_to(archive).as_posix())
    manifest_pngs={name for name in files if name.lower().endswith('.png')}
    if physical!=manifest_pngs:raise ValueError('Actual archive PNG set differs from terminal archive manifest')
    if not actual_names:raise ValueError('No actual isolated screenshot PNGs in this archive')
    refs,used,ignored,identity_issues=source_identity_refs(archive,files,actual_names,manifest.get('raw_namespace_preserved_in_original_bytes'))
    images=[];new={};reuse_failures=[]
    for name in sorted(actual_names):
        raw=archive_member(archive,files,name)
        if not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('PNG signature differs: '+name)
        pin=files[name]['sha256'];row={'file':relative(archive/name),'sha256':pin,'reviewed':False,'method':'direct_view','reviewed_file':None,'review_receipt':None,'review_receipt_sha256':None,'review_actor':None,'registry_proof':None,
            'status':'needs_actual_view','component':PurePosixPath(name).parts[0],'archive_member':name,'bytes':len(raw),'size':list(struct.unpack('>II',raw[16:24])),'identity_refs':refs[name],'identity_reference_available':bool(refs[name]),'actual_new_view_image_called':False}
        entry=registry['entries'].get(pin)
        if entry is not None and pin not in args.fresh_sha256:
            try:row.update(previous_review(entry,raw,relative(registry_path),args.registry_sha256))
            except(ValueError,OSError,KeyError,TypeError)as error:reuse_failures.append({'file':row['file'],'sha256':pin,'reason':str(error),'left_unreviewed':True})
        if row['reviewed']is not True:
            request=new.setdefault(pin,{'sha256':pin,'representative_file':row['file'],'bytes':len(raw),'size':row['size'],'all_same_sha_files':[],'required_action':'Actually call view_image and inspect this representative; only afterward may its byte-identical aliases be sealed as same_byte_reuse','reason':'explicit_fresh_view_required'if pin in args.fresh_sha256 else'no_currently_verifiable_prior_exact_review'})
            request['all_same_sha_files'].append(row['file'])
        images.append(row)
    if not args.actor.startswith('/root'):raise ValueError('Explicit actual root/agent actor required')
    report={'schema':SCHEMA,'section':440,'actual_validation_attempt':args.attempt,'inventory_actor':args.actor,'created_at_utc':datetime.now(timezone.utc).isoformat(),
      'archive':relative(archive),'archive_manifest':relative(archive/'archive-manifest.json'),'archive_manifest_sha256':args.archive_manifest_sha256,'source_freeze_sha256':manifest['source_freeze_sha256'],
      'actual_root_controller_exit':process['actual_observed_exit'],'original_execution_terminal_only_not_PASS':True,'public_registry_ref':{'file':relative(registry_path),'sha256':args.registry_sha256},
      'images':images,'image_count':len(images),'reviewed_prior_exact_rows':sum(r['reviewed']is True for r in images),'method_counts':dict(Counter(r['method']for r in images if r['reviewed']is True)),
      'pending_actual_view_rows':sum(r['reviewed']is False for r in images),'needs_actual_view':list(new.values()),'needs_actual_view_unique_sha256':len(new),'all_reviewed':all(r['reviewed']is True for r in images),
      'new_view_image_calls_performed_by_inventory':0,'unreviewed_direct_view_method_is_requested_action_not_observation':True,'public_identity_receipts_read':used,'binding_ledgers_not_used_for_image_identity':ignored,'identity_reference_issues':identity_issues,
      'prior_reuse_not_authorized':reuse_failures,'manifest_pngs_outside_actual_not_treated_as_screenshots':sorted(manifest_pngs-actual_names),
      'final_available_checks_passed_not_claimed':True,'complete_repository_validation':False,'source_HEAD_or_source_freeze_modified':False,'tests_or_windows_started':False,'private_state_read_copied_or_restored':False,
      'limits':['Every actual screenshot path keeps its own archive identity even when bytes duplicate. Duplicate pending images stay unreviewed until a genuine new review exists.','Prior original reviewer and historical method are preserved. A contact-sheet origin is never called a new original-PNG direct view.','Pixel appearance reuse does not establish this execution semantic PASS, hidden text, current game state, server mechanism or complete project correctness.','Identity metadata is recorded by source JSON pointer and SHA; missing identity metadata is explicit and never filled with a guessed window PID.']}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb')as stream:stream.write((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'inventory':relative(output),'sha256':digest(output.read_bytes()),'actual_PNG_paths':len(images),'prior_reviewed_paths':report['reviewed_prior_exact_rows'],'pending_paths':report['pending_actual_view_rows'],'new_unique_PNGs_to_actually_view':len(new),'complete_validation_PASS_claimed':False},ensure_ascii=False))
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except(Exception)as error:print(json.dumps({'inventory_not_created_or_not_authoritative':True,'error':type(error).__name__,'message':str(error)},ensure_ascii=False),file=sys.stderr);raise SystemExit(2)
