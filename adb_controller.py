# ============================================================
#  adb_controller.py — Kontrol HP Android via ADB
# ============================================================

import subprocess
import base64
import time
import os
from config import ADB_PATH, DEVICE_SERIAL, DEBUG_MODE, DEBUG_FOLDER


def _adb(args: list[str]) -> str:
    """Jalankan perintah ADB, return output string."""
    cmd = [ADB_PATH]
    if DEVICE_SERIAL:
        cmd += ["-s", DEVICE_SERIAL]
    cmd += args
    result = subprocess.run(cmd, capture_output=True)
    return result.stdout.decode("utf-8", errors="ignore").strip()


def get_devices() -> list[str]:
    """Daftar device ADB yang terhubung."""
    out = _adb(["devices"])
    lines = out.strip().splitlines()[1:]
    return [l.split()[0] for l in lines if "device" in l]


def screencap() -> bytes:
    """Ambil screenshot layar HP, return bytes PNG."""
    cmd = [ADB_PATH]
    if DEVICE_SERIAL:
        cmd += ["-s", DEVICE_SERIAL]
    cmd += ["exec-out", "screencap", "-p"]
    result = subprocess.run(cmd, capture_output=True)
    return result.stdout


def screencap_base64() -> str:
    """Ambil screenshot, return string base64 (untuk Claude API)."""
    raw = screencap()
    b64 = base64.standard_b64encode(raw).decode("utf-8")

    if DEBUG_MODE:
        os.makedirs(DEBUG_FOLDER, exist_ok=True)
        ts = int(time.time())
        path = os.path.join(DEBUG_FOLDER, f"screen_{ts}.png")
        with open(path, "wb") as f:
            f.write(raw)
        print(f"[DEBUG] Screenshot disimpan: {path}")

    return b64


def tap(x: int, y: int):
    """Tap koordinat (x, y)."""
    _adb(["shell", "input", "tap", str(x), str(y)])
    print(f"[ADB] Tap → ({x}, {y})")


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 350):
    """Swipe dari (x1,y1) ke (x2,y2) dalam duration_ms milidetik."""
    _adb(["shell", "input", "swipe",
          str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
    print(f"[ADB] Swipe ({x1},{y1}) → ({x2},{y2}) | {duration_ms}ms")


def open_url(url: str):
    """Buka URL di Chrome Android."""
    _adb(["shell", "am", "start", "-a", "android.intent.action.VIEW",
          "-d", url, "com.android.chrome"])
    print(f"[ADB] Buka URL: {url}")


def get_screen_size() -> tuple[int, int]:
    """Return (width, height) resolusi layar HP."""
    out = _adb(["shell", "wm", "size"])
    # Format: "Physical size: 1080x2400"
    try:
        size = out.split(":")[-1].strip()
        w, h = size.split("x")
        return int(w), int(h)
    except Exception:
        print("[ADB] Gagal baca resolusi, pakai default 1080x2400")
        return 1080, 2400


def press_back():
    """Tekan tombol Back."""
    _adb(["shell", "input", "keyevent", "4"])


def keep_screen_on():
    """Paksa layar tetap menyala."""
    _adb(["shell", "settings", "put", "system", "screen_off_timeout", "600000"])
    print("[ADB] Screen timeout diset ke 10 menit")
