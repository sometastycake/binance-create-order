# binance-create-order-test

## Запуск

Необходимо задать следующие переменные окружения

```
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
BINANCE_API_URL=
```

- `BINANCE_API_KEY` - API ключ для доступа к функциональности Binance
- `BINANCE_SECRET_KEY` - секретный ключ для подписывания реквестов 
- `BINANCE_API_URL` - URL Binance API ([Binance API](https://binance-docs.github.io/apidocs/spot/en/#general-info))

Установка зависимостей

```commandline
pip install -r requirements.txt
```

Сервис представляет собой простое API, написанное на FastAPI
(т.к. в ТЗ предполагалась, что данные для создания ордера будут приходить от фронт-енда)

Сам запуск

```commandline
uvicorn source.api.app:app --reload
```

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [94271] using WatchFiles
INFO:     Started server process [94273]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```