#!/usr/bin/env python3
# ============================================================
#  train_auto_continue_next.py
#  Training bot OutiePutt Level 1-18
#
#  Cara pakai:
#    python train_auto_continue_next.py
#    python train_auto_continue_next.py --start-level 3
#
#  Flow:
#  - Dari lobby: klik PLAY SOLO
#  - Tunggu level ready, eksekusi kandidat shot
#  - Input y → simpan best shot, lanjut level berikutnya
#  - Input n → klik X, konfirmasi YES, balik lobby,
#               replay level 1..target-1 pakai best shot,
#               test kandidat berikutnya
#
#  Tidak pakai force-stop. Tidak pakai delay statis utama.
# ============================================================

import sys
import os
import json
import time
import argparse
from datetime import datetime, timezone

# ── Path setup ───────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adb_utils      import (load_recorded_touches, tap, swipe,
                             execute_shot, keep_screen_on,
                             get_devices, get_screen_size)
from vision_utils   import (wait_for_play_solo, wait_for_game_ready,
                             wait_for_continue, wait_for_yes_confirm,
                             tap_button, get_current_state)
from shot_candidates import get_candidate, total_candidates, get_candidates
from config         import CLAUDE_API_KEY

# ── Konstanta ────────────────────────────────────────────────
TOTAL_LEVELS    = 18
BEST_SHOT_DIR   = "."          # folder simpan level_XX_best_shot.json
WAIT_AFTER_SHOT = 3.5          # detik tunggu setelah swipe (bola rolling)


# ============================================================
#  BEST SHOT FILE I/O
# ============================================================

def best_shot_path(level: int) -> str:
    return os.path.join(BEST_SHOT_DIR, f"level_{level:02d}_best_shot.json")


def load_best_shot(level: int) -> dict | None:
    """Return best shot dict atau None jika belum ada."""
    path = best_shot_path(level)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
        # Validasi minimal
        shot = data.get("adb_scaled_shot") or data.get("best_shot")
        if shot and shot.get("start_x", 0) > 0:
            return data
    except Exception as e:
        print(f"[Train] ⚠️  Gagal load {path}: {e}")
    return None


