// modals.js - Lógica visual

// Cambiar entre Login y Registro (Visual)
function switchLoginTab(tab) {
  // Estilos de tabs
  document.getElementById('tab-login').classList.toggle('border-instagram-pink', tab === 'login');
  document.getElementById('tab-login').classList.toggle('text-instagram-pink', tab === 'login');
  document.getElementById('tab-login').classList.toggle('font-bold', tab === 'login');
  document.getElementById('tab-login').classList.toggle('border-transparent', tab !== 'login');
  document.getElementById('tab-login').classList.toggle('text-gray-500', tab !== 'login');
  document.getElementById('tab-login').classList.toggle('font-normal', tab !== 'login');
  
  document.getElementById('tab-register').classList.toggle('border-instagram-pink', tab === 'register');
  document.getElementById('tab-register').classList.toggle('text-instagram-pink', tab === 'register');
  document.getElementById('tab-register').classList.toggle('font-bold', tab === 'register');
  document.getElementById('tab-register').classList.toggle('border-transparent', tab !== 'register');
  document.getElementById('tab-register').classList.toggle('text-gray-500', tab !== 'register');
  document.getElementById('tab-register').classList.toggle('font-normal', tab !== 'register');
  
  // Mostrar formularios
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  
  if (tab === 'login') {
      loginForm.classList.remove('hidden');
      registerForm.classList.add('hidden');
  } else {
      loginForm.classList.add('hidden');
      registerForm.classList.remove('hidden');
      // Configurar fecha cuando se muestra el formulario de registro
      configurarFechaNacimiento();
  }
}

// Configurar límites de fecha de nacimiento
function configurarFechaNacimiento() {
  const fechaNacimientoInput = document.getElementById('fechaNacimiento');
  if (fechaNacimientoInput && !fechaNacimientoInput.hasAttribute('data-configured')) {
    const hoy = new Date();
    const hace14Anos = new Date(hoy.getFullYear() - 14, hoy.getMonth(), hoy.getDate());
    const hace100Anos = new Date(hoy.getFullYear() - 100, hoy.getMonth(), hoy.getDate());
    
    // Formato: YYYY-MM-DD
    fechaNacimientoInput.max = hace14Anos.toISOString().split('T')[0];
    fechaNacimientoInput.min = hace100Anos.toISOString().split('T')[0];
    
    // Marcar como configurado
    fechaNacimientoInput.setAttribute('data-configured', 'true');
  }
}

// Manejar el envío del formulario de registro
document.addEventListener('DOMContentLoaded', function() {
  const registroForm = document.getElementById('registroFormModal');
  if (registroForm) {
    registroForm.addEventListener('submit', function(e) {
      const password1 = document.getElementById('password1').value;
      const password2 = document.getElementById('password2').value;
      const errorsDiv = document.getElementById('registroErrors');
      
      // Validar que las contraseñas coincidan
      if (password1 !== password2) {
        e.preventDefault();
        errorsDiv.textContent = 'Las contraseñas no coinciden.';
        errorsDiv.classList.remove('hidden');
        return false;
      }
      
      // Validar longitud mínima
      if (password1.length < 8) {
        e.preventDefault();
        errorsDiv.textContent = 'La contraseña debe tener al menos 8 caracteres.';
        errorsDiv.classList.remove('hidden');
        return false;
      }
      
      errorsDiv.classList.add('hidden');
    });
  }
});

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

// Variables globales para el calendario de nacimiento
let calendarioNacimientoAbierto = false;
let mesActualNacimiento = 0;
let anioActualNacimiento = 2000;
let fechaSeleccionadaNacimiento = null;

// Abrir/cerrar calendario personalizado
document.addEventListener('DOMContentLoaded', function() {
  const displayInput = document.getElementById('fechaNacimientoDisplay');
  const calendario = document.getElementById('customCalendar');
  
  if (displayInput && calendario) {
    displayInput.addEventListener('click', function() {
      calendarioNacimientoAbierto = !calendarioNacimientoAbierto;
      if (calendarioNacimientoAbierto) {
        // Establecer fecha inicial (hace 25 años)
        const hoy = new Date();
        anioActualNacimiento = hoy.getFullYear() - 25;
        mesActualNacimiento = hoy.getMonth();
        
        document.getElementById('anioNacimiento').value = anioActualNacimiento;
        document.getElementById('mesNacimiento').value = mesActualNacimiento;
        
        renderCalendarioNacimiento();
        calendario.classList.remove('hidden');
      } else {
        calendario.classList.add('hidden');
      }
    });
    
    // Listener para cambio de mes/año
    document.getElementById('mesNacimiento').addEventListener('change', function() {
      mesActualNacimiento = parseInt(this.value);
      renderCalendarioNacimiento();
    });
    
    document.getElementById('anioNacimiento').addEventListener('change', function() {
      anioActualNacimiento = parseInt(this.value);
      renderCalendarioNacimiento();
    });
  }
  
  // Cerrar calendario al hacer clic fuera
  document.addEventListener('click', function(e) {
    const calendario = document.getElementById('customCalendar');
    const displayInput = document.getElementById('fechaNacimientoDisplay');
    if (calendario && displayInput && !calendario.contains(e.target) && e.target !== displayInput) {
      calendario.classList.add('hidden');
      calendarioNacimientoAbierto = false;
    }
  });
});

