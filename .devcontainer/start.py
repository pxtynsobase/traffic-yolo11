"""Start one background server when the Codespace starts or resumes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PORT = 8050


def running():
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/api/health', timeout=2) as response:
            return json.load(response).get('service') == 'traffic-flow'
    except (OSError, ValueError):
        return False


def main():
    if running():
        print('Traffic Flow is already running on port 8050.')
        return
    (ROOT / '.runtime').mkdir(exist_ok=True)
    with (ROOT / '.runtime' / 'server.log').open('a') as output:
        process = subprocess.Popen(
            [sys.executable, '-m', 'gunicorn', 'app:app', '--bind', f'0.0.0.0:{PORT}',
             '--workers', '1', '--threads', '2', '--timeout', '120', '--access-logfile', '-'],
            cwd=ROOT, env=os.environ.copy(), stdout=output, stderr=subprocess.STDOUT,
            start_new_session=True)
    for _ in range(120):
        if running():
            print('Traffic Flow is running. Open port 8050 in the Ports panel.')
            return
        if process.poll() is not None:
            break
        time.sleep(0.25)
    raise SystemExit('Server startup failed. Read .runtime/server.log for details.')


if __name__ == '__main__':
    main()
