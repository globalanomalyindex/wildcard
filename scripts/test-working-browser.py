#!/usr/bin/env python3
"""Recorded working-solutions viewer regression through pinned Playwright CLI.

Run: python3 scripts/test-working-browser.py [--browsers chromium firefox webkit]
Needs the requested installed browser. Uses the same pins as test-browser.py.
No model calls, generated program execution, or writes to study data.
"""
import argparse
import functools
import hashlib
import http.server
import json
import pathlib
import subprocess
import sys
import threading
import time
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ['npx', '--yes', '--package=@playwright/cli@0.1.21', 'playwright-cli']
STABLE_WEBKIT = ['npx', '--yes', '--package=playwright@1.63.0']


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browsers', nargs='+', choices=['chromium', 'firefox', 'webkit'], default=['chromium'])
    parser.add_argument('--output', type=pathlib.Path, default=ROOT/'output/playwright/working-regression')
    parser.add_argument('--focus-only', action='store_true', help='Run only the focused skip-link regression')
    args = parser.parse_args()
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    files = [ROOT/'site/data/working-solutions.json'] + sorted((ROOT/'site/data/working-solutions').glob('*.json'))
    if len(files)<2 or not files[0].is_file():
        parser.error('Recorded working-solutions summary and task archives are required')
    hashes = lambda: {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    before = hashes()
    handler = functools.partial(QuietHandler, directory=str(ROOT/'site'))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    code = (ROOT/'scripts/working-browser-regression.js').read_text()
    summaries = []; failed = False
    try:
        for browser in args.browsers:
            directory = output/browser; directory.mkdir(exist_ok=True)
            session = 'working-regression-'+uuid.uuid4().hex[:12]
            command = CLI+['--json', '-s='+session]
            def run(*parts, timeout=180):
                proc = subprocess.run(command+list(parts), cwd=directory, text=True, capture_output=True, timeout=timeout)
                (directory/(parts[0]+'.log')).write_text(proc.stdout+proc.stderr)
                if proc.returncode:
                    raise RuntimeError(f'{parts[0]} failed: {proc.stdout[-1500:]} {proc.stderr[-1000:]}')
                raw = json.loads(proc.stdout)
                if raw.get('isError'): raise RuntimeError(raw.get('error', str(raw)))
                return raw
            started = time.monotonic()
            try:
                options = dict(base=base,browser=browser,output=str(directory),focusOnly=args.focus_only)
                if browser=='webkit':
                    binary = subprocess.check_output(STABLE_WEBKIT+['--call','command -v playwright'],text=True).strip()
                    path = directory/'options.json'; path.write_text(json.dumps(options))
                    proc = subprocess.run(['node',str(ROOT/'scripts/test-working-webkit.mjs'),str(pathlib.Path(binary).resolve()),str(path)],cwd=directory,text=True,capture_output=True,timeout=180)
                    (directory/'direct-run.log').write_text(proc.stdout+proc.stderr)
                    if proc.returncode: raise RuntimeError(proc.stderr[-2500:])
                    result = json.loads(proc.stdout)
                else:
                    open_args = ['open',base+'/working-solutions/']
                    if browser!='chromium': open_args += ['--browser',browser]
                    run(*open_args); run('snapshot')
                    raw=run('run-code',code.replace('__WORKING_OPTIONS__',json.dumps(options)))
                    result=json.loads(raw['result'])
                result['elapsedSeconds']=round(time.monotonic()-started,2)
                summaries.append(result)
                (directory/'result.json').write_text(json.dumps(result,indent=2)+'\n')
                if not result.get('passed'): failed=True
                print(f"{'PASS' if result.get('passed') else 'FAIL'} {browser}: {result['traceChoices']} trace selections, {len(result['checks'])} checks; {result.get('failures',[])}",flush=True)
            except Exception as error:
                failed=True;summaries.append(dict(browser=browser,passed=False,error=str(error)))
                print(f'FAIL {browser}: {error}',file=sys.stderr,flush=True)
            finally:
                if browser!='webkit':
                    try: run('close',timeout=20)
                    except Exception: pass
    finally:
        server.shutdown();server.server_close()
    stable=before==hashes()
    if not stable: failed=True
    report=dict(passed=not failed,recordedDataUnchanged=stable,dataHashes=before,browsers=summaries)
    (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    return int(failed)


if __name__=='__main__':
    sys.exit(main())
