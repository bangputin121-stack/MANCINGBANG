from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game_data import BOOSTS, RODS, BAITS, BOATS, RARITY_EMOJI


# ── BOOST ─────────────────────────────────────────────────────────────────────
async def boost_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar. Gunakan /start.")
        return

    active = player.get('active_boost')
    active_text = "❌ Tidak ada"
    if active and player.get('boost_expires'):
        boost_exp = datetime.fromisoformat(player['boost_expires'])
        if datetime.now() < boost_exp:
            remaining = (boost_exp - datetime.now()).seconds
            mins, secs = divmod(remaining, 60)
            b = BOOSTS.get(active, {})
            active_text = f"{b.get('name','?')} — {mins}m {secs}s lagi"
        else:
            active_text = "❌ Tidak ada (expired)"

    text = (
        f"🍾 *BOOST PANCINGAN*\n"
        f"{'─'*28}\n"
        f"⚡ Aktif: {active_text}\n\n"
        f"*Pilih Boost:*\n\n"
    )

    keyboard = []
    for bid, b in BOOSTS.items():
        duration_min = b['duration'] // 60
        text += (
            f"{b['emoji']} *{b['name']}*\n"
            f"   💰 {b['cost']:,} koin | ⏱ {duration_min} menit\n\n"
        )
        keyboard.append([InlineKeyboardButton(
            f"{b['emoji']} {b['name']} — {b['cost']:,} koin",
            callback_data=f"boost_buy_{bid}"
        )])

    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def boost_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("boost_buy_"):
        bid = data.replace("boost_buy_", "")
        db = context.bot_data['db']
        user = update.effective_user
        player = db.get_player(user.id)
        boost = BOOSTS.get(bid)

        if not boost:
            await query.answer("Boost tidak ditemukan!", show_alert=True)
            return

        if player['coins'] < boost['cost']:
            await query.answer(f"Koin tidak cukup! Butuh {boost['cost']:,} koin.", show_alert=True)
            return

        expires = (datetime.now() + timedelta(seconds=boost['duration'])).isoformat()
        db.add_coins(user.id, -boost['cost'])
        db.update_player(user.id, active_boost=bid, boost_expires=expires)

        await query.edit_message_text(
            f"✅ *{boost['name']} Aktif!*\n\n"
            f"⏱ Durasi: {boost['duration']//60} menit\n"
            f"💰 Dikurangi: {boost['cost']:,} koin\n\n"
            f"Sekarang mancing dengan /fishing! 🎣",
            parse_mode='Markdown'
        )


# ── BAG ───────────────────────────────────────────────────────────────────────
async def bag_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar. Gunakan /start.")
        return

    page = int(context.args[0]) - 1 if context.args else 0
    bag = db.get_bag(user.id, page=page, per_page=10)
    total = db.get_bag_count(user.id)
    total_pages = (total + 9) // 10

    if not bag:
        await update.message.reply_text(
            "🎒 *Tas Kosong!*\n\nBelum ada ikan yang ditangkap.\nGunakan /fishing untuk mulai memancing!",
            parse_mode='Markdown'
        )
        return

    text = f"🎒 *TAS IKAN* (Halaman {page+1}/{max(total_pages,1)})\n{'─'*28}\n"
    text += f"📦 Total: {total} ikan\n\n"

    for i, fish in enumerate(bag, 1):
        em = RARITY_EMOJI.get(fish['fish_rarity'], '⚪')
        fav = "⭐" if fish['is_favorite'] else ""
        text += f"{em} {fav}{fish['fish_name']} — {fish['fish_weight']}kg — 💰{fish['fish_value']:,}\n"

    nav_btns = []
    if page > 0:
        nav_btns.append(InlineKeyboardButton("◀️ Prev", callback_data=f"bag_p_{page-1}"))
    if page + 1 < total_pages:
        nav_btns.append(InlineKeyboardButton("Next ▶️", callback_data=f"bag_p_{page+1}"))

    keyboard = [nav_btns] if nav_btns else []
    await update.message.reply_text(
        text, parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )


