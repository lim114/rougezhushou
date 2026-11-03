"""Read actual 442954 HTML mode markers, never split concatenated digits."""
from pathlib import Path
from hashlib import sha256
from urllib.parse import unquote
import argparse
import json
import re
import sys

BASE = Path(__file__).resolve().parents[1]
SOURCE_ROOT = BASE if (BASE / 'rouge/expansion_reference.py').is_file() else BASE.parents[1]
sys.path.insert(0, str(SOURCE_ROOT))
from scripts.build_choice_held_reference import Parser, walk, has_class

PACK = 'research/p3-current-settlement-modes-362'
DATA = 'rouge/data/current-settlement-modes-reference.json'
HTML = 'research/p3-current-recruit-tickets-354/topic-page.html'
DOWNLOAD = 'research/p3-current-recruit-tickets-354/source-download.json'
EXCERPTS = PACK + '/documented-settlement-442954.json'
NOTES = PACK + '/source-notes.json'
MANIFEST = PACK + '/runtime-manifest.json'
PIN = 'd5ef91df0e6f5a77db4967ada301b5346a5e1eda11349a7496804b59cb576498'
FLOORS = {'Ⅰ': 'floor1', 'Ⅱ': 'floor2', 'Ⅲ': 'floor3', 'Ⅳ': 'floor4', 'Ⅴ': 'floor5', '0': 'source0'}


def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def document_fragments(text):
    start = text.index('<p>不同区域中作战获得的指挥经验和源石锭有所不同，具体如下：')
    end = text.index('</table>', start) + len('</table>')
    table = text[start:end]
    if table.count('<table ') != 1:
        raise ValueError('Single complete original settlement table required')
    marker = '通常追猎通关时仅会掉落一张招募券，'
    pos = text.index(marker)
    pursuit = text[text.rfind('<li>', 0, pos):text.index('</li>', pos) + len('</li>')]
    side = '<li>完成<b>熄日余径</b>的<b>普通作战节点</b>后，会额外获得一个随机收藏品。</li>'
    if text.count(marker) != 1 or text.count(side) != 1:
        raise ValueError('Unique explicit pursuit and side-path clauses required')
    return {'table_html': table, 'ordinary_pursuit_html': pursuit, 'side_path_bonus_html': side}


def modes(cell):
    original = cell.text().strip()
    spans = [n for n in walk(cell) if has_class(n, 'is6-exp')]
    if not spans:
        if original not in ('——', '?'):
            raise ValueError('Unmarked experience number refused')
        return {'base': None, 'full_technology': None, 'original_cell_text': original,
                'mode_markers_verified': False}
    basic = [n for n in spans if not has_class(n, 'is-fulltech')]
    full = [n for n in spans if has_class(n, 'is-fulltech')]
    if len(spans) != 2 or len(basic) != 1 or len(full) != 1:
        raise ValueError('One base and one full-technology span required')
    for node in spans:
        if (node.tag != 'span' or not node.text().isdigit()
                or node.attrs.get('id') != 'mw-customcollapsible-is6ExpFullTech'
                or not has_class(node, 'mw-collapsible')):
            raise ValueError('Original numeric display binding changed')
    if has_class(basic[0], 'mw-collapsed') or not has_class(full[0], 'mw-collapsed'):
        raise ValueError('Original base/full display-state meaning changed')
    return {'base': int(basic[0].text()), 'full_technology': int(full[0].text()),
            'original_cell_text': original, 'mode_markers_verified': True,
            'base_attributes': basic[0].attrs, 'full_attributes': full[0].attrs}


def gold(cell):
    text = cell.text().strip()
    text = text.removeprefix('紧急作战版本适用此掉落').strip()
    if text in ('?', '——'):
        return None
    match = re.fullmatch(r'(\d+)(?:~(\d+))?', text)
    if not match:
        raise ValueError('Unreviewed gold cell: ' + text)
    lo, hi = int(match[1]), int(match[2] or match[1])
    if hi < lo:
        raise ValueError('Invalid range')
    return {'minimum': lo, 'maximum': hi}


