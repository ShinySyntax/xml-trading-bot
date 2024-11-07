from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, ContextTypes
import requests
import logging

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7274386440:AAEcNC7xzch2jadfyAXlB74ROmwI1lM_ScA'

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# States for ConversationHandler
BUY_AMOUNT, SELL_PERCENTAGE = range(2)

# Fetch price data from a public API
def get_price():
    response = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/XLM-USD")
    if response.status_code == 200:
        data = response.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        return price
    else:
        return "Error fetching price"

# Start command with button layout
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Open Wallet", callback_data='open_wallet'), InlineKeyboardButton("Refresh", callback_data='refresh')],
        [InlineKeyboardButton("Buy 100 XLM", callback_data='buy_100'), InlineKeyboardButton("Buy 500 XLM", callback_data='buy_500'), InlineKeyboardButton("Buy 'X' XLM", callback_data='buy_x')],
        [InlineKeyboardButton("Sell 25%", callback_data='sell_25'), InlineKeyboardButton("Sell 100%", callback_data='sell_100'), InlineKeyboardButton("Sell 'X'%", callback_data='sell_x')],
        [InlineKeyboardButton("Settings", callback_data='settings'), InlineKeyboardButton("Help", callback_data='help')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select an option:", reply_markup=reply_markup)

# Button callbacks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == 'open_wallet':
        await query.edit_message_text(text="Opening wallet... Your current balance is 1000 XLM.")
    elif action == 'refresh':
        price = get_price()
        await query.edit_message_text(text=f"Current XLM Price: ${price}")
    elif action == 'buy_100':
        await query.edit_message_text(text="Buying 100 XLM worth of token (simulated).")
    elif action == 'buy_500':
        await query.edit_message_text(text="Buying 500 XLM worth of token (simulated).")
    elif action == 'buy_x':
        await query.edit_message_text(text="Please enter the XLM amount to buy:")
        return BUY_AMOUNT
    elif action == 'sell_25':
        await query.edit_message_text(text="Selling 25% of your holdings (simulated).")
    elif action == 'sell_100':
        await query.edit_message_text(text="Selling 100% of your holdings (simulated).")
    elif action == 'sell_x':
        await query.edit_message_text(text="Please enter the percentage of holdings to sell:")
        return SELL_PERCENTAGE
    elif action == 'settings':
        await query.edit_message_text(text="Settings menu: Modify preferences here.")
    elif action == 'help':
        await query.edit_message_text(text="Help menu: Use this bot to manage XLM trading actions.")

# Conversation handlers for custom input
async def buy_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Enter the XLM amount to buy:")
    return BUY_AMOUNT

async def sell_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Enter the percentage of holdings to sell:")
    return SELL_PERCENTAGE

async def buy_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    amount = update.message.text
    await update.message.reply_text(f"Simulated buy order for {amount} XLM.")
    return ConversationHandler.END

async def sell_percentage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    percentage = update.message.text
    await update.message.reply_text(f"Simulated sell order for {percentage}% of holdings.")
    return ConversationHandler.END

# Main function to set up the bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Basic command handler to start the bot
    application.add_handler(CommandHandler("start", start))

    # Button callback handler
    application.add_handler(CallbackQueryHandler(button))

    # Conversation handler for buy and sell custom inputs
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            BUY_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_amount)],
            SELL_PERCENTAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_percentage)],
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
