import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game_data import RARITY_EMOJI, VIP_LEVELS, SHOP_ITEMS, BOATS, EVENTS


# ── DAILY ─────────────────────────────────────────────────────────────────────
DAILY_REWARDS = [100, 150, 200, 250, 300, 500, 1000]

async def daily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar. Gunakan /start.")
        return

    if player['last_daily']:
        last = datetime.fromisoformat(player['last_daily'])
        if (datetime.now() - last).total_seconds() < 86400:
            remaining = 86400 - (datetime.now() - last).total_seconds()
            h, rem = divmod(int(remaining), 3600)
            m = rem // 60
            await update.message.reply_text(
                f"🎁 *Hadiah Harian*\n\n"
                f"⏳ Sudah diklaim! Kembali dalam *{h}j {m}m*",
                parse_mode='Markdown'
            )
            return

    base_reward = random.choice(DAILY_REWARDS)
    multiplier = [1, 1, 1.5, 2, 3, 5][min(player['vip_level'], 5)]
    reward = int(base_reward * multiplier)

    db.add_coins(user.id, reward)
    db.add_xp(user.id, 50)
    db.update_player(user.id, last_daily=datetime.now().isoformat())

    text = (
        f"🎁 *HADIAH HARIAN DIKLAIM!*\n"
        f"{'─'*28}\n\n"
        f"💰 Koin: *+{reward:,}*\n"
        f"⭐ XP: *+50*\n"
    )
    if multiplier > 1:
        text += f"👑 Bonus VIP {multiplier}x diterapkan!\n"
    text += f"\nKembali besok untuk hadiah berikutnya! 🎁"

    await update.message.reply_text(text, parse_mode='Markdown')


# ── HISTORY ───────────────────────────────────────────────────────────────────
async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar.")
        return

    history = db.get_history(user.id, limit=15)
    if not history:
        await update.message.reply_text("📖 Belum ada riwayat memancing.")
        return

    text = f"📖 *HISTORI TANGKAPAN* (15 Terakhir)\n{'─'*28}\n\n"
    for h in history:
        if h['result'] == 'catch':
            em = RARITY_EMOJI.get(h['fish_rarity'], '⚪')
            text += f"{em} {h['fish_name']} — {h['fish_weight']}kg — 💰{h['coins_earned']:,}\n"
        elif h['result'] == 'miss':
            text += f"😔 Tidak dapat ikan\n"
        elif h['result'] == 'trash':
            text += f"🗑 Sampah\n"
        dt = h['caught_at'][:16].replace('T', ' ')
        text += f"   🕐 {dt}\n\n"

    await update.message.reply_text(text, parse_mode='Markdown')


# ── VIP ───────────────────────────────────────────────────────────────────────
async def vip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar.")
        return

    text = f"👑 *STATUS VIP*\n{'─'*28}\n\n"
    current_vip = player['vip_level']
    text += f"Statusmu: {'👑 VIP Level ' + str(current_vip) if current_vip > 0 else '❌ Non-VIP'}\n\n"
    text += "*Paket VIP Tersedia:*\n\n"

    keyboard = []
    for lvl, vip in VIP_LEVELS.items():
        perks_text = '\n   '.join(vip['perks'])
        cost_text = f"{vip['cost_coins']:,} koin" if vip['cost_coins'] > 0 else f"{vip['cost_gems']} gems"
        text += (
            f"*{vip['name']}*\n"
            f"   💰 {cost_text}\n"
            f"   ✨ {perks_text}\n\n"
        )
        if lvl > current_vip:
            keyboard.append([InlineKeyboardButton(
                f"Beli {vip['name']} — {cost_text}",
                callback_data=f"vip_buy_{lvl}"
            )])

    await update.message.reply_text(
        text, parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )


# ── SHOP ──────────────────────────────────────────────────────────────────────
async def shop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar.")
        return

    text = f"🛒 *TOKO PERALATAN*\n{'─'*28}\n💰 Koinmu: {player['coins']:,}\n\n*Perahu Tersedia:*\n\n"
    keyboard = []

    for item_id, item in SHOP_ITEMS.items():
        owned = player['boat_level'] >= item.get('boat_level', 0)
        boat = BOATS.get(item.get('boat_level', 1), {})
        text += (
            f"{'✅' if owned else '🛒'} *{item['name']}*\n"
            f"   💰 {item['cost']:,} koin\n"
            f"   +{int(boat.get('bonus_chance',0)*100)}% chance | +{int(boat.get('bonus_value',0)*100)}% nilai\n\n"
        )
        if not owned:
            keyboard.append([InlineKeyboardButton(
                f"Beli {item['name']} — {item['cost']:,} koin",
                callback_data=f"shop_buy_{item_id}"
            )])

    await update.message.reply_text(
        text, parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )


