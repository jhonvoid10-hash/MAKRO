# ============================================================
#  config.py — Konfigurasi OutiePutt AI Vision Bot
# ============================================================

# --- GEMINI API ---
# Daftar gratis di: https://aistudio.google.com/app/apikey
# Ganti dengan API key kamu (AIza...)
GEMINI_API_KEY = "AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"   # ← Isi API key Gemini kamu
GEMINI_MODEL   = "gemini-2.0-flash"                          # Model Gemini Vision (gratis & cepat)

# Legacy aliases — dibiarkan untuk kompatibilitas file lain
GROQ_API_KEY    = GEMINI_API_KEY
GROQ_MODEL      = GEMINI_MODEL
CLAUDE_API_KEY  = GEMINI_API_KEY
CLAUDE_MODEL    = GEMINI_MODEL
CLAUDE_BASE_URL = ""

# --- ADB ---
ADB_PATH        = "adb"          # Kalau adb tidak di PATH, isi full path: "C:/platform-tools/adb.exe"
DEVICE_SERIAL   = None           # None = otomatis, atau isi: "emulator-5554" / "R9WR30XXXXX"

# --- GAME ---
TOTAL_HOLES     = 9              # Jumlah hole dalam satu game
MAX_SHOTS_HOLE  = 6              # Maksimal tembakan per hole sebelum skip

# --- DELAY (detik) ---
DELAY_AFTER_SHOT       = 2.5    # Tunggu bola berhenti
DELAY_HOLE_TRANSITION  = 2.0    # Tunggu transisi antar hole
DELAY_GAME_LOAD        = 4.0    # Tunggu game pertama load
DELAY_SCREENSHOT       = 0.5    # Jeda sebelum ambil screenshot

# --- SWIPE ---
SWIPE_DURATION_MS = 350         # Durasi swipe (ms) — jangan terlalu cepat
MIN_DRAG_PX       = 80          # Minimum panjang drag
MAX_DRAG_PX       = 500         # Maksimum panjang drag

# --- DEBUG ---
DEBUG_MODE        = True         # True = simpan screenshot & log detail
DEBUG_FOLDER      = "debug_screenshots"
