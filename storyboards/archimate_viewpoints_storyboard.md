---
title: archimate_viewpoints
subject: archimate
language: both
assets_dir: /home/alfa/projects/short_video_generator/assets
orientation: both
length: 2-3 minutes
---

# ArchiMate Views & Viewpoints

Video tutorial animasi singkat tentang Views & Viewpoints pada bahasa enterprise-architecture ArchiMate — perbedaan antara MODEL utuh dan sebuah VIEW, serta bagaimana Concern milik Stakeholder menentukan Viewpoint yang dipakai. Audiens pemula. Gaya: bersih, satu ide per layar, transisi halus.

Versi bahasa Inggris seluruhnya bahasa Inggris (termasuk contoh). Versi bahasa Indonesia seluruhnya bahasa Indonesia, kecuali nama elemen/konsep ArchiMate (kosakata standar notasi: Model, View, Viewpoint, Stakeholder, Concern, dll).

Contoh konsisten di SELURUH scene: sebuah RESTORAN dengan satu model utuh, ditampilkan lewat view berbeda untuk stakeholder berbeda (Owner melihat Motivation/Strategy; staf IT melihat Application/Technology).

# Preparation
Tidak perlu MCP/Archi. Ikon tipe elemen tersedia sebagai berkas SVG `_logo` di folder pada `assets_dir` (front-matter) beserta `manifest.json`; generator otomatis menyuntikkan daftar berkas + path absolutnya ke setiap scene.

CARA MENGGAMBAR (strict — konsisten di semua scene dan semua tingkat effort):

ELEMEN = kotak (RoundedRectangle) digambar dengan Manim:
- Warna isi kotak = warna native layer-nya: Motivation = UNGU; Strategy = oranye; Business = kuning; Application = biru muda; Technology = hijau. (Aksen panel/teks boleh memakai variasi warna layernya.)
- Nama elemen sebagai teks DI DALAM kotak (jangan sampai terpotong).
- Ikon tipe dimuat dari berkas `_logo.svg` aslinya via `SVGMobject("<path>")`, diskalakan KECIL, diletakkan di POJOK KANAN ATAS kotak dengan margin kecil — TIDAK menutupi nama/label. JANGAN menggambar/mengarang ikon sendiri dan JANGAN mewarnai ulang logo (tampilkan apa adanya).
- Berkas logo yang dipakai (HANYA enam ini): `motivation_stakeholder_logo.svg`, `motivation_goal_logo.svg`, `strategy_capability_logo.svg`, `business_business_process_logo.svg`, `application_application_component_logo.svg`, `technology_node_logo.svg`.

VIEW = panel/bingkai berlabel (RoundedRectangle besar/semi-transparan + judul panel) yang MENGELOMPOKKAN kotak-kotak terpilih. Sebuah view hanya menampilkan sebagian elemen dari model utuh; gambar bingkai panel mengelilingi kotak-kotak yang dipilih dan beri label nama view-nya. Model utuh = semua kotak + relasi tampil padat tanpa bingkai pemilih.

RELASI = JANGAN memuat SVG. Gambar dengan metode internal Manim (`Line` / `DashedLine` + bentuk kepala dari `Polygon`/`Triangle`/`Dot`) agar bisa menyesuaikan posisi, panjang, dan arah antar kotak. Sediakan helper dan pakai konsisten — pola garis + bentuk kepala sesuai notasi ArchiMate:
- serving_arrow: garis SOLID; kepala panah TERBUKA (dua garis "V", tanpa isi) di target.
- realization_arrow: garis TITIK-TITIK (dotted); kepala SEGITIGA KOSONG (outline) di target.
- association_arrow: garis SOLID polos (tanpa kepala, atau panah terbuka kecil) — pakai untuk menautkan elemen yang dikelompokkan ke dalam sebuah view.
- influence_arrow: garis PUTUS-PUTUS (dashed); kepala panah TERBUKA (V) di target.
Pakai association/serving untuk menunjukkan elemen yang dikumpulkan ke dalam sebuah view. Boleh beri label nama relasi di dekat garis bila membantu.

WARNA SEMANTIK untuk penegasan (terpisah dari warna layer): DANGER untuk kelebihan beban/kekacauan visual, OK untuk hasil yang bersih/terpilih, HIGHLIGHT untuk menyorot fokus, PRIMARY untuk panel/judul view utama, ACCENT untuk garis penghubung Stakeholder → Concern → Viewpoint → View. Hindari kata-kata arah/orientasi pada teks yang ditampilkan/diucapkan.

## 01_model_besar (~16s)
Judul besar "ArchiMate — Views & Viewpoints" di tengah + subjudul singkat "the right slice for the right audience". Tampilkan sekilas keseluruhan model restoran: banyak kotak dari beberapa layer (Motivation ungu, Strategy oranye, Business kuning, Application biru, Technology hijau) berdesakan dengan banyak relasi (gambar Manim) sehingga terasa PADAT. Sorot kepadatan dengan warna DANGER. Tegaskan: model lengkap itu besar — kita jarang menampilkan semuanya sekaligus.

