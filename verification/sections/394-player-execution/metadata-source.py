from pathlib import Path
import runpy,json,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
f=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));read=f['read'];write=f['write'];pin=f['pin'];git=f['git']
proof=read('verification/sections/394-publication.json');cp=read('DEVELOPMENT_CHECKPOINT.json');assert proof['passed']and git('rev-parse','HEAD').decode().strip()==proof['commit']
cp['last_verified_cloud_save']={'section':394,'scope':'current_functional_section','binding':'verified_remote_commit','commit':proof['commit'],'proof':'verification/sections/394-publication.json','proof_sha256':pin('verification/sections/394-publication.json')['sha256']}
cp['batch_status']='PLAYER_SECTION394_PUBLISHED';cp['current_batch'].update(status=cp['batch_status'],batch_closed=False)
cp['cloud_publication_closeout']={'section':394,'functional_commit':proof['commit'],'proof':'verification/sections/394-publication.json','current_commit_kind':'publication metadata only','next_section_started':False,'development_paused':False}
write('DEVELOPMENT_CHECKPOINT.json',cp)
for name in('AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md'):
 p=R/name;t=p.read_text('utf8');pending='<!-- player-publication-pending -->普通推送与远端核对待完成。';assert t.count(pending)==1
 p.write_text(t.replace(pending,f'本节功能提交{proof["commit"]}已普通推送并核对真实远端及{len(proof["verified_commit_tree_and_local_public_bytes"])}份相关公开文件。第394节尚未启动，未指定新的数字终点。'),encoding='utf8',newline='\n')
runpy.run_path(str(R/'scripts/update_cloud_index.py'))['update'](R)
valid=runpy.run_path(str(R/'scripts/update_cloud_index.py'))['validate_delivery'](R,read('DEVELOPMENT_CHECKPOINT.json'));write('verification/sections/394-index-publication-validation.json',{'passed':True,'validation':valid,'scope':'Current actual published functional commit proof, requirements digest and live index.'})
p=R/'verification/sections/394-player-execution/metadata-source.py';p.write_bytes(Path(__file__).read_bytes())
names=['AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md','DEVELOPMENT_CHECKPOINT.json','CLOUD_INDEX.json','CLOUD_HANDOFF.md','verification/sections/394-publication.json','verification/sections/394-publication-execution','verification/sections/394-index-publication-validation.json','verification/sections/394-player-execution/metadata-source.py']
subprocess.run(['git','add','--',*names],check=True);subprocess.run(['git','-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check'],check=True)
subprocess.run(['git','-c','gc.auto=0','commit','--quiet','-m','同步第394节发布证明、要求和云端索引'],check=True)
f['publish'](394,'metadata')
