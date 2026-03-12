from typing import Dict, List
import random

# ── MAPS ──────────────────────────────────────────────────────────────────────
MAPS = {
    "sungai": {
        "name": "🏞 Sungai Desa",
        "description": "Sungai tenang dengan ikan-ikan biasa. Cocok untuk pemula.",
        "unlock_level": 1,
        "unlock_cost": 0,
        "fish_pool": ["ikan_mas", "ikan_lele", "ikan_nila", "ikan_mujair", "ikan_gabus", "sampah"],
        "rare_chance": 0.05,
        "emoji": "🏞"
    },
    "danau": {
        "name": "🏔 Danau Pegunungan",
        "description": "Danau sejuk dengan ikan langka pegunungan.",
        "unlock_level": 5,
        "unlock_cost": 2000,
        "fish_pool": ["ikan_trout", "ikan_salmon", "ikan_mas", "ikan_arwana", "ikan_lele_raksasa"],
        "rare_chance": 0.10,
        "emoji": "🏔"
    },
    "pantai": {
        "name": "🌊 Pantai Biru",
        "description": "Pantai indah dengan ikan laut tropis.",
        "unlock_level": 10,
        "unlock_cost": 5000,
        "fish_pool": ["ikan_tuna", "ikan_kakap", "ikan_kerapu", "ikan_bawal", "gurita", "lobster"],
        "rare_chance": 0.15,
        "emoji": "🌊"
    },
    "laut_dalam": {
        "name": "🌑 Laut Dalam",
        "description": "Kedalaman laut misterius dengan monster laut.",
        "unlock_level": 20,
        "unlock_cost": 15000,
        "fish_pool": ["ikan_pari_manta", "hiu_paus", "cumi_raksasa", "ikan_layar", "ikan_todak"],
        "rare_chance": 0.25,
        "emoji": "🌑"
    },
    "sungai_sakura": {
        "name": "🌸 Sungai Sakura",
        "description": "Sungai mistis Jepang dengan ikan legendaris.",
        "unlock_level": 30,
        "unlock_cost": 30000,
        "fish_pool": ["koi_emas", "koi_platinum", "ikan_dewa", "naga_air", "koi_rainbow"],
        "rare_chance": 0.35,
        "emoji": "🌸"
    }
}

