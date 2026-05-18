# ============================================================
#  adb_utils.py — ADB Utilities untuk Training Bot OutiePutt
#  Resolusi target: 720x1600
#  Tidak pakai force-stop. Tidak pakai delay statis sebagai
#  metode utama — semua wait pakai polling screenshot.
# ============================================================

import subprocess
import base64
import time
import os
import json

# ── Config ──────────────────────────────────────────────────
ADB_PATH       = "adb"      # Ganti ke full path jika perlu
DEVICE_SERIAL  = None       # None = auto, atau isi "XXXXX"
DEBUG_MODE     = True
DEBUG_FOLDER   = "debug_screenshots"

# ── Timeout defaults ────────────────────────────────────────
DEFAULT_POLL_INTERVAL = 0.8   # detik antar screenshot polling
DEFAULT_TIMEOUT       = 30    # detik maksimum wait


# ============================================================
#  INTERNAL ADB RUNNER
# ============================================================

def _adb(args: list) -> str:
    cmd = [ADB_PATH]
    if DEVICE_SERIAL:
        cmd += ["-s", DEVICE_SERIAL]
    cmd += args
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=15)
        return result.stdout.decode("utf-8", errors="ignore").strip()
    except subprocess.TimeoutExpired:
        print(f"[ADB] ⚠️  Timeout: {' '.join(args)}")
        return ""
    except Exception as e:
        print(f"[ADB] ❌ Error: {e}")
        return ""


# ============================================================
#  DEVICE INFO
# ============================================================

def get_devices() -> list:
    out = _adb(["devices"])
    lines = out.strip().splitlines()[1:]
    return [l.split()[0] for l in lines if "\tdevice" in l]


def get_screen_size() -> tuple:
    out = _adb(["shell", "wm", "size"])
    try:
        size = out.split(":")[-1].strip()
        # kadang ada "Override size:" — ambil yang terakhir
        w, h = size.split("x")
        return int(w.strip()), int(h.strip())
    except Exception:
        print("[ADB] ⚠️  Gagal baca resolusi, pakai default 720x1600")
        return 720, 1600


def keep_screen_on():
    _adb(["shell", "settings", "put", "system", "screen_off_timeout", "600000"])
    print("[ADB] ✅ Screen timeout → 10 menit")


# ============================================================
#  SCREENSHOT
# ============================================================

def screencap_bytes() -> bytes:
    """Ambil screenshot, return raw PNG bytes."""
    cmd = [ADB_PATH]
    if DEVICE_SERIAL:
        cmd += ["-s", DEVICE_SERIAL]
    cmd += ["exec-out", "screencap", "-p"]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        return result.stdout
    except Exception as e:
        print(f"[ADB] ❌ screencap gagal: {e}")
        return b""


def screencap_base64(save_debug: bool = True) -> str:
    """Ambil screenshot, return base64 string (untuk Claude API)."""
    raw = screencap_bytes()
    if not raw:
        return ""
    b64 = base64.standard_b64encode(raw).decode("utf-8")

    if DEBUG_MODE and save_debug:
        os.makedirs(DEBUG_FOLDER, exist_ok=True)
        ts = int(time.time() * 1000)
        path = os.path.join(DEBUG_FOLDER, f"screen_{ts}.png")
        with open(path, "wb") as f:
            f.write(raw)

    return b64


def screencap_save(path: str) -> bool:
    """Simpan screenshot ke file path tertentu."""
    raw = screencap_bytes()
    if not raw:
        return False
    with open(path, "wb") as f:
        f.write(raw)
    return True


# ============================================================
#  TAP & SWIPE
# ============================================================

def tap(x: int, y: int, label: str = ""):
    """Tap koordinat (x, y)."""
    _adb(["shell", "input", "tap", str(int(x)), str(int(y))])
    tag = f" [{label}]" if label else ""
    print(f"[ADB] 👆 Tap{tag} → ({int(x)}, {int(y)})")


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 850):
    """Swipe dari (x1,y1) ke (x2,y2)."""
    _adb(["shell", "input", "swipe",
          str(int(x1)), str(int(y1)),
          str(int(x2)), str(int(y2)),
          str(int(duration_ms))])
    print(f"[ADB] ↔️  Swipe ({int(x1)},{int(y1)}) → ({int(x2)},{int(y2)}) | {duration_ms}ms")


def execute_shot(shot: dict):
    """
    Eksekusi tembakan dari dict best_shot atau adb_scaled_shot.
    shot harus punya: start_x, start_y, end_x, end_y, duration_ms
    """
    swipe(
        shot["start_x"], shot["start_y"],
        shot["end_x"],   shot["end_y"],
        shot.get("duration_ms", 850)
    )


def press_back():
    _adb(["shell", "input", "keyevent", "4"])
    print("[ADB] 🔙 Back key")


# ============================================================
#  LOAD FALLBACK KOORDINAT
# ============================================================

_RECORDED: dict = {}

def load_recorded_touches(path: str = "recorded_touches.json") -> dict:
    global _RECORDED
    try:
        with open(path, "r") as f:
            _RECORDED = json.load(f)
        print(f"[ADB] ✅ Loaded recorded_touches: {list(_RECORDED.keys())}")
    except Exception as e:
        print(f"[ADB] ⚠️  Gagal load recorded_touches.json: {e}")
        _RECORDED = {}
    return _RECORDED


def tap_recorded(label: str) -> bool:
    """
    Tap tombol dari recorded_touches.json berdasarkan label.
    Return True jika berhasil.
    """
    btn = _RECORDED.get(label, {})
    x, y = btn.get("x", 0), btn.get("y", 0)
    if x == 0 and y == 0:
        print(f"[ADB] ⚠️  Fallback '{label}' tidak ditemukan di recorded_touches")
        return False
    tap(x, y, label=f"fallback:{label}")
    return True


# ============================================================
#  WAIT-FOR-UI (polling — TIDAK delay statis)
# ============================================================

def wait_for_ui(
    check_fn,
    timeout: float = DEFAULT_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    label: str = "UI"
) -> tuple:
    """
    Poll screenshot sampai check_fn(b64) return (True, data) atau timeout.

    check_fn(b64: str) -> (bool, any)
      - Return (True, data) jika kondisi terpenuhi
      - Return (False, None) jika belum

    Return (True, data) jika berhasil, (False, None) jika timeout.
    """
    deadline = time.time() + timeout
    attempt  = 0
    print(f"[Wait] ⏳ Menunggu {label} (timeout={timeout}s)...")

    while time.time() < deadline:
        attempt += 1
        b64 = screencap_base64(save_debug=False)
        if not b64:
            time.sleep(poll_interval)
            continue

        ok, data = check_fn(b64)
        if ok:
            print(f"[Wait] ✅ {label} terdeteksi (attempt #{attempt})")
            return True, data

        remaining = deadline - time.time()
        print(f"[Wait]    ... belum ({remaining:.0f}s sisa)", end="\r")
        time.sleep(poll_interval)

    print(f"\n[Wait] ❌ Timeout menunggu {label} setelah {timeout}s")
    return False, None
