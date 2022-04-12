# Парсер книг с сайта tululu.org

Скрипт для скачивания книг с [tululu.org](tululu.org).

## Запуск и настройка

- Скачайте код
- Настройте окружение. Для этого выполните следующие действия:
    - установите Python3.6+;
    - создайте виртуальное окружение [virtualenv/venv](https://docs.python.org/3/library/venv.html) для изоляции проекта.
    - активируйте виртуальное окружение:
  
    ```
    . ./env/bin/activate
    ```
    - установите необходимые зависимости:

    ```
    pip install -r requirements.txt
    ```
- Запустите скрипт командой:
    ```
    python main.py
    ```
## Инструкция по использованию

- Запуск скрипта `main.py` скачивает книги. При запуске скрипта можно указать парметры:
  - `--start_page` номер первой страницы с книгами
  - `--end_page` номер последней страницы с книгами
  - `--skip_imgs` Не скачивать картинки
  - `--skip_txt` Не скачивать текст книг
  - `--dest_folder` Указать путь к каталогу с результатами парсинга: картинкам, книгам, JSON. По умолчанию директория файла main.py
  - `--json_path` указать свой путь к *.json файлу с результатами
    ```
    python main.py --skip_imgs --skip_txt --dest_folder books/ --json_path json/ --start_page 1 --end_page 2
    ```
- После запуска скрипта в корневой директории появится три папки `books`, `json` и `images`. Первая содержит скачаные книги, вторая файл со всей информацией о книгах, третья - обложки к ним.
- Запуск скрипта `render_website.py` создает страницы сайта.
    ```
    python render_website.py
    ```
- Открыть файл `index.html` в папке 'pages'
- Размещенный [сайт](https://tapochekmira.github.io/layout_3/pages/)
## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
