# ============================================================
#  vision.py — Analisis Screenshot via Claude Vision API
# ============================================================

import anthropic
import json
import re
from config import CLAUDE_API_KEY, CLAUDE_MODEL


client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


# ============================================================
#  PROMPT UNTUK CLAUDE
# ============================================================

ANALYZE_PROMPT = """
Kamu adalah AI yang membantu memainkan game Golf Billiard di OutiePutt (app.outieputt.com).

Analisis screenshot game ini dan tentukan:

1. **STATE** game saat ini — pilih salah satu:
   - "menu"            : layar menu utama, ada tombol PLAY SOLO / MULTIPLAYER
   - "ready_to_shoot"  : sudah di dalam game, bola putih terlihat, siap ditembak
   - "ball_moving"     : bola sedang bergerak/rolling
   - "hole_complete"   : bola masuk hole, muncul tombol Next/Continue
   - "game_complete"   : game selesai semua hole, ada skor akhir
   - "loading"         : layar loading / transisi / spinner

2. **PLAY_SOLO_BUTTON** (hanya jika state = "menu"):
   - x dan y koordinat tombol "PLAY SOLO" atau "SOLO" atau "1 Player"
   - Cari tombol yang artinya main sendiri (bukan multiplayer)

3. **BALL_POSITION** (hanya jika state = "ready_to_shoot"):
   - x dan y dalam pixel posisi TENGAH bola putih

4. **HOLE_POSITION** (hanya jika state = "ready_to_shoot"):
   - x dan y dalam pixel posisi TENGAH lubang (hole/cup) target
   - Lubang biasanya berwarna gelap/hitam/cokelat, atau ada bendera kecil

5. **NEXT_BUTTON** (hanya jika state = "hole_complete" atau "game_complete"):
   - x dan y koordinat tombol Next/Continue/Play Again

6. **SHOT_POWER** (hanya jika state = "ready_to_shoot"):
   - Nilai 0.1 sampai 1.0
   - Hitung dari jarak bola ke hole relatif ukuran layar
   - Dekat = 0.2, Sedang = 0.5, Jauh = 0.8

7. **NOTES**: Observasi penting (rintangan, cushion/pantulan, dll)

Balas HANYA dengan JSON berikut (tidak ada teks lain):
{
  "state": "...",
  "play_solo_button": {"x": 0, "y": 0},
  "ball": {"x": 0, "y": 0},
  "hole": {"x": 0, "y": 0},
  "next_button": {"x": 0, "y": 0},
  "shot_power": 0.5,
  "notes": "..."
}
"""


# ============================================================
#  FUNGSI ANALISIS
# ============================================================

def analyze_screen(screenshot_b64: str, screen_w: int, screen_h: int) -> dict:
    """
    Kirim screenshot ke Claude dan minta analisis posisi bola, hole, dll.
    Return dict hasil analisis.
    """
    print("[Vision] Mengirim screenshot ke Claude AI...")

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": ANALYZE_PROMPT + f"\n\nResolusi layar: {screen_w}x{screen_h}px"
                        }
                    ],
                }
            ],
        )

        raw = response.content[0].text.strip()
        print(f"[Vision] Respons Claude: {raw}")

        # Parse JSON dari respons
        result = parse_json_response(raw)
        return result

    except Exception as e:
        print(f"[Vision] ERROR saat panggil Claude API: {e}")
        return {"state": "error", "notes": str(e)}





def parse_json_response(text: str) -> dict:
    """Extract dan parse JSON dari teks respons Claude."""
    # Coba langsung parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Coba extract dari ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Coba extract { ... } pertama yang ditemukan
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    print(f"[Vision] Gagal parse JSON dari: {text}")
    return {"state": "parse_error", "notes": text}


# ============================================================
#  KALKULASI TEMBAKAN
# ============================================================

def calculate_shot(ball: dict, hole: dict, power: float,
                   min_drag: int = 80, max_drag: int = 500) -> dict:
    """
    Hitung koordinat swipe berdasarkan posisi bola, hole, dan power.

    Cara main OutiePutt:
    - Kamu drag dari posisi bola ke arah BERLAWANAN dari hole
    - Semakin jauh drag = semakin kuat tembakan
    - Lepas = bola meluncur ke arah hole

    Return dict: {start_x, start_y, end_x, end_y}
    """
    import math

    bx, by = ball["x"], ball["y"]
    hx, hy = hole["x"], hole["y"]

    # Vektor dari bola ke hole
    dx = hx - bx
    dy = hy - by
    distance = math.sqrt(dx**2 + dy**2)

    if distance == 0:
        return {"start_x": bx, "start_y": by,
                "end_x": bx, "end_y": by + 150}

    # Normalize vektor
    nx = dx / distance
    ny = dy / distance

    # Panjang drag berdasarkan power
    drag_length = min_drag + (max_drag - min_drag) * power

    # End point = arah BERLAWANAN dari hole
    end_x = int(bx - nx * drag_length)
    end_y = int(by - ny * drag_length)

    angle_deg = math.degrees(math.atan2(dy, dx))

    print(f"[Shot] Bola({bx},{by}) → Hole({hx},{hy})")
    print(f"[Shot] Sudut: {angle_deg:.1f}° | Power: {power:.2f} | Drag: {drag_length:.0f}px")
    print(f"[Shot] Swipe: ({bx},{by}) → ({end_x},{end_y})")

    return {
        "start_x": bx,
        "start_y": by,
        "end_x": end_x,
        "end_y": end_y,
        "angle": angle_deg,
        "drag_length": drag_length
    }