async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if data.startswith("shop_buy_"):
        item_id = data.replace("shop_buy_", "")
        item = SHOP_ITEMS.get(item_id)
        if not item:
            await query.answer("Item tidak ditemukan!", show_alert=True)
            return
        if player['coins'] < item['cost']:
            await query.answer(f"Koin tidak cukup!", show_alert=True)
            return
        boat_level = item.get('boat_level', 1)
        if player['boat_level'] >= boat_level:
            await query.answer("Sudah memiliki item ini!", show_alert=True)
            return
        db.add_coins(user.id, -item['cost'])
        db.update_player(user.id, boat_level=boat_level)
        await query.edit_message_text(
            f"✅ *{item['name']} Berhasil Dibeli!*\n\n💰 Dikurangi: {item['cost']:,} koin",
            parse_mode='Markdown'
        )


# ── MARKET ────────────────────────────────────────────────────────────────────
async def market_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar.")
        return

    listings = db.get_market_listings(limit=10)
    text = f"🛒 *MARKET IKAN*\n{'─'*28}\n💰 Koinmu: {player['coins']:,}\n\n"

    keyboard = []
    if listings:
        text += "*Listing Terbaru:*\n\n"
        for l in listings:
            em = RARITY_EMOJI.get(l['fish_rarity'], '⚪')
            text += f"{em} {l['fish_name']} — {l['fish_weight']}kg\n   💰 {l['price']:,} koin\n\n"
            if l['seller_id'] != user.id:
                keyboard.append([InlineKeyboardButton(
                    f"Beli {l['fish_name']} — {l['price']:,} koin",
                    callback_data=f"market_buy_{l['id']}"
                )])
    else:
        text += "Belum ada listing di pasar.\n"

    text += "\n*Jual Ikan:*\nFormat: /market jual [id_ikan] [harga]"

    await update.message.reply_text(
        text, parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )


async def market_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    db = context.bot_data['db']
    user = update.effective_user

    if data.startswith("market_buy_"):
        listing_id = int(data.replace("market_buy_", ""))
        result = db.buy_from_market(user.id, listing_id)
        if result['success']:
            l = result['listing']
            await query.edit_message_text(
                f"✅ *Berhasil membeli!*\n\n"
                f"{l['fish_name']} — {l['fish_weight']}kg\n"
                f"💰 Dibayar: {l['price']:,} koin",
                parse_mode='Markdown'
            )
        else:
            await query.answer(result['reason'], show_alert=True)


# ── FAVORITE ─────────────────────────────────────────────────────────────────
async def favorite_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar.")
        return

    favs = db.get_favorites(user.id)
    if not favs:
        await update.message.reply_text(
            "⭐ *IKAN FAVORIT*\n\nBelum ada ikan favorit!\nTandai ikan setelah memancing.",
            parse_mode='Markdown'
        )
        return

    text = f"⭐ *IKAN FAVORIT* ({len(favs)} ikan)\n{'─'*28}\n\n"
    keyboard = []
    for fish in favs:
        em = RARITY_EMOJI.get(fish['fish_rarity'], '⚪')
        text += f"{em} {fish['fish_name']} — {fish['fish_weight']}kg — 💰{fish['fish_value']:,}\n"
        keyboard.append([InlineKeyboardButton(
            f"❌ Hapus {fish['fish_name']}",
            callback_data=f"fav_remove_{fish['id']}"
        )])

    await update.message.reply_text(
        text, parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    db = context.bot_data['db']
    user = update.effective_user

    if data.startswith("fav_remove_"):
        fish_id = int(data.replace("fav_remove_", ""))
        db.toggle_favorite(user.id, fish_id)
        await query.answer("❌ Dihapus dari favorit!", show_alert=True)
        await query.edit_message_text("⭐ Favorit diperbarui. Gunakan /favorite untuk melihat.")


# ── COLLECTION ────────────────────────────────────────────────────────────────
async def collection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar.")
        return

    from game_data import FISH_DATA
    collection = db.get_collection(user.id)
    total_species = len(FISH_DATA) - 1  # exclude sampah

    text = (
        f"🌟 *KOLEKSI IKAN*\n{'─'*28}\n"
        f"📊 Terkumpul: {len(collection)}/{total_species} spesies\n\n"
        f"*Koleksi Kamu:*\n\n"
    )

    from game_data import RARITY_EMOJI
    for fish in collection:
        fd = FISH_DATA.get(fish['fish_id'], {})
        em = RARITY_EMOJI.get(fd.get('rarity', ''), '⚪')
        text += f"{em} {fish['fish_name']}\n"

    if not collection:
        text += "Belum ada koleksi! Mulai memancing 🎣"

    await update.message.reply_text(text, parse_mode='Markdown')


# ── TRANSFER ─────────────────────────────────────────────────────────────────
async def transfer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar.")
        return

    text = (
        f"➡️ *TRANSFER IKAN*\n{'─'*28}\n\n"
        f"Kirim ikan ke pemain lain.\n\n"
        f"*Cara Kirim:*\n"
        f"Reply pesan pemain lain dengan:\n"
        f"`/transfer [id_ikan]`\n\n"
        f"Lihat ID ikan di /bag\n"
        f"Lihat ID pemain di /profil mereka"
    )
    await update.message.reply_text(text, parse_mode='Markdown')


async def transfer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


# ── TOPUP ─────────────────────────────────────────────────────────────────────
async def topup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"💰 *TOPUP COIN / VIP*\n{'─'*28}\n\n"
        f"*Paket COIN:*\n"
        f"💰 1.000 Coin — Rp 5.000\n"
        f"💰 5.000 Coin — Rp 20.000\n"
        f"💰 15.000 Coin — Rp 50.000\n"
        f"💰 50.000 Coin — Rp 150.000\n\n"
        f"*Paket VIP:*\n"
        f"⭐ VIP Bronze (30 hari) — Rp 15.000\n"
        f"🌟 VIP Silver (30 hari) — Rp 35.000\n"
        f"💎 VIP Gold (30 hari) — Rp 75.000\n"
        f"👑 VIP Diamond (30 hari) — Rp 150.000\n\n"
        f"📩 Hubungi admin untuk proses pembelian:\n"
        f"@admin_username"
    )
    await update.message.reply_text(text, parse_mode='Markdown')


