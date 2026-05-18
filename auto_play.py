#!/usr/bin/env python3
# ============================================================
#  auto_play.py — Fully Autonomous OutiePutt Bot
#  Cara pakai:
#    python auto_play.py
#
#  Bot main sendiri Level 1-18, loop terus sampai semua level
#  punya best shot, lalu auto-export ke MacroDroid.
#
#  Tidak butuh input manual sama sekali.
#  Cukup buka game di lobby (ada tombol Play Solo) → jalankan.
# ============================================================

import sys
import os
import json
import time
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adb_utils       import (execute_shot,
                              keep_screen_on, get_devices, get_screen_size,
                              screencap_base64, tap_recorded)
from vision_utils    import (wait_for_play_solo, wait_for_game_ready,
                              wait_for_game_ready_at_level,
                              wait_for_continue, wait_for_yes_confirm,
                              tap_button, get_current_state, set_active_level)
from shot_candidates import get_candidates, total_candidates
from level_mapping   import get_mapping, get_hint_text
from config          import GEMINI_API_KEY

# ── Konstanta ─────────────────────────────────────────────────
TOTAL_LEVELS        = 18
BEST_SHOT_DIR       = "."
WAIT_AFTER_SHOT     = 3.0   # detik setelah swipe, tunggu bola berhenti
MAX_RETRIES_LEVEL   = 2     # coba ulang recovery per level sebelum skip
LOG_FILE            = "auto_play_log.txt"


# ─────────────────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────────────────

def _log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
#  BEST SHOT I/O
# ─────────────────────────────────────────────────────────────

def _best_path(level: int) -> str:
    return os.path.join(BEST_SHOT_DIR, f"level_{level:02d}_best_shot.json")


def load_best(level: int) -> dict | None:
    p = _best_path(level)
    if not os.path.exists(p):
        return None
    try:
        with open(p) as f:
            d = json.load(f)
        shot = d.get("adb_scaled_shot") or d.get("best_shot")
        if shot and shot.get("start_x", 0) > 0:
            return d
    except Exception:
        pass
    return None


def save_best(level: int, candidate: dict, cand_idx: int, run: int):
    # Jangan overwrite yang sudah ada
    if load_best(level):
        return
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "level":           level,
        "status":          "success",
        "source":          "auto_play",
        "candidate_index": cand_idx,
        "run":             run,
        "best_shot": {
            "start_x":    candidate["start_x"],
            "start_y":    candidate["start_y"],
            "end_x":      candidate["end_x"],
            "end_y":      candidate["end_y"],
            "duration_ms": candidate.get("duration_ms", 850),
        },
        "adb_scaled_shot": {
            "start_x":    candidate["start_x"],
            "start_y":    candidate["start_y"],
            "end_x":      candidate["end_x"],
            "end_y":      candidate["end_y"],
            "duration_ms": candidate.get("duration_ms", 850),
            "reverse":    candidate.get("reverse", True),
        },
        "strategy":  candidate.get("strategy", ""),
        "note":      candidate.get("note", ""),
        "saved_at":  now,
    }
    with open(_best_path(level), "w") as f:
        json.dump(data, f, indent=2)
    _log(f"💾 Level {level} best shot disimpan: {_best_path(level)}")


def get_replay_shot(level: int) -> dict | None:
    d = load_best(level)
    if not d:
        return None
    return d.get("adb_scaled_shot") or d.get("best_shot")


def all_done() -> bool:
    return all(load_best(lvl) is not None for lvl in range(1, TOTAL_LEVELS + 1))


def count_done() -> int:
    return sum(1 for lvl in range(1, TOTAL_LEVELS + 1) if load_best(lvl))


# ─────────────────────────────────────────────────────────────
#  CANDIDATE TRACKER  (persisten per sesi, tidak reset saat recover)
# ─────────────────────────────────────────────────────────────

class CandidateTracker:
    """
    Melacak kandidat yang sudah dicoba per level.
    Kalau semua kandidat habis → wrap-around dari index 0 lagi
    (kandidat pertama mungkin berhasil di run berikutnya).
    """
    def __init__(self):
        self._idx: dict[int, int] = {lvl: 0 for lvl in range(1, TOTAL_LEVELS + 1)}
        self._failed: dict[int, set] = {lvl: set() for lvl in range(1, TOTAL_LEVELS + 1)}

    def current(self, level: int) -> dict | None:
        candidates = get_candidates(level)
        if not candidates:
            return None
        idx = self._idx[level]
        return candidates[idx % len(candidates)]

    def current_idx(self, level: int) -> int:
        candidates = get_candidates(level)
        if not candidates:
            return 0
        return self._idx[level] % len(candidates)

    def advance(self, level: int):
        """Pindah ke kandidat berikutnya."""
        candidates = get_candidates(level)
        if not candidates:
            return
        n = len(candidates)
        self._failed[level].add(self._idx[level] % n)
        self._idx[level] = (self._idx[level] + 1) % n

    def reset_level(self, level: int):
        """Reset ke kandidat awal untuk level ini."""
        self._idx[level] = 0

    def all_tried(self, level: int) -> bool:
        n = total_candidates(level)
        return len(self._failed[level]) >= n


