<?php $pageTitle = 'Rapport des ventes'; ?>
<div class="page-header">
    <h2>Ventes</h2>
    <div class="page-actions">
        <form method="GET" class="inline-form">
            <input type="date" name="from" value="<?= $from ?>" class="form-control form-control-sm">
            <input type="date" name="to" value="<?= $to ?>" class="form-control form-control-sm">
            <button type="submit" class="btn btn-sm btn-primary">Filtrer</button>
        </form>
        <a href="/admin/reports/export?from=<?= $from ?>&to=<?= $to ?>" class="btn btn-sm btn-outline">Exporter CSV</a>
    </div>
</div>
<div class="stats-grid">
    <div class="stat-card stat-success"><div class="stat-body"><h3><?= View::money($totalSales) ?></h3><p>Ventes totales</p></div></div>
    <div class="stat-card stat-primary"><div class="stat-body"><h3><?= number_format($totalOrders) ?></h3><p>Commandes payees</p></div></div>
    <div class="stat-card stat-info"><div class="stat-body"><h3><?= View::money($avgOrder) ?></h3><p>Panier moyen</p></div></div>
</div>

<div class="form-row">
    <div class="card" style="flex:2">
        <div class="card-header"><h3>Ventes par jour</h3></div>
        <div class="card-body">
            <?php if (empty($salesByDay)): ?>
                <p class="text-muted">Aucune donnee</p>
            <?php else: ?>
                <div class="chart-bars">
                    <?php $maxAmount = max(array_column($salesByDay, 'amount')); ?>
                    <?php foreach ($salesByDay as $day): ?>
                        <div class="chart-bar-item">
                            <div class="chart-bar" style="height: <?= $maxAmount > 0 ? ($day['amount'] / $maxAmount * 100) : 0 ?>%"></div>
                            <div class="chart-bar-label"><?= date('d/m', strtotime($day['date'])) ?></div>
                            <div class="chart-bar-value"><?= View::money($day['amount']) ?></div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
    </div>
    <div class="card" style="flex:1">
        <div class="card-header"><h3>Par categorie</h3></div>
        <div class="card-body">
            <?php foreach ($salesByCategory as $cat): ?>
                <div class="report-row">
                    <span><?= htmlspecialchars($cat['category']) ?></span>
                    <span><strong><?= View::money($cat['amount']) ?></strong> (<?= $cat['orders'] ?> cmd)</span>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</div>

<div class="form-row">
    <div class="card" style="flex:1">
        <div class="card-header"><h3>Top 10 plats</h3></div>
        <div class="card-body">
            <table class="table">
                <thead><tr><th>Plat</th><th>Qte vendue</th><th>Revenue</th></tr></thead>
                <tbody>
                    <?php foreach ($topProducts as $tp): ?>
                        <tr><td><?= htmlspecialchars($tp['name']) ?></td><td><?= $tp['qty'] ?></td><td><?= View::money($tp['revenue']) ?></td></tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
    <div class="card" style="flex:1">
        <div class="card-header"><h3>Paiements</h3></div>
        <div class="card-body">
            <?php foreach ($payments as $p): ?>
                <div class="report-row">
                    <span><?php $methodLabels = ['cash'=>'Especes','mobile_money'=>'Mobile Money','card'=>'Carte']; echo $methodLabels[$p['method']] ?? $p['method']; ?></span>
                    <span><strong><?= View::money($p['total']) ?></strong> (<?= $p['count'] ?> tx)</span>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</div>
