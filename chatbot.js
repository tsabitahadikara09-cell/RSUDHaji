// Logika chatbot demo; aktif hanya saat halaman Chat dibuka.
function initChatbot() {
  const chatBox = document.getElementById("chat-box");
  const input = document.getElementById("chat-input");
  if (!chatBox || !input) return;

  window.cekEnter = function(e) {
    if (e.key === "Enter") window.kirimPesan();
  };

  window.createBubble = function(posisi, teks) {
    if (posisi === "ai") {
      return `<div class="chat-bubble ai"><div class="chat-avatar">🤖</div><div class="chat-message">${teks}</div></div>`;
    }
    return `<div class="chat-bubble user"><div class="chat-message">${teks}</div><div class="chat-avatar">👦</div></div>`;
  };

  window.simulasiUnggah = function() {
    chatBox.insertAdjacentHTML("beforeend", createBubble("user", "📎 [Berkas X-Ray dikirim] Tolong analisis citra ini."));
    chatBox.scrollTop = chatBox.scrollHeight;
    setTimeout(() => {
      const reply = "<b>Demo analisis</b><br>Fitur pemrosesan citra belum terhubung ke backend. Hasil klinis tidak boleh disimpulkan dari simulasi ini.";
      chatBox.insertAdjacentHTML("beforeend", createBubble("ai", reply));
      chatBox.scrollTop = chatBox.scrollHeight;
    }, 700);
  };

  window.kirimPesan = function() {
    const message = input.value.trim();
    if (!message) return;
    chatBox.insertAdjacentHTML("beforeend", createBubble("user", escapeHTML(message)));
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
    setTimeout(() => {
      let reply = "Saya Asisten OSSIA versi demo. Integrasi AI dan rekam medis belum diaktifkan.";
      if (/hasil|riwayat/i.test(message)) reply = "Buka menu Riwayat untuk meninjau contoh catatan pemeriksaan. Data yang tampil masih data demo.";
      chatBox.insertAdjacentHTML("beforeend", createBubble("ai", reply));
      chatBox.scrollTop = chatBox.scrollHeight;
    }, 500);
  };
}
function escapeHTML(text) {
  return text.replace(/[&<>"']/g, char => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[char]));
}
