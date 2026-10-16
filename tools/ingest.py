"""Разбирает сохранённые ответы Google Sheets (get_values / get_spreadsheet) и раскладывает по ролям.
Использование: python3 tools/ingest.py OUT_DIR file1 file2 ...
Роли определяются по заголовкам листа, имена файлов не важны."""
import sys, json, os, re
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
data = {'days': {}}
def kind_of(rows):
    r0 = rows[0] if rows else []
    h = [str(x) for x in r0]
    first = h[0] if h else ''
    if first.startswith('Воронка «FF-Box главная»'):
        m = re.search(r'(\d{2}\.\d{2}\.\d{4})', first); return ('day', m.group(1) if m else None)
    if h[:3] == ['ID сделки', 'Время', 'Стадия']: return ('hist', None)
    if h[:2] == ['ID дела', 'ID сделки']: return ('acts', None)
    if h[:2] == ['ID сделки', 'Сделка']: return ('deals_detail', None)
    if h[:2] == ['Дата', 'Месяц лидов']: return ('hist_kpi', None)
    if h[:2] == ['Дата', 'В работе, шт']: return ('svod', None)
    if first.startswith('ключ месяца'): return ('plan', None)
    return (None, None)
def add(rows, links=None):
    k, d = kind_of(rows)
    if k == 'day': data['days'][d] = {'rows': rows, 'links': links or {}}
    elif k: data[k] = rows; print('ok', k, len(rows))
    else: print('пропущено: неизвестный лист', rows[:1])
for f in sys.argv[2:]:
    j = json.load(open(f))
    if 'values' in j:
        add(j['values'])
    elif 'sheets' in j:
        for s in j['sheets']:
            rd = ((s.get('data') or [{}])[0]).get('rowData') or []
            rows = [[(c.get('formattedValue') if c else '') or '' for c in (r.get('values') or [])] for r in rd]
            links = {i: r['values'][0].get('hyperlink') for i, r in enumerate(rd) if r.get('values') and r['values'][0] and r['values'][0].get('hyperlink')}
            while rows and all(x == '' for x in rows[-1]): rows.pop()
            add(rows, links)
print('дней:', len(data['days']))
need = ['hist','acts','deals_detail','hist_kpi','svod','plan']
miss = [k for k in need if k not in data]
if miss or not data['days']: print('НЕ ХВАТАЕТ:', miss, 'дней' if not data['days'] else ''); sys.exit(1)
json.dump(data, open(os.path.join(out, 'data.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
