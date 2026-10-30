# Roda um script Playwright (Python) no sandbox da nuvem: Chromium pré-instalado, CDNs servidos de cópias locais do npm.
# uso: python3 run_sandbox.py <script.py> [args...]   (LIBS=<pasta com react-18.3.1/, react-dom-18.3.1/, htm-3.1.1/, lucide-0.460.0/>)
import sys, runpy, os
from playwright.sync_api._generated import BrowserType, Browser
L = os.environ.get('LIBS', '/tmp/claude-0/-home-user/4e54b5af-4e6e-57af-8b75-cf27fd2fc847/scratchpad/libs')
LIBS = {
    'react.production.min.js': L + '/react-18.3.1/package/umd/react.production.min.js',
    'react-dom.production.min.js': L + '/react-dom-18.3.1/package/umd/react-dom.production.min.js',
    'htm.umd.js': L + '/htm-3.1.1/package/dist/htm.umd.js',
    'lucide.min.js': L + '/lucide-0.460.0/package/dist/umd/lucide.min.js',
}
def handle(route):
    u = route.request.url
    for k, f in LIBS.items():
        if u.endswith('/' + k):
            return route.fulfill(status=200, content_type='application/javascript', body=open(f, encoding='utf-8').read())
    if 'cdn.tailwindcss.com' in u:
        return route.fulfill(status=200, content_type='application/javascript', body='window.tailwind={config:{}};')
    if 'fonts.googleapis.com' in u or 'fonts.gstatic.com' in u:
        return route.fulfill(status=200, content_type='text/css', body='')
    return route.abort()
_o = BrowserType.launch
def launch(self, *a, **k):
    k.setdefault('executable_path', '/opt/pw-browsers/chromium')
    return _o(self, *a, **k)
BrowserType.launch = launch
_np = Browser.new_page
def new_page(self, *a, **k):
    pg = _np(self, *a, **k)
    pg.route(lambda u: not u.startswith('http://127.0.0.1') and not u.startswith('data:') and not u.startswith('blob:'), handle)
    return pg
Browser.new_page = new_page
script = sys.argv[1]; sys.argv = sys.argv[1:]
runpy.run_path(script, run_name='__main__')