_tracker = CandidateTracker()


# ─────────────────────────────────────────────────────────────
#  GAME ACTIONS
# ─────────────────────────────────────────────────────────────

def do_play_solo() -> bool:
    ok, det = wait_for_play_solo(timeout=30)
    if not ok:
        _log("❌ PLAY SOLO tidak muncul dalam 30s")
        return False
    tap_button("play_solo", det)
    _log("▶️  Tap PLAY SOLO")
    return True


def do_wait_ready(level: int) -> bool:
    _log(f"⏳ Tunggu game ready Level {level}...")
    ok, _ = wait_for_game_ready_at_level(level, timeout=30)
    if not ok:
        _log(f"❌ Game ready Level {level} timeout")
    return ok


def do_shot(shot: dict, level: int, cand_idx: int):
    mapping = get_mapping(level)
    strat   = shot.get("strategy", mapping.get("strategy", "?"))
    portal  = "🌀" if shot.get("uses_portal") else ""
    _log(f"🎱 L{level} kandidat#{cand_idx} [{strat}]{portal} "
         f"({shot['start_x']},{shot['start_y']})→({shot['end_x']},{shot['end_y']}) "
         f"{shot.get('duration_ms',850)}ms")
    execute_shot(shot)


def do_wait_continue() -> tuple:
    return wait_for_continue(timeout=35)


def do_tap_continue(det: dict = None):
    tap_button("continue", det)
    _log("➡️  Tap CONTINUE")


def do_close_exit() -> bool:
    """Tap X → tunggu YES → tap YES untuk keluar dari level."""
    _log("🔙 Keluar dari level via X + YES...")
    det = get_current_state()
    tap_button("close_x", det)
    time.sleep(0.8)

    ok, det2 = wait_for_yes_confirm(timeout=12)
    if ok:
        tap_button("yes_confirm", det2)
    else:
        _log("⚠️  YES popup tidak muncul, tap fallback")
        tap_recorded("yes_confirm")
    time.sleep(0.5)
    return True


# ─────────────────────────────────────────────────────────────
#  DETECT WHETHER SHOT SUCCEEDED
#  Setelah swipe, tunggu: apakah muncul CONTINUE (sukses) atau
#  bola masih diam/tidak masuk (gagal)?
# ─────────────────────────────────────────────────────────────

def _wait_shot_result(level: int) -> str:
    """
    Tunggu maksimal WAIT_AFTER_SHOT + 5 detik.
    Return:
      "success"  — tombol CONTINUE muncul (bola masuk hole)
      "fail"     — timeout / bola tidak masuk
    """
    time.sleep(WAIT_AFTER_SHOT)
    ok, det = do_wait_continue()
    if ok:
        return "success", det
    return "fail", None


# ─────────────────────────────────────────────────────────────
#  REPLAY ALL LEVELS UP TO target-1
# ─────────────────────────────────────────────────────────────

def replay_to(target_level: int) -> bool:
    """
    Setelah PLAY SOLO + game ready Level 1,
    replay Level 1..target_level-1 pakai best shot tersimpan.
    Return True jika berhasil sampai target_level game ready.
    """
    if target_level <= 1:
        return True

    _log(f"▶▶ Replay Level 1 → {target_level-1}...")
    for lvl in range(1, target_level):
        shot = get_replay_shot(lvl)
        if not shot:
            _log(f"❌ Tidak ada best shot Level {lvl}, tidak bisa replay!")
            return False

        if not do_wait_ready(lvl):
            return False

        do_shot(shot, lvl, -1)
        time.sleep(WAIT_AFTER_SHOT)

        ok, det = do_wait_continue()
        if not ok:
            _log(f"❌ CONTINUE Level {lvl} tidak muncul saat replay!")
            return False

        do_tap_continue(det)
        _log(f"✅ Replay Level {lvl} selesai")

    if not do_wait_ready(target_level):
        return False
    _log(f"✅ Siap di Level {target_level}")
    return True


# ─────────────────────────────────────────────────────────────
#  RECOVER: Keluar → lobby → PLAY SOLO → replay ke target
# ─────────────────────────────────────────────────────────────

