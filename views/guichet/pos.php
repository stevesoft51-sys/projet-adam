<?php $pageTitle = 'Point de Vente'; ?>
<div class="pos-container" data-tax-rate="<?= \SettingModel::getValue('tax_rate', 18) ?>">
    <div class="pos-products">
        <div class="pos-search">
            <input type="text" id="posSearch" class="form-control" placeholder="Rechercher un plat...">
        </div>
        <div class="pos-categories" id="posCategories">
            <button class="pos-cat-btn active" data-cat="all">Tout</button>
            <?php foreach ($categories as $cat): ?>
                <button class="pos-cat-btn" data-cat="<?= $cat['id'] ?>"><?= htmlspecialchars($cat['name']) ?></button>
            <?php endforeach; ?>
        </div>
        <div class="pos-products-grid" id="posProductsGrid">
            <?php foreach ($products as $p): ?>
                <div class="pos-product-card" data-cat="<?= $p['category_id'] ?>" data-name="<?= strtolower($p['name']) ?>" data-id="<?= $p['id'] ?>" data-price="<?= $p['price'] ?>" data-name-display="<?= htmlspecialchars($p['name']) ?>" onclick="addToOrder(this)">
                    <?php if ($p['image']): ?>
                        <img src="<?= htmlspecialchars($p['image']) ?>" alt="" class="pos-product-img">
                    <?php else: ?>
                        <div class="pos-product-img pos-placeholder"><i data-lucide="utensils"></i></div>
                    <?php endif; ?>
                    <div class="pos-product-name"><?= htmlspecialchars($p['name']) ?></div>
                    <div class="pos-product-price"><?= View::money($p['price']) ?></div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>

    <div class="pos-order">
        <div class="pos-order-header">
            <h3>Commande en cours</h3>
            <select id="posTable" class="form-control form-control-sm">
                <option value="">A emporter</option>
                <?php foreach ($tables as $t): ?>
                    <option value="<?= $t['id'] ?>">Table <?= $t['number'] ?> (<?= $t['capacity'] ?> pers.)</option>
                <?php endforeach; ?>
            </select>
        </div>
        <div class="pos-order-items" id="posOrderItems">
            <p class="text-muted" id="posEmptyMsg">Selectionnez des produits</p>
        </div>
        <div class="pos-order-summary">
            <div class="pos-summary-row"><span>Sous-total</span><span id="posSubtotal">0 FCFA</span></div>
            <div class="pos-summary-row"><span>Taxe (18%)</span><span id="posTax">0 FCFA</span></div>
            <div class="pos-summary-row pos-total"><span>TOTAL</span><span id="posTotal">0 FCFA</span></div>
        </div>
        <div class="pos-order-actions">
            <textarea id="posNotes" class="form-control" rows="2" placeholder="Notes..."></textarea>
            <div class="btn-group">
                <button class="btn btn-primary btn-lg" onclick="submitOrder()" id="posSubmitBtn" disabled>Valider</button>
                <button class="btn btn-outline" onclick="clearOrder()">Annuler</button>
            </div>
        </div>
    </div>

    <?php if ($cashRegister): ?>
        <div class="pos-cash-indicator"><span class="dot dot-green"></span> Caisse ouverte</div>
    <?php else: ?>
        <div class="pos-cash-indicator"><span class="dot dot-red"></span> Aucune caisse ouverte - <a href="/guichet/caisse">Ouvrir</a></div>
    <?php endif; ?>
</div>

<div class="pos-active-orders" id="posActiveOrders">
    <h4>Commandes en cours</h4>
    <div class="pos-active-list">
        <?php foreach ($activeOrders as $ao): ?>
            <div class="pos-active-item" data-order-id="<?= $ao['id'] ?>">
                <span class="pos-active-num"><?= $ao['order_number'] ?></span>
                <span class="pos-active-table"><?= $ao['table_number'] ? 'T'.$ao['table_number'] : 'Emporter' ?></span>
                <span class="badge badge-<?= $ao['status'] ?> badge-sm"><?= $ao['status'] ?></span>
            </div>
        <?php endforeach; ?>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const origSubmit = window.submitOrder;
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

        fetch('/guichet/orders/create', {
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
});
</script>
