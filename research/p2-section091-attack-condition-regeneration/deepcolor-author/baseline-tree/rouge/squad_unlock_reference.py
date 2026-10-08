"""Pinned strengthened-squad conditions are references, not account unlock rules."""
from .run_config import config_data
from .technology import technology_node, technology_gates

_TECHNOLOGY_IDS={
    'rogue_6_band_2':'rogue_6_difficulty_1',
    'rogue_6_band_5':'rogue_6_difficulty_2',
    'rogue_6_band_7':'rogue_6_difficulty_3',
    'rogue_6_band_16':'rogue_6_outbuff_43',
    'rogue_6_band_18':'rogue_6_outbuff_45',
    'rogue_6_band_20':'rogue_6_outbuff_44',
}


def squad_unlock_reference(squad_id):
    data=config_data()
    record=data['squads'].get(squad_id)
    if not record or record['bandLevel']!=1:return None
    node_id=_TECHNOLOGY_IDS.get(squad_id)
    technology=None
    if node_id:
        node=technology_node(node_id)
        gate=technology_gates().get(node_id)
        technology={
            'id':node_id,'name':node['buffName'],'node_type':node['nodeType'],
            'effect_text_reference':list(node['rawDesc']),
            'source_selector':'$.customizeData.rogue_6.commonDevelopment.developments.'+node_id,
            'gate_reference':None if gate is None else {
                'enable_grade_parameter':gate['enableGrade'],
                'enable_description_reference':gate['enableDesc'],
                'source_selector':'$.customizeData.rogue_6.commonDevelopment.developmentsDifficultyNodeInfos.'+node_id,
            },
        }
    return {
        'squad_id':squad_id,'base_squad_id':record['normalBandId'],
        'variant_level_parameter':record['bandLevel'],
        'unlock_condition_reference':record['unlockCondDesc'],
        'technology_node_reference':technology,
        'account_unlocked':None,'actual_activation':None,'reference_only':True,
        'source':{'url':data['source_url'],'sha256':data['source_sha256'],'commit':data['commit'],
                  'condition_selector':'$.details.rogue_6.items.'+squad_id+'.unlockCondDesc',
                  'variant_selector':'$.details.rogue_6.bandRef.'+squad_id},
    }
