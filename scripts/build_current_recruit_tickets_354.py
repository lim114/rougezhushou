"""Rebuild the candidate directory from exact public sources; never query a run."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import argparse
import importlib.util
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-recruit-tickets-354'


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf8')


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            self.rows.append(''.join(self.current).strip())
            self.current = None


def build(source_root=ROOT, artifact_root=ROOT):
    source_root, artifact_root = Path(source_root), Path(artifact_root)
    sys.path.insert(0, str(source_root))
    # Candidate preparation can build against the existing public tree; after
    # promotion this loads exactly the same canonical source-row implementation.
    spec = importlib.util.spec_from_file_location('rouge._recruit_ticket_builder_354', ROOT/'rouge/current_recruit_tickets.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    from rouge import current_exit, current_rest_travel
    current = json.loads((source_root/'research/p3-expansion-313/current-topic.json').read_bytes())['details']
    full = (artifact_root/PACK/'topic-page.html').read_bytes()
    download = json.loads((artifact_root/PACK/'source-download.json').read_bytes())
    if download['http_status'] != 200 or download['sha256'] != sha256(full).hexdigest() or download['bytes'] != len(full):
        raise ValueError('Actual successful download must match exact full page bytes')
    html = full.decode('utf8')
    revisions = re.findall(r'"wgRevisionId":(\d+)', html)
    if revisions != ['442954']:
        raise ValueError('Selected current PRTS revision changed')
    title = html.index(' 招募券留存</div>')
    begin = html.rfind('<div class="AKCollapse-title"', 0, title)
    end = html.index('</div>', title+len(' 招募券留存</div>'))+len('</div>')
    section = html[begin:end].encode('utf8')
    parser = Paragraphs()
    parser.feed(section.decode('utf8'))
    required = ('除初始招募外', '血管', '初始上限3张', '不可再次存入',
                '在取出时会重新进行随机判定', '亦无法选择替换已留存的券')
    if len(parser.rows) != 5 or any(term not in '\n'.join(parser.rows) for term in required):
        raise ValueError('Complete five-paragraph stashing section required')
    links = {}
    for key, provider in (('exit', current_exit), ('rest', current_rest_travel)):
        cid, label = model.LINKS[key]
        packet = provider.packet()
        target = provider.locate('choices', cid)
        choice = current['choices'][cid]
        if packet is None or target is None or choice['type'] != 'USE_STASHED_TICKET' or choice['displayData']['effectHintType'] != 'STASHED_RECRUIT':
            raise ValueError('Exact existing stashed-ticket reader entry required')
        links[key] = {'label': label, 'original_choice_id': cid,
                      'original_choice': choice, 'target': target,
                      'source_identity': json.loads(json.dumps(packet['source_identity'])),
                      'actual_inventory': None, 'actual_eligible': None}
    data = {
        'schema': 'current_recruit_tickets_354_v1', 'game_commit': model.version.NEW_COMMIT,
        'rows': model.source_rows(current), 'links': links,
        'configuration_bounds': {k: current['gameConst'][k] for k in ('recruitStashMinNum', 'recruitStashMaxNum')},
        'documented_initial_capacity': 3, 'documented_rules': parser.rows,
        'documented_revision': 442954, 'complete_reward_pool': False,
        'actual_inventory': None, 'actual_capacity': None, 'actual_received': None,
    }
    notes = {
        'section': 354, 'candidate_preparation_only': True,
        'game_commit': model.version.NEW_COMMIT,
        'game_source': 'research/p3-expansion-313/current-topic.json',
        'game_source_scope': ['details.stashableTickets', 'details.recruitTickets', 'details.items',
                              'details.choices', 'details.gameConst.recruitStashMinNum', 'details.gameConst.recruitStashMaxNum'],
        'community_url': download['resolved_url'], 'community_revision': 442954,
        'fixed_revision_url': 'https://m.prts.wiki/index.php?title=%E6%B2%89%E6%B2%A6%E8%80%85%E7%9A%84%E9%BB%91%E6%B5%81%E6%A0%91%E6%B5%B7&oldid=442954',
        'complete_rule_section_span_in_downloaded_html_characters': [begin, end],
        'complete_rule_section_bytes': len(section), 'complete_rule_section_sha256': sha256(section).hexdigest(),
        'rules_scope': 'Current community text corroborates the pinned topic. It is documentation, not an account inventory or current server execution record.',
        'prior_failed_fetches': ['web desktop page timeout', 'desktop prts.wiki HTTP403'],
        'successful_source': 'Actual m.prts.wiki HTTP200 full page retained with SHA256 and revision; five complete stashing paragraphs extracted without dropping qualifications.',
        'exact_pair_scope': '47 explicit pairs cover94 recruitment records once each; all recruitment fields exceptid are identical for each pair. This does not establish preserved random state.',
        'configuration_limit_scope': 'gameConst1/15 are retained as raw configuration boundaries, not current inventory or initial capacity. Community initial capacity3 is separate.',
        'existing_readers_reused': ['current_exit339 exact choice_ro6_final1_2', 'current_rest_travel331 exact choice_ro6_rest_7'],
        'licensing': 'PRTS community text retains source attribution and original public HTML. Consult the source site license before redistribution.',
        'unknown': ['actual owned tickets and quantity', 'actual current capacity', 'complete server eligibility',
                    'hope cost and actual recruit candidates', 'random results or probabilities',
                    'rest stashed-ticket option membership in a randomly offered menu',
                    'actual consumption/receipt and current server execution'],
        'not_performed': ['game operation', 'capture', 'chat', 'credential access', 'private-state read/write'],
    }
    output = {model.DATA: encode(data), PACK+'/source-notes.json': encode(notes),
              PACK+'/documented-stashing.html': section}
    names = {
        model.DATA, PACK+'/source-notes.json', PACK+'/source-download.json',
        PACK+'/documented-stashing.html', PACK+'/topic-page.html',
        'research/p3-expansion-313/current-topic.json', 'rouge/data/current-exit.json',
        'rouge/data/current-rest-travel.json', 'research/p3-current-exit-339/runtime-manifest.json',
        'research/p3-current-rest-travel-331/runtime-manifest.json',
    }
    files = {}
    for name in sorted(names):
        content = output.get(name)
        if content is None:
            base = artifact_root if name.startswith(PACK+'/') else source_root
            content = (base/name).read_bytes()
        files[name] = {'sha256': sha256(content).hexdigest(), 'bytes': len(content)}
    output[model.MANIFEST] = encode({'schema': 'current_recruit_tickets_354_manifest_v1',
                                   'game_commit': model.version.NEW_COMMIT, 'files': files})
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source-root', type=Path, default=ROOT)
    parser.add_argument('--output-root', type=Path, default=ROOT)
    args = parser.parse_args()
    output = build(args.source_root, args.output_root)
    for name, raw in output.items():
        path = args.output_root/name
        if args.check:
            if path.read_bytes() != raw:
                raise ValueError('Build differs: '+name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    digest = sha256(output[PACK+'/runtime-manifest.json']).hexdigest()
    print(json.dumps({'candidate_only': True, 'explicit_pairs': 47, 'original_records': 94,
                      'documented_revision': 442954, 'manifest_sha256': digest}))
