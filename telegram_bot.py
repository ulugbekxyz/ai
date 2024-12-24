from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from ai_logic import demo_balance, trade_history, performance_metrics

logging.basicConfig(level=logging.INFO)

# Токен вашего Telegram-бота
TELEGRAM_TOKEN = "6814039467:AAFU4kk_I4lrNmomSVcFUWGDNeXCjiZcGLk"

# Команда /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance_message = f"Ваш текущий демо-баланс: {demo_balance['USDT']} USDT"
    await update.message.reply_text(balance_message)

# Команда /trades
async def trades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not trade_history:
        await update.message.reply_text("История сделок пуста.")
    else:
        trades_message = "\n".join(
            [
                f"Пара: {trade['pair']}, Сумма: {trade['amount']}, Прибыль: {trade['profit']}, Успешно: {trade['success']}"
                for trade in trade_history[-5:]  # Отображаем последние 5 сделок
            ]
        )
        await update.message.reply_text(f"Последние сделки:\n{trades_message}")

# Команда /analytics
async def analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = performance_metrics["total_trades"]
    success_rate = (performance_metrics["successful_trades"] / total * 100) if total > 0 else 0
    analytics_message = (
        f"Всего сделок: {total}\n"
        f"Успешных сделок: {performance_metrics['successful_trades']}\n"
        f"Неуспешных сделок: {performance_metrics['failed_trades']}\n"
        f"Прибыль: {performance_metrics['profit']} USDT\n"
        f"Успешность сделок: {success_rate:.2f}%"
    )
    await update.message.reply_text(analytics_message)

def main():
    # Создаём приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("trades", trades))
    application.add_handler(CommandHandler("analytics", analytics))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
