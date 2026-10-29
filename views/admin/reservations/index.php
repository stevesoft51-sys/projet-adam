<?php $pageTitle = 'Reservations'; ?>
<div class="page-header">
    <h2>Reservations</h2>
    <button class="btn btn-primary" onclick="document.getElementById('addResModal').classList.add('show')">+ Nouvelle reservation</button>
</div>
<div class="card">
    <div class="card-header">
        <h3>Reservations du <?= View::date($date) ?></h3>
        <form method="GET" class="inline-form">
            <input type="date" name="date" value="<?= $date ?>" class="form-control form-control-sm" onchange="this.form.submit()">
        </form>
    </div>
    <div class="card-body">
        <?php if (empty($reservations)): ?>
            <p class="text-muted">Aucune reservation pour cette date</p>
        <?php else: ?>
            <table class="table">
                <thead><tr><th>Code</th><th>Client</th><th>Telephone</th><th>Heure</th><th>Personnes</th><th>Table</th><th>Statut</th><th>Actions</th></tr></thead>
                <tbody>
                    <?php foreach ($reservations as $r): ?>
                        <tr>
                            <td><code><?= htmlspecialchars($r['code']) ?></code></td>
                            <td><strong><?= htmlspecialchars($r['customer_name']) ?></strong></td>
                            <td><?= htmlspecialchars($r['customer_phone']) ?></td>
                            <td><?= substr($r['time'], 0, 5) ?></td>
                            <td><?= $r['guests'] ?></td>
                            <td><?= $r['table_number'] ? 'T'.$r['table_number'] : '-' ?></td>
                            <td><span class="badge badge-<?= $r['status'] ?>"><?php $statusLabels = ['pending'=>'En attente','confirmed'=>'Confirmee','seated'=>'Installee','completed'=>'Terminee','cancelled'=>'Annulee','no_show'=>'Absent']; echo $statusLabels[$r['status']] ?? $r['status']; ?></span></td>
                            <td>
                                <div class="btn-group">
                                    <?php if ($r['status'] === 'confirmed'): ?>
                                        <button class="btn btn-xs btn-info update-res-status" data-id="<?= $r['id'] ?>" data-status="seated">Installer</button>
                                    <?php endif; ?>
                                    <?php if (in_array($r['status'], ['pending','confirmed'])): ?>
                                        <button class="btn btn-xs btn-success update-res-status" data-id="<?= $r['id'] ?>" data-status="completed">Terminer</button>
                                        <button class="btn btn-xs btn-danger update-res-status" data-id="<?= $r['id'] ?>" data-status="cancelled">Annuler</button>
                                    <?php endif; ?>
                                </div>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>
</div>

<div class="modal" id="addResModal">
    <div class="modal-content">
        <div class="modal-header"><h3>Nouvelle reservation</h3><button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button></div>
        <form method="POST" action="/admin/reservations">
            <?= csrf_field() ?>
            <div class="form-row">
                <div class="form-col-2"><label>Nom du client *</label><input type="text" name="customer_name" required class="form-control"></div>
                <div class="form-col-2"><label>Telephone *</label><input type="text" name="customer_phone" required class="form-control"></div>
            </div>
            <div class="form-group"><label>Email</label><input type="email" name="customer_email" class="form-control"></div>
            <div class="form-row">
                <div class="form-col-2"><label>Date *</label><input type="date" name="date" required class="form-control" value="<?= $date ?>"></div>
                <div class="form-col-2"><label>Heure *</label><input type="time" name="time" required class="form-control"></div>
            </div>
            <div class="form-row">
                <div class="form-col-2"><label>Personnes *</label><input type="number" name="guests" min="1" max="20" required class="form-control" value="2"></div>
                <div class="form-col-2"><label>Table (optionnel)</label>
                    <select name="table_id" class="form-control"><option value="">Auto-assigner</option>
                        <?php foreach ((new RestaurantTableModel())->getAvailable() as $t): ?>
                            <option value="<?= $t['id'] ?>">Table <?= $t['number'] ?> (<?= $t['capacity'] ?> pers.)</option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>
            <div class="form-group"><label>Notes</label><textarea name="notes" class="form-control" rows="2"></textarea></div>
            <button type="submit" class="btn btn-primary btn-block">Creer la reservation</button>
        </form>
    </div>
</div>
