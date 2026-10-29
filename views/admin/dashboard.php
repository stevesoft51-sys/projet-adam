<?php $pageTitle = 'Dashboard'; ?>

<div class="stats-grid">
    <div class="stat-card stat-primary">
        <div class="stat-icon"><i data-lucide="shopping-cart"></i></div>
        <div class="stat-body">
            <h3><?= number_format($todayOrders) ?></h3>
            <p>Commandes aujourd'hui</p>
        </div>
    </div>
    <div class="stat-card stat-success">
        <div class="stat-icon"><i data-lucide="wallet"></i></div>
        <div class="stat-body">
            <h3><?= View::money($todayRevenue) ?></h3>
            <p>Chiffre d'affaires</p>
        </div>
    </div>
    <div class="stat-card stat-info">
        <div class="stat-icon"><i data-lucide="calendar"></i></div>
        <div class="stat-body">
            <h3><?= number_format($todayReservations) ?></h3>
            <p>Réservations du jour</p>
        </div>
    </div>
    <div class="stat-card stat-warning">
        <div class="stat-icon"><i data-lucide="package"></i></div>
        <div class="stat-body">
            <h3><?= number_format($lowStockCount) ?></h3>
            <p>Alertes stock bas</p>
        </div>
    </div>
</div>

<div class="dashboard-grid">
    <div class="card">
        <div class="card-header">
            <h2>Commandes actives</h2>
            <a href="/admin/orders/pos" class="btn btn-sm btn-primary">Nouvelle commande</a>
        </div>
        <div class="card-body">
            <?php if (empty($activeOrders)): ?>
                <p class="text-muted">Aucune commande active</p>
            <?php else: ?>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr><th>#</th><th>Table</th><th>Serveur</th><th>Total</th><th>Statut</th><th>Action</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($activeOrders as $order): ?>
                                <tr>
                                    <td><?= htmlspecialchars($order['order_number']) ?></td>
                                    <td><?= $order['table_number'] ? 'T'.$order['table_number'] : 'A emporter' ?></td>
                                    <td><?= htmlspecialchars($order['server_name']) ?></td>
                                    <td><?= View::money($order['total']) ?></td>
                                    <td><span class="badge badge-<?= $order['status'] ?>"><?php $sl = ['pending'=>'En attente','confirmed'=>'Confirmee','preparing'=>'En preparation','ready'=>'Prete','served'=>'Servie']; echo $sl[$order['status']] ?? $order['status']; ?></span></td>
                                    <td>
                                        <?php if ($order['status']==='confirmed'): ?><button class="btn btn-xs btn-warning update-order-status" data-id="<?=$order['id']?>" data-status="preparing">Preparer</button>
                                        <?php elseif ($order['status']==='preparing'): ?><button class="btn btn-xs btn-success update-order-status" data-id="<?=$order['id']?>" data-status="ready">Prete</button>
                                        <?php elseif ($order['status']==='ready'): ?><button class="btn btn-xs btn-info update-order-status" data-id="<?=$order['id']?>" data-status="served">Servie</button><?php endif; ?>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <h2>Reservations a venir</h2>
            <a href="/admin/reservations" class="btn btn-sm btn-outline">Voir tout</a>
        </div>
        <div class="card-body">
            <?php if (empty($upcomingReservations)): ?>
                <p class="text-muted">Aucune reservation</p>
            <?php else: ?>
                <?php foreach (array_slice($upcomingReservations, 0, 6) as $res): ?>
                    <div class="reservation-item">
                        <div class="reservation-info">
                            <strong><?= htmlspecialchars($res['customer_name']) ?></strong>
                            <span class="text-muted"><?= View::date($res['date']) ?> <?= substr($res['time'],0,5) ?></span>
                        </div>
                        <div class="reservation-meta">
                            <span><?= $res['guests'] ?> pers.</span>
                            <?php if ($res['table_number']): ?><span>T<?= $res['table_number'] ?></span><?php endif; ?>
                        </div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
    </div>

    <?php if ($lowStockCount > 0): ?>
    <div class="card card-warning">
        <div class="card-header"><h2>Stock bas</h2></div>
        <div class="card-body">
            <?php foreach ($lowStockItems as $item): ?>
                <div class="stock-alert-item">
                    <span><?= htmlspecialchars($item['name']) ?></span>
                    <span class="stock-level"><?= number_format($item['current_stock'],1) ?> <?= $item['unit'] ?></span>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
    <?php endif; ?>

    <div class="card">
        <div class="card-header"><h2>Resume</h2></div>
        <div class="card-body">
            <div class="stats-inline">
                <div class="stat-mini"><span class="stat-mini-label">Semaine</span><span class="stat-mini-value"><?= View::money($weekRevenue) ?></span></div>
                <div class="stat-mini"><span class="stat-mini-label">Mois</span><span class="stat-mini-value"><?= View::money($monthRevenue) ?></span></div>
                <div class="stat-mini"><span class="stat-mini-label">Depenses</span><span class="stat-mini-value"><?= View::money($monthExpenses) ?></span></div>
                <div class="stat-mini"><span class="stat-mini-label">Fidelite</span><span class="stat-mini-value"><?= number_format($loyaltyCardCount) ?></span></div>
            </div>
        </div>
    </div>
</div>
