#!/usr/bin/env python3
"""CLI-first browser regression check. No model calls, external writes, or mock study data.

Install: npx --yes --package=@playwright/cli@0.1.21 playwright-cli install-browser chromium --with-deps
WebKit: npx --yes --package=playwright@1.63.0 playwright install webkit --with-deps
Run: python3 scripts/test-browser.py [--browsers chromium firefox webkit]
Each requested browser must be installed; unavailable browsers fail rather than silently skip.
"""
import argparse
import functools
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
    parser.add_argument('--output', type=pathlib.Path, default=ROOT/'output'/'playwright'/'regression')
    args = parser.parse_args()
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(QuietHandler, directory=str(ROOT/'site'))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    seed = "O'Brien $(printf literal) `printf literal`\nλ"
    receipt = json.loads(subprocess.check_output(['bash', str(ROOT/'plugin/scripts/draw.sh'), '--seed', seed, '--json'], text=True))
    code_template = (ROOT/'scripts/browser-regression.js').read_text()
    summaries = []; failed = False
    try:
        for browser in args.browsers:
            session = 'wildcard-regression-'+uuid.uuid4().hex[:12]
            directory = output/browser; directory.mkdir(exist_ok=True)
            command = CLI+['--json', '-s='+session]
            def run(*parts, timeout=90):
                process = subprocess.run(command+list(parts), cwd=directory, text=True, capture_output=True, timeout=timeout)
                (directory/(parts[0]+'.log')).write_text(process.stdout+process.stderr)
                if process.returncode:
                    raise RuntimeError(f'{parts[0]} failed: {process.stdout[-2500:]} {process.stderr[-1000:]}')
                result = json.loads(process.stdout)
                if result.get('isError'):
                    raise RuntimeError(result.get('error', str(result)))
                return result
            started = time.monotonic()
            try:
                options = dict(base=base, browser=browser, output=str(directory), seed=seed,
                               expectedReceipt=receipt, hasStudy=(ROOT/'site/data/transfer-study.json').is_file())
                if browser == 'webkit':
                    # CLI 0.1.21 bundles an alpha WebKit that applies CSP to native
                    # select styles. Stable 1.63.0 does not reproduce that defect.
                    # Resolve the explicitly pinned stable package, never a float.
                    binary = subprocess.check_output(STABLE_WEBKIT+['--call', 'command -v playwright'], text=True).strip()
                    options_path = directory/'options.json'; options_path.write_text(json.dumps(options))
                    direct = subprocess.run(['node', str(ROOT/'scripts/test-webkit.mjs'), str(pathlib.Path(binary).resolve()), str(options_path)],
                                            cwd=directory, text=True, capture_output=True, timeout=90)
                    (directory/'direct-run.log').write_text(direct.stdout+direct.stderr)
                    if direct.returncode: raise RuntimeError(direct.stderr[-3500:])
                    result = json.loads(direct.stdout)
                else:
                    open_args = ['open', base+'/?seed=42&sampler=sha256-counter-v2']
                    if browser != 'chromium': open_args += ['--browser', browser]
                    run(*open_args)
                    # A fresh accessible snapshot grounds the following DOM probes in the actual UI.
                    run('snapshot')
                    raw = run('run-code', code_template.replace('__REGRESSION_OPTIONS__', json.dumps(options)))
                    result = json.loads(raw['result'])
                if not result.get('passed'):
                    raise RuntimeError('Browser probe did not return a passing result')
                result['elapsedSeconds'] = round(time.monotonic()-started, 2)
                (directory/'result.json').write_text(json.dumps(result, indent=2)+'\n')
                summaries.append(result)
                print(f"PASS {browser} {result['version']}: {len(result['checks'])} checks, {result['study']}, {result['elapsedSeconds']}s", flush=True)
            except Exception as error:
                failed = True
                summary = dict(browser=browser, passed=False, error=str(error))
                summaries.append(summary)
                print(f'FAIL {browser}: {error}', file=sys.stderr, flush=True)
                try: run('screenshot', timeout=20)
                except Exception: pass
            finally:
                try: run('close', timeout=20)
                except Exception: pass
    finally:
        server.shutdown(); server.server_close()
    (output/'summary.json').write_text(json.dumps(summaries, indent=2)+'\n')
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
