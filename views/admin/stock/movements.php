<?php $pageTitle = 'Mouvements de stock'; ?>
<div class="page-header"><h2>Mouvements de stock</h2></div>
<div class="form-row">
    <div class="card" style="flex:1">
        <div class="card-header"><h3>Nouveau mouvement</h3></div>
        <div class="card-body">
            <form method="POST" action="/admin/stock/movement">
                <?= csrf_field() ?>
                <div class="form-group"><label>Ingredient *</label>
                    <select name="ingredient_id" required class="form-control">
                        <option value="">Choisir...</option>
                        <?php foreach ($ingredients as $ing): ?>
                            <option value="<?= $ing['id'] ?>"><?= htmlspecialchars($ing['name']) ?> (<?= $ing['current_stock'] ?> <?= $ing['unit'] ?>)</option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <div class="form-row">
                    <div class="form-col-2"><label>Type *</label>
                        <select name="type" required class="form-control"><option value="in">Entree</option><option value="out">Sortie</option><option value="adjust">Ajustement</option></select>
                    </div>
                    <div class="form-col-2"><label>Quantite *</label><input type="number" name="quantity" step="0.1" min="0" required class="form-control"></div>
                </div>
                <div class="form-group"><label>Raison *</label><input type="text" name="reason" required class="form-control" maxlength="255" placeholder="Ex: Reception commande fournisseur"></div>
                <button type="submit" class="btn btn-primary">Enregistrer</button>
            </form>
        </div>
    </div>
    <div class="card" style="flex:2">
        <div class="card-header"><h3>Historique</h3></div>
        <div class="card-body">
            <table class="table">
                <thead><tr><th>Date</th><th>Ingredient</th><th>Type</th><th>Quantite</th><th>Raison</th><th>Par</th></tr></thead>
                <tbody>
                    <?php foreach ($movements as $m): ?>
                        <tr>
                            <td><?= View::datetime($m['created_at']) ?></td>
                            <td><?= htmlspecialchars($m['ingredient_name']) ?></td>
                            <td><span class="badge badge-<?= $m['type']==='in'?'success':($m['type']==='out'?'danger':'info') ?>"><?= $m['type']==='in'?'Entree':($m['type']==='out'?'Sortie':'Ajustement') ?></span></td>
                            <td><?= $m['type']==='adjust'?'=':($m['type']==='in'?'+':'-') ?> <?= number_format($m['quantity'], 1) ?> <?= $m['unit'] ?></td>
                            <td><?= htmlspecialchars($m['reason']) ?></td>
                            <td><?= htmlspecialchars($m['creator_name']) ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
