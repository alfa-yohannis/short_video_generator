---
title: archimate_introduction
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Introduction

Video tutorial animasi singkat sebagai pengantar / gambaran umum ArchiMate — bahasa pemodelan enterprise-architecture terbuka dari The Open Group — sebelum video per-layer. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama elemen ArchiMate (kosakata standar notasi).

Contoh konsisten di SELURUH scene: sebuah RESTORAN yang ingin berkembang (dari arah strategi, proses bisnis, aplikasi, sampai infrastruktur teknologi) — satu model utuh dari strategi hingga teknologi.

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

ELEMEN = kotak (RoundedRectangle) digambar dengan Manim:
- Warna isi kotak = warna native layer-nya: Strategy = ORANYE; Business = KUNING; Application = BIRU MUDA; Technology = HIJAU; Motivation = UNGU; Implementation & Migration = PINK. (Aksen panel/teks boleh memakai variasi warna layer terkait.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Untuk overview ini cukup SATU elemen representatif per layer. Berkas logo per layer:
  - Strategy: `strategy_capability_logo.svg` (Capability).
  - Business: `business_business_process_logo.svg` (Business Process).
  - Application: `application_application_component_logo.svg` (Application Component).
  - Technology: `technology_node_logo.svg` (Node).
  - Motivation: `motivation_goal_logo.svg` (Goal).
  - Implementation & Migration: `implementation_work_package_logo.svg` (Work Package).

RELASI = JANGAN memuat SVG. Gambar dengan metode internal Manim (`Line` / `DashedLine` + bentuk kepala dari `Polygon`/`Triangle`/`Dot`) memakai build-helper yang tersedia (`realization_arrow`, `serving_arrow`, `assignment_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`) agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Pola garis + bentuk kepala sesuai notasi ArchiMate:
- Realization (`realization_arrow`): garis TITIK-TITIK (dotted); kepala SEGITIGA KOSONG (outline) di target. Untuk overview, dipakai NAIK ke atas tumpukan (layer bawah mewujudkan elemen layer di atasnya / Business mewujudkan Strategy).
- Serving (`serving_arrow`): garis SOLID; kepala panah TERBUKA (V) di target. Untuk overview, dipakai TURUN melayani tumpukan (Technology melayani Application melayani Business).
- Assignment (`assignment_arrow`): garis SOLID; bulatan TERISI (`Dot`) di ujung sumber; kepala panah TERISI di target.
- Influence (`influence_arrow`): garis PUTUS-PUTUS (dashed); kepala panah TERBUKA (V) di target. Untuk overview, dipakai dari Motivation yang menjustifikasi semua layer.
- Composition (`composition_arrow`): garis SOLID; BELAH KETUPAT TERISI di ujung sumber.
- Association (`association_arrow`): garis SOLID polos (tanpa kepala, atau panah terbuka kecil).
Beri label nama relasi di dekat garis bila membantu.

Warna semantik untuk penegasan (terpisah dari warna layer): DANGER, OK, HIGHLIGHT, PRIMARY, ACCENT. Hindari kata yang menyebut orientasi/aspek-rasio pada teks yang ditampilkan maupun diucapkan.

## 01_apa_itu_archimate (~22s)
Judul besar "ArchiMate" di tengah layar + subjudul "satu bahasa untuk enterprise architecture" (versi Inggris: "one language for enterprise architecture"). Jelaskan apa itu: bahasa pemodelan terbuka dari The Open Group untuk menggambarkan, menganalisis, dan mengomunikasikan arsitektur enterprise. Tegaskan mengapa dibutuhkan: ia menyatukan strategi sampai teknologi dalam SATU model bersama yang dipahami semua pemangku kepentingan. Sorot kata kunci dengan warna HIGHLIGHT/PRIMARY. Belum ada kotak elemen — fokus pada judul dan ide besar.

## 02_kerangka_berlapis (~30s)
Perkenalkan LAYERED FRAMEWORK: gambar pita-pita berwarna bertumpuk dari atas ke bawah dan beri label tiap pita —
- Strategy (pita ORANYE).
- Business (pita KUNING).
- Application (pita BIRU MUDA).
- Technology (pita HIJAU).
Lalu gambar Motivation sebagai KOLOM UNGU tinggi yang berdiri menyilang di samping seluruh pita (memberi alasan bagi semua layer), dan Implementation & Migration sebagai PITA PINK di paling bawah (mewujudkan perubahan dari rencana ke realisasi). Beri label tiap band/kolom. Munculkan bertahap agar tiap layer dapat perhatian. Tegaskan: empat layer inti bertumpuk, Motivation menyilang, Implementation & Migration menutup di bawah.

## 03_aspek_kerangka (~26s)
Tampilkan kerangka sebagai GRID: tiga kolom ASPECTS + Motivation di sisinya. Jelaskan tiap aspek dengan satu frasa singkat:
- Active Structure = "siapa/apa yang bertindak" (who/what acts).
- Behavior = "apa yang terjadi" (what happens).
- Passive Structure = "apa yang dikenai tindakan" (what is acted on).
- Motivation = "mengapa" (the why), menyilang di samping.
Gambar grid: baris = layer berwarna (Strategy/Business/Application/Technology), kolom = ketiga aspek, dengan kolom Motivation UNGU di sisi. Sorot judul kolom aspek dengan warna ACCENT. Tegaskan: setiap elemen ArchiMate menempati satu sel layer × aspek, sehingga model rapi dan dapat dibandingkan.

## 04_satu_elemen_per_layer (~30s)
Tunjukkan SATU elemen representatif per layer sebagai kotak (sesuai aturan menggambar: warna layer + nama di dalam + logo di pojok kanan atas), tampil bertahap dari atas ke bawah, masing-masing dengan contoh restoran di bawah kotak:
- Strategy — Capability (kotak ORANYE, `strategy_capability_logo.svg`) "Layanan delivery".
- Business — Business Process (kotak KUNING, `business_business_process_logo.svg`) "Proses pesan-antar".
- Application — Application Component (kotak BIRU MUDA, `application_application_component_logo.svg`) "Aplikasi Pemesanan".
- Technology — Node (kotak HIJAU, `technology_node_logo.svg`) "Server aplikasi".
Tunjukkan juga konteksnya: Motivation — Goal (kotak UNGU, `motivation_goal_logo.svg`) "Tingkatkan pendapatan" di samping, dan Implementation & Migration — Work Package (kotak PINK, `implementation_work_package_logo.svg`) "Proyek go-online" di bawah. Tegaskan: satu kosakata yang sama dipakai untuk seluruh restoran, dari arah sampai mesin.

## 05_keterkaitan_antar_layer (~34s)
Susun keenam kotak dari scene sebelumnya menjadi tumpukan, lalu hubungkan dengan RELASI yang DIGAMBAR Manim (lihat pola + helper di Preparation); tiap kotak = warna layer + nama di dalam + logo di pojok kanan atas; beri label tiap garis:
- Node (`technology_node_logo.svg`) "Server aplikasi" —serving (`serving_arrow`)→ Application Component (`application_application_component_logo.svg`) "Aplikasi Pemesanan" (garis SOLID; kepala panah TERBUKA): teknologi MELAYANI aplikasi.
- Application Component "Aplikasi Pemesanan" —serving (`serving_arrow`)→ Business Process (`business_business_process_logo.svg`) "Proses pesan-antar" (garis SOLID; kepala panah TERBUKA): aplikasi MELAYANI bisnis.
- Business Process "Proses pesan-antar" —realization (`realization_arrow`)→ Capability (`strategy_capability_logo.svg`) "Layanan delivery" (garis TITIK-TITIK; kepala SEGITIGA KOSONG mengarah ke atas): bisnis MEWUJUDKAN kemampuan strategi.
- Goal (`motivation_goal_logo.svg`) "Tingkatkan pendapatan" (kotak UNGU di sisi) —influence (`influence_arrow`)→ menyentuh seluruh tumpukan (garis PUTUS-PUTUS; kepala panah TERBUKA): Motivation MENJUSTIFIKASI semua layer.
Tegaskan: serving mengalir TURUN melayani tumpukan, realization mengalir NAIK mewujudkan layer di atasnya, dan Motivation memberi "mengapa" bagi semuanya — model jadi runtut dan dapat ditelusuri.

## 06_mengapa_archimate (~30s)
Recap manfaat: ArchiMate memberi SATU model yang koheren (one coherent model), KETERLACAKAN dari strategi ke teknologi (traceability), dan KOMUNIKASI yang sama bagi semua pemangku kepentingan. Tampilkan lagi rantai ringkas di layar dengan kotak berwarna + logo di pojok kanan atas: Goal (UNGU, `motivation_goal_logo.svg`) → Capability (ORANYE, `strategy_capability_logo.svg`) → Business Process (KUNING, `business_business_process_logo.svg`) → Application Component (BIRU MUDA, `application_application_component_logo.svg`) → Node (HIJAU, `technology_node_logo.svg`), dengan Work Package (PINK, `implementation_work_package_logo.svg`) yang mewujudkan perubahan. Sorot manfaat dengan warna OK/HIGHLIGHT. Tutup dengan ajakan: lanjutkan ke video per-layer — Strategy, Business, Application, Technology, Motivation, dan Implementation & Migration — untuk mendalami tiap layer.
