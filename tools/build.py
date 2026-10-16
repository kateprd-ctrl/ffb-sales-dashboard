"""Собирает index.html и daily.html (зашифрованные паролем).
python3 tools/build.py DATA_JSON OUT_DIR   (пароль в переменной окружения PAGE_PASSWORD)"""
import sys, os, json, re, gzip, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
T = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
pw = os.environ['PAGE_PASSWORD']
rd = lambda n: open(os.path.join(T, n), encoding='utf-8').read()
tokens = rd('tokens.css')
FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"><script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>'
def split(src):
    css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
    return css, src[src.find('</style>') + 8:]
def page(src, title, link_from, link_to, shim, rawjson, extra=''):
    css, body = split(src)
    body = body.replace(link_from, link_to).replace(' target="_blank" rel="noopener"', '')
    html = '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + title + '</title>' + FONT + '<style>' + tokens + css + '</style></head><body><div id="dash-root">' + body
    first = html.find('<script>', html.find('<div id="dash-root">'))
    inject = '<script>window.__RAW=' + rawjson + ';' + extra + '</script><script>' + rd(shim) + '</script>'
    return html[:first] + inject + html[first:] + '</div></body></html>'
v = lambda k: {'values': data[k]}
raw_m = {k: v(k) for k in ['acts', 'deals_detail', 'hist', 'plan', 'hist_kpi', 'money']}
m = page(rd('monthly_src.html'), 'SALES DEPARTMENT', 'https://claude.ai/artifact/NoG7PGVVzZTBpeKUdtLWSA', 'daily.html', 'shim_m.js', json.dumps(raw_m, ensure_ascii=False, separators=(',', ':')))
m = m.replace('<h1>SALES DEPARTMENT <span>по месяцам</span></h1>', '<h1>SALES DEPARTMENT</h1>')
raw_d = {k: v(k) for k in ['acts', 'deals_detail', 'svod']}
gz = base64.b64encode(gzip.compress(json.dumps(data['days'], ensure_ascii=False, separators=(',', ':')).encode(), 9)).decode()
d = page(rd('daily_src.html'), 'SALES DEPARTMENT — по дням', 'https://claude.ai/artifact/KWcKFfGbWZdPn5weFKwKFe', 'index.html', 'shim_d.js', json.dumps(raw_d, ensure_ascii=False, separators=(',', ':')), 'window.__DAYS_GZ="' + gz + '";')
b64 = lambda x: base64.b64encode(x).decode()
logo = b64(open(os.path.join(T, 'logo.png'), 'rb').read())
WRAP = rd('wrapper.html')
def enc(html, title, dst):
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=250000).derive(pw.encode())
    ct = AESGCM(key).encrypt(iv, html.encode('utf-8'), None)
    w = WRAP.replace('%%TITLE%%', title).replace('%%LOGO%%', logo).replace('%%SALT%%', b64(salt)).replace('%%IV%%', b64(iv)).replace('%%CT%%', b64(ct))
    open(os.path.join(out, dst), 'w', encoding='utf-8').write(w); print(dst, len(w))
enc(m, 'SALES DEPARTMENT', 'index.html')
enc(d, 'SALES DEPARTMENT — по дням', 'daily.html')
