"""Public stage selection for Tomimi; no run or account fields enter the URL."""
import base64
from functools import lru_cache
import json
from pathlib import Path
from urllib.parse import quote


@lru_cache(maxsize=1)
def stage_links():
    return json.loads((Path(__file__).parent/'data/tomimi-stage-links.json').read_bytes())['levels']


def target(reference):
    if reference is None:
        return None
    stage = reference['stage']
    level_id = stage['levelId'].rsplit('/', 1)[-1]
    row = stage_links().get(level_id)
    if row is None or row['name'] != stage['name']:
        return None
    index = row['variant_index']
    elite = bool(stage['isElite'])
    # Published v1 format: ro6, zero relics, public config index and mode only.
    payload = bytes([1, 5, 32+(16 if index else 0), 0]+([index] if index else [])+[int(elite)])
    state = base64.urlsafe_b64encode(payload).decode('ascii').rstrip('=')
    return {'stage_id': reference['id'], 'name': row['name'], 'level_id': level_id,
            'variant_index': index, 'elite': elite,
            'url': 'https://tomimi.dev/zh/stages/'+quote(row['slug'], safe='')+'?state='+state}
