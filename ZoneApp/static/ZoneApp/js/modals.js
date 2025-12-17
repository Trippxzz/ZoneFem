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

// Calendario personalizado para fecha de nacimiento
let calendarioAbierto = false;
let fechaSeleccionada = null;

function configurarFechaNacimiento() {
    const input = document.getElementById('fechaNacimiento');
    const hiddenInput = document.getElementById('fechaNacimientoHidden');
    
    if (!input) return;
    
    // Crear contenedor del calendario si no existe
    let calendarioDiv = document.getElementById('calendario-picker');
    if (!calendarioDiv) {
        calendarioDiv = document.createElement('div');
        calendarioDiv.id = 'calendario-picker';
        calendarioDiv.className = 'calendario-container hidden';
        input.parentElement.appendChild(calendarioDiv);
    }
    
    // Abrir calendario al hacer clic en el input
    input.addEventListener('click', function(e) {
        e.stopPropagation();
        if (!calendarioAbierto) {
            abrirCalendario();
        }
    });
    
    // Evitar que se cierre al hacer clic dentro del calendario
    calendarioDiv.addEventListener('click', function(e) {
        e.stopPropagation();
    });
}

function abrirCalendario() {
    const calendarioDiv = document.getElementById('calendario-picker');
    const hoy = new Date();
    const fechaMaxima = new Date(hoy.getFullYear() - 14, hoy.getMonth(), hoy.getDate());
    
    let mesActual = fechaMaxima.getMonth();
    let añoActual = fechaMaxima.getFullYear();
    
    // Inicializar fecha seleccionada si no existe
    if (!fechaSeleccionada) {
        fechaSeleccionada = {
            dia: null,
            mes: mesActual,
            año: añoActual
        };
    }
    
    function renderizarCalendario() {
        const primerDia = new Date(añoActual, mesActual, 1);
        const ultimoDia = new Date(añoActual, mesActual + 1, 0);
        const diasEnMes = ultimoDia.getDate();
        const primerDiaSemana = primerDia.getDay();
        
        const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        
        let html = `
            <div class="calendario-header">
                <button type="button" class="calendario-nav" onclick="cambiarMes(-1)">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <div class="calendario-title">
                    <select id="mesSelect" onchange="cambiarMesSelect(this.value)">
                        ${meses.map((mes, idx) => 
                            `<option value="${idx}" ${idx === mesActual ? 'selected' : ''}>${mes}</option>`
                        ).join('')}
                    </select>
                    <select id="añoSelect" onchange="cambiarAñoSelect(this.value)">
                        ${Array.from({length: 100}, (_, i) => {
                            const año = hoy.getFullYear() - 14 - i;
                            return `<option value="${año}" ${año === añoActual ? 'selected' : ''}>${año}</option>`;
                        }).join('')}
                    </select>
                </div>
                <button type="button" class="calendario-nav" onclick="cambiarMes(1)">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            <div class="calendario-dias-semana">
                <div>Dom</div><div>Lun</div><div>Mar</div><div>Mié</div>
                <div>Jue</div><div>Vie</div><div>Sáb</div>
            </div>
            <div class="calendario-dias">
        `;
        
        // Días vacíos al inicio
        for (let i = 0; i < primerDiaSemana; i++) {
            html += '<div class="calendario-dia vacio"></div>';
        }
        
        // Días del mes
        for (let dia = 1; dia <= diasEnMes; dia++) {
            const fechaActual = new Date(añoActual, mesActual, dia);
            const esSeleccionado = fechaSeleccionada.dia === dia && 
                                  fechaSeleccionada.mes === mesActual && 
                                  fechaSeleccionada.año === añoActual;
            const esFuturo = fechaActual > fechaMaxima;
            
            html += `
                <div class="calendario-dia ${esSeleccionado ? 'seleccionado' : ''} ${esFuturo ? 'deshabilitado' : ''}" 
                     onclick="${esFuturo ? '' : `seleccionarDia(${dia})`}">
                    ${dia}
                </div>
            `;
        }
        
        html += `
            </div>
            <div class="calendario-footer">
                <button type="button" class="calendario-btn-cancelar" onclick="cerrarCalendario()">
                    Cancelar
                </button>
                <button type="button" class="calendario-btn-confirmar" onclick="confirmarFecha()">
                    Confirmar
                </button>
            </div>
        `;
        
        calendarioDiv.innerHTML = html;
    }
    
    renderizarCalendario();
    calendarioDiv.classList.remove('hidden');
    calendarioAbierto = true;
    
    // Funciones globales para el calendario
    window.cambiarMes = function(delta) {
        mesActual += delta;
        if (mesActual > 11) {
            mesActual = 0;
            añoActual++;
        } else if (mesActual < 0) {
            mesActual = 11;
            añoActual--;
        }
        renderizarCalendario();
    };
    
    window.cambiarMesSelect = function(mes) {
        mesActual = parseInt(mes);
        renderizarCalendario();
    };
    
    window.cambiarAñoSelect = function(año) {
        añoActual = parseInt(año);
        renderizarCalendario();
    };
    
    window.seleccionarDia = function(dia) {
        fechaSeleccionada = {
            dia: dia,
            mes: mesActual,
            año: añoActual
        };
        renderizarCalendario();
    };
    
    window.confirmarFecha = function() {
        if (fechaSeleccionada && fechaSeleccionada.dia) {
            const input = document.getElementById('fechaNacimiento');
            const hiddenInput = document.getElementById('fechaNacimientoHidden');
            
            const dia = String(fechaSeleccionada.dia).padStart(2, '0');
            const mes = String(fechaSeleccionada.mes + 1).padStart(2, '0');
            const año = fechaSeleccionada.año;
            
            // Formato para mostrar (DD/MM/YYYY)
            input.value = `${dia}/${mes}/${año}`;
            
            // Formato para enviar al servidor (YYYY-MM-DD)
            hiddenInput.value = `${año}-${mes}-${dia}`;
            
            cerrarCalendario();
        } else {
            alert('Por favor selecciona una fecha');
        }
    };
    
    window.cerrarCalendario = function() {
        const calendarioDiv = document.getElementById('calendario-picker');
        calendarioDiv.classList.add('hidden');
        calendarioAbierto = false;
    };
}