## 02_model_vs_view (~24s)
Tunjukkan perbedaan MODEL vs VIEW. Kiri: model utuh yang padat (semua kotak + relasi, gambar Manim) — tandai DANGER karena terlalu ramai untuk satu audiens. Kanan: sebuah VIEW bersih — panel berlabel (PRIMARY) yang hanya MEMILIH sebagian kotak dari model itu. Untuk view ini pilih beberapa elemen, mis. Business Process (`business_business_process_logo.svg`) "Layani pesanan" dan Application Component (`application_application_component_logo.svg`) "Aplikasi Delivery", bingkai dalam panel berlabel, sisanya diredupkan. Tandai panel hasil dengan OK. Tegaskan: View = irisan model yang dipilih, bukan model baru — elemen yang sama, ditampilkan sebagian.

## 03_mekanisme (~26s)
Jelaskan rantai mekanisme dengan ACCENT, dibangun bertahap, semua relasi DIGAMBAR Manim:
- Stakeholder (kotak UNGU, `motivation_stakeholder_logo.svg`) "Pemilik Restoran" punya sebuah Concern (label/teks "Bagaimana bisnis tumbuh?").
- Concern itu —influence→ memilih sebuah VIEWPOINT (tampilkan sebagai "lensa": panel/bingkai HIGHLIGHT yang menyatakan tipe elemen & relasi APA yang boleh muncul).
- Viewpoint —realization→ menghasilkan sebuah VIEW (panel PRIMARY berisi kotak-kotak yang lolos lensa, ditaut dengan association_arrow).
Tampilkan rantai di layar: Stakeholder → Concern → Viewpoint (lensa) → View (diagram). Tegaskan: Viewpoint menentukan ATURAN (tipe yang diizinkan), View adalah DIAGRAM nyatanya.

## 04_dua_lensa (~32s)
Satu model restoran, DUA lensa — gambar dua panel view berdampingan, tiap kotak = warna native layer + nama di dalam + logo di pojok kanan atas; pengelompokan ke panel pakai association_arrow.
- Panel "Owner View" (PRIMARY) untuk Stakeholder "Pemilik": Motivation Goal (kotak UNGU, `motivation_goal_logo.svg`) "Tingkatkan pendapatan" + Strategy Capability (kotak oranye, `strategy_capability_logo.svg`) "Penjualan online" + Business Process (kotak kuning, `business_business_process_logo.svg`) "Layani pesanan". Concern: arah & nilai bisnis.
- Panel "IT View" (PRIMARY) untuk staf IT: Application Component (kotak biru, `application_application_component_logo.svg`) "Aplikasi Delivery" + Technology Node (kotak hijau, `technology_node_logo.svg`) "Server Cloud". Concern: sistem & infrastruktur.
Tegaskan dengan HIGHLIGHT: MODEL yang sama, DUA view berbeda untuk audiens berbeda — tiap stakeholder hanya melihat irisan yang relevan dengan concern-nya.

## 05_viewpoint_standar (~30s)
Jalan-jalan singkat melalui beberapa Viewpoint standar ArchiMate; tiap viewpoint sebagai panel/bingkai HIGHLIGHT berlabel + 1 kalimat kegunaannya + contoh isi kotak (warna layer + logo di pojok kanan atas):
- Layered viewpoint: melihat banyak layer sekaligus dan bagaimana saling menumpuk — tampilkan kotak lintas layer, mis. Business Process (`business_business_process_logo.svg`) di atas Application Component (`application_application_component_logo.svg`) di atas Technology Node (`technology_node_logo.svg`), ditaut serving_arrow ke atas.
- Business Process viewpoint: fokus alur kerja bisnis — tampilkan Business Process (kotak kuning, `business_business_process_logo.svg`) "Layani pesanan" sebagai pusat.
- Application Cooperation viewpoint: fokus bagaimana aplikasi bekerja sama — tampilkan dua Application Component (kotak biru, `application_application_component_logo.svg`) "Aplikasi Delivery" dan "Aplikasi POS" ditaut serving_arrow.
Sebut singkat dua lagi sebagai contoh: Motivation viewpoint (fokus Goal/Stakeholder) dan Implementation & Migration viewpoint (fokus rencana transisi). Tegaskan: tiap viewpoint = lensa berbeda untuk concern berbeda.

## 06_kesimpulan (~16s)
Ringkas rantai sekali lagi dengan ACCENT: Stakeholder (`motivation_stakeholder_logo.svg`) → Concern → Viewpoint (lensa) → View (diagram). Tampilkan kembali dua panel view dari scene 04 berdampingan (Owner View vs IT View) dari satu model yang sama, tandai keduanya OK. Manfaat: view menyampaikan irisan yang tepat ke audiens yang tepat — model tetap satu dan utuh, sementara tiap orang melihat bagian yang mereka pedulikan. Tutup dengan kalimat penutup singkat.
