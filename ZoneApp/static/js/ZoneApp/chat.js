// --- Funciones del Chat ---
function toggleChat() {
  const chatContainer = document.getElementById('chatContainer');
  
  if (chatContainer.style.display === 'flex') {
    chatContainer.style.display = 'none';
    chatMinimized = false;
  } else {
    chatContainer.style.display = 'flex';
    chatContainer.classList.remove('minimized');
    chatMinimized = false;
    document.getElementById('chatInput').focus();
  }
}

function minimizeChat() {
  const chatContainer = document.getElementById('chatContainer');
  
  if (chatMinimized) {
    chatContainer.classList.remove('minimized');
    chatMinimized = false;
  } else {
    chatContainer.classList.add('minimized');
    chatMinimized = true;
  }
}

function handleChatKeyPress(event) {
  if (event.key === 'Enter') {
    sendMessage();
  }
}

function sendMessage() {
  const chatInput = document.getElementById('chatInput');
  const message = chatInput.value.trim();
  
  if (message === '') return;
  
  addMessage(message, 'user');
  chatInput.value = '';
  
  showTypingIndicator();
  
  setTimeout(() => {
    hideTypingIndicator();
    const botResponse = generateBotResponse(message);
    addMessage(botResponse, 'bot');
  }, 1500);
}

function addMessage(text, sender) {
  const chatMessages = document.getElementById('chatMessages');
  const messageElement = document.createElement('div');
  
  messageElement.classList.add('message', 'max-w-[85%]', 'py-3', 'px-5', 'rounded-2xl', 'text-base', 'leading-relaxed', 'relative');
  
  if (sender === 'user') {
    messageElement.classList.add('user-message', 'self-end', 'bg-instagram-gradient', 'text-white', 'rounded-br-md');
  } else {
    messageElement.classList.add('bot-message', 'self-start', 'bg-white', 'text-gray-800', 'rounded-bl-md', 'shadow-sm');
  }
  
  if (sender === 'bot' && text.includes('tracking-form')) {
    messageElement.innerHTML = text;
  } else {
    messageElement.textContent = text;
  }
  
  chatMessages.appendChild(messageElement);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
  document.getElementById('typingIndicator').style.display = 'block';
  const chatMessages = document.getElementById('chatMessages');
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
  document.getElementById('typingIndicator').style.display = 'none';
}

