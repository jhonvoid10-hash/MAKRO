# ============================================================
#  level_mapping.py — Strategi & Mapping tiap Level 1-18
#  OutiePutt Golf Billiard — Resolusi 720x1600
#
#  Dipakai oleh:
#    - train_auto_continue_next.py  → tampilkan hint saat training
#    - vision_utils.py              → inject ke prompt Claude
#    - shot_candidates.py           → referensi pemilihan kandidat
#
#  Aturan:
#    - Mapping ini HANYA panduan strategi, bukan koordinat final mutlak.
#    - Tetap validasi dengan screenshot & kandidat aktual.
#    - Jangan ubah best_shot yang sudah tersimpan.
#    - Kalau shot sukses → simpan ke level_XX_best_shot.json.
#    - Kalau shot gagal  → catat, jangan ulang kandidat yang sama.
#    - Kalau arah kebalik → reverse=True.
#    - Portal/trap: pakai hanya kalau jelas membantu ke hole asli.
# ============================================================

LEVEL_MAPPING: dict = {

    1: {
        "strategy":    "bank_right",
        "description": (
            "Ada obstacle di tengah/jalur langsung. "
            "Shot yang terbukti: pantulan kanan (right wall bank). "
            "Level 1 dipakai sebagai replay/jalan tol ke level berikutnya — "
            "JANGAN ubah best_shot jika sudah tersimpan."
        ),
        "route":       "right_bank",
        "avoid":       ["center_direct", "left_side"],
        "prefer":      ["right_wall_bank"],
        "power":       "medium",          # low / medium / high / max
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Level paling penting — dipakai ulang setiap recover.",
    },

    2: {
        "strategy":    "gap_through_bars",
        "description": (
            "Ada beberapa obstacle/bar yang menghalangi jalur langsung. "
            "Cari jalur bank/pantulan yang melewati CELAH, "
            "jangan tembak lurus menabrak bar."
        ),
        "route":       "gap_or_bank",
        "avoid":       ["direct_through_bars", "full_left", "full_right"],
        "prefer":      ["gap_left_of_bar", "gap_right_of_bar", "bank_around"],
        "power":       "medium",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Prioritas melewati celah antar bar.",
    },

    3: {
        "strategy":    "center_lane",
        "description": (
            "Jalur utama lewat area tengah. "
            "Ada arah/area seperti up-arrow/guide di tengah. "
            "Prioritas cari lintasan masuk melalui lane tengah, "
            "bukan menabrak sisi obstacle. "
            "Kalau swipe normal kebalik, gunakan reverse swipe."
        ),
        "route":       "center_up",
        "avoid":       ["left_wall_direct", "right_wall_direct"],
        "prefer":      ["center_lane_through", "slight_left_center"],
        "power":       "medium_high",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Reverse swipe mungkin diperlukan.",
    },

    4: {
        "strategy":    "left_route",
        "description": (
            "Ada jalur kiri / area up-arrow kiri yang lebih aman. "
            "Hindari hole/trap bawah kanan jika bukan jalur portal yang benar. "
            "Utamakan jalur yang memanfaatkan sisi kiri untuk menuju target."
        ),
        "route":       "left_lane",
        "avoid":       ["bottom_right_trap", "center_direct"],
        "prefer":      ["left_up_arrow_lane", "slight_left"],
        "power":       "medium",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Waspadai trap bawah kanan.",
    },

    5: {
        "strategy":    "center_lane",
        "description": (
            "Jalur relatif melalui lane tengah. "
            "Cari shot yang melewati area center/cyan lane. "
            "Jangan terlalu melebar ke obstacle samping."
        ),
        "route":       "center_straight",
        "avoid":       ["far_left_obstacle", "far_right_obstacle"],
        "prefer":      ["center_lane", "center_slight_adjust"],
        "power":       "medium_high",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Stay center, jangan melebar.",
    },

    6: {
        "strategy":    "narrow_gate",
        "description": (
            "Layout seperti hourglass/gate sempit. "
            "Shot harus melewati celah tengah. "
            "Akurasi arah lebih penting daripada power kecil. "
            "Power boleh besar selama bola melewati hole/target."
        ),
        "route":       "center_gate",
        "avoid":       ["wide_left", "wide_right", "low_power_stall"],
        "prefer":      ["center_gate_precise", "medium_high_power_center"],
        "power":       "high",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Akurasi > power. Gate sempit.",
    },

    7: {
        "strategy":    "slanted_corridor",
        "description": (
            "Ada koridor miring/slanted corridor. "
            "Jalur aman cenderung lewat sisi kiri/atas atau "
            "mengikuti kemiringan obstacle. "
            "Jangan tembak lurus kalau jalurnya menabrak obstacle."
        ),
        "route":       "left_along_slope",
        "avoid":       ["straight_into_wall", "right_side"],
        "prefer":      ["left_corridor", "follow_slope_angle"],
        "power":       "medium",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Ikuti sudut kemiringan koridor.",
    },

    8: {
        "strategy":    "left_target",
        "description": (
            "Target/jalur cenderung ke sisi kiri. "
            "Cari pantulan atau route yang mengarah ke kiri target. "
            "Hindari terlalu kanan jika ada obstacle menghalangi."
        ),
        "route":       "left_bank_or_direct",
        "avoid":       ["far_right", "direct_center_if_blocked"],
        "prefer":      ["left_of_center", "left_bank"],
        "power":       "high",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Target kiri — arahkan ke sana.",
    },

    9: {
        "strategy":    "portal_aware",
        "description": (
            "Ada kemungkinan hole trap/portal. "
            "Jangan langsung anggap semua hole sebagai target. "
            "Kalau ada portal, kandidat boleh test masuk portal "
            "hanya kalau keluarnya mengarah ke target asli. "
            "Kalau portal tidak terbukti membantu, gunakan safe bridge/lane."
        ),
        "route":       "safe_bridge_or_portal",
        "avoid":       ["blind_hole", "trap_hole"],
        "prefer":      ["safe_lane_bridge", "portal_if_helpful"],
        "power":       "medium",
        "reverse":     True,
        "uses_portal": "maybe",    # True / False / "maybe"
        "timing_sensitive": False,
        "notes":       "Verifikasi portal sebelum dipakai.",
    },

    10: {
        "strategy":    "dual_route",
        "description": (
            "Ada dua kemungkinan rute: kiri dan kanan. "
            "Cek apakah up-arrow kiri atau kanan lebih aman. "
            "Hindari jalur tengah kalau tertutup obstacle. "
            "Kandidat boleh coba left route dan right route."
        ),
        "route":       "left_or_right",
        "avoid":       ["blocked_center"],
        "prefer":      ["left_up_arrow", "right_up_arrow"],
        "power":       "medium_high",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Test kedua rute: kiri dulu, lalu kanan.",
    },

    11: {
        "strategy":    "avoid_center_obstacle",
        "description": (
            "Ada obstacle bergerak/berbentuk windmill atau area tengah berbahaya. "
            "Hindari pusat obstacle. Timing bisa berpengaruh. "
            "Cari jalur sisi kiri/aman yang tidak menabrak bagian tengah."
        ),
        "route":       "left_safe_side",
        "avoid":       ["center_windmill", "center_spinning"],
        "prefer":      ["left_bypass", "timed_gap"],
        "power":       "medium",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": True,
        "notes":       "Timing penting kalau obstacle bergerak.",
    },

    12: {
        "strategy":    "right_route",
        "description": (
            "Ada obstacle/tembok tengah. "
            "Jalur cenderung dari sisi kanan. "
            "Gunakan route kanan untuk melewati penghalang tengah "
            "lalu menuju target."
        ),
        "route":       "right_around_center",
        "avoid":       ["center_wall_direct", "far_left"],
        "prefer":      ["right_side_of_center", "right_bank"],
        "power":       "medium_high",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Putar kanan lewati tembok tengah.",
    },

    13: {
        "strategy":    "flagged_hole_only",
        "description": (
            "Target asli adalah hole yang berflag/tujuan akhir, "
            "bukan semua lubang. Ada kemungkinan hole portal/trap. "
            "Jika memakai portal, simpan catatan uses_portal=True. "
            "Kalau tidak memakai portal, hindari hole trap "
            "dan arahkan ke flagged target."
        ),
        "route":       "direct_to_flag_or_portal",
        "avoid":       ["trap_holes", "unmarked_holes"],
        "prefer":      ["flagged_target_direct", "portal_if_confirmed"],
        "power":       "medium_high",
        "reverse":     True,
        "uses_portal": "maybe",
        "timing_sensitive": False,
        "notes":       "Pastikan hole yang dituju adalah flagged hole.",
    },

    14: {
        "strategy":    "funnel_center",
        "description": (
            "Layout seperti funnel/center route. "
            "Gunakan jalur tengah mengikuti arrow/funnel. "
            "Jangan terlalu menyamping karena bisa mentok obstacle."
        ),
        "route":       "center_funnel",
        "avoid":       ["wide_left_obstacle", "wide_right_obstacle"],
        "prefer":      ["center_through_funnel"],
        "power":       "max",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Ikuti funnel — jangan menyamping.",
    },

    15: {
        "strategy":    "center_shaft",
        "description": (
            "Ada jalur vertikal/center shaft. "
            "Shot perlu power cukup besar melalui jalur tengah. "
            "Arah harus lurus/stabil agar tidak menyentuh dinding shaft."
        ),
        "route":       "vertical_shaft_center",
        "avoid":       ["shaft_wall_left", "shaft_wall_right"],
        "prefer":      ["straight_up_center_shaft"],
        "power":       "high",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Lurus sempurna — jangan geser kiri/kanan.",
    },

    16: {
        "strategy":    "left_bypass_stack",
        "description": (
            "Jalur target cenderung sisi kiri. "
            "Ada stack/obstacle vertikal yang harus dihindari. "
            "Cari jalur kiri yang melewati obstacle, "
            "bukan tembak langsung ke stack."
        ),
        "route":       "left_of_stack",
        "avoid":       ["direct_into_stack", "right_side"],
        "prefer":      ["left_bypass_vertical_stack"],
        "power":       "medium",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Kiri stack — jangan langsung ke tumpukan.",
    },

    17: {
        "strategy":    "short_direct",
        "description": (
            "Target relatif dekat / short route. "
            "Jangan overcomplicate. "
            "Gunakan shot pendek/direct jika memungkinkan. "
            "Kalau ada obstacle kecil, gunakan koreksi arah kecil."
        ),
        "route":       "short_direct_or_minor_adjust",
        "avoid":       ["overpower", "complex_bank"],
        "prefer":      ["direct_short", "slight_angle_correction"],
        "power":       "low_medium",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "Simple shot — jangan terlalu kuat.",
    },

    18: {
        "strategy":    "bottom_bank",
        "description": (
            "Target akhir cenderung bawah/kiri atau perlu route bawah. "
            "Ada kemungkinan portal/trap sisi kanan. "
            "Jangan langsung masuk portal kecuali jelas membantu. "
            "Bisa pakai bottom bank / pantulan bawah untuk melewati obstacle. "
            "Setelah Level 18 flow lanjut FINISH / PLAY AGAIN."
        ),
        "route":       "bottom_left_or_bank",
        "avoid":       ["right_portal_unverified", "direct_right"],
        "prefer":      ["bottom_bank", "left_bottom_route"],
        "power":       "max",
        "reverse":     True,
        "uses_portal": "maybe",
        "timing_sensitive": False,
        "notes":       "Level terakhir. Bottom bank atau kiri-bawah.",
    },
}


