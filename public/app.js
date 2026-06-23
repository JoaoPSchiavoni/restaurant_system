// Global State
let currentUser = null;
let currentToken = null;
let activeOrders = [];
let selectedOrderId = null;

// Pizza Default Prices based on Size
const basePrices = {
  "Pequena": 29.90,
  "Média": 39.90,
  "Grande": 49.90,
  "Família": 59.90
};

// ==========================================================================
// Initialization & Authentication Logic
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
  // Check if user is already logged in
  const savedToken = localStorage.getItem("access_token");
  const savedUser = localStorage.getItem("current_user");

  if (savedToken && savedUser) {
    currentToken = savedToken;
    currentUser = JSON.parse(savedUser);
    showDashboard();
  } else {
    showAuth();
  }

  // Adjust modal price estimates
  updateEstimatedPrice();
});

function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

function switchTab(tab) {
  const tabLogin = document.getElementById("tab-login");
  const tabRegister = document.getElementById("tab-register");
  const formLogin = document.getElementById("login-form");
  const formRegister = document.getElementById("register-form");

  if (tab === "login") {
    tabLogin.classList.add("active");
    tabRegister.classList.remove("active");
    formLogin.classList.add("active-form");
    formRegister.classList.remove("active-form");
  } else {
    tabLogin.classList.remove("active");
    tabRegister.classList.add("active");
    formLogin.classList.remove("active-form");
    formRegister.classList.add("active-form");
  }
}

// User Sign Up
async function handleRegister(event) {
  event.preventDefault();
  const name = document.getElementById("register-name").value.trim();
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;
  const admin = document.getElementById("register-admin").checked;

  try {
    const response = await fetch("/auth/create_account", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password, active: true, admin })
    });

    const data = await response.json();

    if (response.ok) {
      showToast("Conta criada com sucesso! Faça login.", "success");
      document.getElementById("register-form").reset();
      switchTab("login");
    } else {
      showToast(data.detail || "Erro ao registrar conta", "error");
    }
  } catch (err) {
    console.error("Registration error:", err);
    showToast("Não foi possível conectar ao servidor", "error");
  }
}

// User Sign In
async function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
      currentToken = data.access_token;
      
      // Basic fallback since we only get the token.
      // We parse the token payload to see the user_id/sub.
      const payload = parseJwt(currentToken);
      
      currentUser = {
        id: payload ? payload.sub : null,
        email: email,
        name: email.split("@")[0], // Fallback name
        admin: false // Default, will update if we list orders and see admin behavior
      };

      // Store in localStorage
      localStorage.setItem("access_token", currentToken);
      localStorage.setItem("current_user", JSON.stringify(currentUser));

      showToast(`Bem-vindo, ${currentUser.name}!`, "success");
      document.getElementById("login-form").reset();
      showDashboard();
    } else {
      showToast(data.detail || "Credenciais inválidas", "error");
    }
  } catch (err) {
    console.error("Login error:", err);
    showToast("Erro ao conectar ao servidor", "error");
  }
}

// User Log Out
function handleLogout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("current_user");
  currentUser = null;
  currentToken = null;
  activeOrders = [];
  selectedOrderId = null;
  
  showToast("Sessão encerrada com sucesso.", "info");
  showAuth();
}

function showAuth() {
  document.getElementById("auth-view").style.display = "flex";
  document.getElementById("dashboard-view").style.display = "none";
}

function showDashboard() {
  document.getElementById("auth-view").style.display = "none";
  document.getElementById("dashboard-view").style.display = "flex";

  // Setup header info
  document.getElementById("user-display-name").textContent = currentUser.name;
  
  // Refresh Order List
  loadOrders();
}

// ==========================================================================
// Order Management Logic
// ==========================================================================

