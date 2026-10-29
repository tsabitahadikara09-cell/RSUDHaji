(function () {
  "use strict";
  const HISTORY_KEY = "ossia_exam_history";
  // Same-origin API: works when Flask serves the existing OSSIA project root.
  const API_URL = "/api/analyze";

  function initHomeUI() {
    const input = document.getElementById("homeXrayFile");
    const dropzone = document.getElementById("homeDropzone");
    const preview = document.getElementById("homeFilePreview");
    const previewImage = document.getElementById("homePreviewImage");
    const fileName = document.getElementById("homeFileName");
    const fileSize = document.getElementById("homeFileSize");
    const title = document.getElementById("homeUploadTitle");
    const hint = document.getElementById("homeUploadHint");
    const button = document.getElementById("homeTestUpload");
    const message = document.getElementById("homeUploadMessage");
    if (!input || !button || input.dataset.bound === "1") return;
    input.dataset.bound = "1";

    let selectedFile = null;
    let objectUrl = null;
    const notify = text => {
      if (typeof window.showOssiaToast === "function") window.showOssiaToast(text);
      else if (message) message.textContent = text;
    };
    const sizeText = n => n < 1048576 ? `${Math.max(1, Math.round(n / 1024))} KB` : `${(n / 1048576).toFixed(1)} MB`;

    function reset() {
      selectedFile = null;
      input.value = "";
      if (preview) preview.hidden = true;
      if (previewImage) previewImage.removeAttribute("src");
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = null;
      if (title) title.textContent = "Pilih atau seret file X-ray";
      if (hint) hint.textContent = "PNG atau JPG dari perangkatmu";
      button.disabled = true;
      button.innerHTML = 'Proses X-ray & Simpan ke Riwayat <span>→</span>';
      if (message) message.textContent = "Pilih citra X-ray PNG/JPG maksimal 10 MB.";
    }

    function handleFile(file) {
      if (!file) return;
      if (!["image/png", "image/jpeg"].includes(file.type)) {
        notify("Format file belum didukung. Pilih PNG atau JPG.");
        input.value = "";
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        notify("Ukuran file maksimal 10 MB.");
        input.value = "";
        return;
      }
      selectedFile = file;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = URL.createObjectURL(file);
      if (previewImage) previewImage.src = objectUrl;
      if (fileName) fileName.textContent = file.name;
      if (fileSize) fileSize.textContent = sizeText(file.size);
      if (preview) preview.hidden = false;
      if (title) title.textContent = "File berhasil dipilih";
      if (hint) hint.textContent = "Pratinjau siap diproses";
      button.disabled = false;
      button.innerHTML = 'Proses X-ray & Simpan ke Riwayat <span>→</span>';
      if (message) message.textContent = "Citra siap diproses. Hasil akan otomatis masuk ke Riwayat.";
    }

    function compressDataUrl(dataUrl, maxWidth, format, quality) {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
          const scale = Math.min(1, maxWidth / img.naturalWidth);
          const canvas = document.createElement("canvas");
          canvas.width = Math.max(1, Math.round(img.naturalWidth * scale));
          canvas.height = Math.max(1, Math.round(img.naturalHeight * scale));
          canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
          resolve(format === "image/png" ? canvas.toDataURL("image/png") : canvas.toDataURL("image/jpeg", quality));
        };
        img.onerror = () => reject(new Error("Gambar hasil segmentasi tidak dapat dibaca."));
        img.src = dataUrl;
      });
    }

    function readHistory() {
      try {
        const records = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
        return Array.isArray(records) ? records : [];
      } catch (_) { return []; }
    }

    async function processImage() {
      if (!selectedFile) return;
      const file = selectedFile;
      button.disabled = true;
      button.textContent = "Memproses X-ray...";
      button.setAttribute("aria-busy", "true");
      if (message) message.textContent = "Mengirim citra ke backend OSSIA...";
      try {
        const form = new FormData();
        form.append("image", file);
        const response = await fetch(API_URL, { method: "POST", body: form });
        let result;
        try { result = await response.json(); }
        catch (_) { throw new Error("Respons backend tidak valid. Jalankan app.py dan buka OSSIA melalui alamat Flask."); }
        if (!response.ok) throw new Error(result.error || "Analisis citra gagal.");
        if (!result.overlay || !result.mask || !result.status) {
          throw new Error("Backend belum mengirim overlay, mask, dan status yang diperlukan.");
        }

        const record = {
          id: `OSSIA-${Date.now()}`,
          dateISO: new Date().toISOString(),
          filename: file.name,
          status: result.status,
          threshold: Number.isFinite(Number(result.threshold)) ? Number(result.threshold) : null,
          foregroundRatio: Number.isFinite(Number(result.foreground_ratio)) ? Number(result.foreground_ratio) : null,
          overlay: await compressDataUrl(result.overlay, 420, "image/jpeg", 0.68),
          mask: await compressDataUrl(result.mask, 320, "image/png", 1),
          explanation: result.explanation || "Periksa hasil mask secara visual.",
          limitation: result.limitation || "Hasil ini bukan prediksi usia tulang atau diagnosis klinis."
        };

        const records = readHistory();
        // Keep only recent records to reduce localStorage quota risk.
        const updated = [record, ...records].slice(0, 12);
        try {
          localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
        } catch (storageError) {
          // Try without masks if the browser's storage is close to its quota.
          updated.forEach(item => { item.mask = ""; });
          try { localStorage.setItem(HISTORY_KEY, JSON.stringify(updated.slice(0, 6))); }
          catch (_) { throw new Error("Penyimpanan browser penuh. Hapus data situs atau gunakan database backend."); }
        }

        notify("X-ray selesai diproses dan tersimpan di Riwayat.");
        if (message) message.textContent = "Berhasil. Membuka Riwayat pemeriksaan...";
        if (typeof window.bukaHalaman === "function") window.bukaHalaman("riwayat");
        else window.location.href = "riwayat.html";
      } catch (error) {
        console.error("OSSIA:", error);
        if (message) message.textContent = error.message || "Gagal memproses citra.";
        notify(error.message || "Gagal memproses citra.");
        button.disabled = !selectedFile;
        button.innerHTML = 'Coba proses lagi <span>→</span>';
      } finally {
        button.removeAttribute("aria-busy");
      }
    }

    input.addEventListener("change", () => handleFile(input.files && input.files[0]));
    ["dragenter", "dragover"].forEach(name => dropzone && dropzone.addEventListener(name, event => {
      event.preventDefault();
      dropzone.classList.add("dragging");
    }));
    ["dragleave", "drop"].forEach(name => dropzone && dropzone.addEventListener(name, event => {
      event.preventDefault();
      dropzone.classList.remove("dragging");
    }));
    if (dropzone) dropzone.addEventListener("drop", event => {
      const file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
      handleFile(file);
    });
    document.getElementById("homeRemoveFile")?.addEventListener("click", reset);
    button.addEventListener("click", processImage);
    document.getElementById("homeNotifications")?.addEventListener("click", () => notify("Belum ada notifikasi baru."));
    reset();
  }

  window.initHomeUI = initHomeUI;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initHomeUI);
  else initHomeUI();
})();