"""Use the pinned file-only CFG extractor, writing only to this batch."""
from pathlib import Path
source=Path(__file__).resolve().parent.parent/'p1-native-cost-054/extract_cfg.py'
code=source.read_text(encoding='utf-8').replace("helpers=BASE/'helper-map.json'", "helpers=RESEARCH/'p1-native-cost-054/helper-map.json'")
exec(compile(code,str(source),'exec'))
