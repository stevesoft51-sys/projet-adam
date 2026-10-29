<?php $pageTitle = 'Caisse'; ?>
<div class="page-header"><h2>Gestion de la caisse</h2></div>
<?php if (!$openRegister): ?>
    <div class="card card-warning">
        <div class="card-body" style="text-align:center;padding:3rem">
            <h3>Aucune caisse ouverte</h3>
            <p class="text-muted">Ouvrez une caisse pour commencer les encaissements</p>
            <form method="POST" action="/admin/cash/open" style="max-width:300px;margin:1rem auto">
                <?= csrf_field() ?>
                <div class="form-group"><label>Montant d'ouverture (FCFA)</label><input type="number" name="opening_amount" min="0" step="50" required class="form-control" value="0"></div>
                <div class="form-group"><label>Notes</label><textarea name="notes" class="form-control" rows="2"></textarea></div>
                <button type="submit" class="btn btn-primary btn-lg btn-block">Ouvrir la caisse</button>
            </form>
        </div>
    </div>
<?php else: ?>
    <div class="stats-grid">
        <div class="stat-card stat-primary"><div class="stat-body"><h3><?= View::money($openRegister['opening_amount']) ?></h3><p>Ouverture</p></div></div>
        <div class="stat-card stat-success"><div class="stat-body"><h3><?= View::money($openRegister['total_cash_in']) ?></h3><p>Entrees</p></div></div>
        <div class="stat-card stat-danger"><div class="stat-body"><h3><?= View::money($openRegister['total_cash_out']) ?></h3><p>Sorties</p></div></div>
        <div class="stat-card stat-info"><div class="stat-body"><h3><?= View::money($openRegister['opening_amount'] + $openRegister['total_cash_in'] - $openRegister['total_cash_out']) ?></h3><p>Solde actuel</p></div></div>
    </div>

    <div class="form-row">
        <div class="card" style="flex:1">
            <div class="card-header"><h3>Mouvement de caisse</h3></div>
            <div class="card-body">
                <form method="POST" action="/admin/cash/movement">
                    <?= csrf_field() ?>
                    <div class="form-row">
                        <div class="form-col-2"><label>Type *</label>
                            <select name="type" class="form-control"><option value="in">Entree</option><option value="out">Sortie</option></select>
                        </div>
                        <div class="form-col-2"><label>Montant *</label><input type="number" name="amount" min="0" step="50" required class="form-control"></div>
                    </div>
                    <div class="form-group"><label>Raison *</label><input type="text" name="reason" required class="form-control" maxlength="255"></div>
                    <button type="submit" class="btn btn-primary">Enregistrer</button>
                </form>
            </div>
        </div>
        <div class="card" style="flex:2">
            <div class="card-header">
                <h3>Mouvements d'aujourd'hui</h3>
                <form method="POST" action="/admin/cash/close" class="inline-form" onsubmit="return confirm('Fermer la caisse ?')">
                    <?= csrf_field() ?>
                    <input type="hidden" name="id" value="<?= $openRegister['id'] ?>">
                    <input type="number" name="closing_amount" step="50" min="0" required class="form-control form-control-sm" style="width:150px;display:inline-block" placeholder="Montant final">
                    <button type="submit" class="btn btn-warning">Fermer la caisse</button>
                </form>
            </div>
            <div class="card-body">
                <?php if (empty($movements)): ?>
                    <p class="text-muted">Aucun mouvement</p>
                <?php else: ?>
                    <table class="table">
                        <thead><tr><th>Heure</th><th>Type</th><th>Montant</th><th>Raison</th><th>Par</th></tr></thead>
                        <tbody>
                            <?php foreach ($movements as $m): ?>
                                <tr>
                                    <td><?= date('H:i', strtotime($m['created_at'])) ?></td>
                                    <td><span class="badge badge-<?= $m['type']==='in'?'success':'danger' ?>"><?= $m['type']==='in'?'Entree':'Sortie' ?></span></td>
                                    <td><?= View::money($m['amount']) ?></td>
                                    <td><?= htmlspecialchars($m['reason']) ?></td>
                                    <td><?= htmlspecialchars($m['creator_name']) ?></td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                <?php endif; ?>
            </div>
        </div>
    </div>
<?php endif; ?>
