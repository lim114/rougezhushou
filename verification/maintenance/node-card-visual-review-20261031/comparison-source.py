from pathlib import Path
from types import ModuleType
from copy import deepcopy
from hashlib import sha256
import sys,json,subprocess
R=Path.cwd();sys.path.insert(0,str(R));base=R/'verification/maintenance/node-card-visual-review-20261031'
from PySide6.QtWidgets import QApplication
from rouge.player_map_hover import NodeHoverCard
from rouge.player_map import PreviewMapView
qt=QApplication([]);baseline='0d14332be97c18a2cee38f5095d35f1959c141d2';path='rouge/player_map_hover.py';raw=subprocess.check_output(['git','show',baseline+':'+path])
old=ModuleType('rouge._before_visual');old.__package__='rouge';exec(compile(raw,str(R/path),'exec'),old.__dict__)
cases=[]
for observed in('未知的诡秘','不期而遇','作战','林间空地','曲折密道'):
 for history in('none','event','battle'):
  node={'id':'n','row':1,'col':1,'distance':2,'observed_type':observed,'prediction':{'candidates':['诡意行商','不期而遇']}}
  if history=='event':node['remembered_content']={'kind':'event','title':'桑尼的邀请'}
  if history=='battle':node['remembered_content']={'kind':'battle','title':'遗忘时间','variant_id':'ro6_n_1_2'}
  graph={'zone_id':'zone_1','template_id':'isolated','grid':{'rows':3},'nodes':[node]};before=deepcopy(graph);values=[]
  view=PreviewMapView();view.historical=False
  for cls in(old.NodeHoverCard,NodeHoverCard):
   card=cls(view);assert card.install(('run','zone_1','isolated','n'),graph,'n',{},view)
   entries=[{'kind':k,'id':i,'title':b.text().removesuffix('\n暂无对应插图'),'scope':b.property('referenceScope'),'icon_present':not b.icon().isNull()}for k,i,b in card.entry_buttons]
   values.append({'types':card.type_values,'notice':card.notice.text(),'entries':entries})
   card.close();card.deleteLater()
  assert values[0]==values[1],(observed,history)
  assert graph==before
  cases.append({'type':observed,'history':history,'full_entry_identity_order_names_and_source_text_equal':True,'entries':len(values[0]['entries']),'result_sha256':sha256(json.dumps(values[0],ensure_ascii=False,sort_keys=True).encode()).hexdigest()})
  view.close();view.deleteLater();qt.processEvents()
for p in('rouge/node_catalog.py','rouge/player_map_reference.py','rouge/public_node_statistics.py','rouge/node_statistics_source.py','rouge/run_state.py','PROJECT_REQUIREMENTS.md'):
 assert (R/p).read_bytes()==subprocess.check_output(['git','show',baseline+':'+p]),p
result={'passed':True,'baseline_commit':baseline,'old_hover_source_sha256':sha256(raw).hexdigest(),'current_hover_source_sha256':sha256((R/path).read_bytes()).hexdigest(),'cases':cases,'unchanged_models_and_requirements_verified':True,'normalization':'Old missing-art two-line button text suffix removed only for comparison; the new tile visibly renders missing-art message separately. IDs, full titles, source text, icons and ordering match.','game_inputs':False,'chat_sent':False,'whole_program_complete':False}
(base/'before-after.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');(base/'comparison-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'passed':True,'cases':len(cases)}))
