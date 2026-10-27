# OSSIA — versi buka langsung (tanpa Live Server)

## Cara kerja
- Klik dua kali `index.html`: langsung menampilkan Landing Page.
- Tombol Mulai / Masuk membuka `pages/login.html`.
- Tombol Masuk membuka `pages/home.html`.
- Navigasi bawah berpindah ke Home, Riwayat, Chat, dan Me.
- Setiap halaman HTML berdiri sendiri; perpindahan memakai link lokal, bukan `fetch()`.

## Menjalankan
Ekstrak ZIP, lalu klik dua kali `index.html`. Live Server tetap boleh digunakan, tetapi tidak wajib.

## Status
- Home: UI tes upload file dan pratinjau.
- Riwayat: pencarian, filter, dan detail pemeriksaan data contoh.
- Landing, Login, Chat, Me: UI saja.
- Belum ada autentikasi backend, ROI, segmentasi, rasio osifikasi, atau validasi klinis.
