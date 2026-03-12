import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import BOT_TOKEN, GROUP_LINK, CHANNEL_LINK
from database import Database
from handlers.start import start_handler, register_handler
from handlers.profile import profile_handler
from handlers.fishing import fishing_handler, fishing_callback
# from handlers.map import map_handler, map_callback
from handlers.boost import boost_handler, boost_callback
from handlers.bag import bag_handler
from handlers.equipment import equipment_handler
from handlers.upgrade import upgrade_handler, upgrade_callback
from handlers.daily import daily_handler
from handlers.history import history_handler
from handlers.vip import vip_handler
from handlers.shop import shop_handler, shop_callback
from handlers.market import market_handler, market_callback
from handlers.favorite import favorite_handler, favorite_callback
from handlers.collection import collection_handler
from handlers.transfer import transfer_handler, transfer_callback
from handlers.topup import topup_handler
from handlers.event import event_handler
from handlers.leaderboard import leaderboard_handler
from handlers.help import help_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Store db in bot_data
    app.bot_data['db'] = db

    # Command handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("profil", profile_handler))
    app.add_handler(CommandHandler("fishing", fishing_handler))
    #app.add_handler(CommandHandler("map", map_handler))
    app.add_handler(CommandHandler("boost", boost_handler))
    app.add_handler(CommandHandler("bag", bag_handler))
    app.add_handler(CommandHandler("equipment", equipment_handler))
    app.add_handler(CommandHandler("upgrade", upgrade_handler))
    app.add_handler(CommandHandler("daily", daily_handler))
    app.add_handler(CommandHandler("history", history_handler))
    app.add_handler(CommandHandler("vip", vip_handler))
    app.add_handler(CommandHandler("shop", shop_handler))
    app.add_handler(CommandHandler("market", market_handler))
    app.add_handler(CommandHandler("favorite", favorite_handler))
    app.add_handler(CommandHandler("collection", collection_handler))
    app.add_handler(CommandHandler("transfer", transfer_handler))
    app.add_handler(CommandHandler("topup", topup_handler))
    app.add_handler(CommandHandler("event", event_handler))
    app.add_handler(CommandHandler("leaderboard", leaderboard_handler))
    app.add_handler(CommandHandler("help", help_handler))

    # Callback query handlers
    app.add_handler(CallbackQueryHandler(fishing_callback, pattern="^fish_"))
    #app.add_handler(CallbackQueryHandler(map_callback, pattern="^map_"))
    app.add_handler(CallbackQueryHandler(boost_callback, pattern="^boost_"))
    app.add_handler(CallbackQueryHandler(upgrade_callback, pattern="^upgrade_"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^shop_"))
    app.add_handler(CallbackQueryHandler(market_callback, pattern="^market_"))
    app.add_handler(CallbackQueryHandler(favorite_callback, pattern="^fav_"))
    app.add_handler(CallbackQueryHandler(transfer_callback, pattern="^transfer_"))
    app.add_handler(CallbackQueryHandler(register_handler, pattern="^register$"))

    logger.info("🎣 Fishing Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
