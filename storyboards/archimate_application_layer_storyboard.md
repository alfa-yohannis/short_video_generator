---
title: archimate_application_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Application Layer

Video tutorial animasi singkat tentang Application Layer pada bahasa enterprise-architecture ArchiMate — layer yang menangkap aplikasi dan data yang mendukung proses bisnis. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama elemen ArchiMate (kosakata standar notasi).

Contoh konsisten di SELURUH scene: konteks RESTORAN (aplikasi POS, aplikasi delivery, pemesanan online, pembayaran).

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

ELEMEN = kotak (RoundedRectangle) digambar dengan Manim:
- Warna isi kotak = warna native layer-nya: Application = BIRU MUDA (light blue / cyan); Business = kuning; Technology = hijau; Motivation = UNGU; Strategy = oranye/kuning. (Aksen panel/teks boleh memakai variasi warna Application/biru muda.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Berkas logo Application: `application_application_component_logo.svg`, `application_application_collaboration_logo.svg`, `application_application_interface_logo.svg`, `application_application_function_logo.svg`, `application_application_interaction_logo.svg`, `application_application_process_logo.svg`, `application_application_event_logo.svg`, `application_application_service_logo.svg`, `application_data_object_logo.svg`.
- Berkas logo lintas layer (scene 04): `business_business_process_logo.svg`, `business_business_service_logo.svg`, `technology_node_logo.svg`, `technology_system_software_logo.svg`.

RELASI = JANGAN memuat SVG. Gambar dengan metode internal Manim (`Line` / `DashedLine` + bentuk kepala dari `Polygon`/`Triangle`/`Dot`) lewat helper bawaan (`archi_element`, `assignment_arrow`, `serving_arrow`, `realization_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`) agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Pola garis + bentuk kepala sesuai notasi ArchiMate:
- Assignment (`assignment_arrow`): garis SOLID; bulatan TERISI (`Dot`) di ujung sumber; kepala panah TERISI di ujung target. Dipakai Application Component —assignment→ Application Function.
- Realization (`realization_arrow`): garis TITIK-TITIK (dotted); kepala SEGITIGA KOSONG (outline) di target. Dipakai Application Function —realization→ Application Service, dan Application Component —realization→ Application Service.
- Serving (`serving_arrow`): garis SOLID; kepala panah TERBUKA (dua garis "V", tanpa isi) di target. Dipakai Application Service —serving→ Business Process.
- Composition (`composition_arrow`): garis SOLID; BELAH KETUPAT TERISI di ujung sumber (whole). Dipakai untuk mengelompokkan fungsi/komponen.
- Association (`association_arrow`): garis SOLID polos (tanpa kepala, atau panah terbuka kecil).
- Influence (`influence_arrow`): garis PUTUS-PUTUS (dashed); kepala panah TERBUKA (V) di target.
- Access (untuk baca/tulis Data Object): garis TITIK-TITIK (dotted) dengan kepala panah TERBUKA KECIL di Data Object. Dipakai Application Function —access→ Data Object.
Boleh beri label nama relasi di dekat garis bila membantu.

## 01_posisi_layer (~18s)
Judul besar "ArchiMate — Application Layer" di tengah + subjudul singkat "the apps & data that run the business". Gambar kerangka ArchiMate sebagai pita berwarna bertumpuk — Business kuning di lapis atas, Application biru muda di lapis tengah, Technology hijau di lapis bawah. Sorot (HIGHLIGHT) pita Application biru muda di tengah dan tegaskan posisinya: Application berada DI BAWAH Business dan DI ATAS Technology — aplikasi mendukung proses bisnis sambil ditopang teknologi. Narasi singkat: apa itu Application Layer dan perannya sebagai penghubung.

## 02_kosakata_elemen (~34s)
Kotak elemen tampil bertahap; tiap kotak = warna Application (biru muda) + nama di dalam + logo di pojok kanan atas + contoh restoran di bawah kotak:
- Application Component (`application_application_component_logo.svg`): "Aplikasi POS", "Aplikasi Delivery".
- Application Service (`application_application_service_logo.svg`): "Layanan Pemesanan Online".
- Application Function (`application_application_function_logo.svg`): "Proses Pembayaran".
- Application Interface (`application_application_interface_logo.svg`): "API Pembayaran".
- Application Collaboration (`application_application_collaboration_logo.svg`): kerja sama dua komponen aplikasi.
- Application Process (`application_application_process_logo.svg`): alur langkah dalam aplikasi.
- Application Event (`application_application_event_logo.svg`): kejadian yang memicu aplikasi.
- Data Object (`application_data_object_logo.svg`): "Data Pesanan", "Data Menu".
Tampilkan bertahap agar tidak penuh; beri penekanan ACCENT pada perbedaan Component (struktur) vs Function/Service (perilaku) vs Data Object (informasi).

## 03_keterkaitan_antar_elemen (~30s)
Hubungkan kotak elemen Application dengan RELASI yang DIGAMBAR Manim (lihat pola di Preparation); tiap kotak = warna Application biru muda + nama di dalam + logo di pojok kanan atas; tiap garis diberi label:
- Application Component (`application_application_component_logo.svg`) "Aplikasi POS" —assignment→ Application Function (`application_application_function_logo.svg`) "Proses Pembayaran" (garis solid; bulatan di sumber; panah terisi di target): komponen menjalankan fungsi.
- Application Function (`application_application_function_logo.svg`) "Proses Pembayaran" —realization→ Application Service (`application_application_service_logo.svg`) "Layanan Pemesanan Online" (garis titik-titik; segitiga kosong di target): fungsi mewujudkan layanan.
- Application Function (`application_application_function_logo.svg`) "Proses Pembayaran" —access→ Data Object (`application_data_object_logo.svg`) "Data Pesanan" (garis titik-titik; panah terbuka KECIL di Data Object): fungsi membaca/menulis data.
Sorot (HIGHLIGHT) rantai Component → Function → Service sebagai pola inti, dan tegaskan access sebagai cara aplikasi menyentuh data.

## 04_keterkaitan_antar_layer (~32s)
Scene lintas layer — Application sebagai penghubung Business (atas) dan Technology (bawah). Tiap kotak = warna native layer-nya + nama di dalam + logo di pojok kanan atas; semua relasi DIGAMBAR Manim (lihat pola di Preparation):
- KE ATAS: Application Service (kotak Application biru muda, `application_application_service_logo.svg`) "Layanan Pemesanan Online" —serving→ Business Process (kotak Business kuning, `business_business_process_logo.svg`) "Menerima Pesanan" (garis solid; kepala panah TERBUKA mengarah ke Business Process): layanan aplikasi melayani proses bisnis. (Tambahkan Business Service `business_business_service_logo.svg` sebagai konteks atas bila membantu.)
- KE BAWAH: Technology Node (kotak Technology hijau, `technology_node_logo.svg`) "Server Restoran" —realization→ Application Component (kotak Application biru muda, `application_application_component_logo.svg`) "Aplikasi POS" (garis TITIK-TITIK; segitiga KOSONG mengarah ke Application Component); dan Technology System Software (kotak Technology hijau, `technology_system_software_logo.svg`) "Database Engine" —realization→ Application Component "Aplikasi POS". Teknologi mewujudkan/menopang aplikasi.
Tegaskan (PRIMARY): Application = "aplikasi & data", melayani Business di atas dan ditopang Technology di bawah.

## 05_contoh_kasus (~26s)
Mini-diagram aplikasi restoran dibangun bertahap; semua kotak elemen + relasi DIGAMBAR Manim, tiap kotak = warna Application biru muda + nama di dalam + logo di pojok kanan atas:
Application Component (`application_application_component_logo.svg`) "Aplikasi Delivery" —assignment→ Application Function (`application_application_function_logo.svg`) "Proses Pembayaran"; Application Function —realization→ Application Service (`application_application_service_logo.svg`) "Layanan Pemesanan Online"; Application Function —access→ Data Object (`application_data_object_logo.svg`) "Data Pesanan" (titik-titik, panah terbuka kecil) dan Data Object (`application_data_object_logo.svg`) "Data Menu"; lalu Application Interface (`application_application_interface_logo.svg`) "API Pembayaran" —assignment→ Application Component sebagai titik akses layanan. Pakai pola garis + kepala sesuai aturan, susun bertahap agar alur Component → Function → Service + data terbaca jelas.

## 06_kesimpulan (~16s)
Ringkas: Application Layer = aplikasi & data yang mendukung bisnis. Tampilkan lagi kotak elemen kunci (warna Application biru muda + logo di pojok kanan atas):
- Application Component (`application_application_component_logo.svg`) "Component"
- Application Service (`application_application_service_logo.svg`) "Service"
- Application Function (`application_application_function_logo.svg`) "Function"
- Application Interface (`application_application_interface_logo.svg`) "Interface"
- Data Object (`application_data_object_logo.svg`) "Data Object"
Satu kalimat peran tiap elemen, lalu tutup dengan rantai di layar: Component → Function → Service —serving→ Business; ditopang Technology di bawah.
