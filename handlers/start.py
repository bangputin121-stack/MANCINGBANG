from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if player:
        text = (
            f"🎣 *Selamat Datang Kembali, {user.first_name}!*\n\n"
            f"📊 Level: {player['level']} | 💰 Koin: {player['coins']:,}\n"
            f"🐟 Total Tangkapan: {player['total_fish']}\n\n"
            f"Gunakan /help untuk melihat semua perintah."
        )
        await update.message.reply_text(text, parse_mode='Markdown')
    else:
        text = (
            "🎣 *Selamat Datang di Fishing Game Bot!*\n\n"
            "Rasakan serunya memancing virtual dengan ratusan jenis ikan!\n\n"
            "🏞 Jelajahi berbagai lokasi mancing\n"
            "🐟 Tangkap ikan dari Common hingga Legendary\n"
            "⬆️ Upgrade peralatan pancingmu\n"
            "💰 Jual ikan di Market\n"
            "🏆 Bersaing di Leaderboard\n\n"
            "Klik tombol di bawah untuk mulai!"
        )
        keyboard = [[InlineKeyboardButton("📥 Daftar Sekarang", callback_data="register")]]
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = context.bot_data['db']
    user = update.effective_user

    if db.get_player(user.id):
        await query.edit_message_text("✅ Kamu sudah terdaftar! Gunakan /profil untuk melihat akunmu.")
        return

    success = db.register_player(user.id, user.username, user.full_name)
    if success:
        text = (
            f"✅ *Pendaftaran Berhasil!*\n\n"
            f"👤 Nama: {user.full_name}\n"
            f"💰 Koin Awal: 500\n"
            f"🎣 Joran: Joran Bambu\n"
            f"🪱 Umpan: Cacing Biasa\n"
            f"📍 Lokasi: Sungai Desa\n\n"
            f"Selamat memancing! Gunakan /fishing untuk mulai 🎣"
        )
        await query.edit_message_text(text, parse_mode='Markdown')
    else:
        await query.edit_message_text("❌ Gagal mendaftar. Coba lagi.")