# ── EVENT ─────────────────────────────────────────────────────────────────────
async def event_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"🗓 *EVENT AKTIF*\n{'─'*28}\n\n"
    active_events = [e for e in EVENTS if e['active']]
    upcoming = [e for e in EVENTS if not e['active']]

    if active_events:
        text += "*🔥 Sedang Berlangsung:*\n\n"
        for e in active_events:
            text += (
                f"🎉 *{e['name']}*\n"
                f"   📝 {e['description']}\n"
                f"   🎁 Bonus: {e['bonus']}\n"
                f"   📅 {e['period']}\n\n"
            )
    else:
        text += "Tidak ada event aktif saat ini.\n\n"

    if upcoming:
        text += "*📅 Event Mendatang:*\n\n"
        for e in upcoming:
            text += f"🔜 *{e['name']}* — {e['period']}\n"

    await update.message.reply_text(text, parse_mode='Markdown')


# ── LEADERBOARD ───────────────────────────────────────────────────────────────
async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']

    medals = ["🥇", "🥈", "🥉"] + ["4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    categories = [
        ("total_fish", "🐟 Tangkapan Terbanyak"),
        ("level", "⭐ Level Tertinggi"),
        ("coins", "💰 Koin Terbanyak"),
    ]

    text = f"🏆 *LEADERBOARD*\n{'─'*28}\n\n"

    for sort_by, title in categories:
        top = db.get_leaderboard(sort_by=sort_by, limit=5)
        text += f"*{title}:*\n"
        for i, p in enumerate(top):
            medal = medals[i] if i < len(medals) else f"{i+1}."
            val = p[sort_by]
            if sort_by == 'coins':
                val = f"{val:,} 💰"
            text += f"{medal} {p['full_name']} — {val}\n"
        text += "\n"

    await update.message.reply_text(text, parse_mode='Markdown')


# ── HELP ──────────────────────────────────────────────────────────────────────
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"⛑ *BANTUAN & PERINTAH*\n{'─'*28}\n\n"
        f"*📋 Perintah Utama:*\n"
        f"/start — 📥 Daftar / Beranda\n"
        f"/profil — 👤 Info Pemain\n"
        f"/fishing — 🎣 Mulai Memancing\n"
        f"/map — 🗺 Pilih Lokasi\n"
        f"/bag — 🎒 Tas Ikan\n"
        f"/equipment — 🛠 Peralatan\n"
        f"/upgrade — ⬆️ Upgrade Joran/Umpan\n\n"
        f"*💡 Fitur Tambahan:*\n"
        f"/boost — ⚡ Aktifkan Boost\n"
        f"/daily — 🎁 Hadiah Harian\n"
        f"/shop — 🛒 Toko Peralatan\n"
        f"/market — 💹 Jual/Beli Ikan\n"
        f"/favorite — ⭐ Ikan Favorit\n"
        f"/collection — 🌟 Koleksi Spesies\n"
        f"/transfer — ➡️ Transfer Ikan\n\n"
        f"*📊 Info:*\n"
        f"/history — 📖 Riwayat Mancing\n"
        f"/vip — 👑 Info VIP\n"
        f"/topup — 💰 Isi Koin/VIP\n"
        f"/event — 🗓 Event Aktif\n"
        f"/leaderboard — 🏆 Peringkat\n\n"
        f"*🎯 Tips:*\n"
        f"• Upgrade joran & umpan untuk ikan lebih besar\n"
        f"• Aktifkan boost untuk rare chance lebih tinggi\n"
        f"• Klaim /daily setiap hari!\n"
        f"• VIP memberikan bonus extra!\n"
    )
    await update.message.reply_text(text, parse_mode='Markdown')
