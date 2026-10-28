(function () {
  // UI riwayat sengaja dimulai kosong. Database Cloudflare akan dihubungkan pada tahap akhir.
  // Jangan masukkan data contoh ke array ini.
  const records = [];
  let activeFilter = "all";

  function initRiwayatUI() {
    const list = document.getElementById("historyList");
    const search = document.getElementById("historySearch");
    if (!list || !search || search.dataset.bound === "1") return;
    search.dataset.bound = "1";

    const clear = document.getElementById("historyClear");
    const dialog = document.getElementById("historyDetailDialog");

    const months = n => {
      const y = Math.floor(n / 12), m = n % 12;
      return y && m ? `${y} th ${m} bln` : y ? `${y} tahun` : `${m} bulan`;
    };

    const card = r => {
      const diff = r.bone - r.chrono;
      return `<article class="om-history-card">
        <div class="om-history-top">
          <div class="om-history-date">
            <div class="om-xray-thumb" aria-hidden="true">▧</div>
            <div><strong>${r.date}</strong><small>ID pemeriksaan: ${r.id}</small></div>
          </div>
          <span class="om-status ${r.status}">${r.statusLabel}</span>
        </div>
        <div class="om-history-metrics">
          <div><span>Usia kronologis</span><strong>${months(r.chrono)}</strong></div>
          <div><span>Estimasi usia tulang</span><strong class="bone">${months(r.bone)}</strong></div>
        </div>
        <div class="om-history-bottom">
          <p>Selisih: <strong>${diff > 0 ? "+" : ""}${diff} bulan</strong></p>
          <button class="om-detail-button" type="button" data-detail="${r.id}">Detail hasil →</button>
        </div>
      </article>`;
    };

    function showDetail(id) {
      const r = records.find(item => item.id === id);
      if (!r || !dialog) return;
      const diff = r.bone - r.chrono;
      document.getElementById("historyDetailContent").innerHTML = `
        <p class="om-eyebrow">DETAIL PEMERIKSAAN</p>
        <h2>${r.date}</h2><p>ID pemeriksaan: ${r.id} · No. RM: ${r.rm}</p>
        <span class="om-status ${r.status}">${r.statusLabel}</span>
        <div class="om-detail-grid">
          <div><span>Usia kronologis</span><strong>${months(r.chrono)}</strong></div>
          <div><span>Estimasi usia tulang</span><strong>${months(r.bone)}</strong></div>
          <div><span>Selisih</span><strong>${diff > 0 ? "+" : ""}${diff} bulan</strong></div>
          <div><span>Status</span><strong>${r.statusLabel}</strong></div>
        </div>
        <div class="om-detail-explanation"><strong>Penjelasan status</strong><p>${r.explanation || "Penjelasan hasil akan ditampilkan setelah data pemeriksaan tersedia."}</p></div>
        <p>${r.note || ""}</p>
        <p><strong>Catatan:</strong> hasil skrining bukan pengganti diagnosis dokter.</p>`;
      dialog.showModal();
    }

    function emptyStateMessage(query) {
      if (query) {
        return {
          title: "Tidak ada hasil yang cocok",
          body: "Coba gunakan kata kunci lain atau hapus pencarian."
        };
      }
      if (activeFilter === "normal") {
        return {
          title: "Belum ada pemeriksaan normal",
          body: "Pemeriksaan dengan status Normal akan muncul di sini."
        };
      }
      if (activeFilter === "attention") {
        return {
          title: "Belum ada pemeriksaan yang perlu perhatian",
          body: "Pemeriksaan dengan status Perlu Perhatian akan muncul di sini."
        };
      }
      return {
        title: "Belum ada riwayat pemeriksaan",
        body: "Hasil pemeriksaan yang tersimpan akan ditampilkan di sini."
      };
    }

    function render() {
      const query = search.value.trim().toLowerCase();
      const filtered = records.filter(r => {
        const filterOk = activeFilter === "all" || r.status === activeFilter;
        const queryOk = !query || [
          r.date, r.id, r.rm, r.statusLabel,
          months(r.chrono), months(r.bone)
        ].some(value => String(value ?? "").toLowerCase().includes(query));
        return filterOk && queryOk;
      });

      document.getElementById("historyTotal").textContent = records.length;
      document.getElementById("historyAttention").textContent =
        records.filter(r => r.status === "attention").length;

      if (filtered.length) {
        list.innerHTML = filtered.map(card).join("");
      } else {
        const empty = emptyStateMessage(query);
        list.innerHTML = `<div class="om-empty-state"><strong>${empty.title}</strong><span>${empty.body}</span></div>`;
      }

      list.querySelectorAll("[data-detail]").forEach(button => {
        button.addEventListener("click", () => showDetail(button.dataset.detail));
      });

      if (clear) clear.hidden = !search.value;
      document.querySelectorAll("[data-history-filter]").forEach(button => {
        const selected = button.dataset.historyFilter === activeFilter;
        button.classList.toggle("selected", selected);
        button.setAttribute("aria-pressed", String(selected));
      });
    }

    search.addEventListener("input", render);
    if (clear) {
      clear.addEventListener("click", () => {
        search.value = "";
        render();
        search.focus();
      });
    }

    document.querySelectorAll("[data-history-filter]").forEach(button => {
      button.addEventListener("click", () => {
        activeFilter = button.dataset.historyFilter || "all";
        render();
      });
    });

    render();
  }

  window.initRiwayatUI = initRiwayatUI;
  if (document.readyState !== "loading") initRiwayatUI();
  else document.addEventListener("DOMContentLoaded", initRiwayatUI);
})();