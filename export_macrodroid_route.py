#!/usr/bin/env python3
# ============================================================
#  export_macrodroid_route.py
#  Export semua best shot Level 1-18 ke format MacroDroid
#
#  Cara pakai:
#    python export_macrodroid_route.py
#
#  Output:
#    macrodroid_route_export.json  — struktur JSON lengkap
#    macrodroid_route_steps.txt    — teks langkah mudah dibaca
# ============================================================

import os
import sys
import json
from datetime import datetime, timezone

# ── Path setup ───────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_LEVELS     = 18
BEST_SHOT_DIR    = "."
OUTPUT_JSON      = "macrodroid_route_export.json"
OUTPUT_TXT       = "macrodroid_route_steps.txt"


# ============================================================
#  LOAD BEST SHOTS
# ============================================================

def load_best_shot(level: int) -> dict | None:
    path = os.path.join(BEST_SHOT_DIR, f"level_{level:02d}_best_shot.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Export] ⚠️  Gagal load level {level}: {e}")
        return None


def load_recorded_touches(path: str = "recorded_touches.json") -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


# ============================================================
#  BUILD ROUTE STEPS
# ============================================================

def build_route(touches: dict) -> list:
    """
    Bangun daftar step MacroDroid dari level 1 sampai 18.
    Setiap level = [wait_game_ready, swipe, wait_continue, tap_continue]
    Diawali dengan tap PLAY SOLO.
    """
    steps = []

    # ── STEP 0: Tap PLAY SOLO ────────────────────────────────
    ps = touches.get("play_solo", {})
    steps.append({
        "step": 0,
        "action": "tap",
        "label": "play_solo",
        "x": ps.get("x", 360),
        "y": ps.get("y", 980),
        "wait_after": "until_game_ready",
        "note": "Tap tombol PLAY SOLO di lobby"
    })

    cont = touches.get("continue", {})

    # ── STEP per level ───────────────────────────────────────
    step_num = 1
    missing  = []

    for lvl in range(1, TOTAL_LEVELS + 1):
        data = load_best_shot(lvl)

        if not data:
            missing.append(lvl)
            # Placeholder kosong
            steps.append({
                "step": step_num,
                "action": "wait",
                "label": f"wait_game_ready_level_{lvl}",
                "wait_for": "game_ready",
                "level": lvl,
                "note": f"⚠️  LEVEL {lvl} BELUM ADA BEST SHOT — isi manual"
            })
            step_num += 1

            steps.append({
                "step": step_num,
                "action": "swipe",
                "label": f"shot_level_{lvl}",
                "level": lvl,
                "x1": 0, "y1": 0,
                "x2": 0, "y2": 0,
                "duration_ms": 850,
                "reverse": True,
                "wait_after": "until_continue",
                "note": f"⚠️  LEVEL {lvl} BELUM ADA BEST SHOT — isi koordinat manual"
            })
            step_num += 1

        else:
            shot = data.get("adb_scaled_shot") or data.get("best_shot", {})

            # Wait game ready
            steps.append({
                "step": step_num,
                "action": "wait",
                "label": f"wait_game_ready_level_{lvl}",
                "wait_for": "game_ready",
                "level": lvl,
                "note": f"Tunggu Level {lvl} game ready muncul"
            })
            step_num += 1

            # Swipe shot
            steps.append({
                "step": step_num,
                "action": "swipe",
                "label": f"shot_level_{lvl}",
                "level": lvl,
                "x1": shot.get("start_x", 0),
                "y1": shot.get("start_y", 0),
                "x2": shot.get("end_x", 0),
                "y2": shot.get("end_y", 0),
                "duration_ms": shot.get("duration_ms", 850),
                "reverse": shot.get("reverse", True),
                "wait_after": "until_continue",
                "note": data.get("note", f"Level {lvl} best shot")
            })
            step_num += 1

        # Wait continue
        steps.append({
            "step": step_num,
            "action": "wait",
            "label": f"wait_continue_level_{lvl}",
            "wait_for": "continue",
            "level": lvl,
            "note": f"Tunggu tombol CONTINUE muncul setelah Level {lvl}"
        })
        step_num += 1

        # Tap continue
        steps.append({
            "step": step_num,
            "action": "tap",
            "label": "continue",
            "level": lvl,
            "x": cont.get("x", 360),
            "y": cont.get("y", 1100),
            "wait_after": "until_next_level_ready",
            "note": f"Tap CONTINUE setelah Level {lvl} selesai"
        })
        step_num += 1

    return steps, missing


# ============================================================
#  EXPORT JSON
# ============================================================

