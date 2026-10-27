(function () {
  const records = [
    { id:"OSS-1025", date:"25 Okt 2026", rm:"RM-100010", chrono:108, bone:84, status:"attention", statusLabel:"Perlu Perhatian", explanation:"Contoh UI: estimasi usia tulang 7 tahun dibandingkan usia kronologis 9 tahun, sehingga selisihnya 24 bulan. Penjelasan ini belum berasal dari hasil analisis tervalidasi.", note:"Bagian interpretasi klinis dan saran tindak lanjut nantinya perlu diisi berdasarkan validasi data dan masukan dokter RSUD Haji." },
    { id:"OSS-0910", date:"10 Sep 2026", rm:"RM-100010", chrono:108, bone:108, status:"normal", statusLabel:"Normal", explanation:"Contoh UI: usia tulang dan usia kronologis ditampilkan sama. Label ini belum merupakan kesimpulan medis.", note:"Interpretasi akhir harus mempertimbangkan kualitas citra, data pasien, dan validasi tenaga medis." },
    { id:"OSS-0721", date:"21 Jul 2026", rm:"RM-100010", chrono:102, bone:102, status:"normal", statusLabel:"Normal", explanation:"Contoh tampilan dengan selisih nol bulan.", note:"Semua nilai pada daftar ini adalah data contoh untuk mendesain antarmuka." },
    { id:"OSS-0612", date:"12 Jun 2026", rm:"RM-100010", chrono:96, bone:72, status:"attention", statusLabel:"Perlu Perhatian", explanation:"Contoh UI: estimasi usia tulang tertinggal 24 bulan dari usia kronologis.", note:"Penjelasan dan saran tindak lanjut final akan ditentukan setelah validasi metode dan masukan dokter." }
  ];
  let activeFilter = "all";
  function initRiwayatUI() {
    const list = document.getElementById("historyList");
    const search = document.getElementById("historySearch");
    if (!list || search.dataset.bound === "1") return;
    search.dataset.bound = "1";
    const clear = document.getElementById("historyClear");
    const dialog = document.getElementById("historyDetailDialog");
    const notify = text => {
      if (window.showOssiaToast) window.showOssiaToast(text);
    };
    const months = n => {
      const y = Math.floor(n / 12), m = n % 12;
      return y && m ? `${y} th ${m} bln` : y ? `${y} tahun` : `${m} bulan`;
    };
    const card = r => {
      const diff = r.bone - r.chrono;
      return `<article class="om-history-card">
        <div class="om-history-top"><div class="om-history-date"><div class="om-xray-thumb" aria-hidden="true">▧</div><div><strong>${r.date}</strong><small>ID pemeriksaan: ${r.id}</small></div></div><span class="om-status ${r.status}">${r.statusLabel}</span></div>
        <div class="om-history-metrics"><div><span>Usia kronologis</span><strong>${months(r.chrono)}</strong></div><div><span>Estimasi usia tulang</span><strong class="bone">${months(r.bone)}</strong></div></div>
        <div class="om-history-bottom"><p>Selisih contoh: <strong>${diff > 0 ? "+" : ""}${diff} bulan</strong></p><button class="om-detail-button" type="button" data-detail="${r.id}">Detail hasil →</button></div>
      </article>`;
    };
    function showDetail(id) {
      const r = records.find(item => item.id === id);
      if (!r || !dialog) return;
      const diff = r.bone - r.chrono;
      document.getElementById("historyDetailContent").innerHTML = `
        <p class="om-eyebrow">DETAIL PEMERIKSAAN · DATA CONTOH</p>
        <h2>${r.date}</h2><p>ID pemeriksaan: ${r.id} · No. RM: ${r.rm}</p>
        <span class="om-status ${r.status}">${r.statusLabel}</span>
        <div class="om-detail-grid"><div><span>Usia kronologis</span><strong>${months(r.chrono)}</strong></div><div><span>Estimasi usia tulang</span><strong>${months(r.bone)}</strong></div><div><span>Selisih</span><strong>${diff > 0 ? "+" : ""}${diff} bulan</strong></div><div><span>Status data</span><strong>Contoh UI</strong></div></div>
        <div class="om-detail-explanation"><strong>Penjelasan status</strong><p>${r.explanation}</p></div>
        <p>${r.note}</p><p><strong>Catatan:</strong> bukan diagnosis dan tidak digunakan untuk keputusan klinis.</p>`;
      dialog.showModal();
    }
    function render() {
      const q = search.value.trim().toLowerCase();
      const filtered = records.filter(r => {
        const filterOk = activeFilter === "all" || r.status === activeFilter;
        const queryOk = !q || [r.date, r.id, r.rm, r.statusLabel, months(r.chrono), months(r.bone)].some(v => v.toLowerCase().includes(q));
        return filterOk && queryOk;
      });
      document.getElementById("historyTotal").textContent = records.length;
      document.getElementById("historyAttention").textContent = records.filter(r => r.status === "attention").length;
      list.innerHTML = filtered.length ? filtered.map(card).join("") : '<div class="om-empty-state"><strong>Riwayat tidak ditemukan</strong>Coba ubah kata kunci atau filter status.</div>';
      list.querySelectorAll("[data-detail]").forEach(btn => btn.addEventListener("click", () => showDetail(btn.dataset.detail)));
      clear.hidden = !search.value;
    }
    search.addEventListener("input", render);
    clear.addEventListener("click", () => { search.value = ""; render(); search.focus(); });
    document.querySelectorAll("[data-history-filter]").forEach(btn => btn.addEventListener("click", () => {
      activeFilter = btn.dataset.historyFilter;
      document.querySelectorAll("[data-history-filter]").forEach(b => b.classList.toggle("selected", b === btn));
      render();
    }));
    document.getElementById("historyFilterJump")?.addEventListener("click", () => {
      document.getElementById("historyFilters")?.scrollIntoView({ behavior:"smooth", block:"center" });
      notify("Pilih filter status di bawah kolom pencarian.");
    });
    render();
  }
  window.initRiwayatUI = initRiwayatUI;
  if (document.readyState !== "loading") initRiwayatUI();
  else document.addEventListener("DOMContentLoaded", initRiwayatUI);
})();
