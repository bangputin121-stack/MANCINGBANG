import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game_data import catch_fish, RARITY_EMOJI, MAPS, BOOSTS
from config import FISHING_COOLDOWN


FISHING_ANIMATION = ["🌊", "🎣", "💦", "🌀", "✨"]

MISS_MESSAGES = [
    "Ikannya kabur! 🐟💨",
    "Hampir dapat! Umpannya dimakan tapi ikannya lolos...",
    "Tidak ada ikan yang tertarik kali ini.",
    "Tali putus! Ikan berhasil melarikan diri 😅",
    "Tidak ada gigitan... coba lagi!",
]


async def fishing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /start untuk mendaftar.")
        return

    # Check cooldown
    cooldown = FISHING_COOLDOWN
    if player['vip_level'] >= 1:
        reductions = [1.0, 0.9, 0.8, 0.7, 0.5]
        cooldown = int(cooldown * reductions[min(player['vip_level'], 4)])

    if player['last_fishing']:
        last = datetime.fromisoformat(player['last_fishing'])
        elapsed = (datetime.now() - last).total_seconds()
        if elapsed < cooldown:
            remaining = int(cooldown - elapsed)
            mins, secs = divmod(remaining, 60)
            time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
            await update.message.reply_text(
                f"⏳ Tunggu dulu! Kamu masih kelelahan.\n"
                f"⏰ Cooldown: *{time_str}* lagi",
                parse_mode='Markdown'
            )
            return

    # Check active boost
    active_boost = player.get('active_boost')
    if active_boost and player.get('boost_expires'):
        boost_exp = datetime.fromisoformat(player['boost_expires'])
        if datetime.now() > boost_exp:
            active_boost = None
            db.update_player(user.id, active_boost=None, boost_expires=None)

    # Fishing animation message
    anim_msg = await update.message.reply_text("🎣 Sedang memancing...")

    # Update last fishing time
    db.update_player(user.id, last_fishing=datetime.now().isoformat())

    # Simulate fishing
    import asyncio
    await asyncio.sleep(1.5)

    fish = catch_fish(
        map_id=player['current_map'],
        rod_level=player['rod_level'],
        bait_level=player['bait_level'],
        boat_level=player['boat_level'],
        active_boost=active_boost,
        vip_level=player['vip_level']
    )

    map_data = MAPS.get(player['current_map'], MAPS['sungai'])

    if fish is None:
        miss_msg = random.choice(MISS_MESSAGES)
        db.add_history(user.id, 'miss', map_name=player['current_map'])
        await anim_msg.edit_text(
            f"😔 *Tidak Dapat Ikan!*\n\n{miss_msg}\n\n📍 Lokasi: {map_data['name']}",
            parse_mode='Markdown'
        )
        return

    if fish['rarity'] == 'Trash':
        db.add_history(user.id, 'trash', fish_name=fish['name'], map_name=player['current_map'])
        await anim_msg.edit_text(
            f"🗑 *Dapat Sampah!*\n\nKamu mendapatkan {fish['name']}.\nBersihkan pantai yuk! 😅",
            parse_mode='Markdown'
        )
        return

    # Add fish to bag
    db.add_fish(user.id, fish)
    db.add_coins(user.id, fish['value'])
    level_result = db.add_xp(user.id, fish.get('xp', 10))
    db.add_history(
        user.id, 'catch',
        fish_name=fish['name'],
        fish_rarity=fish['rarity'],
        fish_weight=fish['weight'],
        coins_earned=fish['value'],
        map_name=player['current_map']
    )

    rarity_em = RARITY_EMOJI.get(fish['rarity'], '⚪')
    rarity_stars = {"Common":"⚪", "Uncommon":"🟢", "Rare":"🔵", "Epic":"🟣", "Legendary":"🟡"}.get(fish['rarity'], '⚪')

    level_up_text = ""
    if level_result and level_result[0]:
        level_up_text = f"\n\n🎉 *LEVEL UP! → Level {level_result[1]}!* 🎉"

    boost_text = ""
    if active_boost and active_boost in BOOSTS:
        boost_text = f"\n⚡ Boost aktif: {BOOSTS[active_boost]['name']}"

    text = (
        f"🎣 *IKAN TERTANGKAP!*\n"
        f"{'─'*28}\n"
        f"{fish['name']}\n"
        f"{rarity_stars} Rarity: *{fish['rarity']}*\n"
        f"⚖️ Berat: *{fish['weight']} kg*\n"
        f"💰 Nilai: *+{fish['value']:,} koin*\n"
        f"⭐ XP: *+{fish.get('xp', 10)}*\n"
        f"📍 Lokasi: {map_data['name']}"
        f"{boost_text}"
        f"{level_up_text}"
    )

    keyboard = [
        [
            InlineKeyboardButton("⭐ Favoritkan", callback_data=f"fish_fav_{user.id}"),
            InlineKeyboardButton("🎣 Mancing Lagi", callback_data=f"fish_again_{user.id}")
        ]
    ]
    await anim_msg.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def fishing_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("fish_again_"):
        # Re-trigger fishing
        await query.message.reply_text("Gunakan /fishing untuk mancing lagi! 🎣")
    elif data.startswith("fish_fav_"):
        db = context.bot_data['db']
        user = update.effective_user
        bag = db.get_bag(user.id, per_page=1)
        if bag:
            is_fav = db.toggle_favorite(user.id, bag[0]['id'])
            msg = "⭐ Ikan ditambahkan ke favorit!" if is_fav else "❌ Dihapus dari favorit."
            await query.answer(msg, show_alert=True)
        else:
            await query.answer("Tas kosong!", show_alert=True)
