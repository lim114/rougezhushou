"""Extract only named records from the already downloaded pinned public table."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
FULL_SHA256 = 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'


def main():
    source = ROOT / '.cache/p3-287-event-research/fixed-game-topic.json'
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FULL_SHA256:
        raise ValueError('Pinned complete public table bytes differ.')
    topic = json.loads(raw)['details']['rogue_6']
    result = {'schema_version':1,
        'source':{'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/roguelike_topic_table.json',
                  'sha256':FULL_SHA256,'bytes':len(raw),'commit':COMMIT},
        'field_root':'$.details.rogue_6',
        'choiceScenes':{'scene_ro6_normal1_enter':topic['choiceScenes']['scene_ro6_normal1_enter']},
        'choices':{key:topic['choices'][key] for key in ('choice_ro6_normal1_1','choice_ro6_normal1_2')},
        'items':{'rogue_6_scrap_G_12':topic['items']['rogue_6_scrap_G_12']},
        'scope':'Exact selected original objects after complete-file SHA verification; no source-scene choice edge or current execution inferred.'}
    output = Path(__file__).with_name('original-records.json')
    data = (json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with output.open('xb') as stream:
        stream.write(data)
    print(json.dumps({'full_source_bytes':len(raw),'full_source_sha256':FULL_SHA256,
                      'selected_bytes':len(data),'selected_sha256':hashlib.sha256(data).hexdigest()}))


if __name__ == '__main__':
    main()