# ── FISH DATA ──────────────────────────────────────────────────────────────────
FISH_DATA = {
    # Common
    "ikan_mas":         {"id":"ikan_mas",         "name":"🐟 Ikan Mas",          "rarity":"Common",    "weight_range":(0.2,1.5),  "base_value":50,   "xp":10},
    "ikan_lele":        {"id":"ikan_lele",         "name":"🐟 Ikan Lele",         "rarity":"Common",    "weight_range":(0.3,2.0),  "base_value":60,   "xp":12},
    "ikan_nila":        {"id":"ikan_nila",         "name":"🐟 Ikan Nila",         "rarity":"Common",    "weight_range":(0.2,1.2),  "base_value":45,   "xp":10},
    "ikan_mujair":      {"id":"ikan_mujair",       "name":"🐟 Ikan Mujair",       "rarity":"Common",    "weight_range":(0.1,0.8),  "base_value":40,   "xp":8},
    # Uncommon
    "ikan_gabus":       {"id":"ikan_gabus",        "name":"🐠 Ikan Gabus",        "rarity":"Uncommon",  "weight_range":(0.5,3.0),  "base_value":120,  "xp":20},
    "ikan_trout":       {"id":"ikan_trout",        "name":"🐠 Ikan Trout",        "rarity":"Uncommon",  "weight_range":(0.5,2.5),  "base_value":150,  "xp":25},
    "ikan_salmon":      {"id":"ikan_salmon",       "name":"🐠 Ikan Salmon",       "rarity":"Uncommon",  "weight_range":(1.0,5.0),  "base_value":200,  "xp":30},
    "ikan_bawal":       {"id":"ikan_bawal",        "name":"🐠 Ikan Bawal",        "rarity":"Uncommon",  "weight_range":(0.5,3.0),  "base_value":130,  "xp":22},
    # Rare
    "ikan_arwana":      {"id":"ikan_arwana",       "name":"🐡 Arwana",            "rarity":"Rare",      "weight_range":(1.0,4.0),  "base_value":500,  "xp":60},
    "ikan_lele_raksasa":{"id":"ikan_lele_raksasa", "name":"🐡 Lele Raksasa",      "rarity":"Rare",      "weight_range":(5.0,20.0), "base_value":800,  "xp":80},
    "ikan_tuna":        {"id":"ikan_tuna",         "name":"🐡 Ikan Tuna",         "rarity":"Rare",      "weight_range":(10.0,60.0),"base_value":1000, "xp":100},
    "ikan_kakap":       {"id":"ikan_kakap",        "name":"🐡 Ikan Kakap",        "rarity":"Rare",      "weight_range":(2.0,8.0),  "base_value":700,  "xp":70},
    "ikan_kerapu":      {"id":"ikan_kerapu",       "name":"🐡 Ikan Kerapu",       "rarity":"Rare",      "weight_range":(1.0,6.0),  "base_value":600,  "xp":65},
    # Epic
    "gurita":           {"id":"gurita",            "name":"🦑 Gurita",            "rarity":"Epic",      "weight_range":(2.0,10.0), "base_value":2000, "xp":150},
    "lobster":          {"id":"lobster",           "name":"🦞 Lobster",           "rarity":"Epic",      "weight_range":(0.5,3.0),  "base_value":2500, "xp":200},
    "ikan_pari_manta":  {"id":"ikan_pari_manta",   "name":"🐋 Pari Manta",        "rarity":"Epic",      "weight_range":(50.0,200.0),"base_value":5000,"xp":300},
    "hiu_paus":         {"id":"hiu_paus",          "name":"🦈 Hiu Paus",          "rarity":"Epic",      "weight_range":(100.0,500.0),"base_value":8000,"xp":400},
    "cumi_raksasa":     {"id":"cumi_raksasa",      "name":"🦑 Cumi Raksasa",      "rarity":"Epic",      "weight_range":(20.0,80.0),"base_value":6000, "xp":350},
    "ikan_layar":       {"id":"ikan_layar",        "name":"⚡ Ikan Layar",        "rarity":"Epic",      "weight_range":(10.0,40.0),"base_value":4500, "xp":280},
    "ikan_todak":       {"id":"ikan_todak",        "name":"🗡 Ikan Todak",        "rarity":"Epic",      "weight_range":(20.0,100.0),"base_value":5500,"xp":320},
    # Legendary
    "koi_emas":         {"id":"koi_emas",          "name":"🏆 Koi Emas",          "rarity":"Legendary", "weight_range":(1.0,5.0),  "base_value":15000,"xp":800},
    "koi_platinum":     {"id":"koi_platinum",      "name":"💎 Koi Platinum",      "rarity":"Legendary", "weight_range":(1.0,5.0),  "base_value":25000,"xp":1200},
    "ikan_dewa":        {"id":"ikan_dewa",         "name":"✨ Ikan Dewa",         "rarity":"Legendary", "weight_range":(5.0,20.0), "base_value":50000,"xp":2000},
    "naga_air":         {"id":"naga_air",          "name":"🐉 Naga Air",          "rarity":"Legendary", "weight_range":(50.0,200.0),"base_value":100000,"xp":5000},
    "koi_rainbow":      {"id":"koi_rainbow",       "name":"🌈 Koi Rainbow",       "rarity":"Legendary", "weight_range":(2.0,8.0),  "base_value":75000,"xp":3000},
    # Trash
    "sampah":           {"id":"sampah",            "name":"🗑 Sampah",            "rarity":"Trash",     "weight_range":(0.1,0.5),  "base_value":0,    "xp":0},
}

RARITY_EMOJI = {
    "Common":    "⚪",
    "Uncommon":  "🟢",
    "Rare":      "🔵",
    "Epic":      "🟣",
    "Legendary": "🟡",
    "Trash":     "⚫"
}

RARITY_WEIGHTS = {
    "Common":    50,
    "Uncommon":  25,
    "Rare":      15,
    "Epic":      7,
    "Legendary": 3,
}

