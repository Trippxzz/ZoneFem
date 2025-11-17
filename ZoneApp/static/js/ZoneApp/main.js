// --- Variables Globales ---
let cart = [];
const cartCountElement = document.getElementById('cartCount');
const cartTotalElement = document.getElementById('cartTotal');
let currentSlide = 0;
const slides = document.querySelectorAll('.carousel-item');
const dots = document.querySelectorAll('.dot');
let chatMinimized = false;
let isTrackingRequested = false;

// --- Inicialización ---
document.addEventListener('DOMContentLoaded', function() {
  initNavigation();
  updateCartDisplay();
  initPaymentForm();
  initCarousel(); // Inicializar el carrusel
});

// --- Funciones Generales ---
function openCart() {
  document.getElementById('cartModal').style.display = 'flex';
}

function closeCart() {
  document.getElementById('cartModal').style.display = 'none';
}

function openLoginModal() {
  document.getElementById('loginModal').style.display = 'flex';
}

function openSearch() {
  document.getElementById('searchModal').style.display = 'flex';
  document.getElementById('searchInput').focus();
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = 'none';
}

function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  
  function mostrarPagina(pageId) {
    navLinks.forEach(link => {
      link.classList.toggle('active', link.getAttribute('data-page') === pageId);
      if (link.getAttribute('data-page') === pageId) {
        link.classList.add('text-instagram-pink', 'bg-opacity-10', 'bg-instagram-pink');
      } else {
        link.classList.remove('text-instagram-pink', 'bg-opacity-10', 'bg-instagram-pink');
      }
    });
    
    document.querySelectorAll('.content-page').forEach(page => {
      page.classList.toggle('hidden', page.id !== pageId);
      page.classList.toggle('active', page.id === pageId);
    });
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const pageId = this.getAttribute('data-page');
      history.pushState({ page: pageId }, '', `#${pageId}`);
      mostrarPagina(pageId);
    });
  });
  
  window.addEventListener('popstate', function(event) {
    const pageId = event.state?.page || 'home';
    mostrarPagina(pageId);
  });
  
  const hash = window.location.hash.substring(1);
  const paginaInicial = hash || 'home';
  history.replaceState({ page: paginaInicial }, '', `#${paginaInicial}`);
  mostrarPagina(paginaInicial);
}

function showNotification(message) {
  const notification = document.createElement('div');
  notification.className = 'fixed top-5 right-5 bg-instagram-gradient text-white py-4 px-6 rounded-xl shadow-heavy z-50 animate-slideIn max-w-xs flex items-center gap-3';
  notification.innerHTML = `
    <i class="fas fa-check-circle text-xl"></i>
    <span>${message}</span>
  `;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-in forwards';
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 300);
  }, 4000);
}

function submitContactForm() {
  const name = document.getElementById('name').value;
  const phone = document.getElementById('phone').value;
  const email = document.getElementById('email').value;
  const message = document.getElementById('message').value;
  
  if (!name || !phone || !email || !message) {
    alert('Por favor, completa todos los campos del formulario.');
    return;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert('Por favor, ingresa un correo electrónico válido.');
    return;
  }
  
  alert(`¡Gracias ${name}!
Tu mensaje ha sido enviado correctamente. Te contactaremos al ${phone} o al correo ${email} en un plazo máximo de 24 horas.`);
  
  document.getElementById('name').value = '';
  document.getElementById('phone').value = '';
  document.getElementById('email').value = '';
  document.getElementById('message').value = '';
}

// --- Funciones de Búsqueda ---
function handleSearch() {
  const input = document.getElementById('searchInput');
  const clearBtn = document.getElementById('clearSearch');
  const resultsContainer = document.getElementById('searchResults');
  const resultsList = document.getElementById('resultsList');
  
  if (input.value.trim().length > 0) {
    clearBtn.style.opacity = '1';
  } else {
    clearBtn.style.opacity = '0';
  }
  
  const query = input.value.toLowerCase();
  const items = [
    { name: "Control prenatal", url: "#home", category: "Servicios" },
    { name: "Consulta prenatal integrativa", url: "#consultas", category: "Consultas" },
    { name: "Curso preparación al parto online", url: "#cursos", category: "Cursos" },
    { name: "Matronas especializadas", url: "#home", category: "Servicios" },
    { name: "Recuperación postparto", url: "#cursos", category: "Cursos" },
    { name: "Contacto", url: "#contacto", category: "Información" },
    { name: "Plan personalizado de parto", url: "#consultas", category: "Consultas" },
    { name: "Movimiento consciente para el embarazo", url: "#cursos", category: "Cursos" }
  ];
  
  const filtered = items.filter(item => item.name.toLowerCase().includes(query));
  
  if (query.length === 0) {
    resultsContainer.style.display = 'none';
    return;
  }
  
  if (filtered.length === 0) {
    resultsList.innerHTML = '<li class="py-4 text-gray-500 text-center"><i class="fas fa-search"></i> No se encontraron resultados.</li>';
  } else {
    resultsList.innerHTML = filtered.map(item => `
      <li class="py-3 px-4 border-b border-gray-200 transition-all duration-200">
        <a href="${item.url}" class="text-instagram-pink no-underline block" onclick="closeModal('searchModal');">
          <div class="font-medium"><i class="fas fa-search"></i> ${item.name}</div>
          <div class="text-xs text-gray-500 mt-1">${item.category}</div>
        </a>
      </li>
    `).join('');
  }
  
  resultsContainer.style.display = 'block';
}

function performSearch() {
  const query = document.getElementById('searchInput').value.trim();
  if (query === '') {
    alert('Por favor, escribe algo para buscar.');
    return;
  }
  
  showNotification(`Buscando: "${query}"`);
  closeModal('searchModal');
}

// --- Event Listeners ---
document.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && document.activeElement.id === 'searchInput') {
    performSearch();
  }
  
  if (e.key === 'Escape') {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
      if (modal.style.display === 'flex') {
        modal.style.display = 'none';
      }
    });
    
    if (document.getElementById('chatContainer').style.display === 'flex' && !chatMinimized) {
      toggleChat(); // Cierra el chat si no está minimizado
    }
  }
});

window.onclick = function(event) {
  if (event.target.classList.contains('modal')) {
    event.target.style.display = 'none';
  }
};