def recover_and_go(target_level: int) -> bool:
    """Keluar dari level, balik ke lobby, masuk lagi ke target_level."""
    _log(f"🔄 Recovery ke Level {target_level}...")

    do_close_exit()

    ok, det = wait_for_play_solo(timeout=25)
    if not ok:
        _log("❌ Lobby tidak muncul setelah exit!")
        return False

    tap_button("play_solo", det)
    _log("▶️  Tap PLAY SOLO setelah recovery")

    if not do_wait_ready(1):
        return False

    return replay_to(target_level)


# ─────────────────────────────────────────────────────────────
#  PLAY ONE LEVEL (autonomous — deteksi sukses/gagal sendiri)
# ─────────────────────────────────────────────────────────────

def play_level(level: int, run: int) -> str:
    """
    Coba satu kandidat shot di level ini.
    Return:
      "success"   — bola masuk, best shot disimpan
      "fail"      — bola tidak masuk, perlu recover & coba lagi
      "no_shot"   — tidak ada kandidat
    """
    cand = _tracker.current(level)
    if cand is None:
        _log(f"⚠️  Level {level} tidak punya kandidat!")
        return "no_shot"

    cand_idx = _tracker.current_idx(level)
    do_shot(cand, level, cand_idx)

    result, det = _wait_shot_result(level)

    if result == "success":
        _log(f"🎉 Level {level} SUKSES! Kandidat #{cand_idx} "
             f"[{cand.get('strategy','?')}] berhasil!")
        save_best(level, cand, cand_idx, run)
        do_tap_continue(det)
        return "success"
    else:
        _log(f"❌ Level {level} kandidat #{cand_idx} gagal, maju ke kandidat berikutnya")
        _tracker.advance(level)
        return "fail"


# ─────────────────────────────────────────────────────────────
#  MAIN AUTONOMOUS LOOP
# ─────────────────────────────────────────────────────────────

def auto_loop():
    run       = 0
    # Inisialisasi: mulai dari Level 1
    # (asumsi: game sudah di lobby)

    # Cek apakah semua sudah ada best shot
    if all_done():
        _log("✅ Semua 18 level sudah punya best shot! Langsung export...")
        _export()
        return

    done = count_done()
    _log(f"🚀 Auto Play dimulai. Progress: {done}/{TOTAL_LEVELS} level selesai")
    _log("📋 Mapping strategi:")
    for lvl in range(1, TOTAL_LEVELS + 1):
        m     = get_mapping(lvl)
        strat = m.get("strategy", "?")
        n     = total_candidates(lvl)
        status = "✅" if load_best(lvl) else "⬜"
        _log(f"   {status} L{lvl:2d} [{strat}] ({n} kandidat)")

    # Masuk game dari lobby
    run += 1
    _log(f"\n{'='*50}")
    _log(f"🔁 Run #{run} — masuk game...")

    if not do_play_solo():
        _log("❌ Gagal masuk game dari lobby!")
        return

    current_level = 1

    while not all_done():
        # Jika level ini sudah punya best shot → replay saja
        if load_best(current_level):
            shot = get_replay_shot(current_level)
            _log(f"⏩ Level {current_level} sudah ada best shot, replay...")

            if not do_wait_ready(current_level):
                # Timeout → recover dari level ini
                _log(f"⚠️  Timeout di Level {current_level}, recover...")
                if not recover_and_go(current_level):
                    _log("❌ Recovery gagal total!")
                    break
                continue

            do_shot(shot, current_level, -1)
            time.sleep(WAIT_AFTER_SHOT)
            ok, det = do_wait_continue()
            if ok:
                do_tap_continue(det)
                current_level += 1
                if current_level > TOTAL_LEVELS:
                    # Selesai satu putaran, restart
                    run += 1
                    _log(f"\n{'='*50}")
                    _log(f"🔁 Run #{run} selesai! Restart dari Level 1...")
                    if all_done():
                        break
                    if not do_play_solo():
                        break
                    current_level = 1
            else:
                # CONTINUE tidak muncul padahal pakai best shot → recover
                _log(f"⚠️  Best shot Level {current_level} tidak masuk, recover...")
                if not recover_and_go(current_level):
                    break
            continue

        # Level ini belum punya best shot → coba kandidat
        _log(f"\n{'─'*50}")
        _log(f"🎯 Training Level {current_level} "
             f"[{get_mapping(current_level).get('strategy','?')}] "
             f"(kandidat #{_tracker.current_idx(current_level)}/"
             f"{total_candidates(current_level)-1})")

        if not do_wait_ready(current_level):
            _log(f"⚠️  Game ready timeout L{current_level}, recover...")
            if not recover_and_go(current_level):
                break
            continue

        result = play_level(current_level, run)

        if result == "success":
            # Lanjut ke level berikutnya
            current_level += 1
            if current_level > TOTAL_LEVELS:
                run += 1
                _log(f"\n🔁 Run #{run} — restart dari Level 1")
                if all_done():
                    break
                if not do_play_solo():
                    break
                current_level = 1

        elif result == "fail":
            # Perlu recover: keluar → lobby → PLAY SOLO → replay ke level ini
            if not recover_and_go(current_level):
                _log(f"❌ Recovery gagal untuk Level {current_level}!")
                # Skip level ini sementara, coba level berikutnya
                current_level += 1
                if current_level > TOTAL_LEVELS:
                    run += 1
                    if all_done():
                        break
                    if not do_play_solo():
                        break
                    current_level = 1

        else:  # no_shot
            _log(f"⏭️  Level {current_level} tidak ada kandidat, skip")
            current_level += 1
            if current_level > TOTAL_LEVELS:
                current_level = 1

    # Selesai!
    done = count_done()
    _log(f"\n{'='*50}")
    _log(f"🏁 Auto Play selesai! {done}/{TOTAL_LEVELS} level berhasil")
    _print_summary()

    if all_done():
        _log("\n✅ Semua level selesai! Exporting ke MacroDroid...")
        _export()
    else:
        missing = [lvl for lvl in range(1, TOTAL_LEVELS + 1) if not load_best(lvl)]
        _log(f"⚠️  Level belum selesai: {missing}")
        _log("   Jalankan lagi: python auto_play.py")


