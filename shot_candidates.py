# ============================================================
#  shot_candidates.py — Kandidat shot per Level 1-18
#  Resolusi: 720x1600
#
#  Tiap kandidat mengikuti strategi dari level_mapping.py.
#  Format:
#  {
#    "start_x": int,   # koordinat awal swipe
#    "start_y": int,
#    "end_x":   int,   # koordinat akhir swipe (arah drag/backswing)
#    "end_y":   int,
#    "duration_ms": int,
#    "reverse": bool,  # True = drag berlawanan arah tembak
#    "strategy": str,  # nama strategi dari level_mapping
#    "uses_portal": bool,
#    "note":    str
#  }
#
#  ATURAN:
#  - Koordinat mengikuti mapping strategi per level.
#  - Jangan ubah kandidat level yang sudah punya best_shot tersimpan.
#  - Kandidat yang gagal tidak diulang (dicatat di training loop).
#  - Kalau arah kebalik → reverse=True.
#  - Portal hanya dipakai kalau mapping mengizinkan.
# ============================================================

from level_mapping import get_mapping, get_drag_length

# ── STRUKTUR DATA ────────────────────────────────────────────
# CANDIDATES[level] = list of dict
# Index 0 = kandidat utama sesuai mapping, index berikutnya variasi
# ─────────────────────────────────────────────────────────────

