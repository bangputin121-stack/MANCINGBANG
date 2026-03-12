from telegram import Update
from telegram.ext import ContextTypes
from game_data import RODS, BAITS, BOATS, MAPS, VIP_LEVELS


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user = update.effective_user
    player = db.get_player(user.id)

    if not player:
        await update.message.reply_text("❌ Kamu belum terdaftar. Gunakan /start untuk mendaftar.")
        return

    rod = RODS.get(player['rod_level'], RODS[1])
    bait = BAITS.get(player['bait_level'], BAITS[1])
    boat = BOATS.get(player['boat_level'], BOATS[0])
    map_data = MAPS.get(player['current_map'], MAPS['sungai'])

    xp_needed = player['level'] * 100
    xp_bar_fill = int((player['xp'] / xp_needed) * 10)
    xp_bar = "█" * xp_bar_fill + "░" * (10 - xp_bar_fill)

    vip_text = "❌ Tidak aktif"
    if player['vip_level'] > 0:
        vip_name = VIP_LEVELS.get(player['vip_level'], {}).get('name', 'VIP')
        vip_text = f"{vip_name}"
        if player.get('vip_expires'):
            vip_text += f"\n   ⏰ Expires: {player['vip_expires'][:10]}"

    collection_count = len(db.get_collection(user.id))
    bag_count = db.get_bag_count(user.id)

    text = (
        f"👤 *PROFIL PEMAIN*\n"
        f"{'─'*30}\n"
        f"🏷 Nama: {player['full_name']}\n"
        f"🆔 ID: `{player['user_id']}`\n\n"
        f"⚡ Level: *{player['level']}*\n"
        f"📊 XP: {player['xp']}/{xp_needed}\n"
        f"   [{xp_bar}]\n\n"
        f"💰 Koin: *{player['coins']:,}*\n"
        f"💎 Gems: *{player['gems']:,}*\n\n"
        f"🎣 Joran: {rod['name']}\n"
        f"🪱 Umpan: {bait['name']}\n"
        f"🚣 Perahu: {boat['name']}\n"
        f"📍 Lokasi: {map_data['name']}\n\n"
        f"🐟 Total Tangkapan: *{player['total_fish']}*\n"
        f"🎒 Isi Tas: {bag_count} ikan\n"
        f"🌟 Koleksi: {collection_count} spesies\n\n"
        f"👑 VIP: {vip_text}\n"
        f"{'─'*30}\n"
        f"📅 Bergabung: {player['registered_at'][:10]}"
    )
    await update.message.reply_text(text, parse_mode='Markdown')