# ── POWER SCALE (referensi drag length di 720x1600) ──────────
POWER_SCALE = {
    "low":         150,   # px drag
    "low_medium":  200,
    "medium":      250,
    "medium_high": 310,
    "high":        370,
    "max":         430,
}


# ============================================================
#  PUBLIC API
# ============================================================

def get_mapping(level: int) -> dict:
    """Return mapping strategi untuk level tertentu."""
    return LEVEL_MAPPING.get(level, {
        "strategy":    "unknown",
        "description": "Tidak ada mapping untuk level ini.",
        "route":       "unknown",
        "avoid":       [],
        "prefer":      [],
        "power":       "medium",
        "reverse":     True,
        "uses_portal": False,
        "timing_sensitive": False,
        "notes":       "",
    })


def get_hint_text(level: int) -> str:
    """
    Return teks hint singkat untuk ditampilkan saat training.
    Format mudah dibaca di terminal.
    """
    m = get_mapping(level)
    lines = [
        f"  📋 Strategi Level {level}: [{m['strategy'].upper()}]",
        f"  📝 {m['description']}",
        f"  🛣️  Route    : {m['route']}",
        f"  ✅ Prefer  : {', '.join(m['prefer']) if m['prefer'] else '-'}",
        f"  ❌ Avoid   : {', '.join(m['avoid']) if m['avoid'] else '-'}",
        f"  ⚡ Power   : {m['power']}",
        f"  🔄 Reverse : {m['reverse']}",
        f"  🌀 Portal  : {m['uses_portal']}",
        f"  ⏱️  Timing  : {'SENSITIF' if m['timing_sensitive'] else 'tidak sensitif'}",
    ]
    if m.get("notes"):
        lines.append(f"  💡 Catatan : {m['notes']}")
    return "\n".join(lines)


