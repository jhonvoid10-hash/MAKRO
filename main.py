#!/usr/bin/env python3
# ============================================================
#  main.py — OutiePutt AI Vision Bot
#  Cara pakai:
#    pip install anthropic
#    python main.py
# ============================================================

import time
import sys
import os

import adb_controller as adb
import vision
from config import (
    TOTAL_HOLES, MAX_SHOTS_HOLE,
    DELAY_AFTER_SHOT, DELAY_HOLE_TRANSITION,
    DELAY_GAME_LOAD, DELAY_SCREENSHOT,
    SWIPE_DURATION_MS, MIN_DRAG_PX, MAX_DRAG_PX
)


# ============================================================
#  HELPERS
# ============================================================

def banner():
    print("""
╔══════════════════════════════════════════╗
║   🏌️  OutiePutt AI Vision Bot v1.0       ║
║   Claude AI + ADB Auto-Play              ║
╚══════════════════════════════════════════╝
""")


def check_adb():
    """Pastikan ADB terhubung ke HP."""
    devices = adb.get_devices()
    if not devices:
        print("❌ Tidak ada device ADB yang terhubung!")
        print("   Pastikan:")
        print("   1. Kabel USB sudah terpasang")
        print("   2. USB Debugging aktif di HP")
        print("   3. Sudah klik 'Allow' di HP")
        sys.exit(1)
    print(f"✅ Device terhubung: {devices}")
    return devices[0]


def get_analysis(screen_w: int, screen_h: int) -> dict:
    """Ambil screenshot lalu analisis via Claude."""
    time.sleep(DELAY_SCREENSHOT)
    b64 = adb.screencap_base64()
    result = vision.analyze_screen(b64, screen_w, screen_h)
    return result


# ============================================================
#  GAME STATES
# ============================================================

def handle_menu(analysis: dict, screen_w: int, screen_h: int):
    """Klik tombol PLAY SOLO di layar menu."""
    btn = analysis.get("play_solo_button", {})
    x, y = btn.get("x", 0), btn.get("y", 0)

    if x == 0 and y == 0:
        # Fallback koordinat tengah layar
        x, y = screen_w // 2, int(screen_h * 0.6)
        print(f"⚠️  Tombol PLAY SOLO tidak terdeteksi, tap fallback ({x},{y})")
    else:
        print(f"✅ Tombol PLAY SOLO ditemukan di ({x},{y})")

    adb.tap(x, y)
    time.sleep(DELAY_GAME_LOAD)


def handle_ready_to_shoot(analysis: dict) -> bool:
    """
    Tembak bola berdasarkan hasil analisis Claude.
    Return True jika berhasil tembak.
    """
    ball = analysis.get("ball")
    hole = analysis.get("hole")
    power = analysis.get("shot_power", 0.5)
    notes = analysis.get("notes", "")

    if not ball or not hole:
        print("⚠️  Posisi bola/hole tidak terdeteksi!")
        return False

    if ball.get("x", 0) == 0 or hole.get("x", 0) == 0:
        print("⚠️  Koordinat bola/hole = 0, skip tembakan")
        return False

    if notes:
        print(f"📝 Catatan AI: {notes}")

    # Hitung arah & kekuatan swipe
    shot = vision.calculate_shot(ball, hole, power, MIN_DRAG_PX, MAX_DRAG_PX)

    # Eksekusi swipe via ADB
    adb.swipe(
        shot["start_x"], shot["start_y"],
        shot["end_x"],   shot["end_y"],
        SWIPE_DURATION_MS
    )
    return True


def handle_hole_complete(analysis: dict):
    """Klik tombol Next Hole."""
    btn = analysis.get("next_button", {})
    x, y = btn.get("x", 0), btn.get("y", 0)

    if x == 0 and y == 0:
        print("⚠️  Tombol Next tidak terdeteksi, tap fallback")
        # Coba beberapa posisi umum tombol Next
        for fx, fy in [(540, 1900), (540, 1800), (540, 1700)]:
            adb.tap(fx, fy)
            time.sleep(0.5)
    else:
        print(f"➡️  Klik Next Hole di ({x},{y})")
        adb.tap(x, y)

    time.sleep(DELAY_HOLE_TRANSITION)


# ============================================================
#  MAIN LOOP
# ============================================================

