<?php $pageTitle = 'Plan de salle'; ?>
<div class="page-header">
    <h2>Plan de salle</h2>
    <div class="page-actions">
        <form method="GET" action="/admin/tables" class="inline-form">
            <input type="date" name="date" value="<?= $date ?>" class="form-control form-control-sm" onchange="this.form.submit()">
        </form>
        <button class="btn btn-primary" onclick="document.getElementById('addTableModal').classList.add('show')">+ Ajouter table</button>
    </div>
</div>

<div class="floorplan-legend">
    <span class="legend-item"><span class="legend-dot" style="background:#27ae60"></span> Libre</span>
    <span class="legend-item"><span class="legend-dot" style="background:#f39c12"></span> Reservee</span>
    <span class="legend-item"><span class="legend-dot" style="background:#e74c3c"></span> Occupee</span>
    <span class="legend-item"><span class="legend-dot" style="background:#95a5a6"></span> Maintenance</span>
</div>

<div class="floorplan-grid">
    <?php foreach ($tables as $t): ?>
        <div class="table-card table-<?= $t['shape'] ?> table-<?= $t['status'] ?>" data-id="<?= $t['id'] ?>" data-status="<?= $t['status'] ?>">
            <div class="table-number"><?= $t['number'] ?></div>
            <div class="table-capacity"><?= $t['capacity'] ?> pers.</div>
            <div class="table-zone"><?= ucfirst($t['zone']) ?></div>
            <?php if ($t['display_status'] === 'reserved' && isset($t['customer_name'])): ?>
                <div class="table-info">
                    <small><?= htmlspecialchars($t['customer_name']) ?></small>
                    <small><?= substr($t['reservation_time'], 0, 5) ?></small>
                </div>
            <?php endif; ?>
            <div class="table-status-badge badge badge-<?= $t['status'] ?>"><?php $statusLabels = ['free'=>'Libre','reserved'=>'Reservee','occupied'=>'Occupee','maintenance'=>'Maintenance']; echo $statusLabels[$t['status']] ?? $t['status']; ?></div>
        </div>
    <?php endforeach; ?>
</div>

<div class="modal" id="addTableModal">
    <div class="modal-content modal-sm">
        <div class="modal-header"><h3>Ajouter une table</h3><button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button></div>
        <form method="POST" action="/admin/tables">
            <?= csrf_field() ?>
            <div class="form-row">
                <div class="form-col-2"><label>Numero *</label><input type="number" name="number" required min="1" class="form-control"></div>
                <div class="form-col-2"><label>Capacite *</label><input type="number" name="capacity" required min="1" max="20" class="form-control" value="4"></div>
            </div>
            <div class="form-row">
                <div class="form-col-2"><label>Forme</label>
                    <select name="shape" class="form-control"><option value="square">Carree</option><option value="round">Ronde</option><option value="rectangle">Rectangulaire</option></select>
                </div>
                <div class="form-col-2"><label>Zone</label>
                    <select name="zone" class="form-control"><option value="salle">Salle</option><option value="terrasse">Terrasse</option><option value="bar">Bar</option></select>
                </div>
            </div>
            <div class="form-group"><label>Nom (optionnel)</label><input type="text" name="name" class="form-control" maxlength="50"></div>
            <button type="submit" class="btn btn-primary btn-block">Ajouter</button>
        </form>
    </div>
</div>
