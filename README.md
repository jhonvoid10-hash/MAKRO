# 🏌️ MacroDroid - Auto Golf Billiard (OutiePutt)

Makro ini dirancang untuk memainkan game **Golf Billiard** di [https://app.outieputt.com/](https://app.outieputt.com/) secara otomatis menggunakan **MacroDroid** di Android.

---

## 📱 Persyaratan

| Kebutuhan | Detail |
|-----------|--------|
| Aplikasi | [MacroDroid](https://play.google.com/store/apps/details?id=com.arlosoft.macrodroid) versi 5.x ke atas |
| Android | Android 7.0+ |
| Izin | Accessibility Service harus aktif |
| Browser | Chrome / WebView yang buka `app.outieputt.com` |
| Resolusi | Dioptimalkan untuk **1080 x 2400** (FHD+) |

---

## 📂 Struktur File

```
MAKRO/
├── README.md                  ← Panduan ini
├── outieputt_macro.macro      ← File makro utama (import ke MacroDroid)
├── outieputt_helper.js        ← Script JS inject via ADB/WebView console
└── koordinat_kalibrasi.txt    ← Panduan kalibrasi koordinat layar
```

---

## 🚀 Cara Instalasi

### Metode 1: Import File `.macro`

1. Unduh file `outieputt_macro.macro`
2. Buka **MacroDroid** → Menu (☰) → **Import Macro**
3. Pilih file `.macro` yang sudah diunduh
4. Aktifkan makro

### Metode 2: Buat Manual

Ikuti langkah di bawah untuk membuat makro secara manual di MacroDroid.

---

## ⚙️ Cara Kerja Makro

Game OutiePutt menggunakan mekanik **klik + drag** (tarik stik biliar):

```
1. Deteksi posisi bola putih di layar
2. Hitung sudut arah ke lubang (hole)
3. Lakukan swipe dari bola → arah berlawanan (backswing)
4. Lepas untuk menembak
5. Tunggu animasi selesai
6. Ulangi untuk hole berikutnya
```

### Strategi Tembakan:
- **Jarak dekat** (< 30% layar): Swipe pendek ~150px
- **Jarak sedang** (30-60% layar): Swipe sedang ~300px  
- **Jarak jauh** (> 60% layar): Swipe panjang ~500px

---

## 🗺️ Peta Koordinat (Resolusi 1080x2400)

```
┌─────────────────────────┐
│  HOLE 1    │   HOLE 2   │  Y: ~400
│  (200,400) │  (880,400) │
├────────────┼────────────┤
│            │            │
│  HOLE 3    │   HOLE 4   │  Y: ~1200
│  (200,1200)│  (880,1200)│
├────────────┼────────────┤
│  HOLE 5    │   HOLE 6   │  Y: ~2000
│  (200,2000)│  (880,2000)│
└─────────────────────────┘

BOLA PUTIH (Start): ~(540, 1200)
```

---

## 🔧 Konfigurasi Makro di MacroDroid

### TRIGGER (Pemicu)
- **Tipe:** Shake Device (Kocok HP) ATAU Button Tile (Tile di Notification Bar)
- **Setting:** Intensitas shake = Medium

### ACTIONS (Aksi) — Urutan Eksekusi

```
[1] Launch App → Chrome → https://app.outieputt.com/
[2] Wait → 3000ms (tunggu game load)
[3] Loop (9 kali = 9 holes)
    ├─ [3.1] Tap posisi BOLA PUTIH (540, 1400)
    ├─ [3.2] Wait 500ms
    ├─ [3.3] Swipe: Hitung arah ke hole
    ├─ [3.4] Wait 2000ms (tunggu animasi)
    └─ [3.5] Tap tombol NEXT HOLE
[4] Toast "🏌️ Game Selesai!"
```

---

## 📐 Cara Kalibrasi Koordinat

Karena resolusi HP berbeda-beda, lakukan kalibrasi:

1. Buka game di browser
2. Di MacroDroid: **Tools → Screen Capture** untuk lihat koordinat
3. Catat posisi:
   - Titik tengah bola putih
   - Posisi tiap lubang (hole)
   - Tombol "Next Hole" / "Play Again"
4. Update nilai koordinat di makro

---

## 🎯 Tips & Trik

- **Aktifkan "Keep Screen On"** di MacroDroid agar layar tidak mati
- Gunakan **MacroDroid Pro** untuk fitur UI Interaction yang lebih akurat
- Pastikan **Brightness** cukup tinggi agar screen capture akurat
- Mode **Do Not Disturb** agar notifikasi tidak menggangu swipe

---

## ⚠️ Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Makro tidak jalan | Pastikan Accessibility Service aktif |
| Swipe tidak tepat | Kalibrasi ulang koordinat |
| Game tidak loading | Tambah delay di action pertama |
| Layar berputar | Kunci orientasi Portrait di Android |

---

## 📄 Lisensi

Free to use — dibuat untuk keperluan belajar MacroDroid automation.
