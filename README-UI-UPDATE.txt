OSSIA UI UPDATE — 30 Oktober 2026

Perubahan yang dilakukan:
- Menyeragamkan header Home, Riwayat, Chat, dan Me.
- Menggunakan system font stack bergaya iOS (SF Pro pada perangkat Apple; fallback system UI pada perangkat lain).
- Menghapus pembuatan footer .mobile-nav dari halaman individual.
- Menjadikan navigasi di index.html satu-satunya footer dan membuatnya rata/flat di bagian bawah, tanpa kartu mengambang atau bayangan.
- Menyelaraskan tinggi halaman dan area scroll agar konten tidak tertutup footer.
- Menampilkan keadaan awal Home tanpa file/hasil pemeriksaan.
- Mengosongkan satu kali riwayat uji lama pada browser saat update pertama; riwayat upload baru berikutnya tetap disimpan.
- Mempertahankan app.py, proses backend, dan fungsi utama tiap halaman.

Pemasangan:
1. Backup folder project lama.
2. Ekstrak ZIP ini.
3. Jalankan seperti biasa: py app.py
4. Buka http://127.0.0.1:5000
5. Refresh browser dengan Ctrl + Shift + R.

Catatan:
- Navigasi footer tunggal bekerja melalui index.html (iframe aplikasi), jadi buka aplikasi dari index.html/root URL.
- Font SF Pro akan tampil jika tersedia di sistem Apple; pada Windows digunakan system UI/Segoe UI sebagai fallback.
