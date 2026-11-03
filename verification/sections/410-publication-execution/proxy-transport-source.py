"""Existing local proxy, scoped to this Git delivery process; TLS remains verified."""
from pathlib import Path
import os,subprocess,sys
R=Path(__file__).resolve().parents[1];environment=dict(os.environ)
environment.update(GIT_CONFIG_COUNT='3',GIT_CONFIG_KEY_0='http.proxy',GIT_CONFIG_VALUE_0='http://127.0.0.1:7890',GIT_CONFIG_KEY_1='http.version',GIT_CONFIG_VALUE_1='HTTP/1.1',GIT_CONFIG_KEY_2='http.sslBackend',GIT_CONFIG_VALUE_2='openssl')
probe="import subprocess; assert subprocess.check_output(['git','config','--get','http.proxy']).strip()==b'http://127.0.0.1:7890'"
subprocess.run([sys.executable,'-B','-X','utf8','-c',probe],cwd=R,env=environment,check=True)
raise SystemExit(subprocess.call([sys.executable,'-B','-X','utf8',*sys.argv[1:]],cwd=R,env=environment))
