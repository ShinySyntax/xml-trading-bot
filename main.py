from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import logging
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7274386440:AAEcNC7xzch2jadfyAXlB74ROmwI1lM_ScA'

# Stellar setup
STELLAR_SERVER = "https://horizon-testnet.stellar.org"  # Testnet
ISSUER_SECRET = "YOUR_ISSUER_SECRET"
DISTRIBUTOR_SECRET = "YOUR_DISTRIBUTOR_SECRET"

# Keypairs
issuer_keypair = Keypair.from_secret(ISSUER_SECRET)
distributor_keypair = Keypair.from_secret(DISTRIBUTOR_SECRET)

server = Server(horizon_url=STELLAR_SERVER)
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Start command with button layout
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Open Wallet", callback_data='open_wallet'), InlineKeyboardButton("Refresh", callback_data='refresh')],
        [InlineKeyboardButton("Buy 100 XLM", callback_data='buy_100'), InlineKeyboardButton("Buy 500 XLM", callback_data='buy_500')],
        [InlineKeyboardButton("Sell 25%", callback_data='sell_25'), InlineKeyboardButton("Sell 100%", callback_data='sell_100')],
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
        await query.edit_message_text(text="Opening wallet... Your current balance is being fetched.")
    elif action == 'refresh':
        balance = await get_balance(distributor_keypair.public_key)
        await query.edit_message_text(text=f"Your balance: {balance} XLM")
    elif action == 'buy_100':
        result = await trade_token("buy", 100)
        await query.edit_message_text(text=result)
    elif action == 'buy_500':
        result = await trade_token("buy", 500)
        await query.edit_message_text(text=result)
    elif action == 'sell_25':
        result = await trade_token("sell", 25)
        await query.edit_message_text(text=result)
    elif action == 'sell_100':
        result = await trade_token("sell", 100)
        await query.edit_message_text(text=result)
    elif action == 'settings':
        await query.edit_message_text(text="Settings menu: Modify preferences here.")
    elif action == 'help':
        await query.edit_message_text(text="Help menu: Use this bot to trade tokens on Stellar.")

# Get balance from Stellar
async def get_balance(public_key):
    account = server.accounts().account_id(public_key).call()
    for balance in account['balances']:
        if balance['asset_type'] == 'native':  # XLM balance
            return balance['balance']
    return 0

# Trade tokens (buy or sell)
async def trade_token(action, amount):
    try:
        distributor_account = server.load_account(distributor_keypair.public_key)
        token = Asset("MYTOKEN", issuer_keypair.public_key)  # Replace MYTOKEN with your token code

        if action == "buy":
            # Buy operation
            tx = TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=network_passphrase,
                base_fee=100
            ).add_text_memo("Buying tokens").append_manage_buy_offer_op(
                selling=Asset.native(),
                buying=token,
                buy_amount=str(amount),
                price="1"  # 1 XLM = 1 token (adjust as needed)
            ).set_timeout(30).build()

        elif action == "sell":
            # Sell operation
            tx = TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=network_passphrase,
                base_fee=100
            ).add_text_memo("Selling tokens").append_manage_sell_offer_op(
                selling=token,
                buying=Asset.native(),
                amount=str(amount),
                price="1"  # 1 token = 1 XLM (adjust as needed)
            ).set_timeout(30).build()

        tx.sign(distributor_keypair)
        response = server.submit_transaction(tx)
        return f"Trade successful: {response['id']}"

    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return "Failed to execute trade."

# Main function to set up the bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Basic command handler to start the bot
    application.add_handler(CommandHandler("start", start))

    # Button callback handler
    application.add_handler(CallbackQueryHandler(button))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
