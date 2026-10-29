<?php $pageTitle = 'Programme de fidelite'; ?>
<div class="page-header"><h2>Fidelite</h2></div>
<div class="stats-grid">
    <div class="stat-card stat-primary"><div class="stat-body"><h3><?= number_format($totalCards) ?></h3><p>Cartes actives</p></div></div>
    <div class="stat-card stat-success"><div class="stat-body"><h3><?= number_format($totalPoints) ?></h3><p>Points totaux</p></div></div>
</div>
<div class="form-row">
    <div class="card" style="flex:1">
        <div class="card-header"><h3>Creer une carte</h3></div>
        <div class="card-body">
            <form method="POST" action="/admin/loyalty/card">
                <?= csrf_field() ?>
                <div class="form-group"><label>Nom du client *</label><input type="text" name="customer_name" required class="form-control"></div>
                <div class="form-group"><label>Telephone *</label><input type="text" name="customer_phone" required class="form-control"></div>
                <div class="form-group"><label>Email</label><input type="email" name="customer_email" class="form-control"></div>
                <button type="submit" class="btn btn-primary btn-block">Creer la carte</button>
            </form>
        </div>
    </div>
    <div class="card" style="flex:2">
        <div class="card-header"><h3>Top clients</h3></div>
        <div class="card-body">
            <table class="table">
                <thead><tr><th>Code</th><th>Client</th><th>Telephone</th><th>Points</th><th>Niveau</th><th>Total depense</th><th>Actions</th></tr></thead>
                <tbody>
                    <?php foreach ($cards as $c): ?>
                        <tr>
                            <td><code><?= htmlspecialchars($c['code']) ?></code></td>
                            <td><?= htmlspecialchars($c['customer_name']) ?></td>
                            <td><?= htmlspecialchars($c['customer_phone']) ?></td>
                            <td><strong><?= number_format($c['points']) ?></strong></td>
                            <td><span class="badge badge-<?= $c['tier'] ?>"><?= ucfirst($c['tier']) ?></span></td>
                            <td><?= View::money($c['total_spent']) ?></td>
                            <td>
                                <button class="btn btn-xs btn-outline" onclick="showAddPointsModal(<?= $c['id'] ?>, '<?= htmlspecialchars($c['customer_name']) ?>')">+ Points</button>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="modal" id="addPointsModal">
    <div class="modal-content modal-sm">
        <div class="modal-header"><h3 id="pointsModalTitle">Ajouter des points</h3><button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button></div>
        <form method="POST" action="/admin/loyalty/points">
            <?= csrf_field() ?>
            <input type="hidden" name="card_id" id="points_card_id">
            <div class="form-group"><label>Points *</label><input type="number" name="points" required class="form-control" min="1"></div>
            <div class="form-group"><label>Type *</label>
                <select name="type" class="form-control"><option value="earned">Gagnes</option><option value="redeemed">Utilises</option><option value="adjustment">Ajustement</option></select>
            </div>
            <div class="form-group"><label>Description</label><input type="text" name="description" class="form-control"></div>
            <button type="submit" class="btn btn-primary btn-block">Enregistrer</button>
        </form>
    </div>
</div>

<script>
function showAddPointsModal(cardId, name) {
    document.getElementById('points_card_id').value = cardId;
    document.getElementById('pointsModalTitle').textContent = 'Points pour ' + name;
    document.getElementById('addPointsModal').classList.add('show');
}
</script>