async function loadOrders(selectIdAfterLoad = null) {
  try {
    const response = await fetch("/order/", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${currentToken}`
      }
    });

    if (response.status === 401) {
      handleLogout();
      return;
    }

    const data = await response.json();

    if (response.ok) {
      activeOrders = data;
      
      // Determine user privilege from list_orders response
      // (FastAPI lists all orders only if admin=True)
      // Check if we can infer admin from the orders user ids
      const userIds = new Set(activeOrders.map(o => o.user_id));
      if (userIds.size > 1) {
        currentUser.admin = true;
        document.getElementById("user-display-role").textContent = "Administrador";
        localStorage.setItem("current_user", JSON.stringify(currentUser));
      } else {
        document.getElementById("user-display-role").textContent = "Cliente";
      }

      renderOrdersList();

      if (selectIdAfterLoad) {
        selectOrder(selectIdAfterLoad);
      } else if (selectedOrderId) {
        // If an order was already selected, refresh its details
        selectOrder(selectedOrderId);
      }
    } else {
      showToast(data.detail || "Falha ao carregar pedidos", "error");
    }
  } catch (err) {
    console.error("Load orders error:", err);
    showToast("Erro ao carregar pedidos", "error");
  }
}

function renderOrdersList() {
  const container = document.getElementById("orders-list");
  
  if (activeOrders.length === 0) {
    container.innerHTML = `
      <div class="no-orders-state">
        <i class="fa-regular fa-clipboard"></i>
        <p>Nenhum pedido criado ainda.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = activeOrders.map(order => {
    const activeClass = (order.id === selectedOrderId) ? 'active-order-card' : '';
    const statusClass = `status-${order.status.toLowerCase()}`;
    const itemsText = order.items.length === 1 ? '1 item' : `${order.items.length} itens`;
    const formattedPrice = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(order.price);

    return `
      <div class="order-list-card ${activeClass}" onclick="selectOrder(${order.id})">
        <div class="card-header-row">
          <span class="order-card-id">Pedido #${order.id.toString().padStart(2, '0')}</span>
          <span class="status-badge ${statusClass}">${order.status}</span>
        </div>
        <div class="card-details-row">
          <span class="order-card-items-count">${itemsText}</span>
          <span class="order-card-price">${formattedPrice}</span>
        </div>
      </div>
    `;
  }).join('');
}

// Create new, empty order
async function createNewOrder() {
  try {
    const response = await fetch("/order/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${currentToken}`,
        "Content-Type": "application/json"
      }
    });

    const data = await response.json();

    if (response.ok) {
      showToast("Pedido criado com sucesso!", "success");
      // Load orders list and auto-select the new order
      // Extract number from success message (e.g. "Order created successfully 4")
      const match = data.Message.match(/\d+/);
      const newOrderId = match ? parseInt(match[0]) : null;
      loadOrders(newOrderId);
    } else {
      showToast(data.detail || "Erro ao criar pedido", "error");
    }
  } catch (err) {
    console.error("Create order error:", err);
    showToast("Erro de rede ao criar pedido", "error");
  }
}

// Select and show details of an order
async function selectOrder(orderId) {
  selectedOrderId = orderId;
  
  // Highlight card in list immediately
  document.querySelectorAll(".order-list-card").forEach(card => card.classList.remove("active-order-card"));
  const activeCard = Array.from(document.querySelectorAll(".order-list-card"))
    .find(c => c.innerHTML.includes(`Pedido #${orderId.toString().padStart(2, '0')}`));
  if (activeCard) {
    activeCard.classList.add("active-order-card");
  }

  try {
    const response = await fetch(`/order/${orderId}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${currentToken}`
      }
    });

    const order = await response.json();

    if (response.ok) {
      // Toggle display panels
      document.getElementById("order-empty-state").classList.remove("active-state");
      document.getElementById("order-detail-card").style.display = "flex";

      // Populate details
      document.getElementById("detail-order-id").textContent = order.id.toString().padStart(2, '0');
      
      const statusBadge = document.getElementById("detail-order-status");
      statusBadge.className = `status-badge status-${order.status.toLowerCase()}`;
      statusBadge.textContent = order.status;

      const formattedPrice = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(order.price);
      document.getElementById("detail-order-price").textContent = formattedPrice;

      // Populate items table
      renderOrderItemsTable(order.items, order.status);

      // Toggle action buttons based on status
      const isEditable = order.status === "PENDING";
      document.getElementById("open-add-item-btn").style.display = isEditable ? "inline-flex" : "none";
      document.getElementById("cancel-order-btn").style.display = isEditable ? "inline-flex" : "none";
      document.getElementById("finalize-order-btn").style.display = isEditable ? "inline-flex" : "none";
      
    } else {
      showToast(order.detail || "Erro ao carregar detalhes do pedido", "error");
    }
  } catch (err) {
    console.error("Select order error:", err);
    showToast("Erro ao carregar detalhes", "error");
  }
}

function renderOrderItemsTable(items, orderStatus) {
  const tbody = document.getElementById("order-items-tbody");
  const emptyState = document.getElementById("items-empty-state");
  const isEditable = orderStatus === "PENDING";

  if (items.length === 0) {
    tbody.innerHTML = "";
    emptyState.style.display = "flex";
    return;
  }

  emptyState.style.display = "none";
  tbody.innerHTML = items.map((item, index) => {
    const total = item.amount * item.unit_price;
    const formattedUnit = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(item.unit_price);
    const formattedTotal = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(total);
    
    // We assume ID is index + 1 or fetch actual ID if available.
    // In our test, if backend has real item IDs we use them.
    // Let's use item.id or fallback to index.
    const itemId = item.id || (index + 1);

    const deleteBtn = isEditable 
      ? `<button class="delete-item-btn" onclick="handleDeleteOrderItem(${itemId})" title="Remover item"><i class="fa-regular fa-trash-can"></i></button>`
      : `<span class="text-muted" style="font-size:0.8rem">Sem ações</span>`;

    return `
      <tr>
        <td><strong>${item.flavor}</strong></td>
        <td><span class="user-role-badge" style="background-color: rgba(255,255,255,0.04)">${item.size}</span></td>
        <td class="text-center">${item.amount}</td>
        <td class="text-right">${formattedUnit}</td>
        <td class="text-right" style="color: var(--color-primary); font-weight: 600;">${formattedTotal}</td>
        <td class="text-center">${deleteBtn}</td>
      </tr>
    `;
  }).join('');
}

