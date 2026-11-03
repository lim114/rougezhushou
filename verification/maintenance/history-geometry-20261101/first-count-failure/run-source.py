from pathlib import Path
from hashlib import sha256
import subprocess,sys,json
R=Path.cwd();out=R/'verification/maintenance/history-geometry-20261101/first-count-failure';out.mkdir(exist_ok=False)
selectors=['tests.test_history_statistics_layout_review.HistoryStatisticsLayoutReview.test_repeated_confirmed_kettles_are_a_complete_statistical_sample','tests.test_history_statistics_layout_review.HistoryStatisticsLayoutReview.test_holding_rate_and_its_exact_sample_rows_share_repeated_count']
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8','-m','unittest','-v',*selectors],stdout=a,stderr=b,cwd=R);code=child.wait()
(out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code,'selectors':selectors,'source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in['rouge/player_personal_statistics.py','tests/test_history_statistics_layout_review.py']},'earlier_terminal_exit1_also_observed':True,'not_counted_twice':True},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});assert code==1
