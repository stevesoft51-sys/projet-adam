<?php $pageTitle = 'Analyses'; ?>
<div class="page-header"><h2>Analyses & Statistiques</h2></div>
<div class="form-row">
    <div class="card" style="flex:1">
        <div class="card-header"><h3>Heures de pointe</h3></div>
        <div class="card-body">
            <?php if (empty($peakHours)): ?>
                <p class="text-muted">Aucune donnee</p>
            <?php else: ?>
                <?php $maxPeak = max(array_column($peakHours, 'count')); ?>
                <?php foreach ($peakHours as $ph): ?>
                    <div class="report-row">
                        <span><?= str_pad($ph['hour'], 2, '0', STR_PAD_LEFT) ?>h</span>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: <?= ($ph['count'] / $maxPeak * 100) ?>%"></div>
                        </div>
                        <span><?= $ph['count'] ?> cmd</span>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
    </div>
    <div class="card" style="flex:1">
        <div class="card-header"><h3>Sur place vs Emporter</h3></div>
        <div class="card-body">
            <?php foreach ($diningVsTakeaway as $dvt): ?>
                <div class="report-row">
                    <span><?= $dvt['type'] === 'dine_in' ? 'Sur place' : 'A emporter' ?></span>
                    <span><strong><?= View::money($dvt['revenue']) ?></strong> (<?= $dvt['count'] ?> cmd)</span>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</div>
<div class="card">
    <div class="card-header"><h3>Depenses par categorie (mois)</h3></div>
    <div class="card-body">
        <?php if (empty($expenses)): ?>
            <p class="text-muted">Aucune depense enregistree</p>
        <?php else: ?>
            <?php foreach ($expenses as $e): ?>
                <div class="report-row">
                    <span><?= htmlspecialchars($e['category']) ?></span>
                    <span><strong><?= View::money($e['total']) ?></strong> (<?= $e['count'] ?>)</span>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
</div>
