"""Independent literal/enclosure review of frozen878347; no parent self-QA reused."""
from pathlib import Path
from fractions import Fraction
import hashlib
import importlib.util
import json
import struct
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATH = ROOT / '.cache/section283-numeric/rouge/panel_native_precision.py'
EXPECTED = '878347f7f5d69d09535f1bf0aec409068c68a3cdcf54812091c7deb96be838fc'
OUT = HERE / 'independent-numeric-review-283.json'
assert not OUT.exists()
assert hashlib.sha256(PATH.read_bytes()).hexdigest() == EXPECTED
spec = importlib.util.spec_from_file_location('_283_independent_numeric', PATH)
core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
checks, probes = [], []
Q = 4294967296
def check(name, ok): checks.append({'name':name,'passed':bool(ok)})
def rational(bits):
    # Loading a finite binary32 into Python binary64 is exact. There is no host
    # arithmetic rounding oracle or duplicate integer-to-Single implementation.
    value = struct.unpack('<f',struct.pack('<I',bits))[0]
    numerator,denominator = value.as_integer_ratio()
    return Fraction(numerator,denominator)

# RC candidate bits are manually derived IEEE lattice literals, not core helpers.
raw_cases = [
 ('zero',0,[0]*4,True,[0],0),
 ('minimum_nonzero',1,[0x2f800000]*4,True,[0],0),
 ('negative_minimum_nonzero',-1,[0xaf800000]*4,True,[0],0),
 ('positive_half',Q//2,[0x3f000000]*4,True,[0],0),
 ('negative_half',-Q//2,[0xbf000000]*4,True,[0],0),
 ('positive_odd_half',3*Q//2,[0x3fc00000]*4,True,[2],2),
 ('negative_odd_half',-3*Q//2,[0xbfc00000]*4,True,[-2],-2),
 ('positive_even_half',5*Q//2,[0x40200000]*4,True,[2],2),
 ('negative_even_half',-5*Q//2,[0xc0200000]*4,True,[-2],-2),
 ('just_below_half',Q//2-1,[0x3f000000,0x3effffff,0x3f000000,0x3effffff],True,[0],0),
 ('just_above_half',Q//2+1,[0x3f000000,0x3f000000,0x3f000001,0x3f000000],True,[0,1],None),
 ('negative_beyond_half',-Q//2-1,[0xbf000000,0xbf000001,0xbf000000,0xbf000000],True,[-1,0],None),
 ('int_conversion_even_tie',(1<<24)+1,[0x3b800000,0x3b800000,0x3b800001,0x3b800000],True,[0],0),
 ('int_conversion_odd_tie',(1<<24)+3,[0x3b800002,0x3b800001,0x3b800002,0x3b800001],True,[0],0),
 ('negative_directed_tie',-((1<<24)+1),[0xbb800000,0xbb800001,0xbb800000,0xbb800000],True,[0],0),
 ('minimum_signed64',-(1<<63),[0xcf000000]*4,True,[-2147483648],-2147483648),
 ('maximum_signed64',(1<<63)-1,[0x4f000000,0x4effffff,0x4f000000,0x4effffff],False,[2147483520],None),
 ('negative_maximum_magnitude',-((1<<63)-1),[0xcf000000,0xcf000000,0xceffffff,0xceffffff],True,[-2147483648,-2147483520],None),
 ('largest_valid_float_grid',(1<<63)-(1<<39),[0x4effffff]*4,True,[2147483520],2147483520),
 ('just_below_odd_half',3*Q//2-1,[0x3fc00000,0x3fbfffff,0x3fc00000,0x3fbfffff],True,[1,2],None),
]
for name,raw,bits,complete,integers,consensus in raw_cases:
    fp = core.fp_single_reference(raw); integer = core.writer_integer_reference(raw)
    probes.append({'name':name,'raw':raw,'expected_ordered_rc_bits':bits,'actual_float':fp,'actual_writer':integer})
    check(name+'.all_four',fp['complete'] is True and [c['conversion_rc'] for c in fp['candidates']]==[0,1,2,3])
    check(name+'.literal_bits',[c['bits'] for c in fp['candidates']]==bits)
    check(name+'.integer_domain',integer['complete'] is complete and integer['integer_candidates']==integers and integer['integer_consensus']==consensus)
    values=[rational(c['bits']) for c in fp['candidates']]
    ideal=Fraction(raw,Q)
    check(name+'.directed_enclosure',values[1]<=ideal<=values[2] and (values[3]<=ideal if raw>=0 else values[3]>=ideal))
    check(name+'.normal_or_zero_output',all(((c['bits']>>23)&255) in range(1,255) or (c['bits']&0x7fffffff)==0 for c in fp['candidates']))
    check(name+'.nearest_result_distance',abs(values[0]-ideal)==min(abs(values[1]-ideal),abs(values[2]-ideal)))

single_cases=[
 ('single_signed_zero',0x80000000,True,[0],0),
 ('single_just_below_half',0x3effffff,True,[0],0),
 ('single_just_above_half',0x3f000001,True,[1],1),
 ('single_negative_beyond_half',0xbf000001,True,[-1],-1),
 ('single_minimum_normal',0x00800000,True,[0],0),
 ('single_negative_minimum_normal',0x80800000,True,[0],0),
 ('single_tiny_normal_nonQ32',0x2f800001,True,[0],0),
 ('single_int32_min',0xcf000000,True,[-2147483648],-2147483648),
 ('single_positive_int32_boundary',0x4f000000,False,[],None),
 ('single_maximum_finite',0x7f7fffff,False,[],None),
 ('single_subnormal',1,False,[],None),
 ('single_infinity',0x7f800000,False,[],None),
 ('single_nan',0x7fc00001,False,[],None),
]
for name,bits,complete,integers,consensus in single_cases:
    actual=core.single_integer_reference(bits)
    probes.append({'name':name,'bits':bits,'actual':actual})
    check(name+'.literal',actual['complete'] is complete and actual['integer_candidates']==integers and actual['integer_consensus']==consensus)

for name,fn in [('float',core.fp_single_reference),('writer',core.writer_integer_reference),('single',core.single_integer_reference)]:
    r=fn(None);probes.append({'name':name+'.unknown_input','actual':r})
    check(name+'.unknown_input',r['complete'] is False and r['reason']=='unknown_input')
    for bad in (True,1.0):
        try:fn(bad);reject=False
        except ValueError:reject=True
        check(name+'.reject_'+type(bad).__name__,reject)
for bad in (1<<63,-(1<<63)-1):
    try:core.fp_single_reference(bad);reject=False
    except ValueError:reject=True
    check('out_of_signed64_rejected.'+str(bad),reject)
check('frozen_numeric_after',hashlib.sha256(PATH.read_bytes()).hexdigest()==EXPECTED)
report={'kind':'SECTION283_INDEPENDENT_NUMERIC_LITERAL_AND_ENCLOSURE_REVIEW',
 'numeric_sha256':EXPECTED,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'source_gate_reference':'source-gates-283.json','source_gate_sha256':'f58a6091f71d54f0e12eb33cfe7abff0102465843fdfb1b089ba2414cfa93003',
 'probe_count':len(probes),'checks':checks,'check_count':len(checks),'probes':probes,
 'passed':all(c['passed'] for c in checks),'actual_RC_or_masks_claimed':False,
 'parent_author_selftests_reused_as_independence':False,'game_or_DLL_execution':False,
 'process_memory_read':False,'private_state_or_chat_operation':False,
 'new_native_source_spans_claimed':0,
 'limits':['Conditional normal arithmetic only','Subnormal and nonfinite independentSingle input remains unknown','A partial safe Int32 subset cannot establish full consensus','No encoder/decode/reflection/actual panel inference'],
 'scope':'Limited independent numerical review, not complete parent-flow QA or Windows verification.'}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'passed':report['passed'],'probes':len(probes),'checks':len(checks),'receipt_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'failed':[c['name'] for c in checks if not c['passed']]},ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
