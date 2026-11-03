import collections
import gzip
import hashlib
import json
from pathlib import Path
from review76_common import canonical, check_pair

own = Path(__file__).parent
author = Path('/workspace/.continuation/p2-haruka-bubble-qualification-076')
records = []
archives = []
for side in ('baseline', 'draft'):
    source = author / ('public-' + side + '.json.gz')
    packed = source.read_bytes()
    raw = gzip.decompress(packed)
    archive = own / ('final-saved-author-' + side + '.json.gz')
    assert not archive.exists()
    archive.write_bytes(packed)
    parsed = json.loads(raw)
    records.append(parsed)
    archives.append({'source_path': str(source), 'preserved_path': str(archive),
                     'gzip_sha256': hashlib.sha256(packed).hexdigest(),
                     'gzip_bytes': len(packed), 'decompressed_sha256': hashlib.sha256(raw).hexdigest(),
                     'decompressed_bytes': len(raw), 'case_records': len(parsed),
                     'decompression': 'Python gzip.decompress; JSON parsed completely'})
assert len(records[0]) == len(records[1])
counts = collections.Counter()
details = []
for index, (old, new) in enumerate(zip(*records)):
    assert old['label'] == new['label']
    category = check_pair(old, new)
    counts[category] += 1
    details.append({'index': index, 'label': old['label'], 'category': category,
                    'scenario_sha256': hashlib.sha256(canonical(old['scenario']).encode()).hexdigest()})
receipt = {'status': 'PASS', 'baseline_commit': '153b5dbf15d6567746047cbdea7f8d00a6879f3a',
           'paired_saved_case_records': len(details), 'counts': dict(counts),
           'saved_positive_zero_controls_per_side': counts['locked_positive_corrected'],
           'all_positive_control_full_outcomes_equal_between_sides': True,
           'new_calculate_damage_calls': 0,
           'comparison': 'Canonical JSON serialization preserves numeric int/float types; only 3 exact declared-count values and 3 exact new-note entries are normalized for locked-positive comparisons to original zero controls.',
           'archives': archives, 'details': details}
(own / 'final-saved-comparison76.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in receipt.items() if key not in ('details', 'archives')}, ensure_ascii=False))
