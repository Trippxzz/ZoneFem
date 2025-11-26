let currentSlide = 0;
const totalSlides = document.querySelectorAll('.carousel-item').length;

function moveCarousel(direction) {
  currentSlide += direction;
  
  if (currentSlide < 0) {
    currentSlide = totalSlides - 1;
  } else if (currentSlide >= totalSlides) {
    currentSlide = 0;
  }
  
  updateCarousel();
}

function goToSlide(index) {
  currentSlide = index;
  updateCarousel();
}

function updateCarousel() {
  const carousel = document.querySelector('.carousel');
  carousel.style.transform = `translateX(-${currentSlide * 100}%)`;
  
  // Actualizar dots
  document.querySelectorAll('.dot').forEach((dot, index) => {
    if (index === currentSlide) {
      dot.classList.add('active', 'bg-instagram-pink', 'scale-120');
      dot.classList.remove('bg-gray-300');
    } else {
      dot.classList.remove('active', 'bg-instagram-pink', 'scale-120');
      dot.classList.add('bg-gray-300');
    }
  });
}

// Auto-play cada 5 segundos
setInterval(() => {
  moveCarousel(1);
}, 5000);