"""Полная страница «Мотивация + KPI + статус»: для команды (role='team') и для РОПа (role='rop')."""
from motivation import num, eur, CSS, parse, limit_note
ACTIONS = {
 'Конверсия': ('Главный результат', 'Реактивация «молчунов»: серия из 3 касаний за 2 недели (письмо, мессенджер, звонок), сначала 146 клиентов, которые раньше отвечали.', True),
 'Доля лидов': ('Результат', 'Цепочка из 5–6 касаний за 14 дней на «Ожидаем ответа». Сделку с 1–2 касаниями не переводим в «перестал отвечать».', False),
 'Первое касание': ('Скорость', 'Первое касание нового лида не позже 2 часов в рабочее время. Дежурство в пик прихода лидов: 9–11 и 14–15. Каждое утро список «лиды без касания».', False),
 'Лиды без': ('Дисциплина', 'Все касания фиксируем в Битриксе, даже если общались в мессенджере.', False),
 'Живые сделки': ('Дисциплина', 'У каждой живой сделки есть открытое дело с датой следующего шага.', False),
 'Горячие': ('Деньги на столе', 'Горячие сделки («Готов стать клиентом», «Подписание договора», «Оплата депозита»): не больше 5 дней без касания, у каждой дата следующего шага.', False),
}
WEEKS = [('19–23.10', '2026-10-19', 'Горячие и запуск', 'Разбор 11 зависших горячих сделок, раздача 146 «ответивших молчунов», SLA 2 часа.'),
         ('26–30.10', '2026-10-26', 'Реактивация, волна 1', 'Первая серия касаний по всем 146. Открытые дела у всех живых сделок. Шаблон цепочки 5–6 касаний.'),
         ('2–6.11', '2026-11-02', 'Реактивация, волна 2', 'Вторая и третья серии касаний. Причина пропусков в касаниях.'),
         ('9–13.11', '2026-11-09', 'Закрепление', 'Свежие молчуны, разбор слабых мест, проверка SLA.'),
         ('16.11', '2026-11-16', 'Итоги', 'Сравнение с точкой отсчёта, выплата бонусов за период, план на декабрь.')]
def fmt(name, v):
    if v is None: return '—'
    if name.startswith('Первое касание'):
        h = v / 60
        return ('%d ч' % h) if h == int(h) else ('%.1f ч' % h).replace('.', ',')
    if name.split()[0] in ('Конверсия', 'Доля', 'Лиды', 'Живые'):
        return ('%.1f' % (v * 100)).replace('.', ',').replace(',0', '') + '%'
    return '%d' % round(v)
def kpi_html(plan):
    h = ''
    for r in plan[2:]:
        if not r or r[0].startswith('Справочно'): continue
        g = lambda i: num(r[i]) if len(r) > i else None
        name, st, cur, nov, dec = r[0], g(2), g(5), g(6), g(8)
        if cur is None or nov is None: continue
        key = next((a for a in ACTIONS if name.startswith(a)), None)
        tag, act, higher = ACTIONS.get(key, ('', '', False))
        done = cur >= nov if higher else cur <= nov
        if higher: prog = cur / nov if nov else 1
        elif st is not None and st != nov: prog = (st - cur) / (st - nov)
        else: prog = 1 if done else 0
        prog = max(0, min(1, prog))
        pct = name.split()[0] in ('Конверсия', 'Доля', 'Лиды', 'Живые')
        gap = (('%.1f' % (abs(cur - nov) * 100)).replace('.', ',').replace(',0', '') + ' п.п.') if pct else fmt(name, abs(cur - nov))
        status = '<span class="ok">в пределах цели ноября (месяц ещё идёт)</span>' if done else '<span class="no">до цели ноября ещё %s</span>' % gap
        h += ('<div class="kp"><div class="kk">%s</div><div class="kt">%s</div><div class="kb"><i style="width:%d%%"></i></div>'
              '<div class="kr"><span>Сейчас <b>%s</b></span><span>Ноябрь <b>%s</b></span><span>Декабрь <b>%s</b></span><span>%s</span></div>'
              '<p class="ka">%s</p></div>') % (tag, name, round(prog * 100), fmt(name, cur), fmt(name, nov), fmt(name, dec), status, act)
    return h
