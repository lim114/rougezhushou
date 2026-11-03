"""Select four complete original choices after checking the full public table."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHA256 = 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
CHOICES = ('choice_ro6_hire1_1','choice_ro6_hire1_4','choice_ro6_hire1_5','choice_ro6_hire1_6')


def main():
    raw = (ROOT/'.cache/p3-287-event-research/fixed-game-topic.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('Complete original public source hash differs.')
    topic = json.loads(raw)['details']['rogue_6']
    selected = {'schema_version':1,
        'source':{'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/roguelike_topic_table.json',
                  'sha256':SHA256,'bytes':len(raw),'commit':COMMIT},
        'field_root':'$.details.rogue_6',
        'choices':{key:topic['choices'][key] for key in CHOICES},
        'choiceScenes':{'scene_ro6_hire1_enter':topic['choiceScenes']['scene_ro6_hire1_enter']},
        'scope':'Exact selected full objects. Shared nextSceneId is not a source-scene edge or proof of actual recruitment.'}
    output = (json.dumps(selected,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with Path(__file__).with_name('original-records.json').open('xb') as stream:
        stream.write(output)
    print(json.dumps({'full_source_sha256':SHA256,'full_source_bytes':len(raw),
                      'selected_choices':len(CHOICES),'selected_sha256':hashlib.sha256(output).hexdigest(),
                      'selected_bytes':len(output)}))


if __name__ == '__main__':
    main()
