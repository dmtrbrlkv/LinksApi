# LinksApi

Web-приложение на Flask для простого учета посещенных ссылок. Информация сохраняется в Redis. Получение и выдача данных по HTTP в JSON

## Установка

`git clone https://github.com/dmtrbrlkv/LinksApi`

Желательно создать virtualenv

```
cd LinksApi
source venv/bin/activate
```

Перед запуском установить зависимости

`pip install -r requirements.txt`

## Запуск 

`python app.py`

Для задания параметров подлючения к Redis можно воспользоваться аргументами командной строки

```
  --host HOST
  --port PORT
  --db DB
  --password PASSWORD
```

## Запуск тестов
`python -m pytest`
