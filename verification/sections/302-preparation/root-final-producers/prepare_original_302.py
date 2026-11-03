from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
native_path=ROOT/'verification/sections/302-window-attempt1/actual/window.json'
native=json.loads(native_path.read_bytes());assert native['passed'] and native['screenshot_count']==5
for name in ('restart_window','focus_window'):
    target=ROOT/f'.cache/{name}_302.py';assert not target.exists()
    source=(ROOT/f'.cache/{name}_301.py').read_text(encoding='utf8').replace('301','302')
    if name=='restart_window':
        source=source.replace('2952052, 37860','2753884, 35808').replace('len(expected_sources) == 52','len(expected_sources) == '+str(len(native['source_sha256_after'])))
        source=source.replace('302-necessary-final/process.json','302-necessary-first/process.json')
    target.write_text(source,encoding='utf8')
images={}
for row in native['screenshots']:
    path=native_path.with_name(Path(row['path']).name)
    assert sha256(path.read_bytes()).hexdigest()==row['sha256']
    images[path.relative_to(ROOT).as_posix()]=row['sha256']
review={'section':302,'kind':'root_archived_native_images_review','actual_images_opened_with_view_image':True,
 'actual_image_count':5,'images':images,'at_utc':datetime.now(timezone.utc).isoformat(),
 'observations':['Root directly viewed all five archived actual native PNGs.',
  'Three separate effect pages visibly show the correct required item, alternative private key and conditional effect, including first-release limitation.',
  'The damage-reduction page explicitly distinguishes narrative wording from immunity; private key is not all three requirements at once.',
  'The independent related map shows 畸症 and the exact boss image; uncalibrated original-map projection and actual enemy results remain unknown.',
  'Unavailable-source page has no old effect or selection and disables related battle entry.'],
 'actual_reward_or_gameplay_or_weakening_activation_verified':False}
target=ROOT/'verification/sections/302-preparation/root-visual-review.json';assert not target.exists()
target.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
transport={'section':302,'kind':'root_tool_transport_timeout_summary_not_native_failure',
 'tool':'Windows-mcp PowerShell','requested_timeout_seconds':20,'actual_tool_response':'Command execution timed out; Status Code:1',
 'native_runner_was_not_restarted':True,
 'resolved_by':'Read existing owned runner stdout/process/window artifacts and narrow process inventory; owned runner completed actual0, Qt0/job empty, no matching live verification process.',
 'original_stdout':'.cache/p3-302-native-window/root-launch/stdout.txt','original_stderr':'.cache/p3-302-native-window/root-launch/stderr.txt',
 'raw_tool_response_log_claimed':False}
(ROOT/'verification/sections/302-preparation/root-native-launch-transport.json').write_text(json.dumps(transport,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_count':len(native['source_sha256_after']),'actual_images_reviewed':5,'restart_and_focus_prepared_not_executed':True}))