def parse_html(text, stages):
    if ('"wgRevisionId":442954' not in text or 'oldid=442954' not in text
            or 'creativecommons.org/licenses/by-nc-sa/4.0/' not in text):
        raise ValueError('Explicit revision and attribution required')
    fragments = document_fragments(text)
    parser = Parser()
    parser.feed(fragments['table_html'])
    tables = [n for n in walk(parser.root) if n.tag == 'table']
    if len(tables) != 1:
        raise ValueError('Single parsed table required')
    table = tables[0]
    toggles = [n for n in walk(table) if has_class(n, 'is6-exp-toggle')]
    if len(toggles) != 2 or {n.text() for n in toggles} != {'显示满级生命游戏加成', '显示基础数值'}:
        raise ValueError('Both Chinese display switch labels required')
    for node in toggles:
        if node.attrs.get('id') != 'mw-customcollapsible-is6ExpFullTech':
            raise ValueError('Both switch labels must control the actual number spans')
        is_return = node.text() == '显示基础数值'
        if has_class(node, 'mw-collapsed') != is_return or has_class(node, 'is6-exp-toggle-full') != is_return:
            raise ValueError('Chinese switch label/display-state correspondence changed')
    if '多个指挥经验加成之间乘算叠加，最终结果向下取整' not in table.text():
        raise ValueError('Full qualified header required')
    main, special, portal, previous = {}, [], None, None
    for index, row in enumerate(n for n in walk(table) if n.tag == 'tr'):
        cells = [n for n in row.children if n.tag in ('td', 'th')]
        if len(cells) == 9 and cells[0].text() in FLOORS:
            main[FLOORS[cells[0].text()]] = {
                kind: {'experience_modes': modes(cells[1 + offset * 2]),
                       'base_gold': gold(cells[2 + offset * 2]),
                       'original_floor_label': cells[0].text(), 'source_row_index': index, 'column_kind': kind}
                for offset, kind in enumerate(('normal', 'emergency', 'boss', 'boss_pursuit'))}
        if cells and cells[0].text() == '/':
            if len(cells) != 6 or cells[1].attrs.get('colspan') != '4' or cells[1].text() != '与战斗节点所属层/特殊战斗一致' or any(c.text() != '——' for c in cells[2:]):
                raise ValueError('Explicit portal inheritance and unknown boss columns required')
            portal = {'source_text': cells[1].text(), 'source_row_index': index,
                      'inherited_column_kinds': ['normal', 'emergency'],
                      'unknown_column_kinds': ['boss', 'boss_pursuit']}
        links = [n for n in walk(cells[0]) if n.tag == 'a' and n.attrs.get('title', '').startswith('ISW-')] if cells else []
        if links:
            if len(cells) != 3:
                raise ValueError('Three-column special row required')
            previous = {'label': cells[0].text(), 'links': []}
            for link in links:
                code, sep, name = link.attrs['title'].partition(' ')
                if not sep or unquote(link.attrs['href']) != '/w/' + code + '_' + name:
                    raise ValueError('Exact title and linked page must agree')
                previous['links'].append({'code': code, 'name': name, 'url': 'https://prts.wiki' + link.attrs['href']})
            xp, coins, difficulty = cells[1], cells[2], 'NORMAL'
        elif len(cells) == 2 and previous and '紧急作战版本适用此掉落' in row.text():
            xp, coins, difficulty = cells[0], cells[1], 'FOUR_STAR'
        else:
            continue
        identities = [key for key, stage in stages.items() if stage['difficulty'] == difficulty and
                      any(stage['code'] == link['code'] and stage['name'] == link['name'] for link in previous['links'])]
        if not identities:
            raise ValueError('Documented special battle needs exact current original candidates')
        special.append({**previous, 'difficulty': difficulty, 'stage_ids': identities,
                        'experience_modes': modes(xp), 'base_gold': gold(coins), 'source_row_index': index,
                        'actual_entry_verified': False, 'same_name_variant_selection_known': False})
    if set(main) != set(FLOORS.values()) or len(special) != 18 or portal is None:
        raise ValueError('Complete six-row/eighteen-special-row table required')
    pairs = sum(r['experience_modes']['mode_markers_verified'] for cols in main.values() for r in cols.values()) + sum(r['experience_modes']['mode_markers_verified'] for r in special)
    if pairs != 36:
        raise ValueError('All thirty-six marked nonzero mode pairs required')
    clause = Parser()
    clause.feed(fragments['ordinary_pursuit_html'])
    if clause.root.text() != '通常追猎通关时仅会掉落一张招募券，没有任何指挥经验、源石锭和收藏品报酬。险路恶敌追猎通关时则会正常掉落奖励。':
        raise ValueError('Pursuit exception changed')
    return {'schema': 'current_settlement_modes_362_v1',
            'source': {'revision': 442954, 'file': HTML, 'sha256': PIN,
                       'fixed_url': 'https://m.prts.wiki/index.php?title=沉沦者的黑流树海&oldid=442954',
                       'kind': 'Previously acquired complete original HTTP HTML, reused from section354',
                       'mode_basis': 'Chinese switch labels + shared control id + span classes and initial collapsed states; not numeric magnitude or old tokens',
                       'current_server_verified': False, 'license': 'PRTS CC BY-NC-SA4.0; game material remains original rights'},
            'main_floor_table': main, 'special_battle_table': special, 'portal_rule': portal,
            'ordinary_pursuit': {'experience_modes': {'base': 0, 'full_technology': 0, 'basis': 'explicit no experience reward clause'},
                                 'base_gold': {'minimum': 0, 'maximum': 0}, 'recruit_ticket_reference': 1},
            'documented_side_path_bonus': {'random_relics': 1, 'only': 'completed ordinary battle node', 'actual_received': None},
            'marked_nonzero_mode_pairs': pairs, 'covered_document_modes_verified': True,
            'current_technology_active': None, 'all_current_stage_rewards_known': False,
            'hidden_sixth_region_base_known': False, 'side_path_base_known': False,
            'actual_total_reward': None, 'inventory_updated': False}, fragments