// --- Funciones del Bot del Chat ---
function generateTrackingInfo(trackingNumber, status) {
  let statusText = '';
  let statusClass = '';
  let steps = [];
  
  switch(status) {
    case 'pending':
      statusText = 'Pendiente';
      statusClass = 'status-pending';
      steps = [
        { title: 'Pedido recibido', date: 'Hoy, 10:30 AM', completed: true },
        { title: 'En preparación', date: 'Próximamente', completed: false },
        { title: 'Enviado', date: '', completed: false },
        { title: 'Entregado', date: '', completed: false }
      ];
      break;
    case 'processing':
      statusText = 'En proceso';
      statusClass = 'status-processing';
      steps = [
        { title: 'Pedido recibido', date: 'Ayer, 14:20 PM', completed: true },
        { title: 'En preparación', date: 'Hoy, 09:15 AM', completed: true },
        { title: 'Enviado', date: 'Próximamente', completed: false },
        { title: 'Entregado', date: '', completed: false }
      ];
      break;
    case 'shipped':
      statusText = 'Enviado';
      statusClass = 'status-shipped';
      steps = [
        { title: 'Pedido recibido', date: '15/10/2023', completed: true },
        { title: 'En preparación', date: '16/10/2023', completed: true },
        { title: 'Enviado', date: 'Hoy, 11:45 AM', completed: true },
        { title: 'Entregado', date: 'Estimado: 19/10/2023', completed: false }
      ];
      break;
    case 'delivered':
      statusText = 'Entregado';
      statusClass = 'status-delivered';
      steps = [
        { title: 'Pedido recibido', date: '10/10/2023', completed: true },
        { title: 'En preparación', date: '11/10/2023', completed: true },
        { title: 'Enviado', date: '12/10/2023', completed: true },
        { title: 'Entregado', date: '14/10/2023, 15:20 PM', completed: true }
      ];
      break;
  }
  
  let stepsHTML = '';
  steps.forEach((step, index) => {
    const isLast = index === steps.length - 1;
    const stepIconClass = step.completed ? 'step-completed' : (index === 0 || steps[index-1].completed) ? 'step-current' : 'step-pending';
    const stepIcon = step.completed ? '✓' : (index === 0 || steps[index-1].completed) ? '●' : '○';
    
    stepsHTML += `
      <div class="tracking-step flex items-center gap-3">
        <div class="step-icon w-7 h-7 rounded-full flex items-center justify-center text-sm ${stepIconClass}">${stepIcon}</div>
        <div class="step-info flex-1">
          <div class="step-title font-medium text-sm">${step.title}</div>
          <div class="step-date text-xs text-gray-500">${step.date}</div>
        </div>
      </div>
      ${!isLast ? `<div class="step-line w-0.5 h-5 bg-gray-300 ml-3.5 ${step.completed ? 'completed' : ''}"></div>` : ''}
    `;
  });
  
  return `
    <div class="tracking-info bg-white rounded-xl p-5 mt-4 shadow-sm border border-gray-300">
      <div class="tracking-header flex justify-between items-center mb-4">
        <div class="tracking-number font-bold text-instagram-pink text-base">N° de pedido: ${trackingNumber}</div>
        <div class="tracking-status py-1.5 px-3 rounded-xl text-xs font-bold ${statusClass}">${statusText}</div>
      </div>
      <div class="tracking-steps flex flex-col gap-3">
        ${stepsHTML}
      </div>
    </div>
  `;
}

function processTrackingForm() {
  const orderNumber = document.getElementById('trackingOrderNumber').value.trim();
  const email = document.getElementById('trackingEmail').value.trim();
  
  if (!orderNumber || !email) {
    addMessage('Por favor, completa ambos campos para consultar el estado de tu pedido.', 'bot');
    return;
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    addMessage('Por favor, ingresa un correo electrónico válido.', 'bot');
    return;
  }
  
  showTypingIndicator();
  
  setTimeout(() => {
    hideTypingIndicator();
    const statuses = ['pending', 'processing', 'shipped', 'delivered'];
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
    const trackingInfo = generateTrackingInfo(orderNumber, randomStatus);
    addMessage(`Aquí tienes la información de seguimiento para el pedido ${orderNumber}:` + trackingInfo, 'bot');
    isTrackingRequested = false;
  }, 2000);
}

