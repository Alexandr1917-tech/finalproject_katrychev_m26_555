# ValutaTrade Hub

Итоговый проект: Микросервис для управления виртуальным портфелем валют, просмотра курсов и их автоматического обновления через внешние API (CoinGecko и ExchangeRate-API).

## Структура проекта
finalproject_katrychev_m26_555/
├── data/                      # JSON-файлы с данными (пользователи, портфели, кэш)
├── valutatrade_hub/
│   ├── core/                  # Бизнес-логика (модели, юзкейсы, валюты)
│   ├── infra/                 # Инфраструктура (настройки Singleton)
│   ├── parser_service/        # Сервис парсинга (api_clients, updater, storage)
│   ├── cli/                   # Интерфейс командной строки
│   ├── logging_config.py      # Настройка логирования
│   └── decorators.py          # Декоратор @log_action
├── main.py                    # Точка входа
├── pyproject.toml             # Зависимости (uv)
└── README.md

## Установка и запуск
```
# Клонируйте репозиторий и перейдите в папку проекта:
git clone <ссылка_на_ваш_репозиторий>
cd finalproject_katrychev_m26_555

#Установите зависимости (создастся виртуальное окружение .venv):
uv sync
```

## Ключи и Parser Service
```
1. Создайте файл .env в корне проекта (рядом с main.py).
2. Добавьте туда ключ:
EXCHANGE_RATE_API_KEY=ваш_ключ_здесь
```

## Кэш и TTL
```
Курсы сохраняются в файл data/rates.json. Для быстродействия используется кэш с временем жизни (TTL).
TTL задается в infra/settings.py (по умолчанию 300 секунд). Если данные старше этого порога, система сообщает об устаревании и просит запустить команду update-rates для получения свежих данных.
```

## Примеры команд CLI
```
Регистрация и вход:
uv run python main.py register --username alex --password 1234
uv run python main.py login --username alex --password 1234

Работа с портфелем:
uv run python main.py show-portfolio --base USD
uv run python main.py buy --currency BTC --amount 0.5
uv run python main.py sell --currency BTC --amount 0.1
uv run python main.py get-rate --from BTC --to USD

Парсер и обновление курсов:
uv run python main.py update-rates
uv run python main.py update-rates --source coingecko
uv run python main.py show-rates --top 3
uv run python main.py show-rates --currency RUB
uv run python main.py show-rates --base EUR
```

## Демо
```
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py register --username student --password 1234
Пользователь 'student' зарегистрирован (id=2).
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py login --username student --password 1234
Вы вошли как 'student' (id=2).
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py buy --currency BTC --amount 0.5
Покупка выполнена: 0.5000 BTC по курсу 59337.21 USD/BTC
Изменения в портфеле:
- BTC: было 0.0000 -> стало 0.5000
Оценочная стоимость покупки: 29668.60 USD
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py show-portfolio --base USD
Портфель пользователя 'student' (база: USD):
- BTC: 0.5000 -> 25000.00 USD
------------------------------
ИТОГО: 25000.00 USD
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py sell --currency BTC --amount 0.1
Продажа выполнена: 0.1000 BTC по курсу 59337.21 USD/BTC
Изменения в портфеле:
- BTC: было 0.5000 -> стало 0.4000
Оценочная стоимость продажи: 5933.72 USD
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py get-rate --from BTC --to USD
uv run python main.py update-rates
Курс BTC->USD: 59337.21000000 (обновлено: 2026-11-03 19:25:04)
Обратный курс USD->BTC: 0.00
Update successful. Total rates updated: 6. Last refresh: 2026-11-03T16:25:33Z
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py show-rates --top 2
Rates from cache (updated at 2026-11-03T16:25:33Z):
- BTC_USD: 77316.0000
- ETH_USD: 2284.8200
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py sell --currency BTC --amount 1000
Ошибка: Недостаточно средств: доступно 0.40 BTC, требуется 1000.00 BTC
(wallet) aleksandr@MacBook-Air-Aleksandr finalproject_katrychev_m26_555 % uv run python main.py buy --currency DOGE --amount 10
Ошибка: Валюта с кодом 'DOGE' не найдена.
Подсказка: используйте команду `get-rate` для проверки курса.
```