def save_best_shot(level: int, candidate: dict, candidate_index: int):
    """
    Simpan best shot ke level_XX_best_shot.json.
    Tidak overwrite jika sudah ada dan valid.
    """
    path = best_shot_path(level)

    # Jangan overwrite yang sudah ada
    existing = load_best_shot(level)
    if existing:
        print(f"[Train] ℹ️  Level {level} sudah punya best shot, skip save.")
        return existing

    now = datetime.now(timezone.utc).isoformat()
    data = {
        "level": level,
        "status": "success",
        "source": "training",
        "candidate_index": candidate_index,
        "best_shot": {
            "start_x":    candidate["start_x"],
            "start_y":    candidate["start_y"],
            "end_x":      candidate["end_x"],
            "end_y":      candidate["end_y"],
            "duration_ms": candidate.get("duration_ms", 850)
        },
        "adb_scaled_shot": {
            "start_x":    candidate["start_x"],
            "start_y":    candidate["start_y"],
            "end_x":      candidate["end_x"],
            "end_y":      candidate["end_y"],
            "duration_ms": candidate.get("duration_ms", 850),
            "reverse":    candidate.get("reverse", True)
        },
        "note": candidate.get("note", ""),
        "saved_at": now
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[Train] 💾 Disimpan: {path}")
    return data


def get_shot_for_replay(level: int) -> dict | None:
    """
    Return shot dict untuk replay (dari best_shot file).
    Return adb_scaled_shot jika ada, fallback ke best_shot.
    """
    data = load_best_shot(level)
    if not data:
        return None
    return data.get("adb_scaled_shot") or data.get("best_shot")


# ============================================================
#  CORE GAME ACTIONS
# ============================================================

def do_play_solo() -> bool:
    """Tunggu lobby → tap PLAY SOLO."""
    ok, det = wait_for_play_solo(timeout=25)
    if not ok:
        print("[Train] ❌ PLAY SOLO tidak muncul!")
        return False
    tap_button("play_solo", det)
    return True


def do_wait_game_ready(level_hint: int = 0) -> bool:
    """Tunggu sampai game/level ready (meja terlihat, bola ada)."""
    label = f"GAME READY (Level {level_hint})" if level_hint else "GAME READY"
    ok, _ = wait_for_game_ready(timeout=25)
    if not ok:
        print(f"[Train] ❌ {label} timeout!")
        return False
    return True


def do_fire_shot(shot: dict) -> bool:
    """Eksekusi satu tembakan via ADB swipe."""
    if not shot:
        print("[Train] ❌ Shot dict kosong!")
        return False
    execute_shot(shot)
    return True


def do_wait_continue() -> tuple:
    """Tunggu CONTINUE muncul. Return (ok, detection)."""
    return wait_for_continue(timeout=35)


def do_tap_continue(det: dict = None):
    """Tap tombol CONTINUE."""
    tap_button("continue", det)


def do_close_and_confirm() -> bool:
    """
    Tap X (close_x) → tunggu YES → tap YES.
    Return True jika berhasil.
    """
    # Tap X
    det = get_current_state()
    tap_button("close_x", det)

    # Tunggu popup YES
    ok, det2 = wait_for_yes_confirm(timeout=15)
    if not ok:
        print("[Train] ⚠️  Popup YES tidak muncul, coba fallback tap")
        tap_button("yes_confirm", None)
        time.sleep(1)
    else:
        tap_button("yes_confirm", det2)
    return True


# ============================================================
#  RECOVER TO START (kembali ke lobby lalu PLAY SOLO)
# ============================================================

def recover_to_start() -> bool:
    """
    Keluar dari level via X + YES, tunggu lobby, klik PLAY SOLO.
    Return True jika berhasil sampai game ready.
    """
    print("\n[Recover] 🔄 Memulai recovery ke lobby...")

    # Keluar dari level
    ok = do_close_and_confirm()
    if not ok:
        print("[Recover] ⚠️  close_and_confirm gagal, lanjut tetap coba")

    # Tunggu lobby
    ok2, det = wait_for_play_solo(timeout=20)
    if not ok2:
        print("[Recover] ❌ Lobby tidak muncul setelah close!")
        return False

    # Klik PLAY SOLO
    tap_button("play_solo", det)

    # Tunggu game ready (Level 1)
    ok3 = do_wait_game_ready(level_hint=1)
    if not ok3:
        print("[Recover] ❌ Game ready tidak muncul setelah PLAY SOLO!")
        return False

    print("[Recover] ✅ Berhasil kembali ke Level 1")
    return True


# ============================================================
#  REPLAY LEVELS (replay level 1 s/d target-1 pakai best shot)
# ============================================================

def replay_to_target_level(target_level: int) -> bool:
    """
    Replay Level 1 sampai target_level-1 menggunakan best shot tersimpan.
    Dipanggil setelah recover_to_start() yang sudah membawa ke Level 1.

    Return True jika berhasil sampai target level game ready.
    """
    if target_level <= 1:
        print("[Replay] ℹ️  Target Level 1, tidak perlu replay.")
        return True

    print(f"\n[Replay] ▶️  Replay Level 1 → {target_level - 1}...")

    for lvl in range(1, target_level):
        shot = get_shot_for_replay(lvl)
        if not shot:
            print(f"[Replay] ❌ Tidak ada best shot untuk Level {lvl}! Tidak bisa replay.")
            return False

        print(f"\n[Replay] 🎱 Level {lvl}: {shot}")

        # Tunggu game ready
        ok = do_wait_game_ready(level_hint=lvl)
        if not ok:
            print(f"[Replay] ❌ Game ready Level {lvl} timeout!")
            return False

        # Eksekusi shot
        do_fire_shot(shot)
        time.sleep(WAIT_AFTER_SHOT)

        # Tunggu CONTINUE
        ok2, det = do_wait_continue()
        if not ok2:
            print(f"[Replay] ❌ CONTINUE Level {lvl} tidak muncul!")
            return False

        # Tap CONTINUE
        do_tap_continue(det)

        print(f"[Replay] ✅ Level {lvl} selesai → lanjut Level {lvl+1}")

    # Tunggu target level game ready
    ok = do_wait_game_ready(level_hint=target_level)
    if not ok:
        print(f"[Replay] ❌ Game ready Level {target_level} tidak muncul!")
        return False

    print(f"[Replay] ✅ Sudah di Level {target_level}, siap training!")
    return True


# ============================================================
#  TRAINING SATU LEVEL
# ============================================================

def train_level(level: int, start_candidate_idx: int = 0) -> tuple:
    """
    Training interaktif untuk satu level.

    Sudah diasumsikan: layar sudah di game ready level ini.

    Return:
      ("success", candidate_idx) — best shot ditemukan
      ("skip_all", -1)           — semua kandidat habis
      ("abort", -1)              — user abort (Ctrl+C / q)
    """
    candidates = get_candidates(level)
    n = len(candidates)

    if n == 0:
        print(f"[Train] ⚠️  Level {level} tidak punya kandidat shot!")
        return ("skip_all", -1)

    idx = start_candidate_idx

    while idx < n:
        cand = candidates[idx]
        print(f"\n{'='*55}")
        print(f"  Training Level {level}  |  Kandidat {idx+1}/{n}")
        print(f"  Note: {cand.get('note', '-')}")
        print(f"  Shot: ({cand['start_x']},{cand['start_y']}) → "
              f"({cand['end_x']},{cand['end_y']}) | {cand.get('duration_ms',850)}ms")
        print(f"{'='*55}")

        # Eksekusi tembakan
        do_fire_shot(cand)
        time.sleep(WAIT_AFTER_SHOT)

        # Tanya user
        while True:
            try:
                answer = input(
                    f"\n  Level {level} Kandidat {idx+1}: Berhasil? [y/n/q]: "
                ).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n[Train] ⚠️  Abort oleh user.")
                return ("abort", -1)

            if answer == "y":
                print(f"\n[Train] ✅ Kandidat {idx+1} BERHASIL! Menyimpan best shot...")
                save_best_shot(level, cand, idx)

                # Tunggu CONTINUE (bola sudah masuk)
                ok, det = do_wait_continue()
                if ok:
                    do_tap_continue(det)
                else:
                    print("[Train] ⚠️  CONTINUE tidak muncul, coba tap fallback")
                    tap_button("continue", None)

                return ("success", idx)

            elif answer == "n":
                print(f"\n[Train] ❌ Kandidat {idx+1} GAGAL. Recovery & coba kandidat berikutnya...")
                idx += 1
                return ("retry", idx)  # signal ke caller untuk recover & retry

            elif answer == "q":
                print("[Train] ⏹️  Training dihentikan oleh user.")
                return ("abort", -1)

            else:
                print("  Ketik y (berhasil), n (gagal), atau q (berhenti)")

    print(f"[Train] ⚠️  Semua {n} kandidat Level {level} sudah dicoba.")
    return ("skip_all", -1)


# ============================================================
#  MAIN TRAINING LOOP
# ============================================================

def training_loop(start_level: int = 1):
    """
    Loop training dari start_level sampai TOTAL_LEVELS.
    Otomatis recover dan replay saat kandidat gagal.
    """
    print(f"\n[Train] 🚀 Mulai training Level {start_level} → {TOTAL_LEVELS}\n")

    # Track kandidat index per level (untuk lanjut dari index terakhir)
    candidate_idx: dict = {lvl: 0 for lvl in range(1, TOTAL_LEVELS + 1)}

    current_level = start_level
    first_run     = True  # Flag apakah sudah di dalam game atau perlu masuk dulu

    while current_level <= TOTAL_LEVELS:

        # ── Cek apakah level ini sudah punya best shot ──────
        existing = load_best_shot(current_level)
        if existing:
            shot = existing.get("adb_scaled_shot") or existing.get("best_shot")
            print(f"\n[Train] ✅ Level {current_level} sudah punya best shot, skip training.")
            print(f"         Shot: {shot}")

            # Kalau ini start_level pertama dan kita sudah di level ini
            if first_run:
                # Perlu masuk game dulu
                if not _ensure_at_level(current_level, candidate_idx):
                    print(f"[Train] ❌ Gagal sampai Level {current_level}")
                    break
                first_run = False

            # Replay level ini
            ok_game = do_wait_game_ready(level_hint=current_level)
            if not ok_game:
                print(f"[Train] ❌ Game ready Level {current_level} tidak muncul")
                break

            do_fire_shot(shot)
            time.sleep(WAIT_AFTER_SHOT)

            ok_cont, det = do_wait_continue()
            if ok_cont:
                do_tap_continue(det)
            else:
                tap_button("continue", None)

            current_level += 1
            continue

        # ── Level belum punya best shot — mulai training ────
        print(f"\n[Train] 🎯 Training Level {current_level}...")

        # Pastikan kita berada di level ini
        if first_run:
            if not _ensure_at_level(current_level, candidate_idx):
                print(f"[Train] ❌ Gagal sampai Level {current_level}")
                break
            first_run = False
        # else: setelah CONTINUE dari level sebelumnya, sudah di level ini

        # Tunggu game ready
        ok = do_wait_game_ready(level_hint=current_level)
        if not ok:
            print(f"[Train] ❌ Game ready Level {current_level} timeout")
            # Coba recover
            if not recover_to_start():
                break
            if not replay_to_target_level(current_level):
                break
            continue

        # Jalankan training interaktif
        idx = candidate_idx[current_level]
        result, new_idx = train_level(current_level, start_candidate_idx=idx)

        if result == "success":
            # Lanjut ke level berikutnya (sudah tap CONTINUE di dalam train_level)
            current_level += 1
            # Reset index kandidat level berikutnya
            if current_level <= TOTAL_LEVELS:
                candidate_idx[current_level] = 0

        elif result == "retry":
            # Kandidat gagal — recover ke lobby, replay, coba kandidat baru
            candidate_idx[current_level] = new_idx

            if new_idx >= total_candidates(current_level):
                print(f"[Train] ⚠️  Semua kandidat Level {current_level} habis! Skip level ini.")
                current_level += 1
                continue

            # Recover: X → YES → lobby → PLAY SOLO → replay 1..target-1
            ok_rec = recover_to_start()
            if not ok_rec:
                print("[Train] ❌ Recovery gagal!")
                break

            ok_rep = replay_to_target_level(current_level)
            if not ok_rep:
                print("[Train] ❌ Replay gagal!")
                break
            # Loop kembali → training lagi level yang sama, kandidat berikutnya

        elif result == "abort":
            print("[Train] ⏹️  Training dihentikan.")
            break

        elif result == "skip_all":
            print(f"[Train] ⏭️  Level {current_level} skip (tidak ada kandidat / semua habis).")
            current_level += 1

    print("\n" + "="*55)
    print("🏁 Training selesai!")
    _print_summary()
    print("="*55)


def _ensure_at_level(target_level: int, candidate_idx: dict) -> bool:
    """
    Pastikan game sudah di target_level.
    Jika belum masuk game: masuk via PLAY SOLO + replay.
    """
    print(f"\n[Train] 📍 Memastikan posisi di Level {target_level}...")

    if target_level == 1:
        # Masuk dari lobby
        ok = do_play_solo()
        if not ok:
            return False
        return do_wait_game_ready(level_hint=1)
    else:
        # Masuk dari lobby lalu replay 1..target-1
        ok = do_play_solo()
        if not ok:
            return False
        ok2 = do_wait_game_ready(level_hint=1)
        if not ok2:
            return False
        return replay_to_target_level(target_level)


def _print_summary():
    """Tampilkan ringkasan best shot yang sudah tersimpan."""
    print("\n📊 Best Shot Summary:")
    for lvl in range(1, TOTAL_LEVELS + 1):
        data = load_best_shot(lvl)
        if data:
            s = data.get("adb_scaled_shot") or data.get("best_shot", {})
            print(f"  Level {lvl:2d} ✅  ({s.get('start_x')},{s.get('start_y')}) → "
                  f"({s.get('end_x')},{s.get('end_y')}) | {s.get('duration_ms')}ms")
        else:
            print(f"  Level {lvl:2d} ⬜  (belum ada best shot)")


# ============================================================
#  ENTRY POINT
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="OutiePutt Training Bot — Level 1-18"
    )
    parser.add_argument(
        "--start-level", "-s",
        type=int, default=1,
        help="Mulai training dari level ini (default: 1)"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Hanya tampilkan summary best shot yang sudah tersimpan"
    )
    args = parser.parse_args()

    if args.summary:
        _print_summary()
        return

    # Cek ADB
    devices = get_devices()
    if not devices:
        print("❌ Tidak ada device ADB!")
        print("   1. Sambungkan HP via USB")
        print("   2. Aktifkan USB Debugging")
        print("   3. Klik Allow di HP")
        sys.exit(1)
    print(f"✅ Device: {devices}")

    # Cek API key
    if not CLAUDE_API_KEY or "XXXX" in CLAUDE_API_KEY:
        print("❌ CLAUDE_API_KEY belum diisi di config.py!")
        sys.exit(1)

    # Load fallback touches
    load_recorded_touches("recorded_touches.json")

    # Resolusi
    w, h = get_screen_size()
    print(f"📐 Resolusi: {w}x{h}")

    # Jaga layar nyala
    keep_screen_on()

    # Validasi start level
    start = max(1, min(args.start_level, TOTAL_LEVELS))
    print(f"\n⚠️  Pastikan game OutiePutt sudah terbuka di layar HP!")
    print(f"    Tekan Enter untuk mulai training Level {start}...", end="")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print()

    # Mulai training
    try:
        training_loop(start_level=start)
    except KeyboardInterrupt:
        print("\n\n⏹️  Training dihentikan (Ctrl+C)")
        _print_summary()
        sys.exit(0)


if __name__ == "__main__":
    main()
