"""Bounded primary-file joins for gates2/4 and manager order; no prototype execution."""
from pathlib import Path
import hashlib
import json
import mmap
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'source-gates-283.json'
assert not OUT.exists(), 'Preserve the first actual source check.'
sha = lambda b: hashlib.sha256(b).hexdigest()
files = {}
def read(path):
    raw = path.read_bytes(); files[str(path.relative_to(ROOT))] = sha(raw)
    return json.loads(raw)

current = read(HERE / 'common-panel-native-candidate.json')
writer_helper = read(HERE / 'panel-writer-helper-candidate.json')
range_attrs = read(HERE / 'common-panel-field-attributes-283.json')
signatures = read(HERE / 'panel-method-signatures-283.json')
metadata = read(HERE / 'routing-metadata-283.json')
support = read(HERE / 'type-routing-support-283.json')
old280 = read(ROOT / 'research/p2-cost-rounding-consensus-280/source-proof.json')
old273 = read(ROOT / 'research/p2-recovery-attributes-273/source-proof.json')
assert files['research/p2-cost-rounding-consensus-280/source-proof.json'] == '67455e993a068f538bda96bb45d6c5e6b33fb1357894c873bc73c39d691a5bc6'
checks = []
def check(name, ok): checks.append({'name': name, 'passed': bool(ok)})
def method(package, address): return next(m for m in package['methods'] if m['method']['Address'] == address)
manager = next(m for m in current['methods'] if m['method']['metadata_method_index'] == 85517)
raw_round = method(writer_helper, 0x18000cec0)
old_round = method(old280, 0x18059e290)
ctor = method(support, 0x182319960)
new_body = [i for i in raw_round['instructions'] if 0x18000cec0 <= int(i['address'], 16) <= 0x18000cf70]
check('unnamed_round_body_43', len(new_body) == 43)
all_current = {i['address']: i for p in (current, writer_helper, support) for m in p['methods'] for i in m['instructions']}
all_old = {i['address']: i for m in old280['methods'] for i in m['instructions']}
all_generic = {i['address']: i for m in old273['methods'] for i in m['instructions']}
selected = {}
groups = {}
def select(label, items):
    groups[label] = sorted({i['address'] for i in items}, key=lambda s: int(s, 16))
    for i in items:
        if i['address'] in selected: assert selected[i['address']]['bytes'] == i['bytes']
        selected[i['address']] = i
def expect(address, mnemonic, operand, old=False, generic=False):
    i = (all_generic if generic else all_old if old else all_current)[address]
    check('instruction.' + address, i['mnemonic'] == mnemonic and i['operands'] == operand)
    select('source_join_anchors', [i] + [selected[a] for a in groups.get('source_join_anchors', [])])
    return i

select('manager_bounded_body', manager['instructions'])
select('unnamed_double_round_body', new_body)
select('range_ctor30778', ctor['instructions'])
select('ordinary_five_getters', [i for m in current['methods'] if m['method'].get('metadata_method_index') in (66454,66458,66459,66460,66468) for i in m['instructions']])
select('reused_generic_range_helpers', [i for m in old273['methods'] if m['method']['Address'] in (0x182319a00,0x182319850) for i in m['instructions']])
shared = []
for address in (0x1804d57f0, 0x1804d3200, 0x1804d58c0):
    m = method(old280, address)
    select('reused_round_callee_' + hex(address), m['instructions'])
    shared.append({'address': hex(address), 'reachable_bytes_sha256': m['reachable_bytes_sha256'],
                   'selected_instruction_count': len(m['instructions']), 'name_identity_claimed': False})

# Compare the shared floor code already traversed in the new tail jump to the old bound proof.
overlap = [i for i in raw_round['instructions'] if i['address'] in all_old]
check('shared_floor_overlap_exact_bytes', overlap and all(all_old[i['address']]['bytes'] == i['bytes'] for i in overlap))

joins = []
for new, old, target in [
    ('0x18000ceda','0x18059e2e2','0x1804d57f0'),
    ('0x18000cf25','0x18059e336','0x1804d57f0'),
    ('0x18000cf20','0x18059e323','0x1804d3200'),
    ('0x18000cf62','0x18059e377','0x1804d58c0')]:
    a,b = all_current[new], all_old[old]
    check('same_callee.' + new, a.get('target') == b.get('target') == target)
    select('source_join_anchors', [b] + [selected[a] for a in groups.get('source_join_anchors', [])])
    joins.append({'new_site': new, 'old_site': old, 'callee': target,
                  'new_site_bytes': a['bytes'], 'old_site_bytes': b['bytes'],
                  'whole_wrapper_bytes_claimed_equal': False})

