# 🎣 Fishing Game Bot - Telegram

Bot game memancing lengkap untuk Telegram dengan sistem RPG.

---

## 📋 Fitur

| Perintah | Fungsi |
|---|---|
| /start | 📥 Daftar Akun |
| /profil | 👤 Informasi Pemain |
| /fishing | 🎣 Mulai Memancing |
| /map | 🗺 Pilih Tempat Mancing |
| /boost | ⚡ Aktifkan Effect Boost |
| /bag | 🎒 Lihat Ikan di Tas |
| /equipment | 🛠 Peralatan Aktif |
| /upgrade | ⬆️ Upgrade Joran / Umpan |
| /daily | 🎁 Hadiah Harian |
| /history | 📖 Riwayat Tangkapan |
| /vip | 👑 Status & Pembelian VIP |
| /shop | 🛒 Beli Peralatan |
| /market | 💹 Jual / Beli Ikan Antar Pemain |
| /favorite | ⭐ Ikan Favorit |
| /collection | 🌟 Koleksi Spesies Ikan |
| /transfer | ➡️ Transfer Ikan ke Pemain Lain |
| /topup | 💰 Beli COIN / VIP |
| /event | 🗓 Info Event |
| /leaderboard | 🏆 Peringkat Pemain |
| /help | ⛑ Bantuan |

---

## 🚀 Cara Install & Menjalankan

### 1. Buat Bot di Telegram
1. Buka [@BotFather](https://t.me/BotFather) di Telegram
2. Kirim `/newbot`
3. Ikuti langkah-langkah dan salin **TOKEN** yang diberikan

### 2. Install Python & Dependencies
```bash
# Pastikan Python 3.10+ terinstall
python --version

# Install library
pip install -r requirements.txt
```

### 3. Konfigurasi Bot
Edit file `config.py`:
```python
BOT_TOKEN = "ISI_TOKEN_BOT_KAMU_DI_SINI"
GROUP_LINK = "https://t.me/group_kamu"
CHANNEL_LINK = "https://t.me/channel_kamu"
```

### 4. Jalankan Bot
```bash
python bot.py
```

---

## 🗂 Struktur File
```
fishing_bot/
├── bot.py           # Entry point utama
├── config.py        # Konfigurasi token & settings
├── database.py      # Manager database SQLite
├── game_data.py     # Data ikan, peta, peralatan
├── requirements.txt
└── handlers/
    ├── start.py     # /start & register
    ├── profile.py   # /profil
    ├── fishing.py   # /fishing (core game)
    ├── map.py       # /map
    ├── boost.py     # /boost, /bag, /equipment, /upgrade
    └── daily.py     # semua handler lainnya
```

---

## 🎮 Sistem Game

### Rarity Ikan
| Rarity | Simbol | Kelangkaan |
|---|---|---|
| Common | ⚪ | 50% |
| Uncommon | 🟢 | 25% |
| Rare | 🔵 | 15% |
| Epic | 🟣 | 7% |
| Legendary | 🟡 | 3% |

### Peta Tersedia
| Peta | Buka di Level | Biaya |
|---|---|---|
| 🏞 Sungai Desa | 1 | Gratis |
| 🏔 Danau Pegunungan | 5 | 2,000 koin |
| 🌊 Pantai Biru | 10 | 5,000 koin |
| 🌑 Laut Dalam | 20 | 15,000 koin |
| 🌸 Sungai Sakura | 30 | 30,000 koin |

### Upgrade Equipment
- **Joran**: 6 level (Bambu → Bambu → Fiber → Karbon → Titanium → Master → Legenda)
- **Umpan**: 6 level (Cacing → Jangkrik → Ulat Sutera → Udang → Ikan Kecil → Ajaib)
- **Perahu**: 4 jenis (Kayu → Layar → Speedboat → Kapal Nelayan)

---

## 🐛 Troubleshooting

**Error: `ModuleNotFoundError: No module named 'telegram'`**
```bash
pip install python-telegram-bot==20.7
```

**Bot tidak merespons?**
- Pastikan TOKEN benar di `config.py`
- Cek apakah bot sudah di-start dengan `/start` di BotFather

---

## 📞 Kontak
Hubungi admin untuk topup atau pertanyaan.
