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