# ─────────────────────────────────────────────────────────────
#  SUMMARY & EXPORT
# ─────────────────────────────────────────────────────────────

def _print_summary():
    _log("\n📊 SUMMARY:")
    for lvl in range(1, TOTAL_LEVELS + 1):
        d = load_best(lvl)
        m = get_mapping(lvl)
        strat = m.get("strategy", "?")
        if d:
            s = d.get("adb_scaled_shot") or d.get("best_shot", {})
            _log(f"  ✅ L{lvl:2d} [{strat:25s}] "
                 f"({s.get('start_x')},{s.get('start_y')})"
                 f"→({s.get('end_x')},{s.get('end_y')}) "
                 f"{s.get('duration_ms')}ms")
        else:
            n = total_candidates(lvl)
            _log(f"  ⬜ L{lvl:2d} [{strat:25s}] (belum — {n} kandidat tersedia)")


def _export():
    """Jalankan export_macrodroid_route.py secara inline."""
    try:
        import export_macrodroid_route as emr
        touches = emr.load_recorded_touches("recorded_touches.json")
        steps, missing = emr.build_route(touches)
        emr.export_json(steps, missing, emr.OUTPUT_JSON)
        emr.export_txt(steps, missing, emr.OUTPUT_TXT)
        _log(f"📦 Export selesai: {emr.OUTPUT_JSON} & {emr.OUTPUT_TXT}")
    except Exception as e:
        _log(f"⚠️  Export error: {e}")
        _log("   Jalankan manual: python export_macrodroid_route.py")


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OutiePutt Fully Autonomous Bot — Level 1-18"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Hanya tampilkan progress best shot"
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Langsung export ke MacroDroid (tanpa main)"
    )
    args = parser.parse_args()

    if args.summary:
        _print_summary()
        return

    if args.export:
        _export()
        return

    # Cek ADB
    devices = get_devices()
    if not devices:
        print("❌ Tidak ada device ADB!")
        print("   1. Sambungkan HP via USB")
        print("   2. Aktifkan USB Debugging di HP")
        print("   3. Klik Allow/Izinkan di HP")
        sys.exit(1)
    _log(f"✅ Device: {devices}")

    # Cek API Key
    if not GEMINI_API_KEY or "XXXX" in GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY belum diisi di config.py!")
        print("   Daftar gratis di: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    # Setup
    w, h = get_screen_size()
    _log(f"📐 Resolusi HP: {w}x{h}")
    keep_screen_on()

    _log("\n⚠️  Pastikan game OutiePutt sudah terbuka di LOBBY (ada tombol Play Solo)")
    _log("    Bot akan mulai dalam 3 detik...")
    time.sleep(3)

    # Mulai
    try:
        auto_loop()
    except KeyboardInterrupt:
        _log("\n⏹️  Bot dihentikan (Ctrl+C)")
        _print_summary()
        sys.exit(0)


if __name__ == "__main__":
    main()
