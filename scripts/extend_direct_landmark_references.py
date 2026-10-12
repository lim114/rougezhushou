"""Append two independently read fixed bitmaps without new plane assumptions."""
import argparse,copy,hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data,DATA
from rouge.map_projection import grid_digest
BASE=ROOT/'research/p3-direct-ground-expanded'
OUTPUT=DATA/'fixed-landmark-references.json'

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def finite_pair(value):
    return isinstance(value,list) and len(value)==2 and all(type(v) in (int,float) and math.isfinite(v) for v in value)

def build(write=False):
    source=read(BASE/'source-receipt.json')
    for name,digest in source['frozen_sha256'].items():
        if sha(BASE/name)!=digest:raise ValueError('A frozen original, request, or reading changed: '+name)
    request=read(BASE/'independent-reading-request.json');author=read(BASE/'author-readings-frozen.json')
    reader=read(BASE/'independent-reader-frozen.json')
    if reader['author_pixel_values_or_fits_read'] is not False:raise ValueError('The source reader was not independent.')
    if source['agreement_tolerance_px']!=4 or source['source_pixel_adjustments_after_independent_reading']!=0:
        raise ValueError('Frozen pixels and gate must not be tuned to acceptance.')
    prior=read(BASE/'prior-landmark-references.json');output=copy.deepcopy(prior);comparisons=[];excluded_aliases=[]
    if set(request)!=set(author['maps']) or set(request)!=set(reader['maps']):raise ValueError('Frozen map identities disagree.')
    for sid,expected in request.items():
        stage=battle_data()['stages'][sid];image=stage['image'];raw=(DATA/image['file']).read_bytes()
        if expected['source_image']!=image or expected['source_level']!=stage['level_source']:raise ValueError('Request source identity changed.')
        if hashlib.sha256(raw).hexdigest()!=image['sha256'] or len(raw)!=image['bytes']:raise ValueError('The exact bitmap bytes changed.')
        if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=image['source_blob_sha1']:raise ValueError('The source bitmap blob changed.')
        level=BASE/('level_rogue6_'+sid.removeprefix('ro6_n_').replace('_','-')+'.json')
        if sha(level)!=stage['level_source']['sha256'] or level.stat().st_size!=stage['level_source']['bytes']:raise ValueError('The full pinned level changed.')
        primary=read(level)['mapData']
        if primary['map']!=stage['map'] or primary['tiles']!=stage['tiles']:raise ValueError('Cells no longer match the original logical grid.')
        if reader['maps'][sid]['source_sha256']!=image['sha256']:raise ValueError('The reader did not read this exact bitmap.')
        expected_cells=[tuple(v) for v in expected['requested_display_zero_based_cells']]
        first=author['maps'][sid]['points'];second=reader['maps'][sid]['points']
        if [(v['row'],v['col']) for v in first]!=expected_cells:raise ValueError('Author requested cells changed.')
        peer={(v['row'],v['col']):v for v in second}
        if len(peer)!=len(expected_cells) or set(peer)!=set(expected_cells):raise ValueError('Reader requested cells changed.')
        points=[]
        for observation in first:
            row,col=observation['row'],observation['col'];pixel=observation['pixel'];other=peer[(row,col)].get('pixel')
            tile=stage['tiles'][stage['map'][row][col]]
            if tile['tileKey']!='tile_floor' or tile['heightType']!='LOWLAND':raise ValueError('The observed surface is outside the declared floor scope.')
            known=finite_pair(pixel) and finite_pair(other)
            if known and not all(0<=pair[0]<image['width'] and 0<=pair[1]<image['height'] for pair in (pixel,other)):
                raise ValueError('A source pixel is outside the exact original bitmap.')
            distance=math.dist(pixel,other) if known else None;accepted=known and distance<=4
            result={'reference':sid,'row':row,'col':col,'observed_pixel':copy.deepcopy(pixel),
                'independent_pixel':copy.deepcopy(other),'agreement_px':distance,'accepted_for_runtime':accepted,
                'reason':'independent approximate observations agree' if accepted else 'unknown visual observation' if not known else 'independent observations disagree beyond4px'}
            comparisons.append(result)
            if accepted:points.append({k:copy.deepcopy(v) for k,v in result.items() if k not in ('reference','accepted_for_runtime','reason')})
        if not points:continue
        if sid in output['references']:raise ValueError('This source has already been delivered; do not count it again.')
        output['references'][sid]={'rows':len(stage['map']),'cols':len(stage['map'][0]),'width':image['width'],'height':image['height'],
            'bitmap_sha256':image['sha256'],'grid_sha256':grid_digest(stage),'agreement_tolerance_px':4,
            'scope':'Only these independently concordant nominal floor centers. Absolute bitmap/actual combat accuracy unverified.','points':points}
        for alias in (sid,sid.replace('ro6_n_','ro6_e_',1)):
            bound=battle_data()['stages'][alias];alias_image=bound['image'];alias_raw=(DATA/alias_image['file']).read_bytes()
            if any(alias_image[k]!=image[k] for k in ('sha256','source_blob_sha1','bytes','width','height')):
                excluded_aliases.append({'id':alias,'original_bitmap_sha256':alias_image['sha256'],
                    'observed_bitmap_sha256':image['sha256'],'reason':'different exact bitmap; no independent pixel reading for this alias',
                    'accepted_for_runtime':False});continue
            if hashlib.sha256(alias_raw).hexdigest()!=alias_image['sha256'] or len(alias_raw)!=alias_image['bytes']:raise ValueError('Alias exact original bytes differ.')
            if hashlib.sha1(b'blob '+str(len(alias_raw)).encode()+b'\0'+alias_raw).hexdigest()!=alias_image['source_blob_sha1']:raise ValueError('Alias source blob differs.')
            if bound['level_source']!=stage['level_source'] or grid_digest(bound)!=grid_digest(stage):raise ValueError('Alias original level/grid differs.')
            output['stages'][alias]={'reference':sid,'image_file':alias_image['file'],'level_sha256':bound['level_source']['sha256']}
    packs=output['source'].setdefault('additional_source_packs',[])
    if 'research/p3-direct-ground-expanded' not in packs:packs.append('research/p3-direct-ground-expanded')
    regular=read(DATA/'battle-map-projections.json');old_regular=read(BASE/'prior-regular-projections.json')
    for group in ('calibrations','stages'):
        for key,value in old_regular[group].items():
            if regular[group].get(key)!=value:raise ValueError('A regular original plane reference changed.')
    receipt={'status':'PASS_PARTIAL_DIRECT_CENTER_EXTENSION_ONLY','new_requested_points':len(comparisons),
        'new_accepted_points':sum(v['accepted_for_runtime'] for v in comparisons),'new_rejected_or_unknown_points':sum(not v['accepted_for_runtime'] for v in comparisons),
        'new_partial_images':len(output['references'])-len(prior['references']),'new_partial_stage_bindings':len(output['stages'])-len(prior['stages']),
        'new_agreement_comparisons':comparisons,'excluded_aliases':excluded_aliases,'prior_partial_points':sum(len(v['points']) for v in prior['references'].values()),
        'total_partial_points':sum(len(v['points']) for v in output['references'].values()),'total_partial_images':len(output['references']),
        'total_partial_stage_bindings':len(output['stages']),'regular_images_at_baseline':len(old_regular['calibrations']),
        'regular_stage_bindings_at_baseline':len(old_regular['stages']),'complete_calibration_added':0,
        'absolute_position_accuracy_verified':False,'extrapolation':False,'inverse_cell_assignment':False,'checkpoint_connections':False,
        'game_actions':0,'chat_requests':0,'live_samples':0,
        'output_sha256':hashlib.sha256(json.dumps(output,ensure_ascii=False,indent=2).encode('utf-8')).hexdigest()}
    if write:
        OUTPUT.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
        (BASE/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return output,receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args();_,r=build(write=args.write)
    print(json.dumps({k:v for k,v in r.items() if k!='new_agreement_comparisons'},ensure_ascii=False))