function renderCalendarioNacimiento() {
  const diasContainer = document.getElementById('diasCalendarioNacimiento');
  if (!diasContainer) return;
  
  const primerDia = new Date(anioActualNacimiento, mesActualNacimiento, 1).getDay();
  const ultimoDia = new Date(anioActualNacimiento, mesActualNacimiento + 1, 0).getDate();
  const ultimoDiaMesAnterior = new Date(anioActualNacimiento, mesActualNacimiento, 0).getDate();
  
  let html = '';
  
  // Días del mes anterior
  for (let i = primerDia; i > 0; i--) {
    html += `<div class="aspect-square text-gray-300 text-center py-2 opacity-30">${ultimoDiaMesAnterior - i + 1}</div>`;
  }
  
  // Días del mes actual
  for (let dia = 1; dia <= ultimoDia; dia++) {
    const esSeleccionado = fechaSeleccionadaNacimiento && 
                           fechaSeleccionadaNacimiento.getDate() === dia && 
                           fechaSeleccionadaNacimiento.getMonth() === mesActualNacimiento && 
                           fechaSeleccionadaNacimiento.getFullYear() === anioActualNacimiento;
    
    const claseSeleccionado = esSeleccionado ? 'bg-instagram-gradient text-white font-bold' : 'hover:bg-pink-50 hover:text-instagram-pink';
    
    html += `<button type="button" class="aspect-square rounded-full flex items-center justify-center transition-all duration-200 cursor-pointer font-medium ${claseSeleccionado}" onclick="seleccionarDiaNacimiento(${dia})">${dia}</button>`;
  }
  
  diasContainer.innerHTML = html;
}

function cambiarMesNacimiento(direccion) {
  mesActualNacimiento += direccion;
  if (mesActualNacimiento < 0) {
    mesActualNacimiento = 11;
    anioActualNacimiento--;
  } else if (mesActualNacimiento > 11) {
    mesActualNacimiento = 0;
    anioActualNacimiento++;
  }
  
  // Actualizar los selects
  document.getElementById('mesNacimiento').value = mesActualNacimiento;
  document.getElementById('anioNacimiento').value = anioActualNacimiento;
  
  renderCalendarioNacimiento();
}

function seleccionarDiaNacimiento(dia) {
  fechaSeleccionadaNacimiento = new Date(anioActualNacimiento, mesActualNacimiento, dia);
  renderCalendarioNacimiento();
}

function confirmarFechaNacimiento() {
  if (!fechaSeleccionadaNacimiento) {
    alert('Por favor selecciona una fecha');
    return;
  }
  
  // Validar que sea mayor de 14 años
  const hoy = new Date();
  const edad = hoy.getFullYear() - fechaSeleccionadaNacimiento.getFullYear();
  const diferenciaMeses = hoy.getMonth() - fechaSeleccionadaNacimiento.getMonth();
  const diferenciaDias = hoy.getDate() - fechaSeleccionadaNacimiento.getDate();
  
  if (edad < 14 || (edad === 14 && (diferenciaMeses < 0 || (diferenciaMeses === 0 && diferenciaDias < 0)))) {
    alert('Debes ser mayor de 14 años para registrarte');
    return;
  }
  
  // Formatear fecha para mostrar
  const dia = String(fechaSeleccionadaNacimiento.getDate()).padStart(2, '0');
  const mes = String(fechaSeleccionadaNacimiento.getMonth() + 1).padStart(2, '0');
  const anio = fechaSeleccionadaNacimiento.getFullYear();
  
  document.getElementById('fechaNacimientoDisplay').value = `${dia}/${mes}/${anio}`;
  document.getElementById('fechaNacimiento').value = `${anio}-${mes}-${dia}`;
  
  cerrarCalendarioNacimiento();
}

function cerrarCalendarioNacimiento() {
  document.getElementById('customCalendar').classList.add('hidden');
  calendarioNacimientoAbierto = false;
}

window.cambiarMesNacimiento = cambiarMesNacimiento;
window.seleccionarDiaNacimiento = seleccionarDiaNacimiento;
window.confirmarFechaNacimiento = confirmarFechaNacimiento;
window.cerrarCalendarioNacimiento = cerrarCalendarioNacimiento;