CANDIDATES: dict = {

    # ──────────────────── LEVEL 1 ────────────────────────────
    # Strategi: bank_right — obstacle di tengah, pantulan kanan
    # JANGAN ubah kalau best_shot sudah tersimpan
    1: [
        {
            "start_x": 360, "start_y": 900,
            "end_x":   480, "end_y":   1100,
            "duration_ms": 850, "reverse": True,
            "strategy": "bank_right",
            "uses_portal": False,
            "note": "L1 [bank_right] drag kiri-bawah → bola ke kanan, pantulan dinding kanan"
        },
        {
            "start_x": 360, "start_y": 900,
            "end_x":   500, "end_y":   1080,
            "duration_ms": 870, "reverse": True,
            "strategy": "bank_right",
            "uses_portal": False,
            "note": "L1 [bank_right] lebih ke kanan, power sedang"
        },
        {
            "start_x": 360, "start_y": 900,
            "end_x":   460, "end_y":   1120,
            "duration_ms": 830, "reverse": True,
            "strategy": "bank_right",
            "uses_portal": False,
            "note": "L1 [bank_right] koreksi sedikit kiri, power ringan"
        },
    ],

    # ──────────────────── LEVEL 2 ────────────────────────────
    # Strategi: gap_through_bars — lewati celah antar bar, jangan lurus
    2: [
        {
            "start_x": 360, "start_y": 950,
            "end_x":   290, "end_y":   1200,
            "duration_ms": 860, "reverse": True,
            "strategy": "gap_through_bars",
            "uses_portal": False,
            "note": "L2 [gap_left] drag kanan-bawah → bola lewat celah kiri bar"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   430, "end_y":   1200,
            "duration_ms": 860, "reverse": True,
            "strategy": "gap_through_bars",
            "uses_portal": False,
            "note": "L2 [gap_right] drag kiri-bawah → bola lewat celah kanan bar"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   310, "end_y":   1250,
            "duration_ms": 900, "reverse": True,
            "strategy": "gap_through_bars",
            "uses_portal": False,
            "note": "L2 [gap_left+power] celah kiri dengan power lebih kuat"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   450, "end_y":   1250,
            "duration_ms": 900, "reverse": True,
            "strategy": "gap_through_bars",
            "uses_portal": False,
            "note": "L2 [gap_right+power] celah kanan dengan power lebih kuat"
        },
    ],

    # ──────────────────── LEVEL 3 ────────────────────────────
    # Strategi: center_lane — lewati lane tengah, ikuti up-arrow
    3: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1300,
            "duration_ms": 900, "reverse": True,
            "strategy": "center_lane",
            "uses_portal": False,
            "note": "L3 [center] lurus melalui lane tengah/up-arrow"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   340, "end_y":   1300,
            "duration_ms": 900, "reverse": True,
            "strategy": "center_lane",
            "uses_portal": False,
            "note": "L3 [center_slight_left] sedikit kiri dari center"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   380, "end_y":   1300,
            "duration_ms": 900, "reverse": True,
            "strategy": "center_lane",
            "uses_portal": False,
            "note": "L3 [center_slight_right] sedikit kanan dari center"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1350,
            "duration_ms": 950, "reverse": True,
            "strategy": "center_lane",
            "uses_portal": False,
            "note": "L3 [center+power] center lane, power lebih kuat"
        },
    ],

    # ──────────────────── LEVEL 4 ────────────────────────────
    # Strategi: left_route — jalur kiri lebih aman, hindari trap kanan bawah
    4: [
        {
            "start_x": 360, "start_y": 980,
            "end_x":   460, "end_y":   1230,
            "duration_ms": 860, "reverse": True,
            "strategy": "left_route",
            "uses_portal": False,
            "note": "L4 [left_up_arrow] drag kanan-bawah → bola ke kiri via up-arrow"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   490, "end_y":   1210,
            "duration_ms": 840, "reverse": True,
            "strategy": "left_route",
            "uses_portal": False,
            "note": "L4 [left_stronger] lebih ke kiri, power sedang"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   440, "end_y":   1260,
            "duration_ms": 880, "reverse": True,
            "strategy": "left_route",
            "uses_portal": False,
            "note": "L4 [left_medium] kiri medium, hindari trap bawah kanan"
        },
    ],

    # ──────────────────── LEVEL 5 ────────────────────────────
    # Strategi: center_lane — lewati center/cyan lane, jangan melebar
    5: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1310,
            "duration_ms": 900, "reverse": True,
            "strategy": "center_lane",
            "uses_portal": False,
            "note": "L5 [center_straight] lurus melalui cyan center lane"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   345, "end_y":   1310,
            "duration_ms": 900, "reverse": True,
            "strategy": "center_lane",
            "uses_portal": False,
            "note": "L5 [center_slight_left] sedikit kiri, tetap di center"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   375, "end_y":   1310,
            "duration_ms": 900, "reverse": True,
            "strategy": "center_lane",
            "uses_portal": False,
            "note": "L5 [center_slight_right] sedikit kanan, tetap di center"
        },
    ],

    # ──────────────────── LEVEL 6 ────────────────────────────
    # Strategi: narrow_gate — hourglass/gate sempit, akurasi > power
    6: [
        {
            "start_x": 360, "start_y": 950,
            "end_x":   360, "end_y":   1320,
            "duration_ms": 920, "reverse": True,
            "strategy": "narrow_gate",
            "uses_portal": False,
            "note": "L6 [center_gate] lurus melewati gate sempit, power tinggi"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   350, "end_y":   1320,
            "duration_ms": 920, "reverse": True,
            "strategy": "narrow_gate",
            "uses_portal": False,
            "note": "L6 [gate_slight_left] koreksi kiri tipis"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   370, "end_y":   1320,
            "duration_ms": 920, "reverse": True,
            "strategy": "narrow_gate",
            "uses_portal": False,
            "note": "L6 [gate_slight_right] koreksi kanan tipis"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   360, "end_y":   1370,
            "duration_ms": 960, "reverse": True,
            "strategy": "narrow_gate",
            "uses_portal": False,
            "note": "L6 [gate_max_power] center gate, power maksimal"
        },
    ],

    # ──────────────────── LEVEL 7 ────────────────────────────
    # Strategi: slanted_corridor — koridor miring, ikuti sudut, jangan lurus
    7: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   460, "end_y":   1200,
            "duration_ms": 850, "reverse": True,
            "strategy": "slanted_corridor",
            "uses_portal": False,
            "note": "L7 [left_corridor] drag kanan-bawah → ikuti sudut kiri koridor"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   440, "end_y":   1170,
            "duration_ms": 820, "reverse": True,
            "strategy": "slanted_corridor",
            "uses_portal": False,
            "note": "L7 [slope_angle_light] ikuti kemiringan, power ringan"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   480, "end_y":   1220,
            "duration_ms": 870, "reverse": True,
            "strategy": "slanted_corridor",
            "uses_portal": False,
            "note": "L7 [slope_angle_strong] ikuti kemiringan, power sedang"
        },
    ],

    # ──────────────────── LEVEL 8 ────────────────────────────
    # Strategi: left_target — target sisi kiri, arahkan ke kiri
    8: [
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   460, "end_y":   1370,
            "duration_ms": 950, "reverse": True,
            "strategy": "left_target",
            "uses_portal": False,
            "note": "L8 [left_bank] drag kanan-bawah → bola ke kiri target"
        },
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   480, "end_y":   1350,
            "duration_ms": 930, "reverse": True,
            "strategy": "left_target",
            "uses_portal": False,
            "note": "L8 [left_direct] lebih ke kiri, power tinggi"
        },
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   440, "end_y":   1390,
            "duration_ms": 960, "reverse": True,
            "strategy": "left_target",
            "uses_portal": False,
            "note": "L8 [left_medium] kiri medium dengan power besar"
        },
    ],

    # ──────────────────── LEVEL 9 ────────────────────────────
    # Strategi: portal_aware — ada hole trap/portal, pakai safe lane dulu
    9: [
        {
            "start_x": 360, "start_y": 980,
            "end_x":   360, "end_y":   1280,
            "duration_ms": 880, "reverse": True,
            "strategy": "portal_aware",
            "uses_portal": False,
            "note": "L9 [safe_bridge] lurus melalui safe lane, hindari trap hole"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   320, "end_y":   1260,
            "duration_ms": 860, "reverse": True,
            "strategy": "portal_aware",
            "uses_portal": False,
            "note": "L9 [safe_left] sedikit kiri, hindari portal kanan"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   270, "end_y":   1240,
            "duration_ms": 870, "reverse": True,
            "strategy": "portal_aware",
            "uses_portal": True,
            "note": "L9 [portal_test] masuk portal kiri — test apakah membantu ke target"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   400, "end_y":   1260,
            "duration_ms": 860, "reverse": True,
            "strategy": "portal_aware",
            "uses_portal": False,
            "note": "L9 [safe_right_lane] sedikit kanan dari center"
        },
    ],

    # ──────────────────── LEVEL 10 ───────────────────────────
    # Strategi: dual_route — test kiri dan kanan, hindari tengah tertutup
    10: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   460, "end_y":   1310,
            "duration_ms": 900, "reverse": True,
            "strategy": "dual_route",
            "uses_portal": False,
            "note": "L10 [left_arrow] drag kanan-bawah → bola lewat up-arrow kiri"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   260, "end_y":   1310,
            "duration_ms": 900, "reverse": True,
            "strategy": "dual_route",
            "uses_portal": False,
            "note": "L10 [right_arrow] drag kiri-bawah → bola lewat up-arrow kanan"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   480, "end_y":   1340,
            "duration_ms": 930, "reverse": True,
            "strategy": "dual_route",
            "uses_portal": False,
            "note": "L10 [left_arrow+power] kiri lebih kuat"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   240, "end_y":   1340,
            "duration_ms": 930, "reverse": True,
            "strategy": "dual_route",
            "uses_portal": False,
            "note": "L10 [right_arrow+power] kanan lebih kuat"
        },
    ],

    # ──────────────────── LEVEL 11 ───────────────────────────
    # Strategi: avoid_center_obstacle — windmill/center berbahaya, jalur kiri
    11: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   460, "end_y":   1270,
            "duration_ms": 860, "reverse": True,
            "strategy": "avoid_center_obstacle",
            "uses_portal": False,
            "note": "L11 [left_bypass] drag kanan → bola lewat kiri obstacle windmill"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   490, "end_y":   1250,
            "duration_ms": 840, "reverse": True,
            "strategy": "avoid_center_obstacle",
            "uses_portal": False,
            "note": "L11 [left_bypass_wide] lebih ke kiri, hindari pusat"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   460, "end_y":   1300,
            "duration_ms": 880, "reverse": True,
            "strategy": "avoid_center_obstacle",
            "uses_portal": False,
            "note": "L11 [left_timed] kiri bypass dengan power sedang, timing gap"
        },
    ],

    # ──────────────────── LEVEL 12 ───────────────────────────
    # Strategi: right_route — tembok tengah, putar kanan untuk lewati
    12: [
        {
            "start_x": 360, "start_y": 980,
            "end_x":   250, "end_y":   1220,
            "duration_ms": 880, "reverse": True,
            "strategy": "right_route",
            "uses_portal": False,
            "note": "L12 [right_around] drag kiri-bawah → bola ke kanan melewati tembok tengah"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   230, "end_y":   1200,
            "duration_ms": 860, "reverse": True,
            "strategy": "right_route",
            "uses_portal": False,
            "note": "L12 [right_medium] kanan sedang, hindari center wall"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   210, "end_y":   1240,
            "duration_ms": 910, "reverse": True,
            "strategy": "right_route",
            "uses_portal": False,
            "note": "L12 [right_wide] kanan jauh dengan power lebih kuat"
        },
    ],

    # ──────────────────── LEVEL 13 ───────────────────────────
    # Strategi: flagged_hole_only — arahkan ke flagged hole, waspadai trap/portal
    13: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1310,
            "duration_ms": 900, "reverse": True,
            "strategy": "flagged_hole_only",
            "uses_portal": False,
            "note": "L13 [direct_to_flag] lurus ke flagged target, hindari trap hole"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   310, "end_y":   1290,
            "duration_ms": 880, "reverse": True,
            "strategy": "flagged_hole_only",
            "uses_portal": False,
            "note": "L13 [flag_slight_left] sedikit kiri ke flagged hole"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   410, "end_y":   1290,
            "duration_ms": 880, "reverse": True,
            "strategy": "flagged_hole_only",
            "uses_portal": False,
            "note": "L13 [flag_slight_right] sedikit kanan ke flagged hole"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   270, "end_y":   1250,
            "duration_ms": 870, "reverse": True,
            "strategy": "flagged_hole_only",
            "uses_portal": True,
            "note": "L13 [portal_test] masuk portal — test apakah keluar ke flagged target"
        },
    ],

    # ──────────────────── LEVEL 14 ───────────────────────────
    # Strategi: funnel_center — ikuti jalur funnel/center, jangan menyamping
    14: [
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   360, "end_y":   1450,
            "duration_ms": 1000, "reverse": True,
            "strategy": "funnel_center",
            "uses_portal": False,
            "note": "L14 [center_funnel] lurus melalui funnel, power max"
        },
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   352, "end_y":   1445,
            "duration_ms": 1000, "reverse": True,
            "strategy": "funnel_center",
            "uses_portal": False,
            "note": "L14 [funnel_tiny_left] koreksi kiri sangat kecil"
        },
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   368, "end_y":   1445,
            "duration_ms": 1000, "reverse": True,
            "strategy": "funnel_center",
            "uses_portal": False,
            "note": "L14 [funnel_tiny_right] koreksi kanan sangat kecil"
        },
    ],

    # ──────────────────── LEVEL 15 ───────────────────────────
    # Strategi: center_shaft — jalur vertikal/shaft tengah, lurus stabil
    15: [
        {
            "start_x": 360, "start_y": 950,
            "end_x":   360, "end_y":   1320,
            "duration_ms": 930, "reverse": True,
            "strategy": "center_shaft",
            "uses_portal": False,
            "note": "L15 [shaft_center] lurus sempurna melalui vertical shaft"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   355, "end_y":   1320,
            "duration_ms": 930, "reverse": True,
            "strategy": "center_shaft",
            "uses_portal": False,
            "note": "L15 [shaft_tiny_left] koreksi kiri sangat kecil"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   365, "end_y":   1320,
            "duration_ms": 930, "reverse": True,
            "strategy": "center_shaft",
            "uses_portal": False,
            "note": "L15 [shaft_tiny_right] koreksi kanan sangat kecil"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   360, "end_y":   1370,
            "duration_ms": 970, "reverse": True,
            "strategy": "center_shaft",
            "uses_portal": False,
            "note": "L15 [shaft_high_power] shaft tengah, power lebih kuat"
        },
    ],

    # ──────────────────── LEVEL 16 ───────────────────────────
    # Strategi: left_bypass_stack — target kiri, hindari stack vertikal
    16: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   460, "end_y":   1260,
            "duration_ms": 870, "reverse": True,
            "strategy": "left_bypass_stack",
            "uses_portal": False,
            "note": "L16 [left_bypass] drag kanan → bola ke kiri melewati stack vertikal"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   490, "end_y":   1240,
            "duration_ms": 850, "reverse": True,
            "strategy": "left_bypass_stack",
            "uses_portal": False,
            "note": "L16 [left_wider] lebih ke kiri, hindari stack lebih jauh"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   435, "end_y":   1280,
            "duration_ms": 890, "reverse": True,
            "strategy": "left_bypass_stack",
            "uses_portal": False,
            "note": "L16 [left_moderate] kiri sedang, power sedikit lebih"
        },
    ],

    # ──────────────────── LEVEL 17 ───────────────────────────
    # Strategi: short_direct — target dekat, shot pendek/direct
    17: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1200,
            "duration_ms": 780, "reverse": True,
            "strategy": "short_direct",
            "uses_portal": False,
            "note": "L17 [direct_short] shot langsung pendek, target dekat"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   345, "end_y":   1200,
            "duration_ms": 780, "reverse": True,
            "strategy": "short_direct",
            "uses_portal": False,
            "note": "L17 [direct_slight_left] koreksi kiri kecil"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   375, "end_y":   1200,
            "duration_ms": 780, "reverse": True,
            "strategy": "short_direct",
            "uses_portal": False,
            "note": "L17 [direct_slight_right] koreksi kanan kecil"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1240,
            "duration_ms": 820, "reverse": True,
            "strategy": "short_direct",
            "uses_portal": False,
            "note": "L17 [direct_medium] sedikit lebih kuat jika terlalu pendek"
        },
    ],

    # ──────────────────── LEVEL 18 ───────────────────────────
    # Strategi: bottom_bank — target bawah/kiri, waspadai portal kanan
    18: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   460, "end_y":   1400,
            "duration_ms": 1000, "reverse": True,
            "strategy": "bottom_bank",
            "uses_portal": False,
            "note": "L18 [bottom_left] drag kanan → bola ke bawah-kiri via bottom bank"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   490, "end_y":   1380,
            "duration_ms": 980, "reverse": True,
            "strategy": "bottom_bank",
            "uses_portal": False,
            "note": "L18 [bottom_left_wide] lebih ke kiri, power max"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   430, "end_y":   1420,
            "duration_ms": 1000, "reverse": True,
            "strategy": "bottom_bank",
            "uses_portal": False,
            "note": "L18 [bottom_bank_moderate] kiri bawah, power tinggi"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   260, "end_y":   1380,
            "duration_ms": 980, "reverse": True,
            "strategy": "bottom_bank",
            "uses_portal": True,
            "note": "L18 [portal_test] masuk portal kiri — test apakah ke target bawah"
        },
    ],
}


