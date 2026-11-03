"""Bounded author tests on external immutable packages, not root checks."""
import json
import subprocess
import sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
PYTHON='/workspace/rougezhushou/.venv/bin/python'
RELATED=['tests.test_target_count_input_types','tests.test_orchid_arrow_reference',
         'tests.test_xiangzi_notes_reference','tests.test_gnosis_target_lifetime',
         'tests.test_deployment_independent_sources','tests.test_mizuki_talent_identity',
         'tests.test_wisdel_ghost_clock','tests.test_damage','tests.test_report']


def main():
    package=sys.argv[1];assert package in ('baseline','draft')
    modules=RELATED+(['tests.test_remaining_boolean_condition_text_input'] if package=='draft' else [])
    log=OUT/(package+'-related.log')
    with log.open('xb') as f:
        result=subprocess.run([PYTHON,'-m','unittest',*modules,'-v'],cwd=OUT/package,stdout=f,stderr=subprocess.STDOUT)
    print(json.dumps({'package':package,'exit_code':result.returncode,'log':str(log),'modules':modules}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
