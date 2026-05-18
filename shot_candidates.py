# ============================================================
#  shot_candidates.py — Daftar kandidat shot per Level 1-18
#  Resolusi: 720x1600
#
#  Format tiap kandidat:
#  {
#    "start_x": int,   # koordinat awal swipe (posisi dekat bola)
#    "start_y": int,
#    "end_x":   int,   # koordinat akhir swipe (arah drag)
#    "end_y":   int,
#    "duration_ms": int,
#    "reverse": bool,  # True = arah swipe berlawanan dari arah tembak
#    "note":    str    # deskripsi kandidat
#  }
#
#  PENTING:
#  - Koordinat ini adalah POSISI SWIPE DI LAYAR (720x1600).
#  - Untuk game billiard/golf 2D: drag ke arah BERLAWANAN dari
#    target agar bola meluncur ke arah target.
#  - reverse=True: end point adalah arah backswing (berlawanan target).
#  - Setelah training berhasil (y), kandidat tersimpan sebagai best shot.
#  - Kandidat yang sudah punya best shot TIDAK dijalankan lagi.
# ============================================================

# ── STRUKTUR DATA ────────────────────────────────────────────
# CANDIDATES[level] = list of dict
# Index 0 = kandidat pertama yang dicoba
# ─────────────────────────────────────────────────────────────