function generateBotResponse(userMessage) {
  const lowerMessage = userMessage.toLowerCase();
  
  if (lowerMessage.includes('hola') || lowerMessage.includes('buenas')) {
    return '¡Hola! Soy tu asistente de ZONFEM. ¿En qué puedo ayudarte hoy? Puedes preguntarme sobre consultas, cursos, o consultar el estado de tu envío.';
  } else if (lowerMessage.includes('cita') || lowerMessage.includes('consulta') || lowerMessage.includes('agendar')) {
    return 'Puedes agendar una consulta haciendo clic en "Agendar consulta" en nuestra página de inicio o en la sección de consultas. También puedes contactarnos directamente por teléfono o WhatsApp.';
  } else if (lowerMessage.includes('curso') || lowerMessage.includes('taller') || lowerMessage.includes('clase')) {
    return 'Ofrecemos varios cursos y talleres especializados. Puedes verlos todos en la sección "Cursos" de nuestro sitio web. Todos incluyen material de apoyo y certificado de participación.';
  } else if (lowerMessage.includes('precio') || lowerMessage.includes('costo') || lowerMessage.includes('valor')) {
    return 'Los precios de nuestros servicios varían según el tipo de consulta o curso. Puedes encontrar información detallada en las secciones de "Consultas" y "Cursos". También ofrecemos planes personalizados.';
  } else if (lowerMessage.includes('horario') || lowerMessage.includes('disponibilidad') || lowerMessage.includes('cuándo')) {
    return 'Nuestro horario de atención es de lunes a viernes de 8:00 a 18:00 y sábados de 9:00 a 13:00. Para consultas de urgencia fuera de este horario, contamos con un servicio de emergencias.';
  } else if (lowerMessage.includes('embarazo') || lowerMessage.includes('prenatal')) {
    return 'Ofrecemos control prenatal completo con matronas especializadas. Incluye seguimiento mensual, ecografías, asesoramiento nutricional y preparación para el parto. Puedes agendar una consulta en nuestra página.';
  } else if (lowerMessage.includes('parto') || lowerMessage.includes('nacimiento')) {
    return 'Tenemos cursos de preparación al parto y consultas especializadas para resolver todas tus dudas sobre el proceso de parto. ¡Visita nuestra sección de cursos para más información!';
  } else if (lowerMessage.includes('postparto') || lowerMessage.includes('postparto')) {
    return 'Ofrecemos consultas y cursos de recuperación postparto que incluyen cuidado del recién nacido, lactancia materna y recuperación física. Puedes encontrar más información en nuestra página.';
  } else if (lowerMessage.includes('contacto') || lowerMessage.includes('teléfono') || lowerMessage.includes('email')) {
    return 'Puedes contactarnos a través del formulario en la sección "Contacto", llamando al (123) 456-7890, o enviando un WhatsApp al mismo número. Estamos aquí para ayudarte.';
  } else if (lowerMessage.includes('gracias') || lowerMessage.includes('thank')) {
    return '¡De nada! Estoy aquí para ayudarte. ¿Hay algo más en lo que pueda asistirte?';
  } else if (lowerMessage.includes('seguimiento') || lowerMessage.includes('envío') || lowerMessage.includes('entrega') || lowerMessage.includes('pedido') || lowerMessage.includes('estado')) {
    isTrackingRequested = true;
    return `
      <div class="tracking-form bg-white rounded-xl p-5 mt-4 shadow-sm border border-gray-300">
        <p>Para consultar el estado de tu pedido, por favor ingresa:</p>
        <div class="tracking-form-group mb-4">
          <label for="trackingOrderNumber" class="block mb-2 text-sm font-medium text-gray-600">Número de pedido:</label>
          <input type="text" id="trackingOrderNumber" class="w-full py-2.5 px-3.5 border border-gray-300 rounded-lg text-sm outline-none transition-all duration-300 focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="Ej: ZF123456">
        </div>
        <div class="tracking-form-group mb-4">
          <label for="trackingEmail" class="block mb-2 text-sm font-medium text-gray-600">Correo electrónico:</label>
          <input type="email" id="trackingEmail" class="w-full py-2.5 px-3.5 border border-gray-300 rounded-lg text-sm outline-none transition-all duration-300 focus:border-instagram-pink focus:shadow-lg focus:shadow-instagram-pink/10" placeholder="tu@email.com">
        </div>
        <button class="tracking-submit-btn bg-instagram-gradient text-white border-none py-2.5 px-4.5 rounded-xl text-sm font-bold cursor-pointer transition-all duration-300 w-full flex items-center justify-center gap-2 hover:-translate-y-1 hover:shadow-lg hover:shadow-instagram-pink/30" onclick="processTrackingForm()">
          <i class="fas fa-search"></i> Consultar estado
        </button>
      </div>
    `;
  } else {
    return 'Entiendo que quieres información sobre: "' + userMessage + '". Te recomiendo visitar nuestras secciones de Consultas o Cursos, o contactarnos directamente para una atención personalizada. ¿Hay algo específico sobre lo que te gustaría saber más?';
  }
}