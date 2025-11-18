// main.js — Limpio y Compatible con Django

// --- Variables Globales ---
var cart = window.cart || []; 
var cartCountElement = null;
var cartTotalElement = null;

// --- Inicialización ---
document.addEventListener('DOMContentLoaded', function() {
  // Referencias DOM
  cartCountElement = document.getElementById('cartCount');
  cartTotalElement = document.getElementById('cartTotal');

  // Inicializar componentes si existen
  if (typeof updateCartDisplay === 'function') updateCartDisplay();
  if (typeof initPaymentForm === 'function') initPaymentForm();
  if (typeof initCarousel === 'function') initCarousel();
});

// --- Gestión de Modales ---
function openCart() {
  const modal = document.getElementById('cartModal');
  if (modal) {
      modal.style.display = 'flex';
      if(typeof updateCartDisplay === 'function') updateCartDisplay();
  } else {
      console.error("El modal de carrito no existe en el DOM.");
  }
}

function closeCart() {
  const modal = document.getElementById('cartModal');
  if (modal) modal.style.display = 'none';
}

function openLoginModal() {
  const modal = document.getElementById('loginModal');
  if (modal) modal.style.display = 'flex';
}

function openSearch() {
  const modal = document.getElementById('searchModal');
  if (modal) {
      modal.style.display = 'flex';
      setTimeout(() => document.getElementById('searchInput')?.focus(), 100);
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = 'none';
}

// --- Utilidades ---
function showNotification(message) {
  const notification = document.createElement('div');
  notification.className = 'fixed top-5 right-5 bg-instagram-gradient text-white py-4 px-6 rounded-xl shadow-heavy z-50 animate-slideIn max-w-xs flex items-center gap-3';
  notification.innerHTML = `<i class="fas fa-check-circle"></i><span>${message}</span>`;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Cerrar con ESC
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
  }
});

// Cerrar al hacer clic fuera
window.onclick = function(event) {
  if (event.target.classList.contains('modal')) {
    event.target.style.display = 'none';
  }
};

// Exponer al global
window.openCart = openCart;
window.closeCart = closeCart;
window.openLoginModal = openLoginModal;
window.openSearch = openSearch;
window.closeModal = closeModal;
window.showNotification = showNotification;
window.cart = cart;