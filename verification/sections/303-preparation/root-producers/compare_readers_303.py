from pathlib import Path
from hashlib import sha256
import json,math
ROOT=Path(__file__).resolve().parents[1]
pin={'a':'ccef7dd5a1cf227945a29143dfd41eadc4b39deb412b970850d53f3aab8083e2','b':'03179421fe88573290a2fa342bd856eca8b9ba95d443d8a753ebd216c6701994'}
readers={}
for who,value in pin.items():
    path=ROOT/f'.cache/p3-303-reader-{who}/READINGS.json';raw=path.read_bytes();assert sha256(raw).hexdigest()==value
    packet=json.loads(raw);assert packet['schema']=='section303-independent-fixed-image-readings-v1' and packet['reader']==who.upper()
    assert packet['declarations']=={'other_reader_seen':False,'old_projection_or_landmarks_seen':False,'fit_or_interpolation_used':False,'original_images_modified':False,'coordinates_frozen_in_first_formal_record':True}
    for source in packet['source_pins']['files']:
        body=(ROOT/source['path']).read_bytes();assert len(body)==source['bytes'] and sha256(body).hexdigest()==source['sha256']
    readers[who]={item['stage_id']:item for item in packet['images']};assert len(readers[who])==len(packet['images'])==2
request_path=ROOT/'.cache/p3-303-map-candidates/logical-reader-requests-all-lowland.json'
assert sha256(request_path.read_bytes()).hexdigest()=='c5a5ca22b11b36875c8890e8cce3a1f7d465925c7ddb7320de3963bd0b35854a'
requests=json.loads(request_path.read_bytes());comparisons=[];summary={}
for group in requests['groups']:
    sid=group['stage_id'];indexes={}
    for who in readers:
        image=readers[who][sid]
        assert (image['rows'],image['cols'],image['width'],image['height'],image['image_sha256'])==(group['rows'],group['cols'],*group['image_size'],group['image_sha256'])
        entries=image['readings'];indexes[who]={r['request_id']:r for r in entries}
        assert len(entries)==len(indexes[who])==len(group['requests'])
        assert set(indexes[who])=={r['request_id'] for r in group['requests']}
    records=[]
    for requested in group['requests']:
        pair=[]
        for who in readers:
            entry=indexes[who][requested['request_id']]
            assert all(entry[k]==requested[k] for k in ('request_id','row','col','tile_key'))
            pixel=entry['pixel'];assert entry['reason']
            if pixel is not None:
                assert type(pixel)is list and len(pixel)==2 and all(type(n) in(int,float)and math.isfinite(n) for n in pixel)
                assert 0<=pixel[0]<group['image_size'][0] and 0<=pixel[1]<group['image_size'][1]
            pair.append(pixel)
        distance=math.dist(*pair) if all(p is not None for p in pair) else None
        row={'stage_id':sid,'request_id':requested['request_id'],'row':requested['row'],'col':requested['col'],'tile_key':requested['tile_key'],
             'observed_pixel':pair[0],'independent_pixel':pair[1],'agreement_px':distance,'accepted':distance is not None and distance<=4}
        comparisons.append(row);records.append(row)
    summary[sid]={'requested':len(records),'accepted':sum(r['accepted'] for r in records),'rejected_or_unknown':sum(not r['accepted'] for r in records),
       'either_reader_null':sum(r['agreement_px'] is None for r in records),'distance_over4':sum(r['agreement_px'] is not None and r['agreement_px']>4 for r in records)}
assert len(comparisons)==89
record={'section':303,'kind':'root_independent_comparison_of_two_first_frozen_readings_not_product_acceptance',
 'raw_reading_sha256':pin,'source_request_sha256':sha256(request_path.read_bytes()).hexdigest(),'groups':summary,'comparisons':comparisons,
 'source_pixels_adjusted_averaged_or_dropped':False,'threshold_original_pixels':4,'absolute_game_position_accuracy_verified':False}
target=ROOT/'.cache/p3-303-root/first-reading-comparison.json';assert not target.exists();target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_request_count':89,'groups':summary,'comparison_sha256':sha256(target.read_bytes()).hexdigest(),'accepted_total':sum(r['accepted'] for r in comparisons)}))