new_constants = {r['address']: r['bytes8'] for i in new_body for r in i.get('rip_data', [])}
old_constants = {r['address']: r['bytes8'] for i in old_round['instructions'] for r in i.get('rip_data', [])}
check('round_constants_shared_addresses_and_bytes', all(old_constants.get(a) == b for a,b in new_constants.items()))
values = sorted(set(struct.unpack('<d', bytes.fromhex(v))[0] for v in new_constants.values()))
check('round_constants_minus_half_half_one', values == [-0.5,0.5,1.0])
expect('0x18000cef5','cvttsd2si','rax, xmm0')
expect('0x18000cefa','test','al, 1')
expect('0x18000cf3c','cvttsd2si','rax, xmm0')
expect('0x18000cf41','test','al, 1')
expect('0x18231af2e','cvtss2sd','xmm0, xmm6')
expect('0x18231af32','call','0x18000cec0')
expect('0x18231af46','movsd','qword ptr [rsp + 0x80], xmm0')
expect('0x18231afb2','cvtss2sd','xmm0, xmm6')
expect('0x18231afb6','call','0x18000cec0')
expect('0x18231afd3','cvttsd2si','edx, xmm6')
expect('0x18231afdf','call','0x18660b950')
expect('0x18231b0ae','call','0x1866fae20')
expect('0x18231b0d7','call','0x18231ad20')

# Formula and order: two metadata element reads, no ordinary max() in the manager.
for a,m,o in [
    ('0x180d06270','call','0x18231bb70'),
    ('0x180d062c1','call','0x184afcf00'),
    ('0x180d062cf','mov','r14, qword ptr [rax + 0x10]'),
    ('0x180d062ef','call','0x184afcf00'),
    ('0x180d062fd','mov','rbp, qword ptr [rax + 0x20]'),
    ('0x180d06301','test','rbp, rbp'),
    ('0x180d06304','je','0x180d0645d'),
    ('0x180d0630e','test','r14, r14'),
    ('0x180d0638f','call','0x184624db0'),
    ('0x180d063c7','mov','rdx, qword ptr [rdx + 0x20]'),
    ('0x180d063cb','call','0x184624db0'),
    ('0x180d063d9','call','0x1866fb870'),
    ('0x180d06402','call','0x1866fb870'),
    ('0x180d06415','call','0x182319850'),
    ('0x180d06447','call','0x1866ff2e0'),
    ('0x180d06458','call','0x18231b050'),
    ('0x180d0645d','inc','esi')]: expect(a,m,o)
check('manager_no_ordinary_max_callee', not any(i.get('target') == '0x1866ff750' for i in manager['instructions']))
between = [i for i in manager['instructions'] if 0x180d06458 < int(i['address'],16) < 0x180d0645d]
check('writer_boolean_not_checked_before_increment', not between)
expect('0x18064b1c8','call','0x1866ff750',generic=True)
expect('0x18064b1d6','call','0x1866fb870',generic=True)
expect('0x18064b1e4','call','0x184624db0',generic=True)
expect('0x18064b1f2','call','0x1866fb870',generic=True)

# Bind range construction (not field values or live reflection identity).
expect('0x182319994','movss','dword ptr [rdi + 0x18], xmm6')
expect('0x18231999e','movss','dword ptr [rdi + 0x1c], xmm7')
expect('0x1823199b0','mov','word ptr [rdi + 0x20], 0x101')
ranges = {'maxHp': [1, None], 'atk': [0,None], 'def': [0,None],
          'magicResistance': [0,100], 'attackSpeed': [20,None]}
for row in range_attrs['fields']:
    attrs = row['attributes']; check('fully_consumed.' + row['field'], row['fully_consumed'] is True and len(attrs) == 1)
    args = attrs[0]['arguments']; expected = ranges[row['field']]
    check('range_lower.' + row['field'], args[1]['value'] == expected[0])
    check('range_constructor.' + row['field'], attrs[0]['constructor_index'] == (30778 if expected[1] is not None else 30777))
    if expected[1] is not None: check('range_upper.' + row['field'], args[2]['value'] == expected[1])