// Cancel current order
async function cancelCurrentOrder() {
  if (!selectedOrderId) return;
  if (!confirm("Tem certeza que deseja CANCELAR este pedido?")) return;

  try {
    const response = await fetch(`/order/${selectedOrderId}/cancel`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${currentToken}`
      }
    });

    const data = await response.json();

    if (response.ok) {
      showToast("Pedido cancelado com sucesso.", "info");
      loadOrders();
    } else {
      showToast(data.detail || "Não foi possível cancelar o pedido", "error");
    }
  } catch (err) {
    console.error("Cancel order error:", err);
    showToast("Erro ao processar cancelamento", "error");
  }
}

// Finalize current order
async function finalizeCurrentOrder() {
  if (!selectedOrderId) return;
  
  // Verify items list
  const activeOrder = activeOrders.find(o => o.id === selectedOrderId);
  if (activeOrder && activeOrder.items.length === 0) {
    showToast("Adicione pelo menos um item antes de finalizar o pedido.", "error");
    return;
  }

  if (!confirm("Deseja FINALIZAR e fechar a conta deste pedido?")) return;

  try {
    const response = await fetch(`/order/${selectedOrderId}/finish`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${currentToken}`
      }
    });

    const data = await response.json();

    if (response.ok) {
      showToast("Pedido finalizado com sucesso!", "success");
      loadOrders();
    } else {
      showToast(data.detail || "Erro ao finalizar pedido", "error");
    }
  } catch (err) {
    console.error("Finalize order error:", err);
    showToast("Erro ao processar finalização", "error");
  }
}

// ==========================================================================
// Order Items Logic & Modal Handler
// ==========================================================================

function showAddItemForm() {
  const modal = document.getElementById("add-item-modal");
  modal.classList.add("active-modal");
  // Set defaults
  document.getElementById("item-flavor").selectedIndex = 0;
  document.getElementById("item-size").value = "Média";
  document.getElementById("item-amount").value = 1;
  updateEstimatedPrice();
}

function hideAddItemForm() {
  const modal = document.getElementById("add-item-modal");
  modal.classList.remove("active-modal");
}

function updateEstimatedPrice() {
  const size = document.getElementById("item-size").value;
  const amount = parseInt(document.getElementById("item-amount").value) || 1;
  const customPriceInput = document.getElementById("item-price");
  
  // If the size changed, auto-update the unit price input based on static table
  if (document.activeElement !== customPriceInput) {
    const defaultPrice = basePrices[size] || 39.90;
    customPriceInput.value = defaultPrice.toFixed(2);
  }

  const unitPrice = parseFloat(customPriceInput.value) || 0.0;
  const total = amount * unitPrice;
  
  document.getElementById("estimated-total-value").textContent = 
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(total);
}

// Add Item submit action
async function handleAddOrderItem(event) {
  event.preventDefault();
  if (!selectedOrderId) return;

  const flavor = document.getElementById("item-flavor").value;
  const size = document.getElementById("item-size").value;
  const amount = parseInt(document.getElementById("item-amount").value);
  const unit_price = parseFloat(document.getElementById("item-price").value);

  if (!flavor) {
    showToast("Por favor, selecione um sabor de pizza.", "error");
    return;
  }

  try {
    const response = await fetch(`/order/${selectedOrderId}/items`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${currentToken}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ amount, flavor, size, unit_price })
    });

    const data = await response.json();

    if (response.ok) {
      showToast("Item adicionado com sucesso!", "success");
      hideAddItemForm();
      // Reload orders list and refresh detail panel
      loadOrders();
    } else {
      showToast(data.detail || "Erro ao adicionar item", "error");
    }
  } catch (err) {
    console.error("Add item error:", err);
    showToast("Erro ao processar envio", "error");
  }
}

// Delete item
async function handleDeleteOrderItem(itemId) {
  if (!confirm("Remover este item do pedido?")) return;

  try {
    const response = await fetch(`/order/items/${itemId}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${currentToken}`
      }
    });

    const data = await response.json();

    if (response.ok) {
      showToast("Item removido com sucesso.", "info");
      loadOrders();
    } else {
      showToast(data.detail || "Erro ao remover item", "error");
    }
  } catch (err) {
    console.error("Delete item error:", err);
    showToast("Erro de rede ao remover item", "error");
  }
}

// ==========================================================================
// Toast Notification System
// ==========================================================================

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  
  let iconClass = "fa-circle-info";
  if (type === "success") iconClass = "fa-circle-check";
  if (type === "error") iconClass = "fa-triangle-exclamation";
  
  toast.innerHTML = `
    <i class="fa-solid ${iconClass} toast-icon"></i>
    <div class="toast-content">${message}</div>
  `;
  
  container.appendChild(toast);
  
  // Automatic fade out after 3 seconds
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}
