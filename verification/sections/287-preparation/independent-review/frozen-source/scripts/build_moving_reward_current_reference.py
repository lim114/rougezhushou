"""Extract the three reviewed grade blocks from an archived PRTS HTML page.

Offline only. Importing this module does not read, write, fetch or execute game
data. The raw page SHA and revision are fixed; changed source needs new review.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

HTML_SHA256 = 'ac67db472d7cbfe9caef105b9ab17eb4fda43f0b09a8a229e61eeca8392c2430'
REVISION = '435751'
ENTITY = 'enemy_2152_shezlc'
SENTENCE = ('被击倒时战斗结束后额外获得10源石锭；'
            '到达路径终点时战斗结束后扣除10源石锭')


class _Sections(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.offsets = [0]
        for match in re.finditer('\n', text):
            self.offsets.append(match.end())
        self.headings = []
        self.current = None
        self.heading = None
        self.hidden = 0
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag == 'h2' and not self.hidden:
            line, column = self.getpos()
            self.heading = {'start_character': self.offsets[line - 1] + column,
                            'text': [], 'body': []}
            self.current = None

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden:
            self.hidden -= 1
        if tag == 'h2' and self.heading is not None:
            heading = self.heading
            heading['title'] = ''.join(heading.pop('text')).strip()
            self.headings.append(heading)
            self.current = heading
            self.heading = None

    def handle_data(self, data):
        if self.hidden:
            return
        if self.heading is not None:
            self.heading['text'].append(data)
        elif self.current is not None:
            self.current['body'].append(data)


def extract_document(html_bytes):
    """Return exact archived source spans, never an assumed runtime reward."""
    if hashlib.sha256(html_bytes).hexdigest() != HTML_SHA256:
        raise ValueError('Archived public HTML differs from the reviewed original bytes.')
    text = html_bytes.decode('utf8')
    for field in ('wgCurRevisionId', 'wgRevisionId'):
        values = re.findall(r'"' + field + r'":(\d+)', text)
        if values != [REVISION]:
            raise ValueError('Page revision metadata does not bind the reviewed revision.')
    if not re.search(r'oldid=' + REVISION + r'(?:["<&]|$)', text):
        raise ValueError('Missing matching permanent-link revision.')
    if ENTITY not in text or '<title>恶笼草' not in text:
        raise ValueError('Page identity is not the exact moving enemy.')
    parser = _Sections(text)
    rows = []
    for level in range(3):
        matches = [(index, heading) for index, heading in enumerate(parser.headings)
                   if heading['title'] == '级别' + str(level)]
        if len(matches) != 1:
            raise ValueError('Each reviewed grade needs exactly one real h2 block.')
        index, heading = matches[0]
        start = heading['start_character']
        end = (parser.headings[index + 1]['start_character']
               if index + 1 < len(parser.headings) else len(text))
        source_span = text[start:end].encode('utf8')
        plain = re.sub(r'\s+', '', ''.join(heading['body']))
        if plain.count(SENTENCE) != 1 or '???' in plain:
            raise ValueError('Grade block lacks the exact complete documented condition sentence.')
        rows.append({'level': level, 'heading': heading['title'],
                     'start_byte': len(text[:start].encode('utf8')),
                     'end_byte': len(text[:end].encode('utf8')),
                     'source_span_sha256': hashlib.sha256(source_span).hexdigest(),
                     'source_span_bytes': len(source_span),
                     'documented_condition_sentence_occurrences': 1,
                     'defeated_battle_settlement_gold': 10,
                     'reached_route_end_battle_settlement_gold': -10})
    return {'schema_version': 1, 'entity_id': ENTITY, 'revision': REVISION,
            'source_type': 'archived_community_enemy_mechanics_documentation',
            'raw_html_sha256': HTML_SHA256, 'raw_html_bytes': len(html_bytes),
            'shared_condition_sentence': SENTENCE, 'grades': rows,
            'actual_server_script_verified': False,
            'actual_spawn_level': None, 'actual_reward_total': None,
            'scope': 'Each h2 grade block is independently present in one original HTTP body. These are conditional documentation quantities, not current-server execution or selected-instance proof.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = extract_document(args.html.read_bytes())
    payload = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    if args.check:
        if args.output.read_bytes() != payload:
            raise ValueError('Saved extraction does not exactly reproduce from the archived source.')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('xb') as stream:
            stream.write(payload)
    print(json.dumps({'checked_existing': args.check, 'grade_count': len(result['grades']),
                      'revision': REVISION, 'output_sha256': hashlib.sha256(payload).hexdigest()}))


if __name__ == '__main__':
    main()