CANDIDATES: dict = {

    # ──────────────────── LEVEL 1 ────────────────────────────
    1: [
        {
            "start_x": 360, "start_y": 900,
            "end_x":   360, "end_y":   1150,
            "duration_ms": 850, "reverse": True,
            "note": "Level 1 – tembak lurus ke atas, drag ke bawah"
        },
        {
            "start_x": 360, "start_y": 900,
            "end_x":   360, "end_y":   1200,
            "duration_ms": 900, "reverse": True,
            "note": "Level 1 – power lebih kuat"
        },
        {
            "start_x": 360, "start_y": 900,
            "end_x":   320, "end_y":   1150,
            "duration_ms": 850, "reverse": True,
            "note": "Level 1 – sedikit ke kiri"
        },
    ],

    # ──────────────────── LEVEL 2 ────────────────────────────
    2: [
        {
            "start_x": 360, "start_y": 950,
            "end_x":   420, "end_y":   1200,
            "duration_ms": 850, "reverse": True,
            "note": "Level 2 – diagonal kanan atas"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   400, "end_y":   1250,
            "duration_ms": 900, "reverse": True,
            "note": "Level 2 – power lebih kuat diagonal"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   360, "end_y":   1200,
            "duration_ms": 850, "reverse": True,
            "note": "Level 2 – lurus ke atas"
        },
    ],

    # ──────────────────── LEVEL 3 ────────────────────────────
    3: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   300, "end_y":   1250,
            "duration_ms": 850, "reverse": True,
            "note": "Level 3 – diagonal kiri atas"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   280, "end_y":   1280,
            "duration_ms": 900, "reverse": True,
            "note": "Level 3 – lebih ke kiri"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1300,
            "duration_ms": 950, "reverse": True,
            "note": "Level 3 – lurus power tinggi"
        },
    ],

    # ──────────────────── LEVEL 4 ────────────────────────────
    4: [
        {
            "start_x": 360, "start_y": 980,
            "end_x":   450, "end_y":   1230,
            "duration_ms": 850, "reverse": True,
            "note": "Level 4 – diagonal kanan"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   480, "end_y":   1260,
            "duration_ms": 880, "reverse": True,
            "note": "Level 4 – lebih kanan"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   420, "end_y":   1300,
            "duration_ms": 920, "reverse": True,
            "note": "Level 4 – power tinggi diagonal"
        },
    ],

    # ──────────────────── LEVEL 5 ────────────────────────────
    5: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1350,
            "duration_ms": 900, "reverse": True,
            "note": "Level 5 – lurus ke atas power kuat"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   330, "end_y":   1300,
            "duration_ms": 850, "reverse": True,
            "note": "Level 5 – sedikit kiri"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   390, "end_y":   1300,
            "duration_ms": 850, "reverse": True,
            "note": "Level 5 – sedikit kanan"
        },
    ],

    # ──────────────────── LEVEL 6 ────────────────────────────
    6: [
        {
            "start_x": 360, "start_y": 950,
            "end_x":   250, "end_y":   1150,
            "duration_ms": 800, "reverse": True,
            "note": "Level 6 – kiri kuat"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   230, "end_y":   1200,
            "duration_ms": 850, "reverse": True,
            "note": "Level 6 – lebih kiri"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   280, "end_y":   1200,
            "duration_ms": 850, "reverse": True,
            "note": "Level 6 – kiri sedang"
        },
    ],

    # ──────────────────── LEVEL 7 ────────────────────────────
    7: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   480, "end_y":   1100,
            "duration_ms": 750, "reverse": True,
            "note": "Level 7 – kanan dekat, power rendah"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   500, "end_y":   1150,
            "duration_ms": 800, "reverse": True,
            "note": "Level 7 – kanan sedang"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   460, "end_y":   1200,
            "duration_ms": 850, "reverse": True,
            "note": "Level 7 – kanan power sedang"
        },
    ],

    # ──────────────────── LEVEL 8 ────────────────────────────
    8: [
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   360, "end_y":   1400,
            "duration_ms": 950, "reverse": True,
            "note": "Level 8 – lurus power tinggi"
        },
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   340, "end_y":   1380,
            "duration_ms": 930, "reverse": True,
            "note": "Level 8 – sedikit kiri power tinggi"
        },
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   380, "end_y":   1380,
            "duration_ms": 930, "reverse": True,
            "note": "Level 8 – sedikit kanan power tinggi"
        },
    ],

    # ──────────────────── LEVEL 9 ────────────────────────────
    9: [
        {
            "start_x": 360, "start_y": 980,
            "end_x":   260, "end_y":   1180,
            "duration_ms": 850, "reverse": True,
            "note": "Level 9 – kiri atas"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   240, "end_y":   1220,
            "duration_ms": 880, "reverse": True,
            "note": "Level 9 – lebih kiri"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   300, "end_y":   1250,
            "duration_ms": 900, "reverse": True,
            "note": "Level 9 – kiri power sedang"
        },
    ],

    # ──────────────────── LEVEL 10 ───────────────────────────
    10: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   460, "end_y":   1300,
            "duration_ms": 900, "reverse": True,
            "note": "Level 10 – kanan power tinggi"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   440, "end_y":   1280,
            "duration_ms": 880, "reverse": True,
            "note": "Level 10 – kanan sedang"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   480, "end_y":   1350,
            "duration_ms": 950, "reverse": True,
            "note": "Level 10 – kanan power maksimal"
        },
    ],

    # ──────────────────── LEVEL 11 ───────────────────────────
    11: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1250,
            "duration_ms": 850, "reverse": True,
            "note": "Level 11 – lurus sedang"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   340, "end_y":   1280,
            "duration_ms": 870, "reverse": True,
            "note": "Level 11 – sedikit kiri"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   380, "end_y":   1280,
            "duration_ms": 870, "reverse": True,
            "note": "Level 11 – sedikit kanan"
        },
    ],

    # ──────────────────── LEVEL 12 ───────────────────────────
    12: [
        {
            "start_x": 360, "start_y": 980,
            "end_x":   220, "end_y":   1180,
            "duration_ms": 850, "reverse": True,
            "note": "Level 12 – kiri jauh"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   200, "end_y":   1200,
            "duration_ms": 880, "reverse": True,
            "note": "Level 12 – kiri sangat jauh"
        },
        {
            "start_x": 360, "start_y": 980,
            "end_x":   250, "end_y":   1220,
            "duration_ms": 900, "reverse": True,
            "note": "Level 12 – kiri jauh power tinggi"
        },
    ],

    # ──────────────────── LEVEL 13 ───────────────────────────
    13: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   500, "end_y":   1200,
            "duration_ms": 850, "reverse": True,
            "note": "Level 13 – kanan jauh"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   520, "end_y":   1230,
            "duration_ms": 880, "reverse": True,
            "note": "Level 13 – kanan sangat jauh"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   480, "end_y":   1280,
            "duration_ms": 920, "reverse": True,
            "note": "Level 13 – kanan power tinggi"
        },
    ],

    # ──────────────────── LEVEL 14 ───────────────────────────
    14: [
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   360, "end_y":   1450,
            "duration_ms": 1000, "reverse": True,
            "note": "Level 14 – lurus power maksimal"
        },
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   350, "end_y":   1430,
            "duration_ms": 980, "reverse": True,
            "note": "Level 14 – sedikit kiri power maksimal"
        },
        {
            "start_x": 360, "start_y": 1050,
            "end_x":   370, "end_y":   1430,
            "duration_ms": 980, "reverse": True,
            "note": "Level 14 – sedikit kanan power maksimal"
        },
    ],

    # ──────────────────── LEVEL 15 ───────────────────────────
    15: [
        {
            "start_x": 360, "start_y": 950,
            "end_x":   290, "end_y":   1150,
            "duration_ms": 820, "reverse": True,
            "note": "Level 15 – kiri atas ringan"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   270, "end_y":   1180,
            "duration_ms": 850, "reverse": True,
            "note": "Level 15 – kiri atas sedang"
        },
        {
            "start_x": 360, "start_y": 950,
            "end_x":   250, "end_y":   1200,
            "duration_ms": 870, "reverse": True,
            "note": "Level 15 – kiri atas kuat"
        },
    ],

    # ──────────────────── LEVEL 16 ───────────────────────────
    16: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   430, "end_y":   1150,
            "duration_ms": 800, "reverse": True,
            "note": "Level 16 – kanan atas ringan"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   450, "end_y":   1180,
            "duration_ms": 830, "reverse": True,
            "note": "Level 16 – kanan atas sedang"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   470, "end_y":   1220,
            "duration_ms": 870, "reverse": True,
            "note": "Level 16 – kanan atas kuat"
        },
    ],

    # ──────────────────── LEVEL 17 ───────────────────────────
    17: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1300,
            "duration_ms": 900, "reverse": True,
            "note": "Level 17 – lurus power tinggi"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   320, "end_y":   1320,
            "duration_ms": 920, "reverse": True,
            "note": "Level 17 – kiri power tinggi"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   400, "end_y":   1320,
            "duration_ms": 920, "reverse": True,
            "note": "Level 17 – kanan power tinggi"
        },
    ],

    # ──────────────────── LEVEL 18 ───────────────────────────
    18: [
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   260, "end_y":   1300,
            "duration_ms": 950, "reverse": True,
            "note": "Level 18 – kiri power maksimal"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   240, "end_y":   1350,
            "duration_ms": 1000, "reverse": True,
            "note": "Level 18 – kiri sangat kuat"
        },
        {
            "start_x": 360, "start_y": 1000,
            "end_x":   360, "end_y":   1400,
            "duration_ms": 1000, "reverse": True,
            "note": "Level 18 – lurus power penuh"
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


def add_candidate(level: int, shot: dict):
    """Tambahkan kandidat baru ke level tertentu (runtime)."""
    if level not in CANDIDATES:
        CANDIDATES[level] = []
    CANDIDATES[level].append(shot)
    print(f"[Candidates] ✅ Kandidat baru ditambahkan ke Level {level}: {shot.get('note', '')}")
