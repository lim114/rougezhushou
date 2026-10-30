from pathlib import Path
import json,sys
R=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());queue=json.loads((R/'.cache/440-attempt4-preterminal-image-queue.json').read_bytes());folder=R/'verification/full-440/preterminal-root-direct-review-attempt4';seen={row['file']for path in folder.glob('*.json')for row in json.loads(path.read_bytes())['images']}
rows=[row for row in queue['copied_sha256'].values()if row['file']not in seen]
print(json.dumps({'remaining_unique':len(rows),'next':[{'file':row['file'],'sha256':row['sha256']}for row in rows[:int(sys.argv[1])if len(sys.argv)>1 else 4]]},ensure_ascii=False))