def get_prompt_context(level: int) -> str:
    """
    Return konteks mapping dalam format teks untuk diinject ke
    prompt Claude Vision saat analisis screenshot level ini.
    """
    m = get_mapping(level)
    return (
        f"LEVEL {level} STRATEGY CONTEXT:\n"
        f"- Strategy: {m['strategy']}\n"
        f"- Description: {m['description']}\n"
        f"- Preferred route: {m['route']}\n"
        f"- Avoid: {', '.join(m['avoid'])}\n"
        f"- Prefer: {', '.join(m['prefer'])}\n"
        f"- Power level: {m['power']}\n"
        f"- Uses portal: {m['uses_portal']}\n"
        f"- Timing sensitive: {m['timing_sensitive']}\n"
        f"- Notes: {m.get('notes', '')}\n"
        f"- Reverse swipe: {m['reverse']}\n"
        f"\nIMPORTANT: Do NOT shoot into obstacles. "
        f"Only use portal if it clearly leads to the real target hole. "
        f"Do not repeat a failed candidate."
    )


def get_drag_length(level: int) -> int:
    """Return estimasi panjang drag (px) berdasarkan power mapping level."""
    m   = get_mapping(level)
    pwr = m.get("power", "medium")
    return POWER_SCALE.get(pwr, POWER_SCALE["medium"])


def uses_portal(level: int) -> bool | str:
    """Return apakah level ini memakai portal."""
    return get_mapping(level).get("uses_portal", False)


def is_timing_sensitive(level: int) -> bool:
    """Return True jika level ini sensitif terhadap timing."""
    return get_mapping(level).get("timing_sensitive", False)


def print_all_mappings():
    """Print seluruh mapping ke terminal — untuk debugging."""
    print("\n" + "="*60)
    print("  LEVEL MAPPING SUMMARY — OutiePutt Level 1-18")
    print("="*60)
    for lvl in range(1, 19):
        m = get_mapping(lvl)
        print(f"\n  Level {lvl:2d} | {m['strategy']:30s} | power={m['power']:12s} | "
              f"portal={str(m['uses_portal']):5s} | timing={m['timing_sensitive']}")
        print(f"          {m['description'][:80]}{'...' if len(m['description'])>80 else ''}")
    print("="*60)


if __name__ == "__main__":
    print_all_mappings()
