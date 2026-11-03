"""Static original/catalog duration correspondence, no helpers or public calls."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-haruka-repeat-text-input-084')
catalog = json.loads((AUTHOR / 'frozen/rouge/data/catalog.json').read_bytes())
assert isinstance(catalog['operators'], dict)
owner = catalog['operators']['char_4202_haruka']
source = json.loads((AUTHOR / 'source-receipt84.json').read_bytes())
bindings = []
for rank, (raw, current) in enumerate(zip(source['complete_raw_s2_skill']['levels'], owner['skills'][1]['levels'], strict=True), 1):
    assert raw['duration'] == current['duration']
    bindings.append({'rank': rank, 'raw_duration': raw['duration'], 'catalog_duration': current['duration']})
assert len(bindings) == 10
receipt = {'status': 'PASS', 'bindings': bindings, 'source_helper_calls': 0, 'calculate_calls': 0}
(OUT / 'independent-source-duration084.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
