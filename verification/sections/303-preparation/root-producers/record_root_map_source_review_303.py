from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
record={'section':303,'kind':'root_source_image_and_frozen_reading_review_not_third_independent_measurement',
 'at_utc':datetime.now(timezone.utc).isoformat(),'view_image_original_actually_used_for_both':True,
 'original_images':{n:sha256((ROOT/n).read_bytes()).hexdigest() for n in ('rouge/data/battle-maps/ro6_b_6.png','rouge/data/battle-maps/ro6_n_2_3.png')},
 'root_independent_comparison':{'sha256':sha256((ROOT/'.cache/p3-303-root/first-reading-comparison.json').read_bytes()).hexdigest(),'requests':89,'accepted':49,'rejected_or_unknown':40},
 'observations':['The fixed 畸症 image has raised structures, occluded edges and distinct floor/road areas; it does not establish a full ground plane.',
  'The fixed 本性难移 image includes continuous wood textures without independently discernible cell boundaries; unknown road centers remain excluded.',
  'Root reviewed source identity and representative accepted logical-to-bitmap correspondence after both first raw readings were frozen; no new coordinate set was produced.',
  'Two independent model readers are not humans or actual game observers; 4px agreement is consistency evidence, not absolute game-position accuracy.'],
 'source_pixel_adjustment_or_averaging':False,'third_independent_coordinate_measurement_claimed':False,
 'game_sample_or_actual_position_certified':False}
base=ROOT/'verification/sections/303-preparation';target=base/'root-source-visual-review.json';assert not target.exists()
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
public_comparison=base/'root-independent-reading-comparison.json';assert not public_comparison.exists();public_comparison.write_bytes((ROOT/'.cache/p3-303-root/first-reading-comparison.json').read_bytes())
print(json.dumps({'source_images_actually_reviewed':2,'all89_comparisons_preserved_publicly':True,'new_independent_coordinates_by_root':False}))
