# OSSIA — perubahan khusus Home dan Riwayat

Paket ini dibuat berdasarkan `OSSIA-Modular.zip` sebelumnya.

## Yang diubah
- `pages/home.html`: UI Home mobile-first; tes upload PNG/JPG dan detail penjelasan hasil contoh.
- `pages/riwayat.html`: UI riwayat mobile-first; pencarian, filter, dan detail hasil.
- `css/home.css`, `css/riwayat.css`: stylesheet khusus kedua halaman.
- `js/home.js`, `js/riwayat.js`: interaksi UI kedua halaman.
- `js/app.js`: penambahan pemuatan CSS/JS Home dan Riwayat serta notifikasi toast; navigasi dan pemanggilan logika lama tetap dipertahankan.
- `css/style.css`: hanya tambahan kecil untuk navigasi bawah dan toast.

## Tidak diubah
- `pages/landing.html`
- `pages/login.html`
- `pages/chat.html`
- `pages/me.html`
- `js/chatbot.js`
- `js/logic.js`
- `index.html` dan struktur pemanggilan utamanya.

## Menjalankan
Buka folder hasil ekstraksi di VS Code, kemudian jalankan `index.html` melalui Live Server. Jangan buka langsung menggunakan `file://`.

## Batasan
Home hanya menguji pemilihan file, validasi format/ukuran, dan pratinjau di browser. Tidak ada ROI, segmentasi, atau perhitungan rasio yang dijalankan. Nilai pada Home dan Riwayat adalah data contoh UI, bukan hasil medis.
