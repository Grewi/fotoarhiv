## Старт проекта

Для начала нужно 
Услановить в систему Python и rclone
Создать и заполнить .env файл
Запустить файл start.py для конфигурации rclone
Запустить foto.py для запуска указав параметр

up      - Загрузить с сервера

down    - Выгрузить на сервер

up-down - Загрузить, а затем выгрузить

down-up - Выгрузить, а затем загрузить


```
python3 ./foto.py up
```

Для установки на windows7

git version 2.39.1

```
python -m pip install -i https://mirrors.aliyun.com/pypi/simple/ python-dotenv
```