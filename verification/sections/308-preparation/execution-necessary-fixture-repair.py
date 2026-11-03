from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1];PREP=ROOT/'verification/sections/308-preparation'
for name in('tests/test_direct_landmark_308.py','tests/test_direct_landmark_303.py'):
 p=ROOT/name;before=PREP/'before-necessary-attempt1'/name;before.parent.mkdir(parents=True,exist_ok=True);before.write_bytes(p.read_bytes())
name='tests/test_direct_landmark_308.py';p=ROOT/name;s=p.read_text('utf8')
needle="        target = clone / 'rouge/data/fixed-landmark-references.json'"
assert s.count(needle)==1
s=s.replace(needle,"        # The historical source package pins its exact regular snapshot;\n        # this explicit runtime dependency also belongs in a valid clone.\n        shutil.copyfile(self.builder.DATA / 'battle-map-projections.json', clone / 'rouge/data/battle-map-projections.json')\n"+needle)
needle="[sys.executable, str(Path(historical_builder.__file__))]";assert s.count(needle)==1;s=s.replace(needle,"[sys.executable, '-B', '-X', 'utf8', str(Path(historical_builder.__file__))]")
p.write_text(s,encoding='utf8')
p=ROOT/'tests/test_direct_landmark_303.py';s=p.read_text('utf8');needle="command = [sys.executable, str(Path(self.builder.__file__)), '--public-data-dir'";assert s.count(needle)==1;s=s.replace(needle,"command = [sys.executable, '-B', '-X', 'utf8', str(Path(self.builder.__file__)), '--public-data-dir'");p.write_text(s,encoding='utf8')
p=ROOT/'.cache/run308_necessary.py';s=p.read_text('utf8').replace('308-necessary-attempt1','308-necessary-attempt2');s=s.replace("'rouge/data/fixed-landmark-references.json','scripts/extend_direct_landmark_308.py'","'rouge/data/fixed-landmark-references.json','rouge/data/battle-map-projections.json','scripts/extend_direct_landmark_308.py'")
(ROOT/'.cache/run308_necessary2.py').write_text(s,encoding='utf8')
record={'section':308,'actual_failed_receipt':'verification/sections/308-necessary-attempt1/process.json','actual_methods':99,'errors':2,'failures':0,'source_data_or_coordinates_changed':False,'repairs':[{'test':'test_05','cause':'Valid public clone omitted its runtime regular projection file','correction':'Copy the real public runtime regular file explicitly; all authority mutations/negative guards retained'},{'test':'test_16','cause':'Windows child CLI used default local encoding while parent utf8 tried to decode traceback containing Chinese project path; decoding reader failed, stderr None','correction':'Actually execute original CLI with explicit -B -X utf8; historical303 test14 receives same explicit flags; all process/assertion checks preserved'}],'before_test_originals':'verification/sections/308-preparation/before-necessary-attempt1/tests','source_guard_extension':'Necessary attempt2 additionally pins current runtime regular file, not just its original source snapshot'}
(PREP/'necessary-failure-repair.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(PREP/'execution-necessary-fixture-repair.py').write_bytes(Path(__file__).read_bytes())
