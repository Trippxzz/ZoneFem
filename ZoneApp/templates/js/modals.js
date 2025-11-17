// --- Funciones del Modal de Pago ---
function initPaymentForm() {
  const paymentForm = document.getElementById('paymentForm');
  if (paymentForm) {
    paymentForm.addEventListener('submit', processPayment);
  }
  
  const cardNumberInput = document.getElementById('cardNumber');
  const cardExpiryInput = document.getElementById('cardExpiry');
  
  if (cardNumberInput) {
    cardNumberInput.addEventListener('input', function(e) {
      let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
      let formattedValue = '';
      
      for (let i = 0; i < value.length; i++) {
        if (i > 0 && i % 4 === 0) {
          formattedValue += ' ';
        }
        formattedValue += value[i];
      }
      
      e.target.value = formattedValue;
    });
  }
  
  if (cardExpiryInput) {
    cardExpiryInput.addEventListener('input', function(e) {
      let value = e.target.value.replace(/[^0-9]/g, '');
      if (value.length >= 2) {
        value = value.substring(0, 2) + '/' + value.substring(2, 4);
      }
      e.target.value = value;
    });
  }
}

function processPayment(event) {
  event.preventDefault();
  
  const cardName = document.getElementById('cardName').value;
  const cardNumber = document.getElementById('cardNumber').value;
  const cardExpiry = document.getElementById('cardExpiry').value;
  const cardCvv = document.getElementById('cardCvv').value;
  const cardEmail = document.getElementById('cardEmail').value;
  
  if (!cardName || !cardNumber || !cardExpiry || !cardCvv || !cardEmail) {
    alert('Por favor, completa todos los campos.');
    return;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(cardEmail)) {
    alert('Por favor, ingresa un correo electrónico válido.');
    return;
  }
  
  const expiryRegex = /^(0[1-9]|1[0-2])\/([0-9]{2})$/;
  if (!expiryRegex.test(cardExpiry)) {
    alert('Por favor, ingresa una fecha de vencimiento válida (MM/AA).');
    return;
  }
  
  const cvvRegex = /^[0-9]{3,4}$/;
  if (!cvvRegex.test(cardCvv)) {
    alert('Por favor, ingresa un CVV válido (3 o 4 dígitos).');
    return;
  }
  
  showNotification('Procesando tu pago...');
  
  setTimeout(() => {
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    alert(`¡Pago exitoso!
Monto: $${total.toLocaleString('es-CL')} CLP
Se ha enviado el comprobante a: ${cardEmail}
Gracias por tu compra en ZONFEM.`);
    
    cart = [];
    updateCartDisplay();
    document.getElementById('paymentForm').reset();
    closeModal('paymentModal');
    showNotification('¡Pago completado exitosamente!');
  }, 2000);
}

// --- Funciones de Login ---
function switchLoginTab(tab) {
  document.querySelectorAll('.login-tab').forEach(t => {
    t.classList.remove('active', 'border-b-2', 'border-instagram-pink', 'text-instagram-pink', 'font-bold');
    t.classList.add('border-transparent');
  });
  
  document.querySelectorAll('.login-form').forEach(f => {
    f.classList.add('hidden');
    f.classList.remove('active');
  });
  
  document.querySelector(`.login-tab:nth-child(${tab === 'login' ? 1 : 2})`).classList.add('active', 'border-b-2', 'border-instagram-pink', 'text-instagram-pink', 'font-bold');
  document.getElementById(tab === 'login' ? 'loginForm' : 'registerForm').classList.remove('hidden');
  document.getElementById(tab === 'login' ? 'loginForm' : 'registerForm').classList.add('active');
}

function login() {
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  
  if (!email || !password) {
    alert('Por favor, completa todos los campos.');
    return;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert('Por favor, ingresa un correo electrónico válido.');
    return;
  }
  
  closeModal('loginModal');
  showNotification('¡Bienvenido/a! Has iniciado sesión correctamente.');
}

function register() {
  const name = document.getElementById('registerName').value;
  const email = document.getElementById('registerEmail').value;
  const password = document.getElementById('registerPassword').value;
  const confirmPassword = document.getElementById('registerConfirmPassword').value;
  
  if (!name || !email || !password || !confirmPassword) {
    alert('Por favor, completa todos los campos.');
    return;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert('Por favor, ingresa un correo electrónico válido.');
    return;
  }
  
  if (password !== confirmPassword) {
    alert('Las contraseñas no coinciden.');
    return;
  }
  
  if (password.length < 6) {
    alert('La contraseña debe tener al menos 6 caracteres.');
    return;
  }
  
  closeModal('loginModal');
  showNotification('¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.');
}