def get_candidates(level: int) -> list:
    """Return daftar kandidat shot untuk level tertentu."""
    return CANDIDATES.get(level, [])


def get_candidate(level: int, index: int) -> dict:
    """Return satu kandidat shot. Return None jika tidak ada."""
    candidates = get_candidates(level)
    if 0 <= index < len(candidates):
        return candidates[index]
    return None


def total_candidates(level: int) -> int:
    """Jumlah total kandidat untuk level tertentu."""
    return len(get_candidates(level))


def next_candidate(level: int, tried: set) -> tuple:
    """
    Return (index, candidate) kandidat berikutnya yang belum dicoba.
    tried: set of int (index yang sudah dicoba).
    Return (None, None) jika semua kandidat sudah dicoba.
    """
    candidates = get_candidates(level)
    for i, cand in enumerate(candidates):
        if i not in tried:
            return i, cand
    return None, None


def candidates_exhausted(level: int, tried: set) -> bool:
    """Return True jika semua kandidat sudah dicoba."""
    return len(tried) >= total_candidates(level)


def add_candidate(level: int, shot: dict):
    """Tambahkan kandidat baru ke level tertentu (runtime)."""
    if level not in CANDIDATES:
        CANDIDATES[level] = []
    CANDIDATES[level].append(shot)
    print(f"[Candidates] ✅ Kandidat baru ditambahkan ke Level {level}: {shot.get('note', '')}")


