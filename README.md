# OSSIA — Semua Halaman Responsive Mobile

Versi ini menyesuaikan layout **semua halaman** agar nyaman di HP, sambil tetap responsif di tablet/laptop:
- Landing: layout bertumpuk pada layar HP.
- Login: form menyesuaikan lebar layar HP.
- Home: mobile UI, uji upload PNG/JPG dan pratinjau file.
- Riwayat: mobile UI, pencarian, filter, dan detail hasil demo.
- Chat: area chat dan input menyesuaikan layar HP.
- Me: profil dan item menu disusun ulang agar tidak melebar di HP.
- Navigasi Home / Riwayat / Chat / Me menggunakan bottom navigation di layar kecil.
- index.html tetap menjadi shell/pemanggil halaman melalui app.js.

## Menjalankan
Ekstrak ZIP, buka folder ini di VS Code, lalu jalankan `index.html` dengan Live Server. Jangan membuka dengan `file://`, karena halaman dimuat menggunakan `fetch()`.

## Status logika
Hanya Home dan Riwayat yang memiliki interaksi UI demo. Landing, Login, Chat, dan Me masih UI saja (login belum autentikasi nyata; chatbot hanya demo bila logikanya tersedia). Upload hanya menguji pemilihan dan pratinjau gambar, belum melakukan ROI, segmentasi, rasio osifikasi, atau interpretasi klinis. Data hasil adalah contoh.
