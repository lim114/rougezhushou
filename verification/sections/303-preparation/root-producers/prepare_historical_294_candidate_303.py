from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[1]
name='tests/test_direct_landmark_294.py'
before=(ROOT/name).read_bytes();assert sha256(before).hexdigest()=='447b1d84f2eb40fce01e90a9145ce056ea85d21a1f2e399aab060bc2d7ebdfa0'
text=before.decode('utf8');eol='\r\n' if b'\r\n' in before else '\n'
old='''    @classmethod
    def setUpClass(cls):
        cls.output, cls.receipt = builder.build()
'''.replace('\n',eol)
new='''    @classmethod
    def setUpClass(cls):
        # Replay the unchanged historical294 builder against its exact public58
        # input. Actual current appended values remain checked via landmark_data
        # below and the separate303 suite; no runtime source is replaced.
        snapshot = builder.ROOT / 'research/p3-map-direct-ground-303/prior-direct-references.json'
        raw = snapshot.read_bytes()
        if hashlib.sha256(raw).hexdigest() != '63ec9488f8f905d2ced1a4e349413e9c92d78125b9f1c94c00293cafa4d348f5':
            raise ValueError('Historical294 public58 input changed.')
        temporary = tempfile.TemporaryDirectory(prefix='rouge-public294-replay-')
        cls.addClassCleanup(temporary.cleanup)
        history = Path(temporary.name)
        original = DATA
        names = ['battle-previews.json', 'battle-map-projections.json']
        records = builder.read(builder.BASE / 'source-records.json')['stages']
        names += sorted({row['image']['file'] for row in records.values()})
        for name in names:
            target = history / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original / name, target)
        (history / 'fixed-landmark-references.json').write_bytes(raw)
        for owner in (builder, sys.modules[__name__]):
            fixture = patch.object(owner, 'DATA', history)
            fixture.start()
            cls.addClassCleanup(fixture.stop)
        cls.output, cls.receipt = builder.build()
'''.replace('\n',eol)
assert text.count(old)==1;text=text.replace(old,new)
after=text.encode('utf8');ast.parse(after)
def test_methods(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
assert test_methods(before)==test_methods(after) and len(test_methods(after))==18
target=ROOT/'.cache/p3-303-parent'/name;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(after)
proof={'section':303,'kind':'historical294_exact_public_input_fixture_candidate_not_formal_acceptance','path':name,
 'before_sha256':sha256(before).hexdigest(),'after_sha256':sha256(after).hexdigest(),
 'all_original_test_method_AST_unchanged':18,'old_builder_modified':False,
 'snapshot_sha256':'63ec9488f8f905d2ced1a4e349413e9c92d78125b9f1c94c00293cafa4d348f5',
 'current_runtime_landmark_data_not_patched':True,'current_appended_data_covered_by_new303':True,
 'production_or_tests_modified_yet':False}
path=ROOT/'.cache/p3-303-parent/historical294-candidate.json';path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
print(json.dumps(proof))
