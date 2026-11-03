"""Exclude unbound deployment motions from conventional timing previews."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def build(source):
    data=json.loads(source.read_text(encoding='utf-8'))
    excluded=[]
    for profile in data['operators'].values():
        for record in profile['records']:
            if 'Deploy' in record['animation'] and record['selectable_as_conventional_reference']:
                record['selectable_as_conventional_reference']=False
                record['unverified_reasons'].append('deployment animation requires separate lifecycle binding')
                record.pop('preview',None);excluded.append(record['id'])
    records=[r for p in data['operators'].values() for r in p['records']]
    data['counts']['selectable_references']=sum(r['selectable_as_conventional_reference'] for r in records)
    data['counts']['unverified_or_transition_references']=sum(not r['selectable_as_conventional_reference'] for r in records)
    data['selection_derivation']={'source_file':str(source.relative_to(ROOT)),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'excluded_deployment_motions':excluded,'runtime_binding_inferred':False}
    return data


def main():
    source=ROOT/'.cache/research/timing-048/original-animation-references.json'
    output=ROOT/'rouge/data/original-animation-references.json'
    data=build(source);output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data['counts']))


if __name__=='__main__':main()
