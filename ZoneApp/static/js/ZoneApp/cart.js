// --- Funciones del Carrito ---
function updateCartDisplay() {
  const cartItemsElement = document.getElementById('cartItems');
  cartCountElement.textContent = cart.reduce((total, item) => total + item.quantity, 0);
  
  if (cart.length === 0) {
    cartItemsElement.innerHTML = '<p id="cartEmpty">Tu carrito está vacío.</p>';
    cartTotalElement.textContent = '$0';
  } else {
    let itemsHTML = '';
    let total = 0;
    
    cart.forEach((item, index) => {
      itemsHTML += `
        <div class="cart-item flex justify-between items-center py-4 border-b border-border-color">
          <div class="cart-item-info flex-1">
            <div class="cart-item-name font-medium text-base">${item.name}</div>
            <div class="cart-item-price text-text-light text-sm mt-1">$${item.price.toLocaleString('es-CL')} CLP</div>
            <div class="cart-item-quantity flex items-center gap-3 mt-2">
              <button class="quantity-btn w-7 h-7 rounded-full border-none bg-light-bg text-text-dark cursor-pointer flex items-center justify-center font-bold transition-all duration-300 hover:bg-instagram-pink hover:text-white hover:scale-110" onclick="updateQuantity(${index}, -1)">-</button>
              <span class="quantity-value font-bold min-w-6 text-center">${item.quantity}</span>
              <button class="quantity-btn w-7 h-7 rounded-full border-none bg-light-bg text-text-dark cursor-pointer flex items-center justify-center font-bold transition-all duration-300 hover:bg-instagram-pink hover:text-white hover:scale-110" onclick="updateQuantity(${index}, 1)">+</button>
            </div>
          </div>
          <button class="cart-item-remove bg-transparent border-none text-instagram-red cursor-pointer text-lg transition-all duration-300 w-9 h-9 flex items-center justify-center rounded-full hover:scale-120 hover:bg-red-500 hover:bg-opacity-10" onclick="removeFromCart(${index})" aria-label="Eliminar ${item.name}">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      `;
      total += item.price * item.quantity;
    });
    
    cartItemsElement.innerHTML = itemsHTML;
    cartTotalElement.textContent = `$${total.toLocaleString('es-CL')} CLP`;
  }
}

function addToCart(itemName, price) {
  const existingItemIndex = cart.findIndex(item => item.name === itemName);
  
  if (existingItemIndex !== -1) {
    cart[existingItemIndex].quantity += 1;
  } else {
    cart.push({ name: itemName, price: price, quantity: 1 });
  }
  
  updateCartDisplay();
  showNotification(`"${itemName}" agregado al carrito`);
}

function updateQuantity(index, change) {
  cart[index].quantity += change;
  
  if (cart[index].quantity <= 0) {
    removeFromCart(index);
  } else {
    updateCartDisplay();
  }
}

function removeFromCart(index) {
  const itemName = cart[index].name;
  cart.splice(index, 1);
  updateCartDisplay();
  showNotification(`"${itemName}" eliminado del carrito`);
}

function clearCart() {
  if (cart.length === 0) {
    showNotification('El carrito ya está vacío');
    return;
  }
  
  cart = [];
  updateCartDisplay();
  showNotification('Carrito vaciado');
}

function openPaymentModal() {
  if (cart.length === 0) {
    alert('Tu carrito está vacío');
    return;
  }
  
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  document.getElementById('paymentAmount').textContent = `$${total.toLocaleString('es-CL')}`;
  closeCart();
  document.getElementById('paymentModal').style.display = 'flex';
}