# ── RODS ──────────────────────────────────────────────────────────────────────
RODS = {
    1: {"name":"🎣 Joran Bambu",       "bonus_chance":0.00, "bonus_value":0.00, "upgrade_cost":0},
    2: {"name":"🎣 Joran Fiber",       "bonus_chance":0.03, "bonus_value":0.05, "upgrade_cost":1000},
    3: {"name":"🎣 Joran Karbon",      "bonus_chance":0.06, "bonus_value":0.10, "upgrade_cost":3000},
    4: {"name":"🎣 Joran Titanium",    "bonus_chance":0.10, "bonus_value":0.20, "upgrade_cost":8000},
    5: {"name":"🎣 Joran Master",      "bonus_chance":0.15, "bonus_value":0.30, "upgrade_cost":20000},
    6: {"name":"🎣 Joran Legenda",     "bonus_chance":0.25, "bonus_value":0.50, "upgrade_cost":50000},
}

BAITS = {
    1: {"name":"🪱 Cacing Biasa",      "bonus_chance":0.00, "bonus_value":0.00, "upgrade_cost":0},
    2: {"name":"🦗 Jangkrik",          "bonus_chance":0.02, "bonus_value":0.05, "upgrade_cost":500},
    3: {"name":"🐛 Ulat Sutera",       "bonus_chance":0.05, "bonus_value":0.10, "upgrade_cost":2000},
    4: {"name":"🦐 Udang Segar",       "bonus_chance":0.08, "bonus_value":0.20, "upgrade_cost":6000},
    5: {"name":"🐟 Ikan Kecil",        "bonus_chance":0.12, "bonus_value":0.30, "upgrade_cost":15000},
    6: {"name":"✨ Umpan Ajaib",       "bonus_chance":0.20, "bonus_value":0.50, "upgrade_cost":40000},
}

BOATS = {
    0: {"name":"❌ Tidak ada",         "bonus_chance":0.00, "bonus_value":0.00, "buy_cost":0},
    1: {"name":"🚣 Perahu Kayu",       "bonus_chance":0.05, "bonus_value":0.10, "buy_cost":3000},
    2: {"name":"⛵ Perahu Layar",      "bonus_chance":0.10, "bonus_value":0.20, "buy_cost":10000},
    3: {"name":"🚤 Speedboat",         "bonus_chance":0.15, "bonus_value":0.40, "buy_cost":30000},
    4: {"name":"🛥 Kapal Nelayan",     "bonus_chance":0.20, "bonus_value":0.60, "buy_cost":80000},
}

# ── BOOSTS ─────────────────────────────────────────────────────────────────────
BOOSTS = {
    "minuman_energi":  {"name":"⚡ Minuman Energi",   "effect":"rare_chance", "value":0.10, "duration":3600,  "cost":500,  "emoji":"⚡"},
    "umpan_premium":   {"name":"🌟 Umpan Premium",    "effect":"value_bonus",  "value":0.50, "duration":3600,  "cost":800,  "emoji":"🌟"},
    "joran_beruntung": {"name":"🍀 Joran Beruntung",  "effect":"rare_chance", "value":0.20, "duration":7200,  "cost":1500, "emoji":"🍀"},
    "radar_ikan":      {"name":"📡 Radar Ikan",       "effect":"guaranteed",   "value":1.00, "duration":1800,  "cost":2000, "emoji":"📡"},
    "elixir_legenda":  {"name":"💎 Elixir Legenda",   "effect":"legendary",    "value":0.10, "duration":3600,  "cost":5000, "emoji":"💎"},
}

# ── SHOP ITEMS ─────────────────────────────────────────────────────────────────
SHOP_ITEMS = {
    "perahu_kayu":    {"name":"🚣 Perahu Kayu",     "type":"boat",  "boat_level":1, "cost":3000},
    "perahu_layar":   {"name":"⛵ Perahu Layar",    "type":"boat",  "boat_level":2, "cost":10000},
    "speedboat":      {"name":"🚤 Speedboat",        "type":"boat",  "boat_level":3, "cost":30000},
    "kapal_nelayan":  {"name":"🛥 Kapal Nelayan",   "type":"boat",  "boat_level":4, "cost":80000},
}

# ── EVENTS ─────────────────────────────────────────────────────────────────────
EVENTS = [
    {
        "name": "🎃 Halloween Fishing",
        "description": "Ikan-ikan misterius muncul di malam Halloween!",
        "bonus": "2x XP untuk semua tangkapan",
        "period": "31 Oktober - 2 November",
        "active": False
    },
    {
        "name": "🎄 Christmas Event",
        "description": "Santa Fish berkeliaran di semua peta!",
        "bonus": "50% bonus koin",
        "period": "24 - 26 Desember",
        "active": False
    },
    {
        "name": "🌸 Sakura Festival",
        "description": "Koi Langka bermunculan di Sungai Sakura!",
        "bonus": "3x chance Legendary",
        "period": "1 - 7 April",
        "active": True
    }
]