function showForgotPassword() {
  const loginModalContent = document.querySelector('#loginModal .modal-content');
  const forgotPasswordHTML = `
    <div id="forgotPasswordForm" class="login-form active">
      <div class="form-group-modal mb-5">
        <label for="forgotEmail" class="block mb-2 font-medium flex items-center gap-2">
          <i class="fas fa-envelope"></i> Correo Electrónico
        </label>
        <input type="email" id="forgotEmail" class="w-full py-3 px-4 border border-border-color rounded-lg text-base bg-light-bg transition-all duration-300 focus:outline-none focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="tu@email.com" required>
      </div>
      <button class="btn btn-primary w-full text-center py-3 px-6 border-none rounded-full cursor-pointer font-bold transition-all duration-300 bg-instagram-gradient text-white hover:-translate-y-1 hover:shadow-lg hover:shadow-instagram-pink/40" onclick="submitForgotPassword()">
        <i class="fas fa-key"></i> Recuperar Contraseña
      </button>
      <div class="text-center mt-5">
        <a href="#" onclick="returnToLogin()" class="text-instagram-pink underline font-medium inline-flex items-center gap-1 hover:text-instagram-pink">
          <i class="fas fa-arrow-left"></i> Volver al inicio de sesión
        </a>
      </div>
    </div>
  `;
  
  loginModalContent.innerHTML = `
    <span class="btn-close absolute top-4 right-5 text-2xl cursor-pointer text-text-light transition-all duration-300 w-7 h-7 flex items-center justify-center rounded-full hover:text-instagram-red hover:bg-black hover:bg-opacity-5" onclick="closeModal('loginModal')" aria-label="Cerrar modal">×</span>
    <h2 class="modal-title text-2xl mb-6 text-center text-instagram-gradient flex items-center justify-center gap-3">
      <i class="fas fa-user-lock"></i> Recuperar Contraseña
    </h2>
    ${forgotPasswordHTML}
  `;
}

function submitForgotPassword() {
  const email = document.getElementById('forgotEmail').value;
  
  if (!email) {
    alert('Por favor, ingresa tu correo electrónico.');
    return;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert('Por favor, ingresa un correo electrónico válido.');
    return;
  }
  
  alert(`Se ha enviado un enlace de recuperación a: ${email}`);
  returnToLogin();
}

