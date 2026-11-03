from pathlib import Path
from collections import Counter
import json,sys
R=Path.cwd();sys.path.insert(0,str(R));from rouge.relic_recognition import prepared_templates
items=prepared_templates(900);masks=Counter((a[4].shape,a[4].dtype.str,a[4].tobytes())for a in items);report={'height':900,'references':len(items),'exact_unique_masks':len(masks),'duplicate_mask_occurrences':sum(n-1 for n in masks.values()),'largest_shared_groups':sorted(masks.values(),reverse=True)[:12],'no_reference_or_image_data_copied':True};(R/'verification/maintenance/mechanism-focus-20261101/mask-census.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))
