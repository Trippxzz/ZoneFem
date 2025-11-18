// carrusel.js — versión estable y global-friendly

var currentSlide = 0;
var slides = [];
var dots = [];
var autoInterval = null;

function initCarousel() {
    slides = Array.from(document.querySelectorAll('.carousel-item'));
    dots = Array.from(document.querySelectorAll('.dot'));

    // Forzar que cada slide ocupe 100%
    slides.forEach(s => {
        s.style.flex = "0 0 100%";
    });

    updateDots();

    // Auto slide
    if (autoInterval) clearInterval(autoInterval);
    if (slides.length > 1) {
        autoInterval = setInterval(() => moveCarousel(1), 6000);
    }
}

function moveCarousel(direction) {
    if (!slides.length) return;

    currentSlide += direction;

    if (currentSlide < 0) currentSlide = slides.length - 1;
    if (currentSlide >= slides.length) currentSlide = 0;

    const carousel = document.querySelector('.carousel');
    if (!carousel) return;

    carousel.style.transform = `translateX(-${currentSlide * 100}%)`;

    updateDots();
}

function goToSlide(index) {
    if (!slides.length) return;

    currentSlide = index;

    const carousel = document.querySelector('.carousel');
    if (!carousel) return;

    carousel.style.transform = `translateX(-${currentSlide * 100}%)`;

    updateDots();
}

function updateDots() {
    if (!dots.length) return;

    dots.forEach((dot, idx) => {
        if (idx === currentSlide) {
            dot.classList.add("active", "bg-instagram-pink", "scale-120");
            dot.classList.remove("bg-gray-300");
        } else {
            dot.classList.remove("active", "bg-instagram-pink", "scale-120");
            dot.classList.add("bg-gray-300");
        }
    });
}

// Flechas (eventos automáticos)
document.addEventListener("DOMContentLoaded", () => {
    initCarousel();

    document.querySelectorAll('.carousel-arrow').forEach(btn => {
        btn.addEventListener("click", () => {
            if (btn.textContent.includes("❮")) moveCarousel(-1);
            else moveCarousel(1);
        });
    });

    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => goToSlide(index));
    });
});

// --- EXPONER FUNCIONES AL GLOBAL PARA QUE EL HTML PUEDA USARLAS ---
window.moveCarousel = moveCarousel;
window.goToSlide = goToSlide;