# ── VIP PERKS ──────────────────────────────────────────────────────────────────
VIP_LEVELS = {
    1: {"name":"⭐ VIP Bronze",  "cost_coins":10000,  "cost_gems":0,  "perks":["10% bonus koin","5% rare chance","Cooldown -10%"]},
    2: {"name":"🌟 VIP Silver",  "cost_coins":0,      "cost_gems":50, "perks":["25% bonus koin","10% rare chance","Cooldown -20%","Daily bonus x2"]},
    3: {"name":"💎 VIP Gold",    "cost_coins":0,      "cost_gems":150,"perks":["50% bonus koin","20% rare chance","Cooldown -30%","Daily bonus x3","Akses semua peta"]},
    4: {"name":"👑 VIP Diamond", "cost_coins":0,      "cost_gems":500,"perks":["100% bonus koin","30% rare chance","Cooldown -50%","Daily bonus x5","Badge eksklusif"]},
}


def catch_fish(map_id: str, rod_level: int, bait_level: int, boat_level: int,
               active_boost: str = None, vip_level: int = 0) -> Dict:
    """Main fishing logic — returns a fish dict or None for miss/trash."""
    map_data = MAPS.get(map_id, MAPS["sungai"])
    rod = RODS.get(rod_level, RODS[1])
    bait = BAITS.get(bait_level, BAITS[1])
    boat = BOATS.get(boat_level, BOATS[0])

    # Base catch chance (80%)
    catch_chance = 0.80
    catch_chance += rod['bonus_chance'] + bait['bonus_chance'] + boat['bonus_chance']
    if vip_level >= 1:
        catch_chance += 0.05

    # Boost modifiers
    rare_boost = 0.0
    value_boost = 0.0
    legendary_boost = 0.0
    guaranteed = False
    if active_boost and active_boost in BOOSTS:
        boost = BOOSTS[active_boost]
        if boost['effect'] == 'rare_chance':
            rare_boost = boost['value']
        elif boost['effect'] == 'value_bonus':
            value_boost = boost['value']
        elif boost['effect'] == 'guaranteed':
            guaranteed = True
        elif boost['effect'] == 'legendary':
            legendary_boost = boost['value']

    # VIP rare bonus
    vip_rare_bonus = [0, 0.05, 0.10, 0.20, 0.30].get(vip_level, 0) if isinstance(vip_level, int) else 0
    # but dict.get doesn't work on list; fix:
    vip_bonuses = [0, 0.05, 0.10, 0.20, 0.30]
    vip_rare_bonus = vip_bonuses[min(vip_level, 4)]

    if not guaranteed and random.random() > catch_chance:
        return None  # Miss

    # Choose fish from pool
    pool = map_data['fish_pool']
    fish_pool_data = [FISH_DATA[f] for f in pool if f in FISH_DATA]
    if not fish_pool_data:
        return None

    # Apply rarity weights with boosts
    rarities_in_pool = list({f['rarity'] for f in fish_pool_data})
    weighted = []
    for fish in fish_pool_data:
        w = RARITY_WEIGHTS.get(fish['rarity'], 1)
        if fish['rarity'] in ('Rare', 'Epic', 'Legendary'):
            w = w * (1 + rare_boost + vip_rare_bonus)
        if fish['rarity'] == 'Legendary':
            w = w * (1 + legendary_boost)
        weighted.append(w)

    chosen_fish = random.choices(fish_pool_data, weights=weighted, k=1)[0].copy()

    # Randomize weight
    wmin, wmax = chosen_fish['weight_range']
    chosen_fish['weight'] = round(random.uniform(wmin, wmax), 2)

    # Calculate value
    weight_bonus = chosen_fish['weight'] / wmax
    base_val = chosen_fish['base_value']
    val = base_val + int(base_val * weight_bonus * 0.5)
    val += int(val * (rod['bonus_value'] + bait['bonus_value'] + boat['bonus_value']))
    val += int(val * value_boost)
    chosen_fish['value'] = val
    chosen_fish['map'] = map_id

    return chosen_fish
