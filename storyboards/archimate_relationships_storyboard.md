---
title: archimate_relationships
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Relationships

Video tutorial animasi singkat tentang Relationships (Connectors) pada bahasa enterprise-architecture ArchiMate — garis-garis yang menghubungkan antar elemen dan memberi makna pada model. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama relationship dan nama tipe elemen ArchiMate (kosakata standar notasi).

Contoh konsisten di SELURUH scene: konteks RESTORAN (proses dapur, pelayan, sistem pemesanan online, layanan delivery).

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

PENTING — fokus video ini adalah RELATIONSHIPS (connectors), yaitu GARIS antar elemen, BUKAN elemen itu sendiri. Relationship TIDAK punya berkas `_logo.svg` dan TIDAK PERNAH dimuat dari SVG. Setiap relationship SELALU DIGAMBAR dengan Manim (`Line` / `DashedLine` / `DottedLine` + bentuk kepala/ujung dari `Polygon` / `Triangle` / `Dot`). JANGAN merujuk logo relationship apa pun. Logo SVG hanya dipakai untuk kotak demo kecil yang dihubungkan oleh garis.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

KOTAK DEMO = kotak (RoundedRectangle) digambar dengan Manim, sekadar dua ujung untuk memamerkan satu relationship:
- Warna isi kotak = warna native layer-nya: Business = kuning; Application = biru muda; Technology = hijau; Motivation = UNGU; Strategy = oranye/kuning keemasan. (Aksen panel/teks boleh memakai variasi warna HIGHLIGHT/ACCENT.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Berkas logo elemen yang dipakai untuk kotak demo (HANYA ini): `business_business_process_logo.svg`, `business_business_actor_logo.svg`, `business_business_object_logo.svg`, `business_business_service_logo.svg`, `application_application_component_logo.svg`, `application_application_service_logo.svg`, `application_data_object_logo.svg`, `technology_node_logo.svg`.

RELATIONSHIP = JANGAN memuat SVG. SELALU gambar dengan metode internal Manim agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Konvensi arah: SOURCE = kotak asal (sering tempat menempelnya belah ketupat/bulatan), TARGET = kotak tujuan (sering tempat menempelnya kepala panah/segitiga). Pola garis + bentuk ujung sesuai notasi ArchiMate — dokumentasikan SETIAP relationship di sini:

STRUCTURAL (bagaimana elemen tersusun / ditugaskan):
- Composition: garis SOLID (`Line`); BELAH KETUPAT TERISI (`Polygon` 4 titik, fill penuh, warna PRIMARY) menempel di ujung SOURCE. (helper: `composition_arrow`) Makna: bagian milik utuh; bagian tak bisa lepas dari pemiliknya.
- Aggregation: garis SOLID (`Line`); BELAH KETUPAT KOSONG (`Polygon` 4 titik, hanya outline, tanpa fill) menempel di ujung SOURCE. Makna: pengelompokan; bagian bisa berdiri sendiri.
- Assignment: garis SOLID (`Line`); BULATAN TERISI (`Dot`) menempel di ujung SOURCE + kepala panah TERISI (`Triangle`/`Polygon` segitiga, fill penuh) di ujung TARGET. (helper: `assignment_arrow`) Makna: penugasan aktif (siapa menjalankan apa).
- Realization: garis TITIK-TITIK (`DottedLine`); kepala SEGITIGA KOSONG (`Triangle` hanya outline, tanpa fill) di ujung TARGET. (helper: `realization_arrow`) Makna: sesuatu mewujudkan/merealisasikan yang lebih abstrak.

DEPENDENCY (bagaimana elemen saling bergantung / dilayani):
- Serving: garis SOLID (`Line`); kepala panah TERBUKA (dua garis "V", tanpa isi) di ujung TARGET. (helper: `serving_arrow`) Makna: satu elemen melayani/menyediakan fungsi bagi yang lain.
- Access: garis TITIK-TITIK (`DottedLine`); kepala panah TERBUKA KECIL (V kecil) di ujung TARGET (arah panah menandakan read/write). Makna: perilaku mengakses data/objek.
- Influence: garis PUTUS-PUTUS (`DashedLine`); kepala panah TERBUKA (V) di ujung TARGET; opsional label kecil "+" atau "−" di dekat garis. (helper: `influence_arrow`) Makna: sesuatu memengaruhi (positif/negatif) yang lain.

DYNAMIC (bagaimana urutan/aliran berjalan):
- Triggering: garis SOLID (`Line`); kepala panah TERISI (segitiga fill penuh) di ujung TARGET. Makna: urutan kausal/temporal — satu memicu yang berikutnya. (Bedakan dari Assignment: Triggering TANPA bulatan di SOURCE.)
- Flow: garis PUTUS-PUTUS (`DashedLine`); kepala panah TERISI (segitiga fill penuh) di ujung TARGET. Makna: aliran informasi/nilai/barang dari satu ke yang lain.

OTHER:
- Specialization: garis SOLID (`Line`); kepala SEGITIGA KOSONG (`Triangle` hanya outline, tanpa fill) di ujung TARGET (parent). Makna: "adalah jenis dari" (is-a). (Bedakan dari Realization yang garisnya TITIK-TITIK.)
- Association: garis SOLID polos (`Line`) tanpa kepala, atau panah TERBUKA KECIL opsional di salah satu ujung. (helper: `association_arrow`) Makna: hubungan umum yang tidak tercakup tipe lain.
- Junction: BUKAN garis penuh, melainkan SIMPUL kecil — lingkaran KECIL TERISI (`Dot`, AND) atau lingkaran KECIL KOSONG (`Circle` outline kecil, OR) — tempat beberapa relationship sejenis bertemu/bercabang. Gambar sebagai titik penghubung di persimpangan beberapa garis.

Beri label nama relationship di dekat garis bila membantu. Pakai warna semantik (DANGER/OK/HIGHLIGHT/PRIMARY/ACCENT) hanya untuk menegaskan, bukan mengganti makna notasi.

## 01_kenapa_notasi_penting (~18s)
Judul besar "ArchiMate — Relationships" di tengah + subjudul "the lines that give the model meaning". Tampilkan dua kotak demo polos (Business kuning) dengan sebuah garis di antaranya, lalu tegaskan: garis itu sendiri membawa makna — gaya garis (solid / putus-putus / titik-titik) dan bentuk ujung (belah ketupat / bulatan / segitiga / panah) menentukan ARTI hubungan. Pratinjau cepat: geser tiga gaya garis (solid, dashed, dotted) lalu tiga bentuk ujung. Tegaskan relationship adalah CONNECTOR, bukan elemen — selalu digambar, tak punya logo. Sorot pesan dengan warna HIGHLIGHT.

## 02_structural_relationships (~32s)
Perkenalkan keluarga STRUCTURAL satu per satu; tiap pasangan = dua kotak demo (warna layer + nama di dalam + logo di pojok kanan atas) dihubungkan relationship yang DIGAMBAR Manim sesuai pola di Preparation; beri label nama relationship dekat garis:
- Composition: Business Service (`business_business_service_logo.svg`) "Layanan Restoran" —composition→ Business Process (`business_business_process_logo.svg`) "Memasak" (garis SOLID; BELAH KETUPAT TERISI menempel di SOURCE "Layanan Restoran"). Makna: proses adalah bagian utuh dari layanan.
- Aggregation: Business Service (`business_business_service_logo.svg`) "Paket Menu" —aggregation→ Business Object (`business_business_object_logo.svg`) "Menu Item" (garis SOLID; BELAH KETUPAT KOSONG di SOURCE). Makna: pengelompokan longgar; item bisa berdiri sendiri.
- Assignment: Business Actor (`business_business_actor_logo.svg`) "Pelayan" —assignment→ Business Process (`business_business_process_logo.svg`) "Menyajikan" (garis SOLID; BULATAN TERISI di SOURCE "Pelayan" + kepala panah TERISI di TARGET). Sebut helper `assignment_arrow`.
- Realization: Application Component (`application_application_component_logo.svg`) "Aplikasi Pemesanan" —realization→ Application Service (`application_application_service_logo.svg`) "Layanan Pemesanan Online" (garis TITIK-TITIK; SEGITIGA KOSONG di TARGET). Sebut helper `realization_arrow`. Tekankan beda fill diamond (terisi vs kosong) menentukan Composition vs Aggregation.

## 03_dependency_relationships (~26s)
Perkenalkan keluarga DEPENDENCY; tiap pasangan dua kotak demo + relationship DIGAMBAR Manim; label dekat garis:
- Serving: Application Service (`application_application_service_logo.svg`) "Layanan Pemesanan Online" —serving→ Business Process (`business_business_process_logo.svg`) "Menerima Pesanan" (garis SOLID; kepala panah TERBUKA "V" di TARGET). Sebut helper `serving_arrow`. Makna: layanan melayani proses.
- Access: Business Process (`business_business_process_logo.svg`) "Menerima Pesanan" —access→ Data Object (`application_data_object_logo.svg`) "Data Pesanan" (garis TITIK-TITIK; kepala panah TERBUKA KECIL di TARGET). Makna: proses membaca/menulis data.
- Influence: Business Object (`business_business_object_logo.svg`) "Ulasan Pelanggan" —influence→ Business Service (`business_business_service_logo.svg`) "Layanan Restoran" (garis PUTUS-PUTUS; kepala panah TERBUKA "V" di TARGET; tampilkan label kecil "+"). Sebut helper `influence_arrow`. Tegaskan: dependency = "siapa butuh/pengaruhi siapa".

## 04_dynamic_relationships (~24s)
Perkenalkan keluarga DYNAMIC (urutan & aliran); tiap pasangan dua kotak demo + relationship DIGAMBAR Manim; label dekat garis:
- Triggering: Business Process (`business_business_process_logo.svg`) "Menerima Pesanan" —triggering→ Business Process (`business_business_process_logo.svg`) "Memasak" (garis SOLID; kepala panah TERISI di TARGET; TANPA bulatan di SOURCE). Makna: langkah memicu langkah berikutnya secara berurutan.
- Flow: Business Process (`business_business_process_logo.svg`) "Memasak" —flow→ Business Process (`business_business_process_logo.svg`) "Mengantar" (garis PUTUS-PUTUS; kepala panah TERISI di TARGET). Makna: sesuatu (makanan/informasi) mengalir antar langkah. Sandingkan Triggering vs Flow berdampingan dan sorot beda gaya garis (SOLID vs PUTUS-PUTUS) dengan warna ACCENT.

## 05_other_relationships (~24s)
Perkenalkan keluarga OTHER; tiap pasangan dua kotak demo + relationship DIGAMBAR Manim; label dekat garis:
- Specialization: Business Process (`business_business_process_logo.svg`) "Pesan Antar" —specialization→ Business Process (`business_business_process_logo.svg`) "Layani Pesanan" (garis SOLID; SEGITIGA KOSONG di TARGET/parent). Makna: "adalah jenis dari". Tegaskan beda dengan Realization: di sini garis SOLID, Realization garis TITIK-TITIK.
- Association: Business Actor (`business_business_actor_logo.svg`) "Pelanggan" —association→ Business Service (`business_business_service_logo.svg`) "Layanan Restoran" (garis SOLID polos; opsional panah TERBUKA KECIL). Sebut helper `association_arrow`. Makna: hubungan umum.
- Junction: tampilkan dua Triggering dari Business Process (`business_business_process_logo.svg`) "Bayar" dan Business Process "Konfirmasi" bertemu di sebuah JUNCTION (lingkaran KECIL TERISI = AND) lalu satu garis Triggering lanjut ke Business Process "Cetak Struk". Tegaskan Junction menyatukan/mencabangkan beberapa relationship sejenis (gambar sebagai `Dot` kecil di persimpangan).

## 06_mini_diagram_restoran (~30s)
Mini-diagram restoran dibangun bertahap memakai beberapa relationship sekaligus; semua kotak demo + relationship DIGAMBAR Manim sesuai pola di Preparation:
- Business Actor (`business_business_actor_logo.svg`) "Pelanggan" —serving← Application Service (`application_application_service_logo.svg`) "Layanan Pemesanan Online" (layanan melayani pelanggan; kepala panah TERBUKA di TARGET pelanggan).
- Application Component (`application_application_component_logo.svg`) "Aplikasi Pemesanan" —assignment→ Application Service (`application_application_service_logo.svg`) "Layanan Pemesanan Online" (bulatan di SOURCE + panah TERISI di TARGET).
- Application Service —serving→ Business Process (`business_business_process_logo.svg`) "Menerima Pesanan".
- Business Process "Menerima Pesanan" —triggering→ Business Process (`business_business_process_logo.svg`) "Memasak" —flow→ Business Process (`business_business_process_logo.svg`) "Mengantar" (triggering SOLID panah TERISI; flow PUTUS-PUTUS panah TERISI).
- Business Process "Menerima Pesanan" —access→ Data Object (`application_data_object_logo.svg`) "Data Pesanan" (TITIK-TITIK, panah terbuka kecil).
- Technology Node (`technology_node_logo.svg`) "Server" —assignment→ Application Component "Aplikasi Pemesanan" (node menjalankan komponen). Tegaskan: dengan kombinasi relationship inilah model bercerita utuh.

## 07_recap_cheat_sheet (~22s)
Tutup dengan kartu contekan (cheat-sheet) seluruh relationship — tiap baris = potongan garis pendek DIGAMBAR Manim dengan ujungnya + nama:
- Composition: garis SOLID + belah ketupat TERISI.
- Aggregation: garis SOLID + belah ketupat KOSONG.
- Assignment: garis SOLID + bulatan TERISI di sumber + panah TERISI.
- Realization: garis TITIK-TITIK + segitiga KOSONG.
- Serving: garis SOLID + panah TERBUKA.
- Access: garis TITIK-TITIK + panah terbuka KECIL.
- Influence: garis PUTUS-PUTUS + panah TERBUKA (+/−).
- Triggering: garis SOLID + panah TERISI.
- Flow: garis PUTUS-PUTUS + panah TERISI.
- Specialization: garis SOLID + segitiga KOSONG.
- Association: garis SOLID polos.
- Junction: lingkaran kecil (TERISI = AND, KOSONG = OR).
Pesan penutup: ingat dua hal — GAYA GARIS (solid/dashed/dotted) dan BENTUK UJUNG (diamond/ball/triangle/arrow); itulah yang membedakan setiap relationship. Sorot ringkasan dengan warna HIGHLIGHT.
