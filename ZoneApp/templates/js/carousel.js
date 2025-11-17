// --- Funciones del Carrusel ---
function initCarousel() {
  // Auto-avance del carrusel
  setInterval(() => moveCarousel(1), 6000);
}

function moveCarousel(direction) {
  currentSlide += direction;
  if (currentSlide < 0) currentSlide = slides.length - 1;
  if (currentSlide >= slides.length) currentSlide = 0;
  
  const carousel = document.querySelector('.carousel');
  carousel.style.transform = `translateX(-${currentSlide * 100}%)`;
  updateDots();
}

function goToSlide(index) {
  currentSlide = index;
  const carousel = document.querySelector('.carousel');
  carousel.style.transform = `translateX(-${index * 100}%)`;
  updateDots();
}

function updateDots() {
  dots.forEach((dot, index) => {
    if (index === currentSlide) {
      dot.classList.add('active', 'bg-instagram-pink', 'scale-120');
      dot.classList.remove('bg-gray-300');
    } else {
      dot.classList.remove('active', 'bg-instagram-pink', 'scale-120');
      dot.classList.add('bg-gray-300');
    }
  });
}