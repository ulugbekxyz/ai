import time
import logging
import requests
from decimal import Decimal
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json

# Логирование
logging.basicConfig(level=logging.INFO)

# GraphQL-запрос к Bitquery
GRAPHQL_QUERY = """
query LastTrades($network: EthereumNetwork!) {
  ethereum(network: $network) {
    dexTrades(options: {desc: ["block.timestamp.time"], limit: 5}) {
      baseCurrency {
        symbol
      }
      quoteCurrency {
        symbol
      }
      tradeAmount(in: USD)
      block {
        timestamp {
          time(format: "%Y-%m-%d %H:%M:%S")
        }
      }
    }
  }
}
"""

# API настройки
BITQUERY_API_URL = "https://graphql.bitquery.io"
BITQUERY_API_KEY = "BQYAGkn2axdbyYEE9sU5tgU8UsLkPr60"
PUMPFUN_API_URL = "https://api.bitquery.io/v1/marketcap"  # Предполагаемый URL PumpFun

transport = RequestsHTTPTransport(
    url=BITQUERY_API_URL,
    headers={"X-API-KEY": BITQUERY_API_KEY},
    use_json=True,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

demo_balance = Decimal("1000.00")  # Демо-счет
trade_history = []  # История сделок

def fetch_pumpfun_data():
    try:
        response = requests.get(PUMPFUN_API_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Ошибка при запросе PumpFun API: {e}")
        return {}

def fetch_latest_trades(network="ethereum"):
    try:
        variables = {"network": network}
        query = gql(GRAPHQL_QUERY)
        response = client.execute(query, variable_values=variables)
        trades = response.get("ethereum", {}).get("dexTrades", [])

        return [
            {
                "base": trade["baseCurrency"]["symbol"],
                "quote": trade["quoteCurrency"]["symbol"],
                "amount": Decimal(trade["tradeAmount"]),
                "timestamp": trade["block"]["timestamp"]["time"],
            }
            for trade in trades
        ]
    except Exception as e:
        logging.error(f"Ошибка при запросе: {e}")
        return []

def perform_trade(pair, amount):
    global demo_balance
    trade_result = {
        "pair": pair,
        "amount": amount,
        "profit": Decimal("0"),  # Симуляция
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    if demo_balance >= amount:
        demo_balance -= amount
        trade_result["profit"] = amount * Decimal("0.05")  # Пример прибыли 5%
        demo_balance += amount + trade_result["profit"]
        trade_history.append(trade_result)

        logging.info(f"Выполнена сделка: {trade_result}")
        save_trade_data(trade_result)
    else:
        logging.warning("Недостаточно средств для выполнения сделки.")

def save_trade_data(trade):
    try:
        with open("trade_history.json", "a") as f:
            f.write(json.dumps(trade) + "\n")
    except Exception as e:
        logging.error(f"Ошибка при сохранении данных сделки: {e}")

def analyze_trades():
    successful_trades = [t for t in trade_history if t["profit"] > 0]
    failed_trades = [t for t in trade_history if t["profit"] <= 0]
    total_profit = sum(t["profit"] for t in trade_history)

    stats = {
        "total_trades": len(trade_history),
        "successful_trades": len(successful_trades),
        "failed_trades": len(failed_trades),
        "profit": total_profit,
    }

    logging.info(f"Общая статистика: {stats}")

    return stats

def main():
    logging.info("Начало работы AI бота...")
    network = "ethereum"  # Используем только сеть Ethereum

    while True:
        trades = fetch_latest_trades(network)

        if trades:
            for trade in trades:
                pair = f"{trade['base']}/{trade['quote']}"
                amount = trade["amount"] * Decimal("0.01")  # Инвестируем 1% от объема сделки

                perform_trade(pair, amount)
        else:
            logging.info("Сделки отсутствуют.")

        analyze_trades()

        pumpfun_data = fetch_pumpfun_data()
        logging.info(f"Данные из PumpFun: {pumpfun_data}")

        time.sleep(60)  # Ждем 1 минуту перед следующим циклом

if __name__ == "__main__":
    main()
