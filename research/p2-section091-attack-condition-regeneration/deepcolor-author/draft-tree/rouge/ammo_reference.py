"""Two verified refill ratios, not a general client fixed-point emulator."""
import json,math,struct
from copy import deepcopy
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def refill_source():
    return json.loads((Path(__file__).with_name('data')/'ammo-refill-reference.json').read_text(encoding='utf-8'))


def partial_packet_reference(operator_id,skill,cost):
    """Only an explicitly documented skill may complete an underfilled packet."""
    for rule in refill_source().get('partial_packet_rules',[]):
        if (rule['operator_id']==operator_id and rule['skill']==skill and
                rule['attack_cost_reference']==cost and rule['partial_last_packet']=='full_attack'):
            return deepcopy(rule)
    return None


def refill_parameters(maximum,threshold_ratio,refill_ratio):
    if isinstance(maximum,bool) or not isinstance(maximum,(int,float)):
        return None
    try:
        if not math.isfinite(maximum) or not float(maximum).is_integer() or not 0<maximum<=10000:return None
    except OverflowError:return None
    source=refill_source();raw=[]
    for ratio in (threshold_ratio,refill_ratio):
        if isinstance(ratio,bool) or not isinstance(ratio,(int,float)):return None
        if ratio not in source['verified_ratios']:return None
        raw.append(struct.unpack('<f',struct.pack('<f',ratio))[0])
    maximum=int(maximum)
    products=[struct.unpack('<f',struct.pack('<f',maximum*ratio))[0] for ratio in raw]
    threshold=math.floor(products[0]);amount=math.ceil(products[1])
    return {'maximum':maximum,'threshold':threshold,'refill_count':amount,
        'threshold_product_binary32':products[0],'refill_product_binary32':products[1],
        'parameter_arithmetic':source['parameter_arithmetic'],
        'native_parameter_proof_sha256':source['native_parameter_proof_sha256'],
        'can_trigger_before_empty':threshold>0,'require_positive_remaining':True,
        'template_url':source['template_url'],'fixed_point_url':source['fixed_point_url'],
        'client_frame_calibration_verified':False}


def refill_before_empty_is_safe(parameters,cost,minimum_interval):
    """A conservative 30Hz reference bound, not a measured polling phase."""
    if isinstance(cost,bool) or not isinstance(cost,int) or cost<=0:
        raise ValueError('Attack cost must be a positive integer.')
    if not parameters['can_trigger_before_empty']:return True
    if isinstance(minimum_interval,bool) or not isinstance(minimum_interval,(int,float)):return False
    try:
        if not math.isfinite(minimum_interval) or minimum_interval<=0:return False
    except OverflowError:return False
    # The first reachable positive band must survive beyond the documented
    # 0.1s periodic check plus reference frame rounding. Equality can race.
    available_attacks=parameters['threshold']//cost
    return available_attacks*minimum_interval>refill_source()['reference_polling_bound_frames']/30
