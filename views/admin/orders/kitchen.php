<?php $pageTitle = 'Cuisine'; ?>
<div class="page-header">
    <h2>Commandes cuisine</h2>
    <a href="/admin/orders" class="btn btn-outline">Retour</a>
</div>
<div class="kitchen-grid" id="kitchenGrid">
    <?php if (empty($orders)): ?>
        <p class="text-muted" style="grid-column:1/-1">Aucune commande en cours</p>
    <?php else: ?>
        <?php foreach ($orders as $o): ?>
            <div class="kitchen-card kitchen-<?= $o['status'] ?>" id="kitchen-order-<?= $o['id'] ?>">
                <div class="kitchen-card-header">
                    <span class="kitchen-order-num"><?= $o['order_number'] ?></span>
                    <span class="kitchen-table"><?= $o['table_number'] ? 'T'.$o['table_number'] : 'Emporter' ?></span>
                </div>
                <div class="kitchen-card-time"><?= View::timeAgo($o['created_at']) ?></div>
                <div class="kitchen-items">
                    <?php
                    $items = Database::getInstance()->query(
                        "SELECT oi.*, p.name as product_name FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ? AND oi.status != 'cancelled'",
                        [$o['id']]
                    )->fetchAll();
                    foreach ($items as $item):
                    ?>
                        <div class="kitchen-item <?= $item['status'] === 'ready' ? 'kitchen-item-ready' : '' ?>">
                            <span class="kitchen-item-qty"><?= $item['quantity'] ?>x</span>
                            <span class="kitchen-item-name"><?= htmlspecialchars($item['product_name']) ?></span>
                            <?php if ($item['notes']): ?><small class="kitchen-item-notes"><?= htmlspecialchars($item['notes']) ?></small><?php endif; ?>
                        </div>
                    <?php endforeach; ?>
                </div>
                <div class="kitchen-card-actions">
                    <?php if ($o['status'] === 'confirmed'): ?>
                        <button class="btn btn-warning btn-block update-order-status" data-id="<?= $o['id'] ?>" data-status="preparing">Commencer la preparation</button>
                    <?php elseif ($o['status'] === 'preparing'): ?>
                        <button class="btn btn-success btn-block update-order-status" data-id="<?= $o['id'] ?>" data-status="ready">Marquer comme prete</button>
                    <?php endif; ?>
                </div>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>
</div>
