"""Собирает whitelabelexpo.html (зашифрованная страница лидов выставки).
Запуск: WLE_PASSWORD=... python3 tools/wle_build.py LEADS.json LETTERS.json STAGES.json DAILY.json OUT.html
Входные файлы: ответы Google Sheets get_values (как есть, JSON с ключом values) таблицы
«Whitelabelexpo — лиды выставки» (1DpJ1WcnEf3NglBjcD0oUXSuKX9z4l3PoHp2Dil28C_U):
  LEADS   = 'Лиды выставки'!A1:R200
  LETTERS = 'Письма и действия'!A1:J5000
  STAGES  = 'История стадий'!A1:C5000
  DAILY   = 'История по дням'!A1:M200
Пароль в репозитории не хранится."""
import sys, os, json, re, base64
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
T = os.path.dirname(os.path.abspath(__file__))
fl, fe, fs, fd, out = sys.argv[1:6]
rows = lambda f: json.load(open(f, encoding='utf-8'))['values'][1:]
dt = lambda s: datetime.strptime(s, '%d.%m.%Y %H:%M') if ' ' in s else datetime.strptime(s, '%d.%m.%Y')
pad = lambda r, n: list(r) + [''] * (n - len(r))
leads = []
for r in rows(fl):
    r = pad(r, 18)
    if not r[0]: continue
    leads.append(dict(id=r[0], contact=r[1], email=r[3], entry=r[4], resp=r[6], stage=r[7], dN=r[9], dK=r[10], dG=r[11],
                      dY=r[12], last=r[13], did=r[14], days=int(r[15] or 0), qual=r[16], url=r[8]))
ids = {l['id'] for l in leads}
let = {}
for r in rows(fe):
    r = pad(r, 10)
    if r[0] not in ids: continue
    let.setdefault(r[0], []).append(dict(d=r[1], t=r[2], s=r[3], x=r[4], a=r[5], f=r[6], to=r[7], cc=r[8]))
for k in let: let[k].sort(key=lambda e: dt(e['d']))
hist = {}
for r in rows(fs):
    r = pad(r, 3)
    if r[0] not in ids or re.match(r'^C\d+:', r[2]) or not r[2]: continue  # технические коды стадий пропускаем
    hist.setdefault(r[0], []).append((dt(r[1]), r[2]))
trans = []
for i, h in hist.items():
    h.sort(key=lambda x: x[0]); prev = None
    for d, s in h:
        if s == prev: continue
        trans.append(dict(id=i, d=d.strftime('%d.%m.%Y %H:%M'), frm=prev, to=s)); prev = s
trans.sort(key=lambda t: dt(t['d']), reverse=True)
daily = [pad(r, 13) for r in rows(fd) if r and r[0]]
last = daily[-1]
mg = {}
for l in leads:
    m = mg.setdefault(l['resp'], dict(n=0, st={}, out=0, inn=0, last=''))
    m['n'] += 1; m['st'][l['stage']] = m['st'].get(l['stage'], 0) + 1
    if l['last'] and (not m['last'] or dt(l['last']) > dt(m['last'])): m['last'] = l['last']
    for e in let.get(l['id'], []):
        if e['t'] == 'Письмо исходящее': m['out'] += 1
        if e['t'] == 'Письмо входящее': m['inn'] += 1
ysell = sum(1 for l in leads if l['stage'] == 'Подключение к YSELL' or l['dY'])
print('лидов', len(leads), 'писем исх/вх', sum(m['out'] for m in mg.values()), sum(m['inn'] for m in mg.values()),
      'по таблице', last[11], last[12], 'ysell', ysell, 'срез', last[0])
logo = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(T, 'logo.png'), 'rb').read()).decode()
data = dict(leads=leads, letters=let, trans=trans, daily=daily, mg=mg, ysell=ysell, asof=last[0], logo=logo)
js = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
html = open(os.path.join(T, 'wle_tpl.html'), encoding='utf-8').read().replace('/*DATA*/null', js)
if '<meta name="robots"' not in html: html = html.replace('<head>', '<head><meta name="robots" content="noindex">', 1)
b64 = lambda x: base64.b64encode(x).decode()
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=250000).derive(os.environ['WLE_PASSWORD'].encode())
ent = [[b64(salt), b64(iv), b64(AESGCM(key).encrypt(iv, html.encode('utf-8'), None))]]
w = open(os.path.join(T, 'wrapper.html'), encoding='utf-8').read().replace('%%TITLE%%', 'Лиды Whitelabelexpo').replace('%%LOGO%%', b64(open(os.path.join(T, 'logo.png'), 'rb').read())).replace('%%ENTRIES%%', json.dumps(ent))
open(out, 'w', encoding='utf-8').write(w); print('whitelabelexpo.html', len(w))
