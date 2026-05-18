# ============================================================
#  vision_utils.py — Deteksi UI via Claude Vision API
#  Fungsi:
#    wait_for_play_solo()
#    wait_for_game_ready()
#    wait_for_continue()
#    wait_for_yes_confirm()
#    detect_state(b64, level_hint) -> dict
# ============================================================

import anthropic
import json
import re
import time

from config        import CLAUDE_API_KEY, CLAUDE_MODEL
from adb_utils     import wait_for_ui, screencap_base64, tap, tap_recorded
from level_mapping import get_prompt_context, get_mapping

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# ── Timeout per kondisi ──────────────────────────────────────
TIMEOUT_PLAY_SOLO   = 20
TIMEOUT_GAME_READY  = 25
TIMEOUT_CONTINUE    = 30
TIMEOUT_YES_CONFIRM = 15
POLL_INTERVAL       = 0.8

# ── State yang dianggap "game ready / siap tembak" ───────────
GAME_READY_STATES = {"game_ready", "ready_to_shoot", "in_game"}

# ── Level hint aktif (di-set dari training loop) ─────────────
_active_level: int = 0


def set_active_level(level: int):
    """Set level aktif agar detect_state bisa inject mapping context."""
    global _active_level
    _active_level = level


# ============================================================
#  PROMPT CLAUDE — BASE STATE DETECTION
# ============================================================

_DETECT_PROMPT_BASE = """
Kamu adalah AI yang menganalisis screenshot game billiard/golf web (app.outieputt.com).

Identifikasi state layar saat ini dan kembalikan JSON.

State yang mungkin:
- "lobby"        : layar lobby/menu utama. Ada tombol PLAY SOLO atau JOIN.
- "game_ready"   : game sudah dimuat, meja billiard terlihat, bola putih ada, siap tembak.
- "ball_moving"  : bola sedang bergerak/rolling, belum berhenti.
- "continue"     : bola sudah masuk hole, muncul tombol CONTINUE atau NEXT.
- "yes_confirm"  : popup konfirmasi keluar game. Ada tombol YES/CONFIRM dan NO/CANCEL.
- "loading"      : layar loading, spinner, atau transisi.
- "other"        : layar lain yang tidak dikenali.

Untuk setiap tombol yang relevan, berikan koordinat x,y TENGAH tombol (pixel).

Balas HANYA JSON ini (tanpa teks lain):
{
  "state": "...",
  "play_solo":    {"x": 0, "y": 0, "visible": false},
  "continue_btn": {"x": 0, "y": 0, "visible": false},
  "close_x":      {"x": 0, "y": 0, "visible": false},
  "yes_btn":      {"x": 0, "y": 0, "visible": false},
  "level_number": 0,
  "notes": "..."
}
"""

_GAME_READY_PROMPT_SUFFIX = """
Tambahan untuk state game_ready — jika kamu melihat bola putih dan hole target:
- "ball_pos":   {"x": 0, "y": 0}   koordinat TENGAH bola putih
- "hole_pos":   {"x": 0, "y": 0}   koordinat TENGAH hole/target
- "obstacle_warning": ""           deskripsi obstacle yang harus dihindari

Sertakan field ini di JSON jika state = game_ready.
"""


def _build_prompt(level_hint: int, screen_w: int, screen_h: int) -> str:
    """
    Bangun prompt deteksi dengan optional level mapping context.
    Kalau level_hint > 0, inject strategi mapping level tersebut.
    """
    base = _DETECT_PROMPT_BASE + _GAME_READY_PROMPT_SUFFIX
    base += f"\n\nResolusi layar: {screen_w}x{screen_h}px"

    if level_hint and 1 <= level_hint <= 18:
        ctx = get_prompt_context(level_hint)
        base += f"\n\n{ctx}"
        m = get_mapping(level_hint)
        if m.get("timing_sensitive"):
            base += "\n\nPERHATIAN: Level ini TIMING SENSITIVE — ada obstacle bergerak."
        if m.get("uses_portal") in (True, "maybe"):
            base += (
                "\n\nCATATAN PORTAL: Level ini mungkin punya portal/trap hole. "
                "Bedakan hole target asli (berflag) dari portal/trap."
            )

    return base


# ============================================================
#  CORE: DETECT STATE
# ============================================================

def detect_state(b64: str,
                 screen_w: int = 720,
                 screen_h: int = 1600,
                 level_hint: int = 0) -> dict:
    """
    Kirim screenshot ke Claude, return dict state + koordinat tombol.
    level_hint: jika > 0, inject mapping context level tersebut ke prompt.
    Selalu return dict — tidak raise exception.
    """
    # Gunakan _active_level global jika level_hint tidak disuplai
    effective_level = level_hint if level_hint else _active_level

    prompt = _build_prompt(effective_level, screen_w, screen_h)

    try:
        resp = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": b64,
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )
        raw    = resp.content[0].text.strip()
        result = _parse_json(raw)

        # Tambahkan level_hint ke result agar caller tahu konteks
        if effective_level:
            result["_level_hint"] = effective_level

        # Log obstacle warning jika ada
        warn = result.get("obstacle_warning", "")
        if warn:
            print(f"[Vision] ⚠️  Obstacle: {warn}")

        return result

    except Exception as e:
        print(f"[Vision] ❌ detect_state error: {e}")
        return {"state": "error", "notes": str(e)}


