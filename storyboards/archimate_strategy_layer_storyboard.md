---
title: archimate_strategy_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Strategy Layer

Video tutorial animasi singkat tentang Strategy Layer pada bahasa enterprise-architecture ArchiMate. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama elemen ArchiMate (kosakata standar notasi).

Contoh konsisten di SELURUH scene: konteks RESTORAN (penjualan online, layanan delivery, booking online).

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

ELEMEN = kotak (RoundedRectangle) digambar dengan Manim:
- Warna isi kotak = warna native layer-nya: Strategy = oranye/kuning keemasan; Motivation = UNGU; Business = kuning; Application = biru muda. (Aksen panel/teks boleh memakai variasi warna Strategy.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil, dengan margin kanan sedikit lebih besar — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Berkas logo: `strategy_resource_logo.svg`, `strategy_capability_logo.svg`, `strategy_course_of_action_logo.svg`, `strategy_value_stream_logo.svg`, `business_business_process_logo.svg`, `application_application_component_logo.svg`.
- Berkas logo lintas layer (koneksi ke Motivation Layer, scene 05): `motivation_driver_logo.svg`, `motivation_goal_logo.svg`.

RELASI = JANGAN memuat SVG. Gambar dengan metode internal Manim (`Line` / `DashedLine` + bentuk kepala dari `Polygon`/`Triangle`/`Dot`) agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Pola garis + bentuk kepala sesuai notasi ArchiMate:
- Assignment: garis SOLID; bulatan TERISI (`Dot`) di ujung sumber; kepala panah TERISI di ujung target.
- Serving: garis SOLID; kepala panah TERBUKA (dua garis "V", tanpa isi) di target.
- Realization: garis TITIK-TITIK (dotted); kepala SEGITIGA KOSONG (outline) di target.
- Influence: garis PUTUS-PUTUS (dashed); kepala panah TERBUKA (V) di target.
- Composition: garis SOLID; BELAH KETUPAT TERISI di ujung sumber.
Boleh beri label nama relasi di dekat garis bila membantu.

## 01_pengantar (~22s)
Judul besar "ArchiMate — Strategy Layer" di tengah + subjudul singkat. Di bawahnya jajarkan keempat elemen Strategy sebagai kotak (sesuai aturan menggambar): Resource, Capability, Course of Action, Value Stream — tiap kotak warna Strategy, nama di dalam, logo di pojok kanan atas. Narasi: apa itu Strategy Layer, tujuannya (arah & strategi tingkat tinggi), dan posisinya di atas layer Business/Application/Technology.

## 02_elemen_strategy (~34s)
Empat kotak elemen tampil bertahap; tiap kotak = warna Strategy + nama di dalam + logo di pojok kanan atas + 2 contoh restoran di bawah kotak:
- Resource (`strategy_resource_logo.svg`): "Armada kurir", "Aplikasi POS".
- Capability (`strategy_capability_logo.svg`): "Penjualan online", "Layanan delivery".
- Course of Action (`strategy_course_of_action_logo.svg`): "Buka cabang baru", "Gandeng kurir mitra".
- Value Stream (`strategy_value_stream_logo.svg`): "Pesan lalu antar", "Reservasi meja".

## 03_keterkaitan_antar_elemen (~26s)
Hubungkan kotak elemen Strategy dengan RELASI yang DIGAMBAR Manim (lihat pola di Preparation); tiap kotak = warna Strategy + nama di dalam + logo di pojok kanan atas:
- Resource (`strategy_resource_logo.svg`) "Armada kurir" —assignment→ Capability (`strategy_capability_logo.svg`) "Layanan delivery" (garis solid; bulatan di sumber; panah terisi di target).
- Capability (`strategy_capability_logo.svg`) "Layanan delivery" —serving→ Value Stream (`strategy_value_stream_logo.svg`) "Pesan lalu antar" (garis solid; kepala panah terbuka).
- Course of Action (`strategy_course_of_action_logo.svg`) "Gandeng kurir mitra" —influence→ Capability (`strategy_capability_logo.svg`) "Layanan delivery" (garis dashed; kepala panah terbuka).

## 04_keterkaitan_antar_layer (~24s)
Capability (`strategy_capability_logo.svg`) (kotak Strategy) DI-REALISASIKAN oleh elemen layer bawah: Business Process (kotak Business kuning, `business_business_process_logo.svg`) dan Application Component (kotak Application biru, `application_application_component_logo.svg`). Relasi realization DIGAMBAR Manim: garis TITIK-TITIK dengan kepala SEGITIGA KOSONG mengarah ke Capability. Tegaskan: Strategy = "mengapa/arah", layer lain = "bagaimana/pelaksanaan".

## 05_keterkaitan_motivation (~22s)
Hubungkan Strategy Layer ke ATAS dengan Motivation Layer — "mengapa" di balik strateginya (melengkapi scene sebelumnya yang turun ke Business/Application). Tiap kotak = warna native layer-nya + nama di dalam + logo di pojok kanan atas; semua relasi DIGAMBAR Manim (lihat pola di Preparation):
- Motivation Driver (kotak UNGU, `motivation_driver_logo.svg`) "Pendapatan turun" —influence→ Motivation Goal (kotak UNGU, `motivation_goal_logo.svg`) "Tingkatkan pendapatan" (garis PUTUS-PUTUS; kepala panah TERBUKA): pemicu memotivasi tujuan.
- Strategy Course of Action (kotak oranye, `strategy_course_of_action_logo.svg`) "Buka cabang baru" —realization→ Goal (garis TITIK-TITIK; kepala SEGITIGA KOSONG mengarah ke Goal): rencana mewujudkan tujuan.
- Strategy Capability (kotak oranye, `strategy_capability_logo.svg`) "Penjualan online" —realization→ Goal (garis TITIK-TITIK; kepala SEGITIGA KOSONG): kemampuan mewujudkan tujuan.
Tegaskan: elemen Strategy MEWUJUDKAN tujuan di Motivation Layer — Motivation = alasan/arah ("mengapa"), Strategy = cara tingkat tinggi mencapainya.

## 06_contoh_kasus (~32s)
Mini-diagram restoran dibangun bertahap; semua kotak elemen + relasi DIGAMBAR Manim:
Resource (`strategy_resource_logo.svg`) "Armada kurir" + "Aplikasi POS" —assignment→ Capability (`strategy_capability_logo.svg`) "Layanan delivery" —serving→ Value Stream (`strategy_value_stream_logo.svg`) "Pesan lalu antar"; Course of Action "Gandeng kurir mitra" —influence→ Capability (`strategy_course_of_action_logo.svg`). Pakai pola garis + kepala sesuai aturan.

## 07_kesimpulan (~16s)
Tampilkan lagi keempat kotak elemen Strategy (logo di pojok kanan atas), 
- Resource (`strategy_resource_logo.svg`) "Resource"
- Capability (`strategy_capability_logo.svg`) "Capability"
- Course of Action (`strategy_course_of_action_logo.svg`) "Course of Action"
- Value Stream (`strategy_value_stream_logo.svg`) "Value Stream"
- satu kalimat peran tiap elemen, lalu kalimat penutup singkat.
