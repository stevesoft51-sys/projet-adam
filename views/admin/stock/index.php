<?php $pageTitle = 'Gestion des stocks'; ?>
<div class="page-header">
    <h2>Stocks & Ingredients</h2>
    <div class="page-actions">
        <a href="/admin/stock/inventory" class="btn btn-outline">Inventaire</a>
        <a href="/admin/stock/movements" class="btn btn-outline">Mouvements</a>
    </div>
</div>
<?php if (!empty($lowStock)): ?>
<div class="alert alert-warning"><?= count($lowStock) ?> ingredient(s) en stock bas</div>
<?php endif; ?>
<div class="card">
    <div class="card-header">
        <h3>Ingredients</h3>
        <button class="btn btn-sm btn-primary" onclick="document.getElementById('addIngredientModal').classList.add('show')">+ Ajouter</button>
    </div>
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Nom</th><th>Stock</th><th>Seuil min</th><th>Unite</th><th>Cout unitaire</th><th>Fournisseur</th><th>Statut</th></tr></thead>
            <tbody>
                <?php foreach ($ingredients as $ing): ?>
                    <tr class="<?= $ing['current_stock'] <= $ing['min_stock'] && $ing['min_stock'] > 0 ? 'row-warning' : '' ?>">
                        <td><strong><?= htmlspecialchars($ing['name']) ?></strong></td>
                        <td><?= number_format($ing['current_stock'], 1) ?></td>
                        <td><?= number_format($ing['min_stock'], 1) ?></td>
                        <td><?= $ing['unit'] ?></td>
                        <td><?= View::money($ing['cost_per_unit']) ?></td>
                        <td><?= htmlspecialchars($ing['supplier'] ?? '-') ?></td>
                        <td>
                            <?php if ($ing['current_stock'] <= $ing['min_stock'] && $ing['min_stock'] > 0): ?>
                                <span class="badge badge-warning">Stock bas</span>
                            <?php else: ?>
                                <span class="badge badge-success">OK</span>
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>

<div class="modal" id="addIngredientModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Ajouter un ingredient</h3>
            <button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button>
        </div>
        <form method="POST" action="/admin/stock/movement">
            <?= csrf_field() ?>
            <input type="hidden" name="type" value="in">
            <div class="form-group"><label>Nom de l ingredient</label><input type="text" name="ingredient_name" class="form-control" required></div>
            <div class="form-row">
                <div class="form-col-2"><label>Quantite initiale</label><input type="number" name="quantity" step="0.1" min="0" class="form-control" required></div>
                <div class="form-col-2"><label>Unite</label>
                    <select name="unit" class="form-control"><option value="kg">kg</option><option value="L">L</option><option value="piece">Piece</option><option value="sachet">Sachet</option></select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-col-2"><label>Seuil minimum</label><input type="number" name="min_stock" step="0.1" min="0" class="form-control" value="0"></div>
                <div class="form-col-2"><label>Cout unitaire (FCFA)</label><input type="number" name="cost_per_unit" step="1" min="0" class="form-control" value="0"></div>
            </div>
            <div class="form-group"><label>Fournisseur</label><input type="text" name="supplier" class="form-control"></div>
            <div class="form-group"><label>Raison</label><input type="text" name="reason" class="form-control" value="Stock initial" required></div>
            <button type="submit" class="btn btn-primary">Ajouter</button>
        </form>
    </div>
</div>
