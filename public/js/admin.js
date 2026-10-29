/* ============================================
   RESTAURANT ADAM - Admin JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {

    // ---- Sidebar Toggle ----
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    }
    if (sidebarClose) {
        sidebarClose.addEventListener('click', () => sidebar.classList.remove('open'));
    }

    // Close sidebar on outside click (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('open') 
            && !sidebar.contains(e.target) && e.target !== sidebarToggle) {
            sidebar.classList.remove('open');
        }
    });

    // ---- Auto-close alerts ----
    autoCloseAlerts();

    // ---- Order status update ----
    document.querySelectorAll('.update-order-status').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.id;
            const status = this.dataset.status;
            const form = new FormData();
            form.append('id', id);
            form.append('status', status);
            form.append('_token', getCsrfToken());

            fetch('/admin/orders/update-status', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: form
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.error || 'Erreur lors de la mise a jour');
                }
            })
            .catch(() => location.reload());
        });
    });

    // ---- Reservation status update ----
    document.querySelectorAll('.update-res-status').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.id;
            const status = this.dataset.status;
            const form = new FormData();
            form.append('id', id);
            form.append('status', status);
            form.append('_token', getCsrfToken());

            fetch('/admin/reservations/status', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: form
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) location.reload();
                else alert(data.error || 'Erreur');
            })
            .catch(() => location.reload());
        });
    });

    // ---- Table status update ----
    document.querySelectorAll('.table-card').forEach(card => {
        card.addEventListener('click', function() {
            const id = this.dataset.id;
            const statuses = ['free', 'reserved', 'occupied', 'maintenance'];
            const currentStatus = this.dataset.status;
            const currentIdx = statuses.indexOf(currentStatus);
            const newStatus = statuses[(currentIdx + 1) % statuses.length];

            const form = new FormData();
            form.append('id', id);
            form.append('status', newStatus);
            form.append('_token', getCsrfToken());

            fetch('/admin/tables/status', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: form
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) location.reload();
            });
        });
    });

    // ---- Product toggle ----
    window.toggleProduct = function(btn) {
        const id = btn.dataset.id;
        const form = new FormData();
        form.append('id', id);
        form.append('_token', getCsrfToken());

        fetch('/admin/menu/toggle', {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: form
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                btn.classList.toggle('active');
            }
        });
    };

    // ---- Payment modal ----
    document.querySelectorAll('.show-payment-modal').forEach(btn => {
        btn.addEventListener('click', function() {
            document.getElementById('payment_order_id').value = this.dataset.id;
            document.getElementById('payment_amount').value = this.dataset.total;
            document.getElementById('paymentModal').classList.add('show');
        });
    });

    // ---- POS Functions ----
    window.posOrderItems = [];

    window.addToOrder = function(card) {
        const id = parseInt(card.dataset.id);
        const price = parseFloat(card.dataset.price);
        const name = card.dataset.nameDisplay;

        const existing = posOrderItems.find(item => item.id === id);
        if (existing) {
            existing.qty++;
        } else {
            posOrderItems.push({ id, name, price, qty: 1, notes: '' });
        }
        renderOrder();
    };

    window.updateQty = function(id, delta) {
        const item = posOrderItems.find(i => i.id === id);
        if (item) {
            item.qty += delta;
            if (item.qty <= 0) {
                posOrderItems = posOrderItems.filter(i => i.id !== id);
            }
        }
        renderOrder();
    };

    window.removeOrderItem = function(id) {
        posOrderItems = posOrderItems.filter(i => i.id !== id);
        renderOrder();
    };

    window.clearOrder = function() {
        posOrderItems = [];
        renderOrder();
    };

    function renderOrder() {
        const container = document.getElementById('posOrderItems');
        const emptyMsg = document.getElementById('posEmptyMsg');
        const submitBtn = document.getElementById('posSubmitBtn');

        if (!container) return;

        if (posOrderItems.length === 0) {
            container.innerHTML = '<p class="text-muted" id="posEmptyMsg">Selectionnez des produits</p>';
            if (submitBtn) submitBtn.disabled = true;
            updateSummary(0);
            return;
        }

        if (submitBtn) submitBtn.disabled = false;

        let html = '';
        let subtotal = 0;

        posOrderItems.forEach(item => {
            const total = item.price * item.qty;
            subtotal += total;
            html += `
                <div class="pos-order-item">
                    <div class="pos-order-item-name">${item.name}</div>
                    <div class="pos-order-item-qty">
                        <button onclick="updateQty(${item.id}, -1)">-</button>
                        <span>${item.qty}</span>
                        <button onclick="updateQty(${item.id}, 1)">+</button>
                    </div>
                    <div class="pos-order-item-price">${formatMoney(total)}</div>
                    <button onclick="removeOrderItem(${item.id})" style="background:none;border:none;cursor:pointer;color:#e74c3c;font-size:1.1rem" title="Retirer">&times;</button>
                </div>
            `;
        });

        container.innerHTML = html;
        updateSummary(subtotal);
    }

    function updateSummary(subtotal) {
        const posContainer = document.querySelector('.pos-container');
        const taxRate = parseFloat(posContainer?.dataset?.taxRate || 18) / 100;
        const tax = subtotal * taxRate;
        const total = subtotal + tax;
        const subEl = document.getElementById('posSubtotal');
        const taxEl = document.getElementById('posTax');
        const totalEl = document.getElementById('posTotal');
        if (subEl) subEl.textContent = formatMoney(subtotal);
        if (taxEl) taxEl.textContent = formatMoney(tax);
        if (totalEl) totalEl.textContent = formatMoney(total);
    }

    window.submitOrder = function() {
        if (posOrderItems.length === 0) return;

        const form = new FormData();
        form.append('items', JSON.stringify(posOrderItems.map(item => ({
            product_id: item.id,
            quantity: item.qty,
            unit_price: item.price,
            notes: item.notes
        }))));
        form.append('table_id', document.getElementById('posTable')?.value || '');
        form.append('order_type', document.getElementById('posTable')?.value ? 'dine_in' : 'takeaway');
        form.append('notes', document.getElementById('posNotes')?.value || '');
        form.append('_token', getCsrfToken());

        fetch('/admin/orders/create', {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: form
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                posOrderItems = [];
                renderOrder();
                location.reload();
            } else {
                alert(data.error || 'Erreur lors de la creation');
            }
        })
        .catch(err => {
            console.error(err);
            alert('Erreur de connexion');
        });
    };

    // ---- POS Search ----
    const posSearch = document.getElementById('posSearch');
    if (posSearch) {
        posSearch.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            document.querySelectorAll('.pos-product-card').forEach(card => {
                const name = card.dataset.name || '';
                card.style.display = name.includes(query) ? '' : 'none';
            });
        });
    }

    // ---- POS Category filter ----
    document.querySelectorAll('.pos-cat-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.pos-cat-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const cat = this.dataset.cat;
            document.querySelectorAll('.pos-product-card').forEach(card => {
                if (cat === 'all' || card.dataset.cat === cat) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // ---- Menu category filter (client) ----
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const filter = this.dataset.filter;
            document.querySelectorAll('.menu-category-section').forEach(section => {
                if (filter === 'all' || section.dataset.category === filter) {
                    section.style.display = '';
                } else {
                    section.style.display = 'none';
                }
            });
        });
    });

    // ---- Ingredient rows ----
    window.addIngredientRow = function() {
        const list = document.getElementById('ingredients-list');
        if (!list) return;
        const firstRow = list.querySelector('.ingredient-row');
        if (!firstRow) return;
        const newRow = firstRow.cloneNode(true);
        newRow.querySelectorAll('input, select').forEach(el => {
            if (el.tagName === 'SELECT') el.selectedIndex = 0;
            else el.value = '';
        });
        list.appendChild(newRow);
    };

    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-ingredient')) {
            const row = e.target.closest('.ingredient-row');
            const list = document.getElementById('ingredients-list');
            if (list && list.children.length > 1) {
                row.remove();
            }
        }
    });

    // ---- Payment method toggle ----
    window.togglePhoneField = function() {
        const method = document.getElementById('payment_method');
        const phoneGroup = document.getElementById('phone_group');
        if (method && phoneGroup) {
            phoneGroup.style.display = method.value === 'mobile_money' ? 'block' : 'none';
        }
    };

    // ---- Modals ----
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').classList.remove('show');
        });
    });

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) this.classList.remove('show');
        });
    });
});

// ---- Helpers ----
function getCsrfToken() {
    const tokenInput = document.querySelector('input[name="_token"]');
    if (tokenInput) return tokenInput.value;
    // Fallback: read from meta tag or cookie
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;
    // Fallback: extract from any CSRF form on the page
    const allInputs = document.querySelectorAll('input[name="_token"]');
    if (allInputs.length > 0) return allInputs[0].value;
    return '';
}

// ---- Kitchen auto-refresh ----
(function() {
    const kitchenContainer = document.querySelector('.admin-content');
    if (kitchenContainer && window.location.pathname === '/admin/orders/kitchen') {
        let lastHTML = kitchenContainer.innerHTML;
        setInterval(function() {
            fetch('/admin/orders/kitchen', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(r => r.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newContent = doc.querySelector('.admin-content')?.innerHTML || '';
                    if (newContent !== lastHTML) {
                        lastHTML = newContent;
                        kitchenContainer.innerHTML = newContent;
                        // Re-bind event listeners
                        if (typeof autoCloseAlerts === 'function') autoCloseAlerts();
                    }
                })
                .catch(() => {});
        }, 15000);
    }
})();

// ---- Dashboard auto-refresh ----
(function() {
    const dashContent = document.querySelector('.admin-content');
    if (dashContent && (window.location.pathname === '/admin/dashboard' || window.location.pathname === '/admin')) {
        let lastHTML = dashContent.innerHTML;
        setInterval(function() {
            fetch(window.location.pathname, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(r => r.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newContent = doc.querySelector('.admin-content')?.innerHTML || '';
                    if (newContent !== lastHTML) {
                        lastHTML = newContent;
                        dashContent.innerHTML = newContent;
                        if (typeof autoCloseAlerts === 'function') autoCloseAlerts();
                    }
                })
                .catch(() => {});
        }, 30000);
    }
})();

function formatMoney(amount) {
    return new Intl.NumberFormat('fr-FR').format(Math.round(amount)) + ' FCFA';
}

function autoCloseAlerts() {
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}