manager_meta = next(t for t in metadata if t['name'] == 'Torappu.Battle.Roguelike.RoguelikeBattleManager')
for name,offset in [('m_attributeAdditions',0xb8),('m_attributeMultipliers',0xc0),('m_attributeFinalScalers',0xc8)]:
    check('manager_layout.' + name, next(f for f in manager_meta['fields'] if f['name'] == name)['offset'] == offset)
check('manager_void_signature', next(r for r in signatures if r['index'] == 85517)['return_type'] == 'System.Void')
check('both_writer_boolean_signatures', all(next(r for r in signatures if r['index'] == n)['return_type'] == 'System.Boolean' for n in (30791,30792)))

# Every selected instruction/RIP constant and the five custom-attribute spans is physically rechecked.
spans = []
for i in selected.values():
    spans.append({'source':'dll','physical_offset':i['physical_offset'],'raw_hex':i['bytes'],'label':i['address']})
    for rip in i.get('rip_data', []):
        # PE mapping is unchanged; fixed current .text/.rdata RVA relation is read from the known map.
        address = int(rip['address'],16)
        verification = json.loads((ROOT / '.cache/research/p2-native-current-263/mapping-verification.json').read_bytes())
        rva = address - verification['image_base']
        section = next(s for s in verification['sections'] if s['rva'] <= rva < s['rva'] + s['raw_size'])
        offset = section['offset'] + rva - section['rva']
        spans.append({'source':'dll','physical_offset':offset,'raw_hex':rip['bytes8'],'label':'RIP '+rip['address']})
spans += [{'source':'metadata','physical_offset':r['physical_offset'],'raw_hex':r['raw_hex'],'label':r['field']+' custom attributes'} for r in range_attrs['fields']]
fresh = {}; mismatches = []
for kind,path,expected in [
    ('dll',Path(r'D:\Hypergryph Launcher\games\Arknights\GameAssembly.dll'),'583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5'),
    ('metadata',Path(r'D:\Hypergryph Launcher\games\Arknights\Arknights_Data\il2cpp_data\Metadata\global-metadata.dat'),'d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f')]:
    with path.open('rb') as handle, mmap.mmap(handle.fileno(),0,access=mmap.ACCESS_READ) as raw:
        actual = sha(raw); check('full_primary_sha.' + kind, actual == expected)
        rows = [s for s in spans if s['source'] == kind]
        for span in rows:
            o=span['physical_offset'];o=int(o,0) if isinstance(o,str) else o;b=bytes.fromhex(span['raw_hex'])
            if raw[o:o+len(b)] != b:mismatches.append(span)
        fresh[kind]={'sha256':actual,'selected_spans':len(rows)}
check('all_selected_primary_spans', not mismatches)

