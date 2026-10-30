import sys, runpy, os
from playwright.sync_api._generated import BrowserType, Browser
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs')
LIBS = {
    'react.production.min.js': L + '/react-18.3.1/package/umd/react.production.min.js',
    'react-dom.production.min.js': L + '/react-dom-18.3.1/package/umd/react-dom.production.min.js',
    'htm.umd.js': L + '/htm-3.1.1/package/dist/htm.umd.js',
    'lucide.min.js': L + '/lucide-0.460.0/package/dist/umd/lucide.min.js',
}
EXT = []
def handle(route):
    u = route.request.url
    for k, f in LIBS.items():
        if u.endswith('/' + k):
            return route.fulfill(status=200, content_type='application/javascript', body=open(f, encoding='utf-8').read())
    if 'cdn.tailwindcss.com' in u:
        return route.fulfill(status=200, content_type='application/javascript', body='window.tailwind={config:{}};')
    EXT.append(u)
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
import atexit
atexit.register(lambda: print('EXTERNAL_ABORTED', len(EXT), sorted(set(u.split('/')[2] for u in EXT))))
script = sys.argv[1]; sys.argv = sys.argv[1:]
runpy.run_path(script, run_name='__main__')
