from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game_data import MAPS

async def map_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /start.")
        return

    text = "🗺 *PETA MANCING*\n" + "─"*28 + "\n\nPilih lokasi memancingmu:\n\n"

    keyboard = []
    for map_id, map_data in MAPS.items():
        is_current = player['current_map'] == map_id
        is_unlocked = player['level'] >= map_data['unlock_level']

        status_icon = "✅ " if is_current else ("🔓 " if is_unlocked else "🔒 ")
        btn_text = f"{status_icon}{map_data['name']}"
        
        if is_current:
            btn_text += " (Aktif)"

        lock_info = ""
        if not is_unlocked:
            lock_info = f" [Lv.{map_data['unlock_level']}]"

        # 1. Info dasar map
        text += (
            f"{map_data['emoji']} *{map_data['name']}*{lock_info}\n"
            f"📝 {map_data['description']}\n"
            f"🎯 Rare Chance: {int(map_data['rare_chance']*100)}%\n"
        )

        # 2. Logika penentuan status teks (DILUAR tanda kurung)
        if is_current:
            status_text = "✅ Aktif"
        elif is_unlocked:
            status_text = "🔓 Tersedia"
        else:
            lvl = map_data["unlock_level"]
            status_text = f"🔒 Butuh Level {lvl}"

        # 3. Tambahkan status ke text (Pastikan indentasi sejajar)
        text += f"Status: {status_text}\n\n"

        # 4. Logika Tombol
        if is_unlocked and not is_current:
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"map_go_{map_id}")])
        elif is_current:
            keyboard.append([InlineKeyboardButton(f"📍 {map_data['name']} (Lokasi Saat Ini)", callback_data="map_noop")])

    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def map_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "map_noop":
        return

    if data.startswith("map_go_"):
        map_id = data.replace("map_go_", "")
        db = context.bot_data['db']
        user = update.effective_user
        player = db.get_player(user.id)

        if not player:
            return

        map_data = MAPS.get(map_id)
        if not map_data:
            await query.answer("Peta tidak ditemukan!", show_alert=True)
            return

        if player['level'] < map_data['unlock_level']:
            await query.answer(f"Butuh Level {map_data['unlock_level']}!", show_alert=True)
            return

        # Cek biaya buka peta
        if map_data.get('unlock_cost', 0) > 0:
            if player['coins'] < map_data['unlock_cost']:
                await query.answer(
                    f"Butuh {map_data['unlock_cost']:,} koin untuk membuka peta ini!",
                    show_alert=True
                )
                return
            db.add_coins(user.id, -map_data['unlock_cost'])

        db.update_player(user.id, current_map=map_id)
        await query.edit_message_text(
            f"✅ *Berhasil pindah ke {map_data['name']}!*\n\n"
            f"📝 {map_data['description']}\n"
            f"🎯 Rare Chance: {int(map_data['rare_chance']*100)}%\n\n"
            f"Gunakan /fishing untuk mulai memancing! 🎣",
            parse_mode='Markdown'
        )
