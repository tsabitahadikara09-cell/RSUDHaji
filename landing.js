(() => {
  "use strict";

  const track = document.getElementById("slides");
  const dots = Array.from(document.querySelectorAll("[data-slide]"));
  const loginButtons = Array.from(document.querySelectorAll("[data-go-login]"));
  if (!track || !dots.length) return;

  let scrollTimer = null;

  function setActiveSlide(index) {
    const safeIndex = Math.max(0, Math.min(index, dots.length - 1));
    dots.forEach((dot, dotIndex) => {
      const active = dotIndex === safeIndex;
      dot.classList.toggle("is-active", active);
      dot.setAttribute("aria-pressed", String(active));
    });
  }

  function goToSlide(index) {
    const safeIndex = Math.max(0, Math.min(index, dots.length - 1));
    track.scrollTo({ left: safeIndex * track.clientWidth, behavior: "smooth" });
    setActiveSlide(safeIndex);
  }

  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      const index = Number(dot.dataset.slide);
      if (Number.isInteger(index)) goToSlide(index);
    });
  });

  track.addEventListener("scroll", () => {
    window.clearTimeout(scrollTimer);
    scrollTimer = window.setTimeout(() => {
      const index = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));
      setActiveSlide(index);
    }, 60);
  }, { passive: true });

  track.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      const index = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));
      goToSlide(index + 1);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      const index = Math.round(track.scrollLeft / Math.max(track.clientWidth, 1));
      goToSlide(index - 1);
    }
  });

  // Sesuai permintaan UI: tombol di semua slide langsung membuka halaman login.
  loginButtons.forEach((button) => {
    button.addEventListener("click", () => {
      window.location.href = "login.html";
    });
  });

  // Membantu halaman kembali ke slide pertama jika browser memulihkan posisi scroll lama.
  window.addEventListener("pageshow", () => {
    if (track.scrollLeft === 0) setActiveSlide(0);
  });
})();
