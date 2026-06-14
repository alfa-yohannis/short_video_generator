---
title: archimate_technology_layer
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Technology Layer

Video tutorial animasi singkat tentang Technology Layer pada bahasa enterprise-architecture ArchiMate — layer fondasi yang menyediakan infrastruktur (perangkat keras, perangkat lunak sistem, dan jaringan) bagi layer di atasnya, termasuk elemen Physical untuk dunia fisik. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama elemen ArchiMate (kosakata standar notasi).

Contoh konsisten di SELURUH scene: sebuah RESTORAN yang menjalankan layanan online (server, database, tablet kasir, aplikasi delivery, jaringan internet) beserta sisi fisiknya (dapur, oven, bahan makanan, rute pengantaran).

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

ELEMEN = kotak (RoundedRectangle) digambar dengan Manim:
- Warna isi kotak = warna native layer-nya: Technology = HIJAU; elemen Physical JUGA hijau (bagian dari Technology Layer); Application = biru muda; Business = kuning; Strategy = oranye/kuning; Motivation = ungu. (Aksen panel/teks boleh memakai variasi warna Technology/hijau.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Berkas logo Technology: `technology_node_logo.svg`, `technology_device_logo.svg`, `technology_system_software_logo.svg`, `technology_technology_collaboration_logo.svg`, `technology_technology_interface_logo.svg`, `technology_path_logo.svg`, `technology_communication_network_logo.svg`, `technology_technology_function_logo.svg`, `technology_technology_process_logo.svg`, `technology_technology_interaction_logo.svg`, `technology_technology_event_logo.svg`, `technology_technology_service_logo.svg`, `technology_artifact_logo.svg`.
- Berkas logo Physical (warna hijau, bagian dari layer ini): `physical_equipment_logo.svg`, `physical_facility_logo.svg`, `physical_distribution_network_logo.svg`, `physical_material_logo.svg`.
- Berkas logo lintas layer (koneksi ke Application Layer, scene 05): `application_application_component_logo.svg`.

RELASI = JANGAN memuat SVG. Gambar dengan metode internal Manim (`Line` / `DashedLine` + bentuk kepala dari `Polygon`/`Triangle`/`Dot`) memakai helper build yang tersedia (`archi_element`, `assignment_arrow`, `serving_arrow`, `realization_arrow`, `influence_arrow`, `composition_arrow`, `association_arrow`) agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Pola garis + bentuk kepala sesuai notasi ArchiMate:
- Assignment: garis SOLID; bulatan TERISI (`Dot`) di ujung sumber; kepala panah TERISI di ujung target. Dipakai untuk: System Software ditempatkan (assigned) ke Node; Artifact di-deploy ke Node.
- Composition: garis SOLID; BELAH KETUPAT TERISI di ujung sumber. Dipakai untuk: sebuah Node tersusun (composed of) atas beberapa Device.
- Serving: garis SOLID; kepala panah TERBUKA (dua garis "V", tanpa isi) di target. Dipakai untuk: Technology Service —serving→ Application Component.
- Realization: garis TITIK-TITIK (dotted); kepala SEGITIGA KOSONG (outline) di target. Dipakai untuk: Node / System Software —realization→ Application Component; Artifact / Node —realization→ Technology Service.
- Association: garis SOLID polos (tanpa kepala, atau panah terbuka kecil). Dipakai untuk kaitan netral antar elemen (mis. Path & Communication Network, Equipment & Material).
- Influence: garis PUTUS-PUTUS (dashed); kepala panah TERBUKA (V) di target. (Cadangan bila perlu menandai pengaruh.)
Boleh beri label nama relasi di dekat garis bila membantu.

## 01_posisi_layer (~18s)
Judul besar "ArchiMate — Technology Layer" di tengah + subjudul "the foundation that runs everything". Gambar kerangka ArchiMate sebagai tumpukan pita berwarna — Motivation ungu, Strategy oranye, Business kuning, Application biru muda — lalu tampilkan Technology sebagai pita HIJAU paling BAWAH yang menopang semuanya. Sorot pita hijau dan tegaskan dengan warna HIGHLIGHT: Technology Layer adalah fondasi (infrastruktur perangkat keras, perangkat lunak sistem, dan jaringan) yang berada di bawah Application Layer dan menjalankan semua yang di atasnya. Sebutkan elemen Physical ikut tinggal di sini untuk dunia nyata (dapur, oven, bahan).

## 02_kosakata_technology (~30s)
Perkenalkan kosakata inti Technology; tiap kotak HIJAU + nama di dalam + logo di pojok kanan atas + contoh restoran, muncul bertahap (atur agar tidak penuh):
- Node (`technology_node_logo.svg`) "Server Cloud": unit komputasi tempat perangkat lunak berjalan.
- Device (`technology_device_logo.svg`) "Tablet Kasir": perangkat keras fisik.
- System Software (`technology_system_software_logo.svg`) "Database" dan "Sistem Operasi": perangkat lunak sistem.
- Technology Service (`technology_technology_service_logo.svg`) "Layanan Hosting": kemampuan teknologi yang ditawarkan ke layer atas. Tandai dengan warna ACCENT.
- Artifact (`technology_artifact_logo.svg`) "delivery-app.jar": berkas terdeploy yang merepresentasikan komponen aplikasi.
- Communication Network (`technology_communication_network_logo.svg`) "Internet": jaringan yang menghubungkan node.
- Technology Function (`technology_technology_function_logo.svg`) "Pemrosesan Pesanan": perilaku internal yang dijalankan sebuah node.

## 03_elemen_physical (~28s)
Perkenalkan elemen PHYSICAL — bagian dari Technology Layer namun untuk dunia fisik; tiap kotak HIJAU + nama di dalam + logo di pojok kanan atas + contoh restoran:
- Facility (`physical_facility_logo.svg`) "Dapur Pusat": fasilitas fisik (analog Node untuk dunia fisik). Tandai dengan warna PRIMARY.
- Equipment (`physical_equipment_logo.svg`) "Oven" dan "Kompor": peralatan fisik (analog Device).
- Material (`physical_material_logo.svg`) "Bahan Makanan": material berwujud yang diolah/dipindahkan.
- Distribution Network (`physical_distribution_network_logo.svg`) "Rute Pengantaran": jaringan distribusi fisik (analog Communication Network).
Tunjukkan kaitan DIGAMBAR Manim: Facility "Dapur Pusat" —composition→ Equipment "Oven" (garis solid; belah ketupat terisi di sumber Facility); Equipment "Oven" —association→ Material "Bahan Makanan"; Material —association→ Distribution Network "Rute Pengantaran". Tegaskan: Physical adalah cermin fisik dari konsep Technology yang digital.

## 04_keterkaitan_antar_elemen (~26s)
Hubungkan kotak Technology dengan RELASI yang DIGAMBAR Manim (lihat pola di Preparation); tiap kotak = warna HIJAU + nama di dalam + logo di pojok kanan atas:
- System Software (`technology_system_software_logo.svg`) "Database" —assignment→ Node (`technology_node_logo.svg`) "Server Cloud" (garis solid; bulatan terisi di sumber; panah terisi di target): perangkat lunak ditempatkan pada node.
- Artifact (`technology_artifact_logo.svg`) "delivery-app.jar" —assignment→ Node "Server Cloud" (garis solid; bulatan terisi di sumber; panah terisi): artifact di-deploy ke node.
- Node "Server Cloud" —composition→ Device (`technology_device_logo.svg`) "Tablet Kasir" (garis solid; belah ketupat terisi di sumber Node): node tersusun atas perangkat.
- Node "Server Cloud" —realization→ Technology Service (`technology_technology_service_logo.svg`) "Layanan Hosting" (garis titik-titik; segitiga kosong di target): node mewujudkan layanan teknologi yang dipakai layer atas.

## 05_keterkaitan_application (~24s)
Hubungkan Technology Layer ke ATAS dengan Application Layer — bagaimana fondasi menjalankan sistem. Tiap kotak = warna native layer-nya + nama di dalam + logo di pojok kanan atas; semua relasi DIGAMBAR Manim (lihat pola di Preparation):
- Technology Service (`technology_technology_service_logo.svg`) (kotak HIJAU) "Layanan Hosting" —serving→ Application Component (`application_application_component_logo.svg`) (kotak BIRU MUDA) "Aplikasi Delivery" (garis solid; kepala panah terbuka): layanan teknologi melayani komponen aplikasi.
- Node (`technology_node_logo.svg`) (kotak HIJAU) "Server Cloud" —realization→ Application Component "Aplikasi Delivery" (garis titik-titik; segitiga kosong di target): infrastruktur mewujudkan komponen aplikasi.
- System Software (`technology_system_software_logo.svg`) (kotak HIJAU) "Database" —realization→ Application Component "Aplikasi Delivery" (garis titik-titik; segitiga kosong): perangkat lunak sistem mewujudkan komponen aplikasi.
Tegaskan dengan warna HIGHLIGHT: Technology = fondasi/"di atas apa berjalan", Application = sistem/"apa yang dipakai".

## 06_contoh_kasus (~30s)
Mini-diagram restoran dibangun bertahap; semua kotak elemen + relasi DIGAMBAR Manim (pakai pola garis + kepala sesuai aturan):
Node (`technology_node_logo.svg`) "Server Cloud" menampung System Software (`technology_system_software_logo.svg`) "Database" —assignment→ "Server Cloud", dan Artifact (`technology_artifact_logo.svg`) "delivery-app.jar" —assignment→ "Server Cloud" (di-deploy). "Server Cloud" —composition→ Device (`technology_device_logo.svg`) "Tablet Kasir", dan terhubung lewat Communication Network (`technology_communication_network_logo.svg`) "Internet" (association). "Server Cloud" —realization→ Technology Service (`technology_technology_service_logo.svg`) "Layanan Hosting" —serving→ Application Component (`application_application_component_logo.svg`) (kotak BIRU MUDA) "Aplikasi Delivery". Di sisi fisik, Facility (`physical_facility_logo.svg`) "Dapur Pusat" —composition→ Equipment (`physical_equipment_logo.svg`) "Oven", yang mengolah Material (`physical_material_logo.svg`) "Bahan Makanan" (association). Tegaskan: satu gambar memperlihatkan fondasi digital DAN fisik restoran menopang aplikasi di atasnya.

## 07_kesimpulan (~16s)
Tampilkan lagi kotak-kotak inti (logo di pojok kanan atas) sebagai ringkasan:
- Node (`technology_node_logo.svg`) "Node"
- Device (`technology_device_logo.svg`) "Device"
- System Software (`technology_system_software_logo.svg`) "System Software"
- Technology Service (`technology_technology_service_logo.svg`) "Technology Service"
- Artifact (`technology_artifact_logo.svg`) "Artifact"
- Communication Network (`technology_communication_network_logo.svg`) "Communication Network"
- Facility (`physical_facility_logo.svg`) "Facility" + Equipment (`physical_equipment_logo.svg`) "Equipment" + Material (`physical_material_logo.svg`) "Material" + Distribution Network (`physical_distribution_network_logo.svg`) "Distribution Network" (sisi Physical).
Satu kalimat peran tiap kelompok, lalu kalimat penutup singkat: Technology Layer (termasuk Physical) adalah fondasi yang menjalankan dan menopang seluruh arsitektur. Tutup dengan rantai di layar: Node → Technology Service → Application Component.
