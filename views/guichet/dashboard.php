<?php $pageTitle = 'Tableau de bord'; ?>

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
            <p>Recettes du jour</p>
        </div>
    </div>
    <div class="stat-card stat-info">
        <div class="stat-icon"><i data-lucide="banknote"></i></div>
        <div class="stat-body">
            <h3><?= View::money($todayPaymentsCash) ?></h3>
            <p>Especes</p>
        </div>
    </div>
    <div class="stat-card stat-warning">
        <div class="stat-icon"><i data-lucide="smartphone"></i></div>
        <div class="stat-body">
            <h3><?= View::money($todayPaymentsMobile) ?></h3>
            <p>Mobile Money</p>
        </div>
    </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem">
    <div class="card">
        <div class="card-header">
            <h2>Commandes actives</h2>
            <a href="/guichet/pos" class="btn btn-sm btn-primary">Nouvelle commande</a>
        </div>
        <div class="card-body">
            <?php if (empty($activeOrders)): ?>
                <p class="text-muted">Aucune commande active</p>
            <?php else: ?>
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr><th>#</th><th>Table</th><th>Total</th><th>Statut</th><th>Action</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($activeOrders as $order): ?>
                                <tr>
                                    <td><?= htmlspecialchars($order['order_number']) ?></td>
                                    <td><?= $order['table_number'] ? 'T'.$order['table_number'] : 'A emporter' ?></td>
                                    <td><?= View::money($order['total']) ?></td>
                                    <td><span class="badge badge-<?= $order['status'] ?>"><?php
                                        $sl = ['pending'=>'En attente','confirmed'=>'Confirmee','preparing'=>'En preparation','ready'=>'Prete','served'=>'Servie'];
                                        echo $sl[$order['status']] ?? $order['status'];
                                    ?></span></td>
                                    <td>
                                        <?php if ($order['status'] === 'served'): ?>
                                            <a href="/guichet/bill?id=<?= $order['id'] ?>" class="btn btn-xs btn-success">Encaisser</a>
                                        <?php endif; ?>
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
            <h2>Dernieres commandes</h2>
            <a href="/guichet/factures" class="btn btn-sm btn-outline">Voir tout</a>
        </div>
        <div class="card-body">
            <?php if (empty($recentOrders)): ?>
                <p class="text-muted">Aucune commande</p>
            <?php else: ?>
                <div class="table-responsive">
                    <table class="table">
                        <thead><tr><th>#</th><th>Table</th><th>Total</th><th>Statut</th></tr></thead>
                        <tbody>
                            <?php foreach (array_slice($recentOrders, 0, 8) as $order): ?>
                                <tr>
                                    <td><a href="/guichet/bill?id=<?= $order['id'] ?>"><?= htmlspecialchars($order['order_number']) ?></a></td>
                                    <td><?= $order['table_number'] ? 'T'.$order['table_number'] : 'A emporter' ?></td>
                                    <td><?= View::money($order['total']) ?></td>
                                    <td><span class="badge badge-<?= $order['status'] ?>"><?= $order['status'] ?></span></td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>
