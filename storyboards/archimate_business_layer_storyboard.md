---
title: archimate_business_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Business Layer

Video tutorial animasi singkat tentang Business Layer pada bahasa enterprise-architecture ArchiMate — layer yang menangkap "apa" yang dilakukan organisasi: aktor, peran, proses, dan layanan yang diberikan kepada pelanggan. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama elemen ArchiMate (kosakata standar notasi).

Contoh konsisten di SELURUH scene: sebuah RESTORAN yang melayani pelanggan (makan di tempat dan pesan antar) — pemilik, kasir, koki, proses pesanan, hingga paket hemat.

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

ELEMEN = kotak (RoundedRectangle) digambar dengan Manim:
- Warna isi kotak = warna native layer-nya: Business = KUNING; Application = biru muda; Strategy = oranye; Motivation = ungu; Technology = hijau. (Aksen panel/teks boleh memakai variasi warna Business/kuning.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Berkas logo Business: `business_business_actor_logo.svg`, `business_business_role_logo.svg`, `business_business_collaboration_logo.svg`, `business_business_interface_logo.svg`, `business_business_process_logo.svg`, `business_business_function_logo.svg`, `business_business_interaction_logo.svg`, `business_business_event_logo.svg`, `business_business_service_logo.svg`, `business_business_object_logo.svg`, `business_contract_logo.svg`, `business_product_logo.svg`, `business_representation_logo.svg`.
- Berkas logo lintas layer (hanya scene lintas-layer): `application_application_service_logo.svg`, `application_application_component_logo.svg`, `strategy_capability_logo.svg`.

RELASI = JANGAN memuat SVG. Gambar dengan metode internal Manim (`Line` / `DashedLine` + bentuk kepala dari `Polygon`/`Triangle`/`Dot`) agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Helper build tersedia: `archi_element`, `assignment_arrow`, `serving_arrow`, `realization_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`. Pola garis + bentuk kepala sesuai notasi ArchiMate:
- Assignment: garis SOLID; bulatan TERISI (`Dot`) di ujung sumber; kepala panah TERISI di ujung target. Dipakai Actor→Role dan Role→Process.
- Serving: garis SOLID; kepala panah TERBUKA (dua garis "V", tanpa isi) di target. Dipakai Service yang melayani pelanggan/proses.
- Realization: garis TITIK-TITIK (dotted); kepala SEGITIGA KOSONG (outline) di target. Dipakai Business Process merealisasikan Business Service, dan Business Process merealisasikan Strategy Capability.
- Composition: garis SOLID; BELAH KETUPAT TERISI di ujung sumber (whole→part). Dipakai Product yang tersusun atas Service/Contract.
- Association: garis SOLID polos (tanpa kepala, atau panah terbuka kecil). Dipakai kaitan netral, mis. proses dengan Business Object.
- Triggering (Process→Process): garis SOLID; kepala panah TERISI di target (alur antar proses).
Boleh beri label nama relasi di dekat garis bila membantu.

## 01_posisi_layer (~20s)
Judul besar "ArchiMate — Business Layer" di tengah + subjudul singkat "what the organization does for its customers". Gambar kerangka ArchiMate sebagai pita berwarna bertumpuk — Strategy oranye, Business kuning, Application biru, Technology hijau — lalu sorot pita KUNING Business yang berada di bawah Strategy dan di atas Application. Pakai warna HIGHLIGHT untuk pita Business. Narasi: Business Layer menggambarkan layanan, proses, dan pelaku yang menjalankan organisasi sehari-hari; ia menerima arah dari Strategy dan ditopang oleh Application.

## 02_kosakata_elemen (~34s)
Perkenalkan kosakata inti Business; tiap kotak = warna Business KUNING + nama di dalam + logo di pojok kanan atas + contoh restoran. Muncul bertahap agar tidak penuh:
- Business Actor (`business_business_actor_logo.svg`) "Pemilik Restoran".
- Business Role (`business_business_role_logo.svg`) "Kasir", "Koki".
- Business Process (`business_business_process_logo.svg`) "Proses Pesanan", "Penyajian".
- Business Function (`business_business_function_logo.svg`) "Manajemen Dapur".
- Business Service (`business_business_service_logo.svg`) "Layanan Makan di Tempat", "Layanan Pesan Antar".
- Business Object (`business_business_object_logo.svg`) "Pesanan".
- Product (`business_product_logo.svg`) "Paket Hemat".
- Business Event (`business_business_event_logo.svg`) "Pesanan Masuk".
Tegaskan dengan warna ACCENT bahwa Actor itu pelaku nyata, sedang Role itu peran yang dijalankan pelaku.

## 03_keterkaitan_antar_elemen (~28s)
Hubungkan kotak elemen Business dengan RELASI yang DIGAMBAR Manim (lihat pola di Preparation); tiap kotak = warna Business KUNING + nama di dalam + logo di pojok kanan atas; tiap garis diberi label:
- Business Actor (`business_business_actor_logo.svg`) "Pemilik Restoran" —assignment→ Business Role (`business_business_role_logo.svg`) "Kasir" (garis solid; bulatan TERISI di sumber; panah TERISI di target): pelaku diberi peran.
- Business Role (`business_business_role_logo.svg`) "Kasir" —assignment→ Business Process (`business_business_process_logo.svg`) "Proses Pesanan" (garis solid; bulatan TERISI di sumber; panah TERISI di target): peran menjalankan proses.
- Business Process (`business_business_process_logo.svg`) "Proses Pesanan" —realization→ Business Service (`business_business_service_logo.svg`) "Layanan Makan di Tempat" (garis TITIK-TITIK; kepala SEGITIGA KOSONG di target): proses mewujudkan layanan.
- Business Service (`business_business_service_logo.svg`) "Layanan Makan di Tempat" —serving→ Business Role (`business_business_role_logo.svg`) "Pelanggan" (garis solid; kepala panah TERBUKA): layanan melayani pihak yang dilayani.
Sorot dengan warna PRIMARY alur "pelaku → peran → proses → layanan".

## 04_keterkaitan_antar_layer (~26s)
Scene lintas-layer dua arah; tiap kotak = warna native layer-nya + nama di dalam + logo di pojok kanan atas; semua relasi DIGAMBAR Manim:
- KE BAWAH (ditopang Application): Application Service (kotak Application biru muda, `application_application_service_logo.svg`) "Layanan POS" —serving→ Business Process (kotak Business KUNING, `business_business_process_logo.svg`) "Proses Pesanan" (garis solid; kepala panah TERBUKA): sistem melayani proses bisnis.
- KE ATAS (mewujudkan Strategy): Business Process (kotak Business KUNING, `business_business_process_logo.svg`) "Proses Pesanan" —realization→ Strategy Capability (kotak Strategy oranye, `strategy_capability_logo.svg`) "Penjualan online" (garis TITIK-TITIK; kepala SEGITIGA KOSONG mengarah ke Capability): proses bisnis mewujudkan kemampuan strategis.
Tegaskan dengan warna OK: Business = "apa yang dilakukan", Application = "sistem yang menopang", Strategy = "arah yang diwujudkan".

## 05_contoh_kasus (~32s)
Rakit model restoran secara bertahap; semua kotak elemen + relasi DIGAMBAR Manim, tiap kotak = warna Business KUNING + nama di dalam + logo di pojok kanan atas:
- Business Event (`business_business_event_logo.svg`) "Pesanan Masuk" memicu Business Process (`business_business_process_logo.svg`) "Proses Pesanan" (garis solid; kepala panah TERISI): event memicu proses.
- Business Actor (`business_business_actor_logo.svg`) "Pemilik Restoran" —assignment→ Business Role (`business_business_role_logo.svg`) "Koki"; Role "Koki" —assignment→ Business Process (`business_business_process_logo.svg`) "Penyajian".
- Business Process (`business_business_process_logo.svg`) "Proses Pesanan" —triggering→ Business Process (`business_business_process_logo.svg`) "Penyajian" (garis solid; kepala panah TERISI): satu proses mengalir ke proses berikutnya.
- Business Process (`business_business_process_logo.svg`) "Proses Pesanan" —association→ Business Object (`business_business_object_logo.svg`) "Pesanan" (garis solid polos): proses mengolah objek data.
- Business Process (`business_business_process_logo.svg`) "Penyajian" —realization→ Business Service (`business_business_service_logo.svg`) "Layanan Makan di Tempat".
- Product (`business_product_logo.svg`) "Paket Hemat" —composition→ Business Service (`business_business_service_logo.svg`) "Layanan Pesan Antar" dan —composition→ Contract (`business_contract_logo.svg`) "Syarat Promo" (garis solid; BELAH KETUPAT TERISI di ujung Product): produk tersusun atas layanan dan kontrak.
Sorot dengan warna HIGHLIGHT rantai utama: Event → Process → Service → Product.

## 06_kesimpulan (~16s)
Ringkas: Business Layer menangkap "apa yang dilakukan" lewat pelaku, peran, proses, fungsi, layanan, objek, dan produk — tampilkan lagi ikon aslinya (kotak Business KUNING + logo di pojok kanan atas):
- Business Actor (`business_business_actor_logo.svg`) "Actor"
- Business Role (`business_business_role_logo.svg`) "Role"
- Business Process (`business_business_process_logo.svg`) "Process"
- Business Function (`business_business_function_logo.svg`) "Function"
- Business Service (`business_business_service_logo.svg`) "Service"
- Business Object (`business_business_object_logo.svg`) "Object"
- Product (`business_product_logo.svg`) "Product"
- Business Event (`business_business_event_logo.svg`) "Event"
Satu kalimat peran tiap elemen, tegaskan dengan warna OK bahwa layer ini menghubungkan arah Strategy ke dukungan Application, lalu tutup dengan rantai di layar: Actor → Role → Process → Service → Product.
