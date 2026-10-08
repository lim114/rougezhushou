import collections
import gzip
import json
from pathlib import Path
from review76_common import canonical, check_pair

own = Path(__file__).parent
data = [json.loads(gzip.decompress((own / ('final-focused-' + side + '76.json.gz')).read_bytes()))
        for side in ('baseline', 'draft')]
initial = json.loads((own / 'author-initial-public-cases.json').read_text())
counts = collections.Counter()
details = []
for index, (old, new) in enumerate(zip(*data)):
    assert old['label'] == new['label']
    if index < len(initial):
        previous = {key: value for key, value in initial[index].items() if key != 'scenario'}
        assert canonical(previous) == canonical(old['outcome'])
    category = check_pair(old, new)
    counts[category] += 1
    if category == 'locked_positive_corrected':
        assert canonical(old['zero_control_formatted_reports']) == canonical(new['zero_control_formatted_reports'])
        assert canonical(new['normalized_formatted_reports']) == canonical(old['zero_control_formatted_reports'])
    elif 'result' in old['outcome']:
        assert canonical(old['formatted_reports']) == canonical(new['formatted_reports'])
    if new['label'].startswith('e2-') and 'result' in new['outcome']:
        result = new['outcome']['result']
        flower = next(x for x in result['components'] if x['name'] == '扶摇花火')
        assert flower['hits'] == 1.0 and type(flower['hits']) is float
        assert flower['actual_total'] is None and result['total_healing'] is None
        assert result['external_event_reference']['actual_event_times_seconds'] is None
    details.append({'index': index, 'label': old['label'], 'category': category})
receipts = [json.loads((own / ('final-focused-' + side + '76-receipt.json')).read_text())
            for side in ('baseline', 'draft')]
receipt = {'status': 'PASS', 'paired_fresh_cases': len(details),
           'actual_public_calls_both_sides': sum(x['actual_public_calls'] for x in receipts),
           'counts': dict(counts), 'replayed_initial_whole_outcomes': len(initial),
           'all_whole_JSON_errors_and_reports_checked': True,
           'only_locked_declared_count_and_exact_exclusion_note_normalized_for_zero_comparison': True,
           'details': details}
(own / 'final-focused-comparison76.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in receipt.items() if key != 'details'}))