def _parse_json(text: str) -> dict:
    """Robust JSON parser — coba berbagai format."""
    # Langsung parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Dari code block ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Extract { ... } pertama
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {"state": "parse_error", "notes": text[:200]}


# ============================================================
#  CHECK FUNCTIONS — dipakai oleh wait_for_ui()
# ============================================================

def _check_play_solo(b64: str) -> tuple:
    result = detect_state(b64, level_hint=0)   # lobby → no level context
    state  = result.get("state", "")
    btn    = result.get("play_solo", {})
    if state == "lobby" and btn.get("visible", False):
        return True, result
    if state == "lobby" and btn.get("x", 0) > 0:
        return True, result
    return False, None


def _check_game_ready(b64: str) -> tuple:
    result = detect_state(b64, level_hint=_active_level)
    state  = result.get("state", "")
    if state in GAME_READY_STATES:
        return True, result
    return False, None


def _check_continue(b64: str) -> tuple:
    result = detect_state(b64, level_hint=_active_level)
    state  = result.get("state", "")
    btn    = result.get("continue_btn", {})
    if state == "continue":
        return True, result
    if btn.get("visible", False) and btn.get("x", 0) > 0:
        return True, result
    return False, None


def _check_yes_confirm(b64: str) -> tuple:
    result = detect_state(b64, level_hint=0)   # confirm popup → no level context
    state  = result.get("state", "")
    btn    = result.get("yes_btn", {})
    if state == "yes_confirm":
        return True, result
    if btn.get("visible", False) and btn.get("x", 0) > 0:
        return True, result
    return False, None


# ============================================================
#  PUBLIC WAIT FUNCTIONS
# ============================================================

def wait_for_play_solo(timeout: float = TIMEOUT_PLAY_SOLO) -> tuple:
    """
    Tunggu layar lobby + tombol PLAY SOLO muncul.
    Return (True, detection_result) atau (False, None).
    """
    return wait_for_ui(
        check_fn=_check_play_solo,
        timeout=timeout,
        poll_interval=POLL_INTERVAL,
        label="PLAY SOLO"
    )


def wait_for_game_ready(timeout: float = TIMEOUT_GAME_READY) -> tuple:
    """
    Tunggu layar game ready (meja billiard, bola putih terlihat).
    Return (True, detection_result) atau (False, None).
    """
    return wait_for_ui(
        check_fn=_check_game_ready,
        timeout=timeout,
        poll_interval=POLL_INTERVAL,
        label="GAME READY"
    )


def wait_for_continue(timeout: float = TIMEOUT_CONTINUE) -> tuple:
    """
    Tunggu tombol CONTINUE muncul setelah bola masuk hole.
    Return (True, detection_result) atau (False, None).
    """
    return wait_for_ui(
        check_fn=_check_continue,
        timeout=timeout,
        poll_interval=POLL_INTERVAL,
        label="CONTINUE"
    )


def wait_for_yes_confirm(timeout: float = TIMEOUT_YES_CONFIRM) -> tuple:
    """
    Tunggu popup YES/CONFIRM muncul.
    Return (True, detection_result) atau (False, None).
    """
    return wait_for_ui(
        check_fn=_check_yes_confirm,
        timeout=timeout,
        poll_interval=POLL_INTERVAL,
        label="YES CONFIRM"
    )


# ============================================================
#  TAP BUTTON — coba Vision dulu, fallback ke recorded_touches
# ============================================================

def tap_button(label: str, detection: dict = None):
    """
    Tap tombol berdasarkan label.
    Prioritas:
      1. Koordinat dari hasil detection Claude (jika tersedia & valid)
      2. Fallback dari recorded_touches.json

    label: "play_solo" | "continue" | "close_x" | "yes_confirm"
    """
    # Map label ke key di detection result
    key_map = {
        "play_solo":   "play_solo",
        "continue":    "continue_btn",
        "close_x":     "close_x",
        "yes_confirm": "yes_btn",
        "play_again":  "play_solo",  # sama lokasinya
    }

    vision_key = key_map.get(label)
    tapped = False

    # Coba dari detection Claude
    if detection and vision_key:
        btn = detection.get(vision_key, {})
        x, y = btn.get("x", 0), btn.get("y", 0)
        if x > 0 and y > 0:
            tap(x, y, label=f"vision:{label}")
            tapped = True

    # Fallback recorded_touches
    if not tapped:
        print(f"[Vision] ⚠️  Koordinat '{label}' dari Vision tidak valid, pakai fallback")
        tap_recorded(label)


# ============================================================
#  QUICK STATE CHECK
# ============================================================

def get_current_state(level_hint: int = 0) -> dict:
    """Ambil screenshot sekarang dan deteksi state via Claude."""
    b64 = screencap_base64(save_debug=True)
    if not b64:
        return {"state": "error", "notes": "screencap gagal"}
    effective = level_hint if level_hint else _active_level
    return detect_state(b64, level_hint=effective)


def wait_for_game_ready_at_level(level: int,
                                  timeout: float = TIMEOUT_GAME_READY) -> tuple:
    """
    Versi wait_for_game_ready dengan level mapping context aktif.
    Set _active_level ke level ini, lalu tunggu game_ready.
    """
    set_active_level(level)
    return wait_for_game_ready(timeout=timeout)
