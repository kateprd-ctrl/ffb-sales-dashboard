"""Отдельная страница «Мотивация» (блок 'План KPI'!A13:C28). Без данных по отдельным сотрудникам."""
from html import escape
import re
def num(x):
    if x is None: return None
    s = re.sub(r'[^\d,.\-%]', '', str(x))
    if s == '': return None
    pc = s.endswith('%')
    if pc: s = s[:-1]
    if ',' in s: s = s.replace('.', '').replace(',', '.')
    elif re.fullmatch(r'\d{1,3}(\.\d{3})+', s): s = s.replace('.', '')
    try: n = float(s)
    except ValueError: return None
    return n / 100 if pc else n
def eur(n): return format(round(n), ',').replace(',', ' ') + ' €'
CSS = '''html,body{margin:0;background:#fafafa;color:#111;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
.w{max-width:980px;margin:0 auto;padding:16px}.top{display:flex;align-items:center;gap:14px;margin:8px 0 18px}.top h1{font-size:1.4rem;margin:0}
.m{background:#fff;border:1px solid #ececec;border-radius:24px;box-shadow:0 10px 30px -18px rgba(0,0,0,.22);padding:1.4rem;display:flex;flex-direction:column;gap:.7rem}
.k{color:#d03040;font-weight:700;font-size:.8125rem;letter-spacing:.04em;text-transform:uppercase}h3{margin:0;font-size:1.125rem}
.t{font-weight:800;letter-spacing:-.02em;font-size:clamp(2.2rem,5vw,3.6rem);line-height:1;color:#d03040}
.g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}.g>div{display:flex;flex-direction:column;gap:.3rem;justify-content:space-between}
.g span{font-size:.8125rem;color:#6b7280;line-height:1.25;min-height:2.5em}.g b{font-weight:800;font-size:clamp(1.4rem,2.6vw,2rem);line-height:1;white-space:nowrap}.g small{color:#6b7280;font-size:.8125rem}
.n{color:#6b7280;font-size:.8125rem;margin:0}@media(max-width:560px){.g{grid-template-columns:1fr}}'''
def render(rows, tokens, font, logo):
    by = lambda p: next(({'v': num(r[1] if len(r) > 1 else None), 's': num(r[2] if len(r) > 2 else None)} for r in rows if r and r[0].startswith(p)), {'v': None, 's': None})
    fot, months, pct = by('ФОТ')['v'], by('Месяцев')['v'], by('Премиальный фонд, %')['v']
    fund = by('Премиальный фонд при')['v']
    rop, team, back = by('РОП'), by('Менеджеры — командный'), by('Менеджеры — доплата')
    pm, pd_ = by('Командный бонус на одного')['v'], by('Доплата за одну')['v']
    nm, nd = by('Менеджеров в команде')['v'], by('Ожидаемо возвращённых')['v']
    body = '<div class="k">Что получит отдел</div><h3>Если выполним план, отдел получит</h3>'
    if fund is None:
        body += '<div class="t">—</div><p class="n">Суммы пока не заданы в таблице.</p>'
    else:
        c = lambda l, val, sub: '<div><span>%s</span><b>%s</b><small>%s</small></div>' % (l, eur(val) if val is not None else '—', sub)
        body += '<div class="t">%s</div><div class="g">' % eur(fund)
        body += c('РОП, бонус за период плана', rop['s'], ('%d%% фонда' % round((rop['v'] or 0) * 100)) if rop['v'] is not None else '')
        body += c('Менеджерам, командный бонус за дисциплину', team['s'], ('%s на человека (%d)' % (eur(pm), nm)) if pm is not None and nm else '')
        body += c('Менеджерам, доплата за возвращённых клиентов', back['s'], ('%s за сделку (при %d возвратах)' % (eur(pd_), nd)) if pd_ is not None and nd else '')
        body += '</div>'
        if fot and months and pct is not None:
            body += '<p class="n">Фонд = ФОТ %s × %d мес. × %s%%. Период плана — ноябрь и декабрь вместе. Полная выплата — при 100%% плана; ниже 80%% по блоку премия не платится.</p>' % (eur(fot), months, ('%.1f' % (pct * 100)).rstrip('0').rstrip('.'))
    return '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Мотивация отдела продаж</title><style>' + CSS + '</style></head><body><div class="w"><div class="top"><h1>Мотивация отдела продаж</h1></div><div class="m">' + body + '</div></div></body></html>'
