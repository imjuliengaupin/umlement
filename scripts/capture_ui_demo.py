from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('UMLEMENT_CAPTURE_OUT', str(BASE_DIR / 'demo' / 'images' / 'ui-demo.png')))
PORT = int(os.environ.get('UMLEMENT_UI_PORT', '5011'))
URL = f'http://127.0.0.1:{PORT}'
CAPTURE_PATH = os.environ.get('UMLEMENT_CAPTURE_PATH')
CAPTURE_FIT_MODE = os.environ.get('UMLEMENT_CAPTURE_FIT_MODE', 'width')
CAPTURE_THEME = os.environ.get('UMLEMENT_CAPTURE_THEME', 'dark')


def wait_for_server(url: str, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(url) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f'Server did not become ready at {url}')


def main() -> None:
    env = os.environ.copy()
    env['UMLEMENT_UI_PORT'] = str(PORT)
    server = subprocess.Popen(
        [str(BASE_DIR / '.venv' / 'bin' / 'python'), 'ui_app.py'],
        cwd=BASE_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_server(URL)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 1480}, device_scale_factor=1)
            page.goto(URL, wait_until='networkidle')
            if CAPTURE_THEME == 'light':
                page.locator('#themeToggle').click()
                page.wait_for_timeout(150)
            if CAPTURE_PATH:
                path_input = page.locator('#path')
                path_input.fill(CAPTURE_PATH)
            else:
                page.get_by_text('Load Demo Project').click()
            page.get_by_role('button', name='Generate').click()
            page.wait_for_timeout(2500)
            if CAPTURE_FIT_MODE == 'full':
                page.locator('#fitModeButton').click()
                page.wait_for_timeout(250)
            page.get_by_role('button', name='−').click()
            page.wait_for_timeout(200)
            page.get_by_role('button', name='−').click()
            page.wait_for_timeout(200)
            page.locator('.wrap').screenshot(path=str(OUT))
            browser.close()
        print(OUT)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


if __name__ == '__main__':
    main()
