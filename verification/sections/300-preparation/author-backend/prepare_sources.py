"""Copy exact public authority originals into the isolated section300 candidate."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CANDIDATE=HERE/'candidate'
PACK=CANDIDATE/'research/p3-future-region-effects-300'
SOURCES={
 'game-topic-complete.json':('.cache/p3-287-event-research/fixed-game-topic.json','f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'),
 'prts-main-433770.html':('research/p3-stage-context/community-main.html','366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'),
 'prts-events-427904.html':('research/p3-choice-recruitment-290/prts-events-427904.html','faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9'),
 'prts-events-440271.html':('research/p3-choice-recruitment-290/prts-events-440271.html','e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8'),
 'bwiki-events-349818.html':('.cache/p3-287-event-research/bwiki-investigation.html','26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908'),
 'weather-ordinary-tool-response.json':('.cache/p3-299-event-gap-research/actual-weather-and-event-web.json','ce8b30ff6d394e7e5fcdf6eb75600eb71b93c60d7c5431ca9b389ed5ddaa42f1'),
 'weather-footer-tool-response.json':('.cache/p3-299-event-gap-research/actual-weather-footer-web.json','198489e0cd04494f16ddcd558331935959cc921c224a9a2b4052e2f4586400cb')}
report={}
for name,(relative,pin) in SOURCES.items():
 raw=(ROOT/relative).read_bytes()
 assert sha256(raw).hexdigest()==pin,relative
 (PACK/name).write_bytes(raw)
 report[name]={'original':relative,'sha256':pin,'bytes':len(raw)}
raw=(ROOT/'rouge/data/node-catalog.json').read_bytes()
assert sha256(raw).hexdigest()=='7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'
(CANDIDATE/'rouge/data/node-catalog.json').write_bytes(raw)
print(json.dumps({'public_source_copies':report,'existing_dependency_not_for_promotion':'rouge/data/node-catalog.json'},ensure_ascii=False,indent=2))
