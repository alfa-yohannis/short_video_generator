---
title: archimate_motivation_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Motivation Layer

Video tutorial animasi singkat tentang Motivation Layer pada bahasa enterprise-architecture ArchiMate — layer yang menangkap "mengapa" di balik semua elemen lain. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama elemen ArchiMate (kosakata standar notasi).

Contoh konsisten di SELURUH scene: sebuah RESTORAN yang ingin berkembang (pendapatan turun → ingin tumbuh → terima pesanan online).

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

ELEMEN = kotak (RoundedRectangle) digambar dengan Manim:
- Warna isi kotak = warna native layer-nya: Motivation = UNGU; Strategy = oranye/kuning; Application = biru muda; Business = kuning; Technology = hijau. (Aksen panel/teks boleh memakai variasi warna Motivation/ungu.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Berkas logo Motivation: `motivation_stakeholder_logo.svg`, `motivation_driver_logo.svg`, `motivation_assessment_logo.svg`, `motivation_goal_logo.svg`, `motivation_outcome_logo.svg`, `motivation_principle_logo.svg`, `motivation_requirement_logo.svg`, `motivation_constraint_logo.svg`, `motivation_value_logo.svg`, `motivation_meaning_logo.svg`.
- Berkas logo lintas layer (scene 7): `strategy_course_of_action_logo.svg`, `application_application_component_logo.svg`.

RELASI = JANGAN memuat SVG. Gambar dengan metode internal Manim (`Line` / `DashedLine` + bentuk kepala dari `Polygon`/`Triangle`/`Dot`) agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Pola garis + bentuk kepala sesuai notasi ArchiMate:
- Influence: garis PUTUS-PUTUS (dashed); kepala panah TERBUKA (V) di target.
- Realization: garis TITIK-TITIK (dotted); kepala SEGITIGA KOSONG (outline) di target.
- Association: garis SOLID polos (tanpa kepala, atau panah terbuka kecil).
- Serving: garis SOLID; kepala panah TERBUKA di target.
Beri label nama relasi di dekat garis bila membantu.

## 01_posisi_layer (~16s)
Judul besar "ArchiMate — Motivation Layer" di tengah + subjudul "the why behind the architecture". Gambar kerangka ArchiMate sebagai pita berwarna — Strategy oranye, Business kuning, Application biru, Technology hijau — lalu tampilkan Motivation sebagai kolom UNGU tinggi yang berdiri menyilang di samping semuanya (karena memberi alasan bagi elemen di setiap layer lain). Sorot kolom ungu.

## 02_tujuan_layer (~22s)
Jelaskan tujuannya: Motivation Layer mencatat siapa yang peduli, apa yang mendorong, dan apa yang diinginkan — niat yang menjustifikasi setiap elemen lain. Contoh restoran: model inti menunjukkan ia memasak dan menyajikan, tetapi hanya Motivation Layer yang menyatakan MENGAPA ia akan berubah. Tampilkan satu pita ungu di belakang sebuah proses Business polos; tegaskan tanpa layer ini model punya "apa" dan "bagaimana" tetapi tak punya "mengapa".

## 03_sumber_motivasi (~26s)
Perkenalkan trio sumber motivasi, tiap kotak ungu + nama di dalam + logo di pojok kanan atas, muncul bertahap:
- Stakeholder (`motivation_stakeholder_logo.svg`) "Pemilik Restoran", "Pelanggan".
- Driver (`motivation_driver_logo.svg`) "Persaingan", "Pendapatan".
- Assessment (`motivation_assessment_logo.svg`) "Penjualan menurun".
Hubungkan dengan relasi DIGAMBAR Manim: Stakeholder —association→ Driver; Driver —association→ Assessment (kepedulian mengalir menjadi temuan).

## 04_intensi (~30s)
Perkenalkan kelompok intensi, tiap kotak ungu + logo di pojok kanan atas:
- Goal (`motivation_goal_logo.svg`) "Tingkatkan pendapatan".
- Outcome (`motivation_outcome_logo.svg`) "Penjualan naik 30%".
- Requirement (`motivation_requirement_logo.svg`) "Terima pesanan online".
- Constraint (`motivation_constraint_logo.svg`) "Anggaran terbatas".
- Principle (`motivation_principle_logo.svg`) "Utamakan layanan cepat".
Tampilkan bertahap agar tidak penuh.

## 05_value_meaning (~16s)
Lengkapi kosakata dengan dua elemen yang mengaitkan motivasi ke persepsi stakeholder, tiap kotak ungu + logo di pojok kanan atas:
- Value (`motivation_value_logo.svg`) "Kenyamanan" — nilai yang didapat pelanggan saat memesan tanpa keluar rumah.
- Meaning (`motivation_meaning_logo.svg`) "Pesanan siap" — dimaknai "makanan siap diambil".
Catat keduanya menempel pada elemen inti yang dideskripsikan, menggenapkan layer menjadi sepuluh elemen.

## 06_keterkaitan (~26s)
Rangkai kosakata dengan relasi ArchiMate yang DIGAMBAR Manim, tiap kotak ungu + logo di pojok kanan atas, tiap garis diberi label:
- Assessment (`motivation_assessment_logo.svg`) "Penjualan menurun" —influence→ Goal (`motivation_goal_logo.svg`) "Tingkatkan pendapatan".
- Outcome (`motivation_outcome_logo.svg`) "Penjualan naik 30%" —realization→ Goal.
- Requirement (`motivation_requirement_logo.svg`) "Terima pesanan online" —realization→ Goal.
- Principle (`motivation_principle_logo.svg`) "Utamakan layanan cepat" —influence→ Requirement; Constraint (`motivation_constraint_logo.svg`) "Anggaran terbatas" —influence→ Requirement.
Sorot bahwa influence + realization mengubah keinginan kabur menjadi kebutuhan yang teruji.

## 07_contoh_kasus (~28s)
Rakit model motivasi restoran secara bertahap, semua kotak + relasi DIGAMBAR Manim, lalu tunjukkan menggerakkan layer bawah:
Stakeholder "Pemilik Restoran" —association→ Driver "Pendapatan"; Assessment "Penjualan menurun" —influence→ Goal "Tingkatkan pendapatan"; Goal direalisasikan Outcome "Penjualan naik 30%" dan disempurnakan menjadi Requirement "Terima pesanan online", dibatasi Constraint "Anggaran terbatas". Lalu menyeberang ke bawah: Outcome —realization→ Course of Action "Mulai jualan online" (kotak Strategy oranye, `strategy_course_of_action_logo.svg`); Requirement —realization→ Application Component "Aplikasi Delivery" (kotak Application biru, `application_application_component_logo.svg`). "Mengapa" ungu kini terbukti menggerakkan rencana oranye dan sistem biru.

## 08_kesimpulan (~14s)
Ringkas: Motivation Layer menangkap "mengapa" lewat sepuluh elemen — tampilkan lagi kesepuluh ikon aslinya (kotak ungu + logo di pojok kanan atas): Stakeholder (`motivation_stakeholder_logo.svg`), Driver (`motivation_driver_logo.svg`), Assessment (`motivation_assessment_logo.svg`), Goal (`motivation_goal_logo.svg`), Outcome (`motivation_outcome_logo.svg`), Principle (`motivation_principle_logo.svg`), Requirement (`motivation_requirement_logo.svg`), Constraint (`motivation_constraint_logo.svg`), Value (`motivation_value_logo.svg`), Meaning (`motivation_meaning_logo.svg`). Manfaat: tiap elemen bisa dilacak ke alasannya, pilihan terjustifikasi, model tetap selaras. Tutup dengan rantai di layar: Stakeholder → Driver → Assessment → Goal → Requirement.
