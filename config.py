# ============================================================
#  config.py — Konfigurasi OutiePutt AI Vision Bot
# ============================================================

# --- KIRO / CLAUDE API ---
# Isi dengan API key dari Kiro (ksk_...) atau Anthropic (sk-ant-...)
CLAUDE_API_KEY = "ksk_XXXXXXXXXXXXXXXXXXXXXXXX"   # Ganti dengan ksk_... dari Kiro Settings → API Keys
CLAUDE_MODEL   = "claude-opus-4-5"                # Model Claude yang dipakai

# Kiro API endpoint (compatible dengan Anthropic SDK)
# Kalau pakai Kiro key (ksk_...), set ini. Kalau Anthropic langsung, kosongkan.
CLAUDE_BASE_URL = "https://api.kiro.dev/v1"       # Endpoint Kiro API

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
