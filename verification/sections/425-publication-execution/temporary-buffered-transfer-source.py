"""Retry the exact authorized HEAD with temporary verified TLS and buffered HTTP.

The previous RPC explicitly requested a rewind and failed with curl 65. Raising
postBuffer is a transfer experiment, not proof of a TLS root cause or a general
speed improvement. No persistent Git, proxy, DNS, or credential settings change.
Git reference: https://git-scm.com/docs/git-config#Documentation/git-config.txt-httppostBuffer
"""
from pathlib import Path
import os, subprocess, sys
R = Path(__file__).resolve().parents[1]
environment = dict(os.environ)
temporary = {
    'http.proxy': '',
    'http.version': 'HTTP/1.1',
    'http.sslBackend': 'schannel',
    'http.curloptResolve': 'github.com:443:20.27.177.113',
    'http.postBuffer': str(256 * 1024 * 1024),
    'http.sslVerify': 'true',
}
environment['GIT_CONFIG_COUNT'] = str(len(temporary))
for i, (key, value) in enumerate(temporary.items()):
    environment[f'GIT_CONFIG_KEY_{i}'] = key
    environment[f'GIT_CONFIG_VALUE_{i}'] = value
environment.update(GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
raise SystemExit(subprocess.call(
    [sys.executable, '-B', '-X', 'utf8', *sys.argv[1:]],
    cwd=R, env=environment))
