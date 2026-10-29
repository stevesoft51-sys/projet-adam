<?php $pageTitle = 'Categories'; ?>
<div class="page-header"><h2>Categories du menu</h2></div>
<div class="form-row">
    <div class="card" style="flex:1">
        <div class="card-header"><h3>Ajouter une categorie</h3></div>
        <div class="card-body">
            <form method="POST" action="/admin/categories">
                <?= csrf_field() ?>
                <div class="form-group"><label>Nom *</label><input type="text" name="name" required class="form-control" maxlength="100"></div>
                <div class="form-group"><label>Description</label><textarea name="description" class="form-control" rows="2"></textarea></div>
                <div class="form-group"><label>Ordre</label><input type="number" name="sort_order" value="0" class="form-control"></div>
                <button type="submit" class="btn btn-primary">Ajouter</button>
            </form>
        </div>
    </div>
    <div class="card" style="flex:2">
        <div class="card-header"><h3>Liste</h3></div>
        <div class="card-body">
            <table class="table">
                <thead><tr><th>Nom</th><th>Description</th><th>Ordre</th><th>Actions</th></tr></thead>
                <tbody>
                    <?php foreach ($categories as $cat): ?>
                        <tr>
                            <td><?= htmlspecialchars($cat['name']) ?></td>
                            <td><?= htmlspecialchars($cat['description'] ?? '-') ?></td>
                            <td><?= $cat['sort_order'] ?></td>
                            <td>
                                <form method="POST" action="/admin/categories/delete" class="inline" onsubmit="return confirm('Supprimer cette categorie ?')">
                                    <?= csrf_field() ?>
                                    <input type="hidden" name="id" value="<?= $cat['id'] ?>">
                                    <button type="submit" class="btn btn-xs btn-danger">Supprimer</button>
                                </form>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