def get_strategy_summary(level: int) -> str:
    """Return satu baris ringkasan strategi + jumlah kandidat."""
    mapping = get_mapping(level)
    n       = total_candidates(level)
    strat   = mapping.get("strategy", "?")
    power   = mapping.get("power", "?")
    portal  = mapping.get("uses_portal", False)
    portal_s = f" | portal={'yes' if portal is True else ('maybe' if portal == 'maybe' else 'no')}"
    return (f"Level {level:2d} | strategy={strat:30s} | power={power:12s}"
            f"{portal_s} | candidates={n}")


def get_strategy_summary(level: int) -> str:
    """Return satu baris ringkasan strategi + jumlah kandidat."""
    mapping = get_mapping(level)
    n       = total_candidates(level)
    strat   = mapping.get("strategy", "?")
    power   = mapping.get("power", "?")
    portal  = mapping.get("uses_portal", False)
    portal_s = f" | portal={'yes' if portal is True else ('maybe' if portal == 'maybe' else 'no')}"
    return (f"Level {level:2d} | strategy={strat:30s} | power={power:12s}"
            f"{portal_s} | candidates={n}")


def print_all_candidates():
    """Debug: print semua kandidat beserta strategi."""
    for lvl in range(1, 19):
        mapping = get_mapping(lvl)
        print(f"\n{'─'*60}")
        print(f"  Level {lvl} — [{mapping.get('strategy', '?').upper()}]")
        print(f"  {mapping.get('description', '')[:80]}")
        for i, c in enumerate(get_candidates(lvl)):
            print(f"    [{i}] ({c['start_x']},{c['start_y']})→({c['end_x']},{c['end_y']})"
                  f"  {c.get('duration_ms')}ms  portal={c.get('uses_portal',False)}"
                  f"  | {c.get('note','')}")