EXTRA_CSS = (".sec{margin:0 0 .4rem;font-size:1.05rem;font-weight:700}.stamp{color:#6b7280;font-size:.875rem;margin:-10px 0 14px}"
 ".kp{border-top:1px solid #f0f0f0;padding:.8rem 0}.kt{font-weight:600}.kk{color:#d03040;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em}"
 ".kb{height:8px;background:#f1f1f1;border-radius:99px;overflow:hidden;margin:.55rem 0}.kb i{display:block;height:100%;background:#d03040;border-radius:99px}"
 ".kr{display:flex;flex-wrap:wrap;gap:.4rem 1.2rem;font-size:.875rem;color:#6b7280}.kr b{color:#111}.ok{color:#14804a;font-weight:600}.no{color:#b3261e;font-weight:600}.ka{margin:.4rem 0 0;font-size:.875rem}"
 ".wk{display:grid;gap:.5rem}.wk>div{border:1px solid #ececec;border-radius:14px;padding:.6rem .8rem;font-size:.875rem}.wk>div.now{border-color:#d03040;background:#fff4f5}.wk b{display:block}"
 ".rules{margin:0;padding-left:1.1rem;font-size:.875rem;line-height:1.5}.m+.m{margin-top:1rem}")
SCRIPT = ("<script>(function(){var d=new Date(),el=document.getElementById('today');if(el)el.textContent=d.toLocaleDateString('ru-RU',{day:'numeric',month:'long',year:'numeric'});"
 "var w=document.querySelectorAll('.wk>div'),cur=-1;w.forEach(function(x,i){if(d>=new Date(x.dataset.s))cur=i});if(cur>=0)w[cur].classList.add('now');})();</script>")
def full(rows, plan, snapshot, role):
    by = parse(rows)
    t, b, r = by('Менеджеры — командный'), by('Менеджеры — доплата'), by('РОП')
    nm, nd = by('Менеджеров в команде')['v'], by('Ожидаемо возвращённых')['v']
    cell = lambda l, val, sub: '<div><span>%s</span><b>%s</b><small>%s</small></div>' % (l, eur(val), sub)
    if role == 'rop':
        title = 'Мотивация РОПа: KPI и статус'
        money = '<div class="k">Бонус РОПа за период плана</div><div class="t">%s</div>' % eur(r['s'] or 0)
        money += '<p class="n">Вес: 50% конверсия лидов в YSELL, 30% дисциплина отдела (SLA 2 часа, открытые дела, нет зависших горячих), 20% развитие команды (1:1, разбор слабых мест). Ниже 80% по блоку блок не платится, 80–100% платится пропорционально, выше 100% ускоритель, потолок 120%.</p>'
    else:
        title = 'Мотивация команды: KPI и статус'
        money = '<div class="k">Что получит команда</div><div class="t">%s</div><div class="g">' % eur((t['s'] or 0) + (b['s'] or 0))
        money += cell('Командный бонус за дисциплину', t['s'] or 0, ('%s на человека (%d)' % (eur(t['s'] / nm), nm)) if nm else '')
        money += cell('Доплата за возвращённых клиентов', b['s'] or 0, ('%s за сделку (при %d возвратах)' % (eur(b['s'] / nd), nd)) if nd else '') + '</div>'
        money += '<ul class="rules"><li>Командный бонус: SLA 2 часа и открытые дела у живых сделок не ниже 90% по обоим показателям, без личных сравнений.</li><li>Доплата: за каждую сделку из «молчунов», которая дошла до YSELL, с подтверждённым ответом клиента в Битриксе.</li></ul>'
    wk = ''.join('<div data-s="%s"><b>%s · %s</b>%s</div>' % (d, a, nme, c) for a, d, nme, c in WEEKS)
    body = '<p class="stamp">Данные на %s · сегодня <span id="today"></span> · обновляется по будням</p>' % snapshot
    body += '<div class="m">' + money + limit_note(by) + '<p class="n">Период плана — ноябрь и декабрь вместе. Полная выплата при 100% плана, ниже 80% по блоку премия не платится.</p></div>'
    body += '<div class="m"><div class="sec">KPI: что должно измениться</div><p class="n">Показатели месяца пока идут, цифры предварительные.</p>' + kpi_html(plan) + '</div>'
    body += '<div class="m"><div class="sec">План на ближайшие недели</div><div class="wk">' + wk + '</div></div>' + SCRIPT
    return ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>'
            + title + '</title><style>' + CSS + EXTRA_CSS + '</style></head><body><div class="w"><div class="top"><h1>' + title + '</h1></div>' + body + '</div></body></html>')
