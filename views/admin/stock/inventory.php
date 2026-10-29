<?php $pageTitle = 'Inventaire'; ?>
<div class="page-header"><h2>Inventaire physique</h2></div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Ingredient</th><th>Stock actuel</th><th>Unite</th><th>Seuil min</th><th>Ajuster</th></tr></thead>
            <tbody>
                <?php foreach ($ingredients as $ing): ?>
                    <tr>
                        <td><strong><?= htmlspecialchars($ing['name']) ?></strong></td>
                        <td id="stock-<?= $ing['id'] ?>"><?= number_format($ing['current_stock'], 1) ?></td>
                        <td><?= $ing['unit'] ?></td>
                        <td><?= number_format($ing['min_stock'], 1) ?></td>
                        <td>
                            <form method="POST" action="/admin/stock/adjust" class="inline-form">
                                <?= csrf_field() ?>
                                <input type="hidden" name="ingredient_id" value="<?= $ing['id'] ?>">
                                <input type="number" name="quantity" step="0.1" min="0" class="form-control form-control-sm" style="width:100px;display:inline-block" required>
                                <button type="submit" class="btn btn-xs btn-primary">Ajuster</button>
                            </form>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