def build(root):
    body = (root / HTML).read_bytes()
    receipt = json.loads((root / DOWNLOAD).read_bytes())
    if (sha256(body).hexdigest() != PIN or receipt['http_status'] != 200 or receipt['sha256'] != PIN
            or receipt['bytes'] != len(body) or receipt['file'] != HTML):
        raise ValueError('Prior actual HTTP receipt and exact original bytes required')
    current = json.loads((root / 'research/p3-expansion-313/current-topic.json').read_bytes())
    data, fragments = parse_html(body.decode('utf8'), current['details']['stages'])
    old = json.loads((root / 'rouge/data/current-settlement-reference.json').read_bytes())
    for floor, columns in data['main_floor_table'].items():
        for kind, row in columns.items():
            if row['base_gold'] != old['main_floor_table'][floor][kind]['base_gold']:
                raise ValueError('New source gold differs from previous pinned row; independent review required')
    additions = sorted({link['name'] for row in data['special_battle_table'] for link in row['links']} -
                       {link['name'] for row in old['special_battle_table'] for link in row['links']})
    if additions != ['晶矿惊蝗']:
        raise ValueError('Unexpected newly documented named special battle')
    notes = {'section_candidate': 362, 'new_download_performed': False, 'original_source_reused_from': HTML,
             'original_download_receipt': DOWNLOAD, 'prior318_original_failure_retained': True,
             'new_api_attempt': {'url': 'https://prts.wiki/api.php?action=parse&oldid=441984&prop=wikitext&format=json',
                                 'tool': 'web.open', 'result': 'URL is not accessible via this tool', 'http_status_known': False},
             'new_evidence_lead': 'Actual complete HTML acquired in354 is newer than318 and retains disambiguating original DOM',
             'new_documented_named_battles': additions,
             'new_crystal_original_candidates': [key for key, row in current['details']['stages'].items()
                                                 if row['code'] == 'ISW-NO' and row['name'] == '晶矿惊蝗' and row['difficulty'] == 'NORMAL'],
             'no_algorithm_invented': True, 'full_technology_multiplier_not_inferred': True,
             'limits': ['Documented values are conditional base/full-technology references, not actual reward total',
                        'No current player technology, server entry or victory verified',
                        'Hidden sixth region and side-path base rows remain absent and unknown',
                        'Two original crystal configs remain candidates; shared level file does not select one'],
             'not_performed': ['tests', 'GUI', 'game', 'chat', 'private state access', 'formal tree modification']}
    output = {DATA: enc(data), EXCERPTS: enc(fragments), NOTES: enc(notes)}
    names = set(output) | {HTML, DOWNLOAD}
    files = {}
    for name in sorted(names):
        raw = output.get(name)
        if raw is None:
            raw = (root / name).read_bytes()
        files[name] = {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()}
    output[MANIFEST] = enc({'schema': 'current_settlement_modes_362_manifest_v1', 'files': files,
                            'current_stage_directory_and_318_context_required': True})
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=SOURCE_ROOT)
    parser.add_argument('--output-root', type=Path, default=BASE)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = build(args.source_root.resolve())
    for name, value in output.items():
        dest = args.output_root / name
        if args.check:
            if dest.read_bytes() != value:
                raise ValueError('Source build differs: ' + name)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(value)
    print(json.dumps({'mode_pairs': 36, 'special_rows': 18, 'new_named_battle': '晶矿惊蝗',
                      'manifest_sha256': sha256(output[MANIFEST]).hexdigest()}, ensure_ascii=False))