def export_json(steps: list, missing: list, output_path: str):
    now = datetime.now(timezone.utc).isoformat()
    export = {
        "_info": {
            "generated_at": now,
            "total_levels": TOTAL_LEVELS,
            "total_steps":  len(steps),
            "missing_levels": missing,
            "device": "720x1600",
            "note": (
                "File ini untuk MacroDroid. "
                "Isi koordinat manual untuk level yang ⚠️. "
                "wait_after = kondisi yang harus terpenuhi sebelum lanjut."
            )
        },
        "steps": steps
    }
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"[Export] ✅ JSON: {output_path}  ({len(steps)} steps)")


# ============================================================
#  EXPORT TXT (mudah dibaca, bisa input manual ke MacroDroid)
# ============================================================

def export_txt(steps: list, missing: list, output_path: str):
    lines = []
    lines.append("=" * 60)
    lines.append("  MACRODROID ROUTE — OutiePutt Level 1-18")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Device: 720x1600")
    if missing:
        lines.append(f"  ⚠️  Level belum ada best shot: {missing}")
    lines.append("=" * 60)
    lines.append("")

    for s in steps:
        action = s.get("action")
        step_n = s.get("step", "?")
        note   = s.get("note", "")

        if action == "tap":
            label = s.get("label", "?")
            x, y  = s.get("x", 0), s.get("y", 0)
            wait  = s.get("wait_after", "")
            lines.append(f"[Step {step_n:3d}] TAP  {label.upper()}")
            lines.append(f"           Koordinat : x={x}, y={y}")
            if wait:
                lines.append(f"           Tunggu    : {wait}")
            lines.append(f"           Note      : {note}")

        elif action == "swipe":
            lvl   = s.get("level", "?")
            x1,y1 = s.get("x1",0), s.get("y1",0)
            x2,y2 = s.get("x2",0), s.get("y2",0)
            dur   = s.get("duration_ms", 850)
            rev   = s.get("reverse", True)
            wait  = s.get("wait_after", "")
            lines.append(f"[Step {step_n:3d}] SWIPE  Level {lvl}")
            lines.append(f"           Start     : x={x1}, y={y1}")
            lines.append(f"           End       : x={x2}, y={y2}")
            lines.append(f"           Duration  : {dur}ms")
            lines.append(f"           Reverse   : {rev}")
            if wait:
                lines.append(f"           Tunggu    : {wait}")
            lines.append(f"           Note      : {note}")

        elif action == "wait":
            wf    = s.get("wait_for", "?")
            lvl   = s.get("level", "")
            lvl_s = f" (Level {lvl})" if lvl else ""
            lines.append(f"[Step {step_n:3d}] WAIT  {wf.upper()}{lvl_s}")
            lines.append(f"           Note      : {note}")

        lines.append("")

    lines.append("=" * 60)
    lines.append("  END OF ROUTE")
    lines.append("=" * 60)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[Export] ✅ TXT:  {output_path}")


# ============================================================
#  SUMMARY
# ============================================================

def print_summary(missing: list):
    print("\n📊 Status Best Shot per Level:")
    for lvl in range(1, TOTAL_LEVELS + 1):
        data = load_best_shot(lvl)
        if data:
            s = data.get("adb_scaled_shot") or data.get("best_shot", {})
            print(f"  Level {lvl:2d} ✅  ({s.get('start_x')},{s.get('start_y')}) → "
                  f"({s.get('end_x')},{s.get('end_y')}) | {s.get('duration_ms')}ms")
        else:
            print(f"  Level {lvl:2d} ⬜  (belum ada — perlu training)")

    if missing:
        print(f"\n  ⚠️  Level belum lengkap: {missing}")
        print("     Jalankan training dulu: python train_auto_continue_next.py")
    else:
        print("\n  ✅ Semua level sudah punya best shot!")


# ============================================================
#  MAIN
# ============================================================

def main():
    print("\n" + "="*55)
    print("  📦 Export MacroDroid Route — OutiePutt")
    print("="*55)

    touches = load_recorded_touches("recorded_touches.json")
    steps, missing = build_route(touches)

    print_summary(missing)

    print(f"\n[Export] Membuat file output...")
    export_json(steps, missing, OUTPUT_JSON)
    export_txt(steps, missing, OUTPUT_TXT)

    print(f"\n✅ Export selesai!")
    print(f"   📄 {OUTPUT_JSON}")
    print(f"   📄 {OUTPUT_TXT}")

    if missing:
        print(f"\n⚠️  {len(missing)} level belum ada best shot: {missing}")
        print("   Koordinat di file akan 0,0 — isi manual setelah training selesai.")


if __name__ == "__main__":
    main()