def play_game():
    banner()

    # 1. Cek ADB
    device = check_adb()
    print(f"📱 Menggunakan device: {device}")

    # 2. Baca resolusi layar
    screen_w, screen_h = adb.get_screen_size()
    print(f"📐 Resolusi layar: {screen_w}x{screen_h}")

    # 3. Jaga layar tetap nyala
    adb.keep_screen_on()

    # 4. Langsung screenshot — game harus sudah terbuka di HP!
    print("\n📸 Screenshot layar HP sekarang...")
    print("⚠️  Pastikan game OutiePutt sudah terbuka di HP!\n")
    time.sleep(1)

    # 5. Statistik
    stats = {
        "holes_completed": 0,
        "total_shots": 0,
        "scores": []
    }

    # 6. State machine utama
    consecutive_errors = 0
    max_errors = 5
    hole_shot_count = 0

    print("🎮 Mulai scan layar...\n")

    while stats["holes_completed"] < TOTAL_HOLES:
        # Ambil screenshot dan analisis
        analysis = get_analysis(screen_w, screen_h)
        state = analysis.get("state", "unknown")

        print(f"\n[State] {state} | Hole: {stats['holes_completed']+1}/{TOTAL_HOLES} | Shot: {hole_shot_count}")

        # ── Handle tiap state ──────────────────────────────

        if state in ("error", "parse_error"):
            consecutive_errors += 1
            print(f"⚠️  Error #{consecutive_errors}: {analysis.get('notes')}")
            if consecutive_errors >= max_errors:
                print("❌ Terlalu banyak error berturut-turut, berhenti.")
                break
            time.sleep(2)
            continue

        consecutive_errors = 0  # Reset counter error

        if state == "loading":
            print("⏳ Loading... tunggu sebentar")
            time.sleep(2)
            continue

        if state == "menu":
            print("\n🏠 Menu terdeteksi — klik PLAY SOLO...")
            handle_menu(analysis, screen_w, screen_h)
            hole_shot_count = 0
            continue

        if state == "ready_to_shoot":
            if hole_shot_count >= MAX_SHOTS_HOLE:
                print(f"⚠️  Maks {MAX_SHOTS_HOLE} tembakan tercapai, paksa Next Hole")
                adb.tap(screen_w // 2, int(screen_h * 0.8))
                time.sleep(DELAY_HOLE_TRANSITION)
                stats["scores"].append(hole_shot_count)
                stats["holes_completed"] += 1
                hole_shot_count = 0
                continue

            success = handle_ready_to_shoot(analysis)
            if success:
                hole_shot_count += 1
                stats["total_shots"] += 1
                print(f"⏳ Tunggu bola berhenti ({DELAY_AFTER_SHOT}s)...")
                time.sleep(DELAY_AFTER_SHOT)
            else:
                time.sleep(1)
            continue

        if state == "ball_moving":
            print("🎱 Bola masih bergerak, tunggu...")
            time.sleep(1.5)
            continue

        if state == "hole_complete":
            print(f"🎉 HOLE {stats['holes_completed']+1} SELESAI! ({hole_shot_count} tembakan)")
            stats["scores"].append(hole_shot_count)
            stats["holes_completed"] += 1
            handle_hole_complete(analysis)
            hole_shot_count = 0
            continue

        if state == "game_complete":
            print("🏆 GAME SELESAI!")
            btn = analysis.get("next_button", {})
            if btn.get("x", 0) > 0:
                adb.tap(btn["x"], btn["y"])
            break

        # State tidak dikenal
        print(f"❓ State tidak dikenal: '{state}', tunggu...")
        time.sleep(2)

    # ── Tampilkan hasil ────────────────────────────────────
    print("\n" + "="*45)
    print("🏆 HASIL AKHIR")
    print("="*45)
    for i, s in enumerate(stats["scores"]):
        emoji = "🟢" if s <= 2 else "🟡" if s <= 4 else "🔴"
        print(f"  Hole {i+1:2d}: {s} tembakan {emoji}")
    print(f"\n  Total tembakan : {stats['total_shots']}")
    print(f"  Hole selesai   : {stats['holes_completed']}/{TOTAL_HOLES}")
    if stats["scores"]:
        avg = sum(stats["scores"]) / len(stats["scores"])
        print(f"  Rata-rata      : {avg:.1f} tembakan/hole")
    print("="*45)


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot dihentikan oleh user (Ctrl+C)")
        sys.exit(0)