report = {'kind':'SECTION283_SOURCE_GATES2_4_AND_MANAGER_BOUNDED_REVIEW',
    'script_sha256':sha(Path(__file__).read_bytes()),'source_artifacts_sha256':files,
    'fresh_primary_files':fresh,'selected_unique_instructions':len(selected),'selected_byte_spans':len(spans),
    'byte_spans':spans,'selected_instruction_groups':groups,'shared_old280_callees':shared,
    'new_round_metadata_identity_known':False,'whole_wrapper_bytes_claimed_equal':False,
    'callee_and_constant_joins':joins,'shared_round_constants':new_constants,
    'ranges_reference_raw':{n:[int(v[0]*(1<<32)),9223372036854775806 if v[1] is None else int(v[1]*(1<<32))] for n,v in ranges.items()},
    'gate2_source_supported_conditionally':True,'gate4_source_supported_conditionally':True,
    'fresh_whole_game_mechanisms_claimed':0,'new_full_audit_of273_or280_proofs':False,
    'game_dll_executed':False,'process_memory_read':False,'prototype_or_production_modified':False,
    'source_facts':[
      'Manager rune formula is (raw+ADD)*(ONE+MULT)*FINAL_SCALER, then field metadata range. It has no ordinary max0 multiplier or FINALADD bucket.',
      'Ordinary273 generic formula remains ((raw+ADD)*Max(0,MULT)+FINALADD)*FINALSCALER. Default bounds apply during qualified recomputation; clean decoded cache is not re-clamped.',
      'Five default ranges: HP>=1, ATK/DEF>=0, MR0..100, AS>=20 with no600 metadata upper bound. FP.MaxValue upper is9223372036854775806. Dynamic ranges and attack timing limits are distinct qualifications.',
      'Manager count capture precedes the loop; each iteration reads FieldMeta twice. First supplies FieldInfo, second supplies AttributeMeta. NULL second metadata skips the field before the first FieldInfo NULL guard.',
      'RangeMeta.Attribute indexes the ADD/MULT/FINAL_SCALER arrays; a field label does not establish actual matching FieldInfo/rangeMeta identity or actual rune inventory.',
      'Manager ignores the Boolean writer return and increments unconditionally on a normal return. Normal false or unknown Boolean does not block later fields; exception or unknown normality changes future reachability. Manager returns Void.',
      'FP writer overload calls AsFloat before the Single writer checks FieldInfo. The Double helper is unnamed, receives exact Single-to-Double input in the qualified normal domain, and returns Double.',
      'Raw Double helper and old280 wrapper share exact unchanged modf/floor/ceil code addresses and constants. They are not claimed to be byte-identical functions. Parity checks use Int64 only for tie handling.',
      'ObscuredInt path adds explicit CVTTSD2SI32 before its encoder. Another writer path boxes returned Double for reflection; runtime selector identity is delegated to the independent routing source proof, and SetValue acceptance remains independent.',
    ],
    'round_domain_contract':[
      'Conditional ordinary normal hardware completion, no operand/result rewriting; no actual MXCSR, exception-mask or current-hotfix claim.',
      'For finite normal/zero Single inputs whose rounded integer is in signed32, conversion to Double is exact. For |x|>=0.5 within this domain, x+/-0.5 is exact in Double and the proven branches yield half-even.',
      'For |x|<0.5 arbitrary tiny normal Single, x+/-0.5 need not be Double-exact, but all allowed normal modes stay between neighboring integers and floor/ceil yield0. No blanket exact-add claim.',
      'AsFloat outputs are integer-Single conversions scaled by2^-32, hence a Q32 lattice and no nonzero output smaller than2^-32; its qualified output has enough Double precision for the helper offsets.',
      'Do not extend the half-even proof to arbitrary huge finite Single or subnormal independent input without separate evidence. Nonfinite/unsupported/overflow or any candidate outside signed32 keeps the full integer writer unknown.',
      'MAX64 may convert to+2^31; that is outside Int32, not a proven normal0x80000000 encoder argument. MIN64 maps to-2^31 and is valid. Returned Double or encoder argument never establishes a subsequent protected decode.',
    ],
    'necessary_source_contract_counterexamples':[
      {'scope':'conditional arithmetic, not an observed inventory','raw':2*(1<<32),'ADD':0,'MULT':-2*(1<<32),'FINAL_SCALER':-(1<<32),'rune_before_range':2*(1<<32),'ordinary_max0_before_range':0,'reason':'Negative scaler makes an illicit inserted max0 observable even after ATK lower0 range.'},
      {'scope':'source control','first_FieldInfo_exists':False,'second_rangeMeta_exists':False,'required':'normal skip without FieldInfo guard or writer'},
      {'scope':'source control','writer_normal':True,'writer_return':False,'required':'continue next field, no fabricated manager Boolean failure'},
      {'scope':'source control','writer_normal':None,'required':'preserve earlier completed assignments; later field reachability unknown'},
      {'scope':'source control','FP_writer_FieldInfo_exists':False,'required':'AsFloat conversion is reached before the Single overload NULL failure'},
    ],
    'remaining_unknowns':['actual FieldInfo/metadata-list identity, inventory and attachment/order','actual RC/masks/hotfix/current objects','reflection acceptance or conversion and protected roundtrip','main four-layer integration and actual window acceptance remain root work'],
    'checks':checks,'check_count':len(checks),'all_source_checks_passed':all(c['passed'] for c in checks),'mismatches':mismatches,
    'scope':'Source gate review only; neither implementation tests nor completion of section283.'}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'passed':report['all_source_checks_passed'],'checks':len(checks),'selected_unique_instructions':len(selected),'selected_byte_spans':len(spans),'receipt_sha256':sha(OUT.read_bytes()),'failed':[c['name'] for c in checks if not c['passed']]},ensure_ascii=False))
raise SystemExit(0 if report['all_source_checks_passed'] else 1)