function returnToLogin() {
  const loginModalContent = document.querySelector('#loginModal .modal-content');
  
  loginModalContent.innerHTML = `
    <span class="btn-close absolute top-4 right-5 text-2xl cursor-pointer text-text-light transition-all duration-300 w-7 h-7 flex items-center justify-center rounded-full hover:text-instagram-red hover:bg-black hover:bg-opacity-5" onclick="closeModal('loginModal')" aria-label="Cerrar modal">×</span>
    <h2 class="modal-title text-2xl mb-6 text-center text-instagram-gradient flex items-center justify-center gap-3">
      <i class="fas fa-user"></i> Iniciar Sesión
    </h2>
    <div class="login-tabs flex mb-6 border-b border-border-color">
      <div class="login-tab flex-1 text-center py-3 cursor-pointer transition-all duration-300 border-b-2 border-instagram-pink text-instagram-pink font-bold active" onclick="switchLoginTab('login')">Iniciar Sesión</div>
      <div class="login-tab flex-1 text-center py-3 cursor-pointer transition-all duration-300 border-b-2 border-transparent font-medium hover:bg-instagram-pink hover:bg-opacity-5" onclick="switchLoginTab('register')">Registrarse</div>
    </div>
    <div id="loginForm" class="login-form active">
      <div class="form-group-modal mb-5">
        <label for="loginEmail" class="block mb-2 font-medium flex items-center gap-2">
          <i class="fas fa-envelope"></i> Correo Electrónico
        </label>
        <input type="email" id="loginEmail" class="w-full py-3 px-4 border border-border-color rounded-lg text-base bg-light-bg transition-all duration-300 focus:outline-none focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="tu@email.com" required>
      </div>
      <div class="form-group-modal mb-5">
        <label for="loginPassword" class="block mb-2 font-medium flex items-center gap-2">
          <i class="fas fa-lock"></i> Contraseña
        </label>
        <input type="password" id="loginPassword" class="w-full py-3 px-4 border border-border-color rounded-lg text-base bg-light-bg transition-all duration-300 focus:outline-none focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="••••••••" required>
      </div>
      <div class="form-actions flex justify-between mt-6">
        <button type="button" class="btn-link bg-transparent border-none text-instagram-purple underline cursor-pointer font-medium transition-all duration-300 hover:text-instagram-pink" onclick="showForgotPassword()">¿Olvidaste tu contraseña?</button>
        <button type="button" class="btn btn-primary py-3 px-6 border-none rounded-full cursor-pointer font-bold transition-all duration-300 inline-flex items-center gap-2 text-base bg-instagram-gradient text-white hover:-translate-y-1 hover:shadow-lg hover:shadow-instagram-pink/40" onclick="login()">
          <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
        </button>
      </div>
      <div class="social-login mt-6 text-center">
        <div class="social-login-title mb-5 text-text-light text-sm relative">
          O inicia sesión con
        </div>
        <div class="social-buttons flex justify-center gap-4">
          <div class="social-btn w-12 h-12 rounded-full flex items-center justify-center text-white text-xl cursor-pointer transition-all duration-300 social-google bg-red-500 hover:-translate-y-1 hover:shadow-lg" onclick="socialLogin('google')" title="Google" aria-label="Iniciar sesión con Google">
            <i class="fab fa-google"></i>
          </div>
          <div class="social-btn w-12 h-12 rounded-full flex items-center justify-center text-white text-xl cursor-pointer transition-all duration-300 social-facebook bg-blue-600 hover:-translate-y-1 hover:shadow-lg" onclick="socialLogin('facebook')" title="Facebook" aria-label="Iniciar sesión con Facebook">
            <i class="fab fa-facebook-f"></i>
          </div>
        </div>
      </div>
    </div>
    <div id="registerForm" class="login-form hidden">
      <div class="form-group-modal mb-5">
        <label for="registerName" class="block mb-2 font-medium flex items-center gap-2">
          <i class="fas fa-user"></i> Nombre completo:
        </label>
        <input type="text" id="registerName" class="w-full py-3 px-4 border border-border-color rounded-lg text-base bg-light-bg transition-all duration-300 focus:outline-none focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="Tu nombre completo">
      </div>
      <div class="form-group-modal mb-5">
        <label for="registerEmail" class="block mb-2 font-medium flex items-center gap-2">
          <i class="fas fa-envelope"></i> Correo:
        </label>
        <input type="email" id="registerEmail" class="w-full py-3 px-4 border border-border-color rounded-lg text-base bg-light-bg transition-all duration-300 focus:outline-none focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="tu@email.com">
      </div>
      <div class="form-group-modal mb-5">
        <label for="registerPassword" class="block mb-2 font-medium flex items-center gap-2">
          <i class="fas fa-lock"></i> Contraseña:
        </label>
        <input type="password" id="registerPassword" class="w-full py-3 px-4 border border-border-color rounded-lg text-base bg-light-bg transition-all duration-300 focus:outline-none focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="••••••••">
      </div>
      <div class="form-group-modal mb-5">
        <label for="registerConfirmPassword" class="block mb-2 font-medium flex items-center gap-2">
          <i class="fas fa-lock"></i> Confirmar contraseña:
        </label>
        <input type="password" id="registerConfirmPassword" class="w-full py-3 px-4 border border-border-color rounded-lg text-base bg-light-bg transition-all duration-300 focus:outline-none focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="••••••••">
      </div>
      <div class="form-actions">
        <button class="btn btn-primary py-3 px-6 border-none rounded-full cursor-pointer font-bold transition-all duration-300 inline-flex items-center gap-2 text-base bg-instagram-gradient text-white hover:-translate-y-1 hover:shadow-lg hover:shadow-instagram-pink/40" onclick="register()">
          <i class="fas fa-user-plus"></i> Registrarse
        </button>
      </div>
    </div>
  `;
}

function socialLogin(provider) {
  showNotification(`Iniciando sesión con ${provider}...`);
}