// Cerrar calendario al hacer clic fuera
document.addEventListener('click', function(e) {
    const calendarioDiv = document.getElementById('calendario-picker');
    const input = document.getElementById('fechaNacimiento');
    
    if (calendarioAbierto && calendarioDiv && input && 
        !calendarioDiv.contains(e.target) && 
        !input.contains(e.target)) {
        window.cerrarCalendario();
    }
});

// Manejar el envío del formulario de registro con AJAX
document.addEventListener('DOMContentLoaded', function() {
  const registroForm = document.getElementById('registroFormModal');
  if (registroForm) {
    registroForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const password1 = document.getElementById('passwordModal1').value;
      const password2 = document.getElementById('passwordModal2').value;
      const errorsDiv = document.getElementById('registroErrors');
      
      // Validar que las contraseñas coincidan
      if (password1 !== password2) {
        errorsDiv.innerHTML = '<i class="fas fa-exclamation-circle mr-2"></i>Las contraseñas no coinciden.';
        errorsDiv.classList.remove('hidden');
        return false;
      }
      
      // Enviar formulario con AJAX
      const formData = new FormData(registroForm);
      
      fetch(registroForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        if (response.redirected) {
          // Si hay redirect, significa que el registro fue exitoso
          window.location.href = response.url;
          return null;
        }
        return response.json();
      })
      .then(data => {
        if (data && !data.success) {
          // Mostrar errores sin borrar el formulario
          let errorHtml = '<i class="fas fa-exclamation-circle mr-2"></i>';
          for (let field in data.errors) {
            errorHtml += data.errors[field].join(', ') + '<br>';
          }
          errorsDiv.innerHTML = errorHtml;
          errorsDiv.classList.remove('hidden');
          
          // Mantener los datos del formulario (excepto contraseñas)
          if (data.data) {
            document.querySelector('input[name="first_name"]').value = data.data.first_name || '';
            document.querySelector('input[name="email"]').value = data.data.email || '';
            document.getElementById('rutModalInput').value = data.data.rut || '';
            document.querySelector('input[name="telefono"]').value = data.data.telefono || '';
          }
        }
      })
      .catch(error => {
        console.error('Error:', error);
        errorsDiv.innerHTML = '<i class="fas fa-exclamation-circle mr-2"></i>Ocurrió un error. Por favor intenta nuevamente.';
        errorsDiv.classList.remove('hidden');
      });
      
      return false;
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
    displayInput.addEventListener('click', function(e) {
      e.stopPropagation(); // Prevenir que el click se propague
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
    
    // Prevenir que clicks dentro del calendario se propaguen
    calendario.addEventListener('click', function(e) {
      e.stopPropagation();
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
  
  // Cerrar calendario al hacer clic fuera (pero no cuando son eventos automáticos del carrusel)
  document.addEventListener('click', function(e) {
    const calendario = document.getElementById('customCalendar');
    const displayInput = document.getElementById('fechaNacimientoDisplay');
    
    // Verificar que el click es real (tiene coordenadas) y no un evento sintético
    if (e.isTrusted && calendario && displayInput && 
        !calendario.contains(e.target) && 
        e.target !== displayInput &&
        !e.target.closest('.carousel-item')) { // Ignorar clicks dentro del carrusel
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
  // Solo marcar el día seleccionado, NO cerrar el calendario
  fechaSeleccionadaNacimiento = new Date(anioActualNacimiento, mesActualNacimiento, dia);
  renderCalendarioNacimiento();
  // No llamar a cerrarCalendarioNacimiento() aquí
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

// ============================================
// VALIDACIÓN DE RUT EN TIEMPO REAL
// ============================================

function validarRUT(rut) {
  // Limpiar RUT
  rut = rut.replace(/\./g, '').replace(/-/g, '').toUpperCase();
  
  // Validar formato básico
  if (!/^\d{7,8}[0-9K]$/.test(rut)) {
    return false;
  }
  
  // Separar número y dígito verificador
  const numero = rut.slice(0, -1);
  const dvIngresado = rut.slice(-1);
  
  // Calcular dígito verificador
  let suma = 0;
  let multiplo = 2;
  
  for (let i = numero.length - 1; i >= 0; i--) {
    suma += parseInt(numero[i]) * multiplo;
    multiplo = multiplo === 7 ? 2 : multiplo + 1;
  }
  
  const resto = suma % 11;
  const dvCalculado = 11 - resto;
  
  let dvEsperado;
  if (dvCalculado === 11) {
    dvEsperado = '0';
  } else if (dvCalculado === 10) {
    dvEsperado = 'K';
  } else {
    dvEsperado = dvCalculado.toString();
  }
  
  return dvIngresado === dvEsperado;
}

// Configurar validación del RUT cuando se carga el modal
document.addEventListener('DOMContentLoaded', function() {
  const rutInput = document.getElementById('rutModalInput');
  
  if (rutInput) {
    const rutStatus = document.getElementById('rutModalStatus');
    const rutMessage = document.getElementById('rutModalMessage');
    
    rutInput.addEventListener('input', function(e) {
      let value = e.target.value.replace(/\./g, '').replace(/-/g, '').toUpperCase();
      
      // Solo permitir números y K
      value = value.replace(/[^0-9K]/g, '');
      
      if (value.length === 0) {
        e.target.value = '';
        rutStatus.classList.add('hidden');
        rutMessage.textContent = 'Ingresa tu RUT';
        rutMessage.className = 'text-xs text-gray-500 mt-1';
        e.target.className = 'w-full py-3 px-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-instagram-pink pr-12';
        return;
      }
      
      // Formatear con puntos y guión
      if (value.length > 1) {
        const dv = value.slice(-1);
        let numero = value.slice(0, -1);
        
        // Agregar puntos cada 3 dígitos
        numero = numero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        
        e.target.value = numero + '-' + dv;
      } else {
        e.target.value = value;
      }
      
      // Validar solo si tiene formato completo, mínimo 8 caracteres sin formato
      if (value.length >= 8) {
        const esValido = validarRUT(value);
        
        if (esValido) {
          rutStatus.classList.remove('hidden');
          rutStatus.innerHTML = '<i class="fas fa-check-circle text-green-500 text-xl"></i>';
          rutMessage.textContent = '✓ RUT válido';
          rutMessage.className = 'text-xs text-green-600 font-medium mt-1';
          e.target.className = 'w-full py-3 px-4 border-2 border-green-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-600 pr-12';
        } else {
          rutStatus.classList.remove('hidden');
          rutStatus.innerHTML = '<i class="fas fa-times-circle text-red-500 text-xl"></i>';
          rutMessage.textContent = '✗ RUT inválido - Verifica el dígito verificador';
          rutMessage.className = 'text-xs text-red-600 font-medium mt-1';
          e.target.className = 'w-full py-3 px-4 border-2 border-red-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 pr-12';
        }
      } else {
        rutStatus.classList.add('hidden');
        rutMessage.textContent = 'Ingresa al menos 7 números + dígito verificador';
        rutMessage.className = 'text-xs text-gray-500 mt-1';
        e.target.className = 'w-full py-3 px-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-instagram-pink pr-12';
      }
    });
  }
});

// ============================================
// TOGGLE PASSWORD VISIBILITY EN MODAL
// ============================================

function togglePasswordModal(fieldId) {
  const field = document.getElementById(fieldId);
  const button = event.currentTarget;
  const icon = button.querySelector('i');
  
  if (field.type === 'password') {
    field.type = 'text';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  } else {
    field.type = 'password';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  }
}

window.togglePasswordModal = togglePasswordModal;