import argparse

from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.core.usecases import (
    buy_currency,
    get_portfolio_info,
    get_rate,
    login_user,
    register_user,
    sell_currency,
)
from valutatrade_hub.core.utils import META_FILE, load_json, load_session


def cmd_register(args):
    try:
        user = register_user(args.username, args.password)
        print(f"Пользователь '{user.username}' зарегистрирован (id={user.user_id}).")
    except ValueError as e:
        print(f"Ошибка: {e}")

def cmd_login(args):
    try:
        user_id, username = login_user(args.username, args.password)
        print(f"Вы вошли как '{username}' (id={user_id}).")
    except ValueError as e:
        print(f"Ошибка: {e}")           

def cmd_show_portfolio(args):
    try:
        info = get_portfolio_info(args.base)
        if info is None:
            print("У вас пока нет кошельков.")
            return

        users = load_json(META_FILE, default=[])
        username = next((u["username"] for u in users if u["user_id"] == info["user_id"]), "unknown") # noqa: E501
        
        base = info["base_currency"]
        print(f"Портфель пользователя '{username}' (база: {base}):")
        for item in info["items"]:
            print(f"- {item['currency_code']}: {item['balance']:.4f} -> {item['value_in_base']:.2f} {base}") # noqa: E501
        
        print("-" * 30)
        print(f"ИТОГО: {info['total']:.2f} {base}")
    except ValueError as e:
        print(f"Ошибка: {e}")

def cmd_buy(args):
    user_id = load_session()
    if user_id is None:
        print("Ошибка: Сначала выполните login")
        return

    try:
        result = buy_currency(user_id, args.currency, args.amount)
        print(f"Покупка выполнена: {result['amount']:.4f} {result['currency_code']} "
              f"по курсу {result['rate']:.2f} {result['base_currency']}/{result['currency_code']}") # noqa: E501
        print("Изменения в портфеле:")
        print(f"- {result['currency_code']}: было {result['old_balance']:.4f} "
              f"-> стало {result['new_balance']:.4f}")
        print(f"Оценочная стоимость покупки: {result['cost']:.2f} {result['base_currency']}") # noqa: E501
    except CurrencyNotFoundError as e:
        print(f"Ошибка: {e}")
        print("Подсказка: используйте команду `get-rate` для проверки курса.")
    except InsufficientFundsError as e:
        print(f"Ошибка: {e}")
    except ApiRequestError as e:
        print(f"Ошибка: {e}")
        print("Подсказка: проверьте соединение или повторите позже.")
    except ValueError as e:
        print(f"Ошибка: {e}")

def cmd_get_rate(args):
    try:
        result = get_rate(args.from_currency, args.to_currency)
        updated_at = result["updated_at"].replace("T", " ")[:19]
        print(f"Курс {args.from_currency.upper()}->{args.to_currency.upper()}: "
              f"{result['rate']:.8f} (обновлено: {updated_at})")
        if result["reverse_rate"]:
            print(f"Обратный курс {args.to_currency.upper()}->{args.from_currency.upper()}: " # noqa: E501
                  f"{result['reverse_rate']:.2f}")
    except CurrencyNotFoundError as e:
        print(f"Ошибка: {e}")
        print("Подсказка: проверьте доступные коды валют (USD, EUR, BTC, ETH).")
    except ApiRequestError as e:
        print(f"Ошибка: {e}")
        print("Подсказка: проверьте соединение или повторите позже.")
    except ValueError as e:
        print(f"Ошибка: {e}")   

def cmd_sell(args):
    user_id = load_session()
    if user_id is None:
        print("Ошибка: Сначала выполните login")
        return

    try:
        result = sell_currency(user_id, args.currency, args.amount)
        print(f"Продажа выполнена: {result['amount']:.4f} {result['currency_code']} "
              f"по курсу {result['rate']:.2f} {result['base_currency']}/{result['currency_code']}") # noqa: E501
        print("Изменения в портфеле:")
        print(f"- {result['currency_code']}: было {result['old_balance']:.4f} "
              f"-> стало {result['new_balance']:.4f}")
        print(f"Оценочная стоимость продажи: {result['cost']:.2f} {result['base_currency']}") # noqa: E501
    except CurrencyNotFoundError as e:
        print(f"Ошибка: {e}")
        print("Подсказка: проверьте доступные коды валют (USD, EUR, BTC, ETH).")
    except InsufficientFundsError as e:
        print(f"Ошибка: {e}")
    except ApiRequestError as e:
        print(f"Ошибка: {e}")
        print("Подсказка: проверьте соединение или повторите позже.")
    except ValueError as e:
        print(f"Ошибка: {e}")                   

def build_parser():
    parser = argparse.ArgumentParser(prog="wallet")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_register = subparsers.add_parser("register", help="Регистрация")
    p_register.add_argument("--username", required=True, help="Имя пользователя")
    p_register.add_argument("--password", required=True, help="Пароль")
    p_register.set_defaults(func=cmd_register)
    p_login = subparsers.add_parser("login", help="Вход в систему")
    p_login.add_argument("--username", required=True, help="Имя пользователя")
    p_login.add_argument("--password", required=True, help="Пароль")
    p_login.set_defaults(func=cmd_login)
    p_show = subparsers.add_parser("show-portfolio", help="Показать портфель")
    p_show.add_argument("--base", default="USD", help="Базовая валюта (по умолчанию USD)") # noqa: E501
    p_show.set_defaults(func=cmd_show_portfolio)
    p_buy = subparsers.add_parser("buy", help="Купить валюту")
    p_buy.add_argument("--currency", required=True, help="Код валюты (например, BTC)")
    p_buy.add_argument("--amount", required=True, type=float, help="Количество валюты")
    p_buy.set_defaults(func=cmd_buy)
    p_get = subparsers.add_parser("get-rate", help="Получить курс валюты")
    p_get.add_argument("--from", dest="from_currency", required=True, help="Исходная валюта") # noqa: E501
    p_get.add_argument("--to", dest="to_currency", required=True, help="Целевая валюта")
    p_get.set_defaults(func=cmd_get_rate)
    p_sell = subparsers.add_parser("sell", help="Продать валюту")
    p_sell.add_argument("--currency", required=True, help="Код валюты")
    p_sell.add_argument("--amount", required=True, type=float, help="Количество валюты")
    p_sell.set_defaults(func=cmd_sell)

    return parser


def run_cli():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

 