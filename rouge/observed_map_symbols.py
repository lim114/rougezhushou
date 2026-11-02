"""Additional visible symbols for first-floor maps without prior point data."""
from hashlib import sha256
import json
from pathlib import Path
from .expansion_reference import NEW_COMMIT

ROOT=Path(__file__).resolve().parents[1]
DATA='rouge/data/observed-map-symbols.json'
DATA_SHA256='ecc542bfa6fb4a2c548d2c403dc704fdbfbebabaee9988a9aa4f4c4ca8aac6e9'
STAGES=('ro6_n_1_1','ro6_e_1_1','ro6_n_1_2','ro6_e_1_2',
        'ro6_n_1_3','ro6_e_1_3','ro6_n_1_4','ro6_e_1_4')


def mapping_for(stage_id,current):
    """Use a declared stage from an already qualified current battle packet."""
    try:raw=(ROOT/DATA).read_bytes()
    except OSError:return None
    if sha256(raw).hexdigest()!=DATA_SHA256:return None
    data=json.loads(raw)
    if data['game_commit']!=NEW_COMMIT:return None
    row=data['bindings'][stage_id]
    if row['expected_stage']!=current['version']['current']['details']['stages'][stage_id]:return None
    # The owning map reader checks the exact image, level and full geometry.
    return {'mapping':row,'source_identity':DATA_SHA256}
