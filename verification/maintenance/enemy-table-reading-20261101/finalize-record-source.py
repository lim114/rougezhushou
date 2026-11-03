from pathlib import Path
from hashlib import sha256
import json,difflib,runpy
R=Path.cwd();B=R/'verification/maintenance/enemy-table-reading-20261101'
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(p):
 raw=p.read_bytes();return {'receipt':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
p=B/'summary.json';v=json.loads(p.read_bytes());v['unresolved_observations'].append('Updated actual test app had two visible responding owned windows at startup; later battle finished signal observed, toolbar still Win32-visible/not-cloaked/responding. Windows-mcp crop shows background, so direct desktop visible-pixel verification remains unavailable, not passed. No actor/cause inferred.');v['actual_desktop_pixels_verified']=False;v['desktop_review']=pin(B/'live-final/desktop-review.json');write(p,v)
p=R/'PROJECT_PROGRESS.md';raw=p.read_bytes().decode('utf8');old='窗口绑定的真实游戏/多屏复核';assert old in raw;new=raw.replace(old,'本机工具条的桌面像素核对（Win32可见/响应而MCP截图返回背景，原因未定）；窗口绑定的真实游戏/多屏复核',1);p.write_bytes(new.encode('utf8'))
p=R/'DEVELOPMENT_CHECKPOINT.json';lines=p.read_bytes().decode('utf8').splitlines(keepends=True);v=json.loads(p.read_bytes());v['current_batch']['scope']+=' Actual test toolbar Win32-visible/responding but MCP crop returns background; physical desktop-pixel proof remains unavailable, not passed.';new=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').splitlines(keepends=True)
for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in lines],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():new[y:y+k]=lines[x:x+k]
p.write_bytes(''.join(new).encode('utf8'));idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,v)['current_section']==447
p=B/'final-audit.json';v=json.loads(p.read_bytes());v['maintenance_receipt']=pin(B/'summary.json');v['index']=pin(R/'CLOUD_INDEX.json');v['actual_desktop_pixels_verified']=False;write(p,v)
(B/'live-final/toolbar-exposure-source.py').write_bytes((R/'.cache/expose_owned_test_toolbar.py').read_bytes());(B/'finalize-record-source.py').write_bytes(Path(__file__).read_bytes())
for a,b in [('publish_battle_overview.py','publish_enemy_table.py'),('record_battle_overview_publication.py','record_enemy_table_publication.py'),('publish_battle_overview_metadata.py','publish_enemy_table_metadata.py')]:
 s=(R/'.cache'/a).read_text('utf8').replace('battle-overview-sections-20261101','enemy-table-reading-20261101').replace('battle-overview','enemy-table').replace('f43b87e6f995358c499c65498d5ee315bd88e92c','c1d790288fc1e65000630015109717336ca0ead5').replace("audit['current_distinct_tests']==86 and audit['native_unique_checks']==99","audit['current_distinct_tests']==52 and audit['native_unique_checks']==137").replace('复用公开折叠源码完善作战地图与敌人首页','移植Qt原版排版并完整显示敌人机制表').replace('核对作战首页维护发布并同步云端索引','核对敌人机制表发布并同步云端索引');(R/'.cache'/b).write_text(s,'utf8')
archive={p.relative_to(R).as_posix():pin(p)for root in(B,R/'research/enemy-table-reading-20261101')for p in root.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};write(B/'archive-manifest.json',{'kind':'explicit_public_archive_no_private_cache_or_video','files':archive});print(json.dumps({'prepared':True,'archive_files':len(archive),'actual_desktop_pixels_not_claimed':True}))
