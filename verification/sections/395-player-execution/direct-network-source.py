"""Per-process direct Git HTTPS with normal certificate verification retained."""
from pathlib import Path
import os,subprocess,sys
R=Path(__file__).resolve().parents[1];environment=dict(os.environ)
environment.update(GIT_CONFIG_COUNT='3',GIT_CONFIG_KEY_0='http.proxy',GIT_CONFIG_VALUE_0='',GIT_CONFIG_KEY_1='http.version',GIT_CONFIG_VALUE_1='HTTP/1.1',GIT_CONFIG_KEY_2='http.sslBackend',GIT_CONFIG_VALUE_2='openssl')
probe="import subprocess; result=subprocess.check_output(['git','config','--get','http.proxy']); assert result.strip()==b'', result"
subprocess.run([sys.executable,'-B','-X','utf8','-c',probe],cwd=R,env=environment,check=True)
raise SystemExit(subprocess.call([sys.executable,'-B','-X','utf8',*sys.argv[1:]],cwd=R,env=environment))
