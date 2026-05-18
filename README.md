# 🏌️ OutiePutt AI Vision Bot

Bot otomatis untuk main game **Golf Billiard** di [app.outieputt.com](https://app.outieputt.com/) menggunakan **Claude AI Vision** + **ADB Android**.

```
HP Android (game jalan)
      ↓ screenshot via ADB
PC/Laptop (Python script)
      ↓ kirim ke Claude AI
Claude API (analisis posisi bola & hole)
      ↓ balik koordinat tembakan
PC/Laptop
      ↓ adb shell input swipe
HP Android (bola ditembak otomatis) 🎯
```

---

## 📂 Struktur File

```
MAKRO/
├── main.py              ← Script utama — jalankan ini
├── vision.py            ← Analisis screenshot via Claude AI
├── adb_controller.py    ← Kontrol HP via ADB (tap/swipe/screencap)
├── config.py            ← Konfigurasi (API key, delay, dll)
└── README.md            ← Panduan ini
```

---

## ✅ Persyaratan

### Di PC/Laptop:
| Kebutuhan | Cara Install |
|-----------|-------------|
| Python 3.10+ | [python.org](https://python.org) |
| Library `anthropic` | `pip install anthropic` |
| ADB (Android Debug Bridge) | [Download Platform Tools](https://developer.android.com/tools/releases/platform-tools) |

### Di HP Android:
| Kebutuhan | Cara Aktifkan |
|-----------|--------------|
| USB Debugging | Pengaturan → Tentang HP → ketuk "Nomor Build" 7x → Opsi Developer → USB Debugging ✅ |
| Browser Chrome | Sudah terinstall default |
| Kabel USB | Sambungkan ke PC |

### API Key Claude:
1. Daftar di [console.anthropic.com](https://console.anthropic.com)
2. Buat API Key baru
3. Isi di `config.py` → `CLAUDE_API_KEY`

---

## 🚀 Cara Pakai

### 1. Install dependencies
```bash
pip install anthropic
```

### 2. Setup ADB
```bash
# Pastikan ADB terinstall
adb version

# Cek HP terdeteksi (sambungkan USB dulu, klik Allow di HP)
adb devices
```

### 3. Edit config.py
```python
CLAUDE_API_KEY = "sk-ant-xxxxxxxxxxxx"   # ← Isi API key kamu
ADB_PATH       = "adb"                   # ← Kalau adb tidak di PATH, isi full path
```

### 4. Buka game di HP
- Buka Chrome di HP
- Navigasi ke `https://app.outieputt.com/`
- Biarkan game tampil di layar

### 5. Jalankan bot
```bash
python main.py
```

Bot akan otomatis:
1. 📸 Screenshot layar HP
2. 🤖 Kirim ke Claude AI untuk analisis
3. 🎯 Hitung arah & kekuatan tembakan
4. 📲 Swipe otomatis via ADB
5. 🔁 Ulangi sampai 9 hole selesai

---

## ⚙️ Konfigurasi (`config.py`)

```python
# API
CLAUDE_API_KEY  = "sk-ant-..."     # API Key Claude (WAJIB diisi)
CLAUDE_MODEL    = "claude-opus-4-5" # Model AI yang dipakai

# ADB
ADB_PATH        = "adb"            # Path ke ADB executable
DEVICE_SERIAL   = None             # None = otomatis, atau "R9WR30XXXXX"

# Game
TOTAL_HOLES     = 9                # Jumlah hole per game
MAX_SHOTS_HOLE  = 6                # Maks tembakan per hole

# Delay (detik)
DELAY_AFTER_SHOT      = 2.5       # Tunggu bola berhenti
DELAY_HOLE_TRANSITION = 2.0       # Tunggu transisi hole
DELAY_GAME_LOAD       = 4.0       # Tunggu game pertama load

# Debug
DEBUG_MODE      = True             # True = simpan screenshot ke folder debug/
```

---

## 🧠 Cara Kerja AI Vision

Setiap loop, bot melakukan:

```
1. adb exec-out screencap -p  →  PNG bytes
2. Encode ke Base64
3. Kirim ke Claude API dengan prompt:
   "Dimana posisi bola putih? Dimana posisi hole?
    Berapa kekuatan tembakan yang tepat?"
4. Claude balas JSON:
   {
     "state": "ready_to_shoot",
     "ball":  {"x": 540, "y": 1350},
     "hole":  {"x": 200, "y": 480},
     "shot_power": 0.6,
     "notes": "Ada tikungan, tembak ke kiri dulu"
   }
5. Hitung koordinat swipe (drag berlawanan arah hole)
6. adb shell input swipe x1 y1 x2 y2 350
```

### State yang Dikenali Claude:
| State | Aksi Bot |
|-------|----------|
| `start_screen` | Klik tombol Play/Start |
| `loading` | Tunggu 2 detik |
| `ready_to_shoot` | Analisis & tembak bola |
| `ball_moving` | Tunggu bola berhenti |
| `hole_complete` | Klik tombol Next Hole |
| `game_complete` | Tampilkan skor, selesai |

---

## 📊 Contoh Output

```
╔══════════════════════════════════════════╗
║   🏌️  OutiePutt AI Vision Bot v1.0       ║
║   Claude AI + ADB Auto-Play              ║
╚══════════════════════════════════════════╝

✅ Device terhubung: ['R9WR30A1ZGJ']
📐 Resolusi layar: 1080x2400
🌐 Membuka https://app.outieputt.com/...

[State] start_screen | Hole: 1/9
▶️  Klik tombol Play di (540, 1750)

[State] ready_to_shoot | Hole: 1/9 | Shot: 0
[Shot] Bola(540,1350) → Hole(200,480)
[Shot] Sudut: -113.5° | Power: 0.65 | Drag: 282px
[ADB]  Swipe (540,1350) → (651,1462) | 350ms
⏳ Tunggu bola berhenti (2.5s)...

[State] hole_complete | Hole: 1/9
🎉 HOLE 1 SELESAI! (1 tembakan)

...

═══════════════════════════════════════════
🏆 HASIL AKHIR
═══════════════════════════════════════════
  Hole  1:  1 tembakan 🟢
  Hole  2:  2 tembakan 🟢
  Hole  3:  3 tembakan 🟡
  ...
  Total tembakan : 22
  Rata-rata      : 2.4 tembakan/hole
═══════════════════════════════════════════
```

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `adb: command not found` | Tambahkan platform-tools ke PATH atau isi `ADB_PATH` di config |
| `No device connected` | Pastikan USB debugging aktif & sudah klik Allow di HP |
| `AuthenticationError` | API key salah atau expired, cek di console.anthropic.com |
| Bot swipe meleset | Normal di awal — AI belajar dari screenshot, akurasi meningkat setelah beberapa shot |
| Layar mati saat bot jalan | Bot otomatis set screen timeout 10 menit via ADB |
| `hole_complete` tidak terdeteksi | Naikkan `DELAY_AFTER_SHOT` di config.py menjadi 3.0+ |

---

## 💡 Tips

- Gunakan `DEBUG_MODE = True` untuk menyimpan semua screenshot ke folder `debug_screenshots/` — berguna untuk lihat apa yang dilihat AI
- Pastikan **brightness layar HP cukup tinggi** agar screenshot jelas
- Jangan gerakkan HP saat bot jalan
- Kalau punya banyak HP, isi `DEVICE_SERIAL` di config untuk pilih device tertentu

---

## 📄 Lisensi

Free to use — dibuat untuk belajar AI Vision + Android Automation.
