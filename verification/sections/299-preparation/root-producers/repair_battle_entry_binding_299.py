from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[1];PREP=ROOT/'verification/sections/299-preparation'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
old_manifest='research/p3-battle-event-references-296/source-manifest.json'
assert digest(ROOT/old_manifest)=='c6a7d1294e48b6fec896f736d56baa0c09f25f3365de471cc11c88d74705de21'
old=json.loads((ROOT/old_manifest).read_bytes());new=json.loads((ROOT/old_manifest).read_bytes())
before={}
for name in ('rouge/event_planning.py','rouge/node_catalog.py'):
 p=ROOT/name;historical=ROOT/'verification/sections/298-preparation/before'/name
 assert digest(historical)==old['files'][name]['sha256']
 before[name]={'old':old['files'][name],'current':{'sha256':digest(p),'bytes':p.stat().st_size},
  'historical_original':'verification/sections/298-preparation/before/'+name}
 new['files'][name]=before[name]['current']
new['section']=299
new['compatibility_rebinding']={'original_manifest':old_manifest,'original_sha256':digest(ROOT/old_manifest),
 'changed_source_bindings':before,'mechanics_or_data_changed':False,
 'reason':'Section298 added independently source-bound natural-floor checks. Default unknown-context forward event links and all original records remain unchanged; retain strict exact-byte guards and revalidate all14 event-to-stage links against current source.'}
package=ROOT/'research/p3-battle-entry-compatibility-299';package.mkdir(exist_ok=False)
manifest=package/'source-manifest.json';manifest.write_bytes(encode(new))
name='rouge/battle_event_references.py';p=ROOT/name;raw=p.read_bytes();saved=PREP/'before'/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(raw)
raw_new=raw.replace(old_manifest.encode(),b'research/p3-battle-entry-compatibility-299/source-manifest.json')
raw_new=raw_new.replace(digest(ROOT/old_manifest).encode(),digest(manifest).encode())
assert raw_new!=raw
def normalized(raw):
 t=ast.parse(raw);t.body=[n for n in t.body if not(isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id in ('MANIFEST','MANIFEST_SHA256')for x in n.targets))]
 return ast.dump(t,include_attributes=False)
assert normalized(raw)==normalized(raw_new)
p.write_bytes(raw_new)
record={'section':299,'kind':'source_compatibility_repair_in_functional_section','first_necessary_receipt':'verification/sections/299-necessary-first/process.json',
 'actual_first_methods':135,'actual_first_failures':1,'actual_first_errors':5,
 'cause':'The unchanged296 reverse-link reader still required exact pre298 parser/planning source bytes. Current298 source no longer matched those two pins, so old entry references safely returned unknown. No game record or event link was missing.',
 'old_manifest':old_manifest,'old_manifest_sha256':digest(ROOT/old_manifest),
 'new_manifest':manifest.relative_to(ROOT).as_posix(),'new_manifest_sha256':digest(manifest),
 'old_controller':'verification/sections/299-preparation/before/'+name,'old_controller_sha256':digest(saved),
 'new_controller':name,'new_controller_sha256':digest(p),
 'only_controller_MANIFEST_and_MANIFEST_SHA_assignments_changed':True,'data_or_game_mechanics_changed':False,
 'original296_data_catalog_and_forward_reference_bytes_unchanged':True,'all_existing_tests_preserved':True,
 'changed_source_bindings':before,'requires_actual_revalidation':True}
(PREP/'entry-binding-repair.json').write_bytes(encode(record))
(package/'README.md').write_bytes(('''# 固定战斗入口的当前代码绑定

本目录仅重新绑定当前解析和条件查询代码的精确字节。296节的完整事件、原选项、14条关卡联系、11条可阅读入口及3条明确普通版本排除保持原资料，不修改游戏机制或推定实际入口。

原296来源清单及两份前298代码原件继续保留。当前两份代码在298增加自然主层条件；默认未知上下文的资源/作战查询已经逐项保持。本次继续运行原296完整来源/损坏/身份与UI验收，并检查190场景默认资源，不能仅更新哈希声称兼容。

修复缘由、原失败及前后身份见 `verification/sections/299-preparation/entry-binding-repair.json`。来源失效仍返回未知，旧令牌必须因来源身份变化而被拒绝；不关闭任何来源保护。
''').encode())
print(json.dumps({'controller_AST_unchanged_except_two_binding_constants':True,'new_manifest_sha256':digest(manifest),'controller_sha256':digest(p),'no_existing_test_changed':True}))
