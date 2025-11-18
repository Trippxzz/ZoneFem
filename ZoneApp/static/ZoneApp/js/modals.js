// modals.js - Lógica visual

// Cambiar entre Login y Registro (Visual)
function switchLoginTab(tab) {
  // Estilos de tabs
  document.getElementById('tab-login').classList.toggle('border-instagram-pink', tab === 'login');
  document.getElementById('tab-login').classList.toggle('border-transparent', tab !== 'login');
  
  document.getElementById('tab-register').classList.toggle('border-instagram-pink', tab === 'register');
  document.getElementById('tab-register').classList.toggle('border-transparent', tab !== 'register');
  
  // Mostrar formularios
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  
  if (tab === 'login') {
      loginForm.classList.remove('hidden');
      registerForm.classList.add('hidden');
  } else {
      loginForm.classList.add('hidden');
      registerForm.classList.remove('hidden');
  }
}

// Simulación de pago
function initPaymentForm() {
    // lógica de máscaras de input...
}

function processPayment(event) {
  event.preventDefault();
  // Validaciones básicas...
  
  // Éxito simulado
  window.showNotification('Procesando pago...');
  setTimeout(() => {
      alert('¡Pago realizado con éxito!');
      window.cart = []; // Vaciar carrito global
      if(typeof updateCartDisplay === 'function') updateCartDisplay();
      window.closeModal('paymentModal');
  }, 1500);
}

window.switchLoginTab = switchLoginTab;
window.processPayment = processPayment;
window.initPaymentForm = initPaymentForm;