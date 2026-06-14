---
title: archimate_implementation_migration_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Implementation & Migration Layer

Video tutorial animasi singkat tentang Implementation & Migration Layer pada bahasa enterprise-architecture ArchiMate — layer yang merencanakan transisi: roadmap, paket kerja, dan tonggak yang membawa arsitektur dari kondisi sekarang ke kondisi yang diinginkan. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama elemen ArchiMate (kosakata standar notasi).

Contoh konsisten di SELURUH scene: sebuah RESTORAN yang menggelar layanan pemesanan online / delivery secara BERTAHAP (dari hanya offline menuju online + delivery).

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

ELEMEN = kotak (RoundedRectangle) digambar dengan Manim:
- Warna isi kotak = warna native layer-nya: Implementation & Migration = MERAH MUDA / PINK; Strategy = oranye; Motivation = UNGU; Business = kuning; Application = biru muda; Technology = hijau. (Aksen panel/teks boleh memakai variasi warna Implementation/pink.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Berkas logo Implementation & Migration: `implementation_work_package_logo.svg`, `implementation_deliverable_logo.svg`, `implementation_implementation_event_logo.svg`, `implementation_plateau_logo.svg`, `implementation_gap_logo.svg`.
- Berkas logo lintas layer (HANYA scene lintas-layer 05): `strategy_course_of_action_logo.svg`, `motivation_goal_logo.svg`.

RELASI = JANGAN memuat SVG. Gambar dengan metode internal Manim (`Line` / `DashedLine` + bentuk kepala dari `Polygon`/`Triangle`/`Dot`) memakai helper build yang tersedia (`archi_element`, `assignment_arrow`, `serving_arrow`, `realization_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`) agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Pola garis + bentuk kepala sesuai notasi ArchiMate (pola yang DIPAKAI di layer ini):
- Realization (`realization_arrow`): garis TITIK-TITIK (dotted); kepala SEGITIGA KOSONG (outline) di target. Dipakai: Work Package —realization→ Deliverable; Plateau —realization→ Motivation Goal; Work Package —realization→ Strategy Course of Action.
- Composition (`composition_arrow`): garis SOLID; BELAH KETUPAT TERISI di ujung sumber. Dipakai: Plateau tersusun dari (composed of) elemen-elemen arsitektur penyusunnya.
- Association (`association_arrow`): garis SOLID polos (tanpa kepala, atau panah terbuka kecil). Dipakai: sebuah Gap dikaitkan ke DUA Plateau (Baseline dan Target).
- Triggering (urutan antar Work Package sepanjang waktu): garis SOLID dengan kepala panah TERISI di target — menyatakan "lalu lanjut ke" (sequence/temporal).
Beri label nama relasi di dekat garis bila membantu.

## 01_posisi_layer (~18s)
Judul besar "ArchiMate — Implementation & Migration Layer" di tengah + subjudul "the roadmap that delivers the change". Gambar kerangka ArchiMate sebagai pita berwarna — Strategy oranye, Business kuning, Application biru, Technology hijau, Motivation ungu — lalu tampilkan Implementation & Migration sebagai pita MERAH MUDA / PINK yang membentang di BAWAH dan MEMBUNGKUS semua layer lain (karena ia merencanakan bagaimana semua perubahan itu DIWUJUDKAN bertahap dari waktu ke waktu). Sorot pita pink dengan warna HIGHLIGHT. Tegaskan: layer ini menjawab "kapan & dalam langkah apa" perubahan terjadi.

## 02_kosakata_elemen (~30s)
Perkenalkan kosakata layer; tiap kotak = warna Implementation/PINK + nama di dalam + logo di pojok kanan atas + contoh restoran di bawah kotak, muncul bertahap:
- Work Package (`implementation_work_package_logo.svg`): "Bangun Aplikasi Delivery", "Pelatihan Staf" — sekumpulan pekerjaan untuk mencapai hasil.
- Deliverable (`implementation_deliverable_logo.svg`): "Aplikasi Delivery v1", "Dokumen SOP" — hasil nyata dan terukur dari sebuah Work Package.
- Plateau (`implementation_plateau_logo.svg`): "Baseline: Hanya Offline", "Target: Online + Delivery" — kondisi arsitektur yang stabil pada satu titik waktu.
- Gap (`implementation_gap_logo.svg`): "Belum ada sistem pemesanan online" — selisih antara dua Plateau.
- Implementation Event (`implementation_implementation_event_logo.svg`): "Go-Live" — peristiwa/tonggak yang menandai perubahan keadaan.
Tampilkan bertahap agar tidak penuh; pakai warna ACCENT untuk label contoh.

## 03_plateau_dan_gap (~26s)
Fokus pada perpindahan keadaan; tiap kotak = warna Implementation/PINK + nama di dalam + logo di pojok kanan atas; relasi DIGAMBAR Manim:
- Plateau (`implementation_plateau_logo.svg`) "Baseline: Hanya Offline" di kiri (warna netral/DANGER untuk menandai keadaan lama yang ingin ditinggalkan).
- Plateau (`implementation_plateau_logo.svg`) "Target: Online + Delivery" di kanan (warna OK untuk keadaan yang diinginkan).
- Di antara keduanya, Gap (`implementation_gap_logo.svg`) "Belum ada sistem pemesanan online" —association→ KEDUA Plateau (garis SOLID polos ke Baseline dan ke Target), disorot HIGHLIGHT. Tegaskan: Gap = apa yang HILANG/HARUS DITUTUP saat berpindah dari Baseline ke Target.

## 04_keterkaitan_elemen (~26s)
Rangkai elemen dengan relasi ArchiMate yang DIGAMBAR Manim; tiap kotak = warna Implementation/PINK + nama di dalam + logo di pojok kanan atas; tiap garis diberi label:
- Work Package (`implementation_work_package_logo.svg`) "Bangun Aplikasi Delivery" —realization→ Deliverable (`implementation_deliverable_logo.svg`) "Aplikasi Delivery v1" (garis TITIK-TITIK; kepala SEGITIGA KOSONG di Deliverable): paket kerja menghasilkan deliverable.
- Work Package "Pelatihan Staf" —realization→ Deliverable "Dokumen SOP".
- Urutan antar Work Package (triggering sepanjang waktu): Work Package "Bangun Aplikasi Delivery" —triggering→ Work Package "Pelatihan Staf" (garis SOLID; kepala panah TERISI), lalu menuju Implementation Event (`implementation_implementation_event_logo.svg`) "Go-Live". Tegaskan: paket kerja dijalankan BERURUTAN menuju tonggak Go-Live.

## 05_keterkaitan_lintas_layer (~28s)
Ikat roadmap kembali ke "mengapa" (Motivation) dan "cara tingkat tinggi" (Strategy). Tiap kotak = warna native layer-nya + nama di dalam + logo di pojok kanan atas; semua relasi DIGAMBAR Manim (lihat pola di Preparation):
- Work Package (kotak PINK, `implementation_work_package_logo.svg`) "Bangun Aplikasi Delivery" —realization→ Strategy Course of Action (kotak ORANYE, `strategy_course_of_action_logo.svg`) "Mulai jualan online" (garis TITIK-TITIK; kepala SEGITIGA KOSONG): paket kerja mewujudkan rencana strategis.
- Plateau (kotak PINK, `implementation_plateau_logo.svg`) "Target: Online + Delivery" —realization→ Motivation Goal (kotak UNGU, `motivation_goal_logo.svg`) "Tingkatkan pendapatan" (garis TITIK-TITIK; kepala SEGITIGA KOSONG): kondisi target mewujudkan tujuan.
Tegaskan dengan warna PRIMARY: Implementation & Migration = "kapan & dalam langkah apa" yang MEWUJUDKAN Strategy ("cara tingkat tinggi") dan Motivation ("mengapa").

## 06_contoh_roadmap (~32s)
Rakit roadmap restoran secara bertahap; semua kotak elemen + relasi DIGAMBAR Manim, dari kiri (sekarang) ke kanan (tujuan):
Plateau (`implementation_plateau_logo.svg`) "Baseline: Hanya Offline" — Gap (`implementation_gap_logo.svg`) "Belum ada sistem pemesanan online" —association→ kedua Plateau. Plateau "Target: Online + Delivery" tersusun dari (composition; garis SOLID, BELAH KETUPAT TERISI di Plateau) Deliverable (`implementation_deliverable_logo.svg`) "Aplikasi Delivery v1" + "Dokumen SOP". Work Package (`implementation_work_package_logo.svg`) "Bangun Aplikasi Delivery" —triggering→ Work Package "Pelatihan Staf" (garis SOLID; kepala panah TERISI), masing-masing —realization→ Deliverable-nya, lalu —triggering→ Implementation Event (`implementation_implementation_event_logo.svg`) "Go-Live" yang menandai tercapainya Plateau Target. Sorot jalur waktu dengan warna HIGHLIGHT.

## 07_kesimpulan (~16s)
Ringkas: Implementation & Migration Layer merencanakan transisi lewat lima elemen — tampilkan lagi kelima ikon aslinya (kotak PINK + logo di pojok kanan atas): Work Package (`implementation_work_package_logo.svg`), Deliverable (`implementation_deliverable_logo.svg`), Plateau (`implementation_plateau_logo.svg`), Gap (`implementation_gap_logo.svg`), Implementation Event (`implementation_implementation_event_logo.svg`). Satu kalimat peran tiap elemen. Manfaat: perubahan terbagi jadi langkah jelas, setiap Plateau dapat dilacak ke tujuan, dan tim tahu apa yang harus diserahkan kapan. Tutup dengan rantai di layar: Baseline → (Work Package → Deliverable) → Go-Live → Target.
