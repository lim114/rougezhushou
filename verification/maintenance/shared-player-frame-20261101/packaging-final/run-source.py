from pathlib import Path
import sys,subprocess,json,zipfile
from hashlib import sha256
R=Path.cwd();B=R/'verification/maintenance/shared-player-frame-20261101';out=B/'packaging-final';out.mkdir(exist_ok=False);target=R/'.cache/shared-frame-wheel-final';assert not target.exists()
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
 p=subprocess.Popen([sys.executable,'-B','-X','utf8','-m','pip','wheel','--no-deps','--no-build-isolation','--wheel-dir',str(target),'.'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
(out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code,'local_build_only':True,'not_install':True},indent=2)+'\n','utf8');assert code==0
wheel=next(target.glob('*.whl'));files={}
with zipfile.ZipFile(wheel)as z:
 for p in (R/'third_party/qframelesswindow').rglob('*'):
  if not p.is_file():continue
  name=p.relative_to(R).as_posix();raw=z.read(name);assert raw==p.read_bytes(),name;files[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
 name='rouge/player_window_frame.py';raw=z.read(name);assert raw==(R/name).read_bytes();files[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
 assert not any(n.startswith(('.local/','.cache/','local-settings'))for n in z.namelist())
value={'kind':'selected_local_wheel_scope','actual_observed_build_exit':code,'actual_retained_PID':p.pid if False else json.loads((out/'process.json').read_bytes())['actual_retained_PID'],'wheel':wheel.name,'wheel_bytes':wheel.stat().st_size,'wheel_sha256':sha256(wheel.read_bytes()).hexdigest(),'verified_selected_files':files,'selected_library_adapter_both_licenses_and_original_qrc_svg_bytes_match_current':True,'local_wheel_not_published':True,'no_install_or_dependency_upgrade':True,'whole_wheel_clean_machine_or_installer_acceptance':False,'scope':'Actual local build with selected core library/adapter and all source resources verified. Not an installer or a new-machine launch test.'};(out/'receipt.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'build_exit':code,'verified_selected_files':len(files)},flush=True)