# ── EQUIPMENT ─────────────────────────────────────────────────────────────────
async def equipment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar. Gunakan /start.")
        return

    rod = RODS.get(player['rod_level'], RODS[1])
    bait = BAITS.get(player['bait_level'], BAITS[1])
    boat = BOATS.get(player['boat_level'], BOATS[0])

    next_rod = RODS.get(player['rod_level'] + 1)
    next_bait = BAITS.get(player['bait_level'] + 1)

    text = (
        f"🎣 *PERALATAN SAAT INI*\n"
        f"{'─'*28}\n\n"
        f"🎣 *Joran:* {rod['name']} (Lv.{player['rod_level']})\n"
        f"   +{int(rod['bonus_chance']*100)}% chance | +{int(rod['bonus_value']*100)}% nilai\n"
    )
    if next_rod:
        text += f"   ⬆️ Upgrade ke {next_rod['name']}: {next_rod['upgrade_cost']:,} koin\n\n"
    else:
        text += "   ✅ Sudah maksimal!\n\n"

    text += (
        f"🪱 *Umpan:* {bait['name']} (Lv.{player['bait_level']})\n"
        f"   +{int(bait['bonus_chance']*100)}% chance | +{int(bait['bonus_value']*100)}% nilai\n"
    )
    if next_bait:
        text += f"   ⬆️ Upgrade ke {next_bait['name']}: {next_bait['upgrade_cost']:,} koin\n\n"
    else:
        text += "   ✅ Sudah maksimal!\n\n"

    text += (
        f"🚣 *Perahu:* {boat['name']}\n"
        f"   +{int(boat['bonus_chance']*100)}% chance | +{int(boat['bonus_value']*100)}% nilai\n\n"
        f"{'─'*28}\n"
        f"Gunakan /upgrade untuk meningkatkan peralatan!"
    )

    await update.message.reply_text(text, parse_mode='Markdown')


# ── UPGRADE ───────────────────────────────────────────────────────────────────
async def upgrade_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Belum terdaftar. Gunakan /start.")
        return

    next_rod = RODS.get(player['rod_level'] + 1)
    next_bait = BAITS.get(player['bait_level'] + 1)

    text = (
        f"⬆️ *UPGRADE PERALATAN*\n"
        f"{'─'*28}\n"
        f"💰 Koinmu: {player['coins']:,}\n\n"
    )

    keyboard = []
    if next_rod:
        text += (
            f"🎣 *Upgrade Joran* → {next_rod['name']}\n"
            f"   Biaya: {next_rod['upgrade_cost']:,} koin\n"
            f"   +{int(next_rod['bonus_chance']*100)}% chance | +{int(next_rod['bonus_value']*100)}% nilai\n\n"
        )
        keyboard.append([InlineKeyboardButton(
            f"🎣 Upgrade Joran — {next_rod['upgrade_cost']:,} koin",
            callback_data=f"upgrade_rod"
        )])
    else:
        text += "🎣 Joran sudah *MAKSIMAL!* ✅\n\n"

    if next_bait:
        text += (
            f"🪱 *Upgrade Umpan* → {next_bait['name']}\n"
            f"   Biaya: {next_bait['upgrade_cost']:,} koin\n"
            f"   +{int(next_bait['bonus_chance']*100)}% chance | +{int(next_bait['bonus_value']*100)}% nilai\n"
        )
        keyboard.append([InlineKeyboardButton(
            f"🪱 Upgrade Umpan — {next_bait['upgrade_cost']:,} koin",
            callback_data=f"upgrade_bait"
        )])
    else:
        text += "🪱 Umpan sudah *MAKSIMAL!* ✅"

    await update.message.reply_text(
        text, parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
    )


async def upgrade_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if data == "upgrade_rod":
        next_rod = RODS.get(player['rod_level'] + 1)
        if not next_rod:
            await query.answer("Joran sudah maksimal!", show_alert=True)
            return
        if player['coins'] < next_rod['upgrade_cost']:
            await query.answer(f"Koin tidak cukup! Butuh {next_rod['upgrade_cost']:,} koin.", show_alert=True)
            return
        db.add_coins(user.id, -next_rod['upgrade_cost'])
        db.update_player(user.id, rod_level=player['rod_level'] + 1)
        await query.edit_message_text(
            f"✅ *Joran Berhasil Di-upgrade!*\n\n"
            f"🎣 {next_rod['name']} (Lv.{player['rod_level']+1})\n"
            f"💰 Dikurangi: {next_rod['upgrade_cost']:,} koin",
            parse_mode='Markdown'
        )

    elif data == "upgrade_bait":
        next_bait = BAITS.get(player['bait_level'] + 1)
        if not next_bait:
            await query.answer("Umpan sudah maksimal!", show_alert=True)
            return
        if player['coins'] < next_bait['upgrade_cost']:
            await query.answer(f"Koin tidak cukup! Butuh {next_bait['upgrade_cost']:,} koin.", show_alert=True)
            return
        db.add_coins(user.id, -next_bait['upgrade_cost'])
        db.update_player(user.id, bait_level=player['bait_level'] + 1)
        await query.edit_message_text(
            f"✅ *Umpan Berhasil Di-upgrade!*\n\n"
            f"🪱 {next_bait['name']} (Lv.{player['bait_level']+1})\n"
            f"💰 Dikurangi: {next_bait['upgrade_cost']:,} koin",
            parse_mode='Markdown'
        )
