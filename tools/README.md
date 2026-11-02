# Сборка страниц

Страницы `index.html` и `daily.html` собирает скрипт из данных Google-таблицы «Отчет воронка FFB» и шифрует паролем.

1. `python3 tools/ingest.py /tmp/ing <файлы с ответами Google Sheets>` — раскладывает данные.
2. `PAGE_PASSWORD=... python3 tools/build.py /tmp/ing/data.json /tmp/out` — собирает и шифрует.
3. Файлы из `/tmp/out` копируются в корень репозитория.

Пароль в репозитории не хранится. Данные в репозитории только в зашифрованном виде.

## Страница лидов выставки (whitelabelexpo.html)

Собирается отдельно от основных страниц: `WLE_PASSWORD=... python3 tools/wle_build.py LEADS.json LETTERS.json STAGES.json DAILY.json whitelabelexpo.html`.
Входные файлы это ответы Google Sheets get_values по листам таблицы «Whitelabelexpo — лиды выставки» (список листов и диапазонов в начале `wle_build.py`). Шаблон страницы: `wle_tpl.html`. Пароль в репозитории не хранится, данные только в зашифрованном виде.
