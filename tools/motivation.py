"""Страницы «Мотивация»: для команды (без ФОТ и без бонуса РОПа) и отдельная для РОПа.
Данные — блок 'План KPI'!A13:D38."""
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
.w{max-width:980px;margin:0 auto;padding:16px}.top h1{font-size:1.4rem;margin:8px 0 18px}
.m{background:#fff;border:1px solid #ececec;border-radius:24px;box-shadow:0 10px 30px -18px rgba(0,0,0,.22);padding:1.4rem;display:flex;flex-direction:column;gap:.7rem}
.k{color:#d03040;font-weight:700;font-size:.8125rem;letter-spacing:.04em;text-transform:uppercase}h3{margin:0;font-size:1.125rem}
.t{font-weight:800;letter-spacing:-.02em;font-size:clamp(2.2rem,5vw,3.6rem);line-height:1;color:#d03040}
.g{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.g>div{display:flex;flex-direction:column;gap:.3rem;justify-content:space-between}
.g span{font-size:.8125rem;color:#6b7280;line-height:1.25;min-height:2.5em}.g b{font-weight:800;font-size:clamp(1.4rem,2.6vw,2rem);line-height:1;white-space:nowrap}.g small{color:#6b7280;font-size:.8125rem}
.n{color:#6b7280;font-size:.8125rem;margin:0}.lim{background:#fff6e5;border-radius:12px;padding:.7rem .9rem;font-size:.875rem;color:#7a4b00;margin:0}
@media(max-width:560px){.g{grid-template-columns:1fr}}'''
def parse(rows):
    def by(p):
        for r in rows:
            if r and r[0].startswith(p):
                g = lambda i: num(r[i]) if len(r) > i else None
                return {'v': g(1), 's': g(2), 'k': g(3)}
        return {'v': None, 's': None, 'k': None}
    return by
def limit_note(by):
    c = by('Коэффициент выплаты')['v']
    if c is None or c >= 1: return ''
    return '<p class="lim">Выплата ограничена лимитом ФОТ: к выплате %d%% от суммы по плану. Лимит не должен превышаться.</p>' % round(c * 100)
def shell(title, body):
    return '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>' + title + '</title><style>' + CSS + '</style></head><body><div class="w"><div class="top"><h1>' + title + '</h1></div><div class="m">' + body + '</div></div></body></html>'
def team(rows):
    by = parse(rows)
    t, b = by('Менеджеры — командный'), by('Менеджеры — доплата')
    pm, pd = by('Командный бонус на одного')['v'], by('Доплата за одну')['v']
    nm, nd = by('Менеджеров в команде')['v'], by('Ожидаемо возвращённых')['v']
    c = by('Коэффициент выплаты')['v']
    if t['s'] is None or b['s'] is None:
        return shell('Мотивация отдела продаж', '<p class="n">Суммы пока не заданы.</p>')
    plan_pm = t['s'] / nm if nm else None; plan_pd = b['s'] / nd if nd else None
    cell = lambda l, val, sub: '<div><span>%s</span><b>%s</b><small>%s</small></div>' % (l, eur(val), sub)
    body = '<div class="k">Что получит команда</div><h3>Если выполним план, команда получит</h3><div class="t">%s</div><div class="g">' % eur(t['s'] + b['s'])
    body += cell('Командный бонус за дисциплину', t['s'], ('%s на человека (%d)' % (eur(plan_pm), nm)) if plan_pm is not None else '')
    body += cell('Доплата за возвращённых клиентов', b['s'], ('%s за сделку (при %d возвратах)' % (eur(plan_pd), nd)) if plan_pd is not None else '')
    body += '</div>' + limit_note(by) + '<p class="n">Период плана — ноябрь и декабрь вместе. Полная выплата — при 100% плана; ниже 80% по блоку премия не платится. Суммы приведены по плану, к выплате — в пределах лимита ФОТ.</p>'
    return shell('Мотивация отдела продаж', body)
def rop(rows):
    by = parse(rows)
    r = by('РОП')
    if r['s'] is None: return shell('Мотивация РОПа', '<p class="n">Сумма пока не задана.</p>')
    body = '<div class="k">Бонус РОПа</div><h3>Если выполним план, РОП получит</h3><div class="t">%s</div>' % eur(r['s'])
    body += limit_note(by) + '<p class="n">Период плана — ноябрь и декабрь вместе. Выплата — при выполнении плана и в пределах лимита ФОТ отдела.</p>'
    return shell('Мотивация РОПа', body)
