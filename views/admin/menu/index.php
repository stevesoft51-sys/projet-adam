<?php $pageTitle = 'Gestion du Menu'; ?>
<div class="page-header">
    <h2>Menu du restaurant</h2>
    <div class="page-actions">
        <a href="/admin/menu/create" class="btn btn-primary">+ Ajouter un plat</a>
        <a href="/admin/categories" class="btn btn-outline">Categories</a>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <?php if (empty($products)): ?>
            <p class="text-muted">Aucun produit. <a href="/admin/menu/create">Ajouter le premier plat</a></p>
        <?php else: ?>
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr><th>Image</th><th>Nom</th><th>Categorie</th><th>Prix</th><th>Disponible</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                        <?php foreach ($products as $p): ?>
                            <tr>
                                <td>
                                    <?php if ($p['image']): ?>
                                        <img src="<?= htmlspecialchars($p['image']) ?>" alt="" class="table-thumb">
                                    <?php else: ?>
                                        <div class="table-thumb placeholder-thumb">N/A</div>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <strong><?= htmlspecialchars($p['name']) ?></strong>
                                    <?php if ($p['is_featured']): ?><span class="badge badge-info badge-sm">Vedette</span><?php endif; ?>
                                </td>
                                <td><?= htmlspecialchars($p['category_name']) ?></td>
                                <td><?= View::money($p['price']) ?></td>
                                <td>
                                    <button class="toggle-switch <?= $p['is_available'] ? 'active' : '' ?>" data-id="<?= $p['id'] ?>" onclick="toggleProduct(this)">
                                        <span class="toggle-slider"></span>
                                    </button>
                                </td>
                                <td>
                                    <a href="/admin/menu/edit?id=<?= $p['id'] ?>" class="btn btn-xs btn-outline">Modifier</a>
                                    <form method="POST" action="/admin/menu/delete" class="inline" onsubmit="return confirm('Supprimer ce produit ?')">
                                        <?= csrf_field() ?>
                                        <input type="hidden" name="id" value="<?= $p['id'] ?>">
                                        <button type="submit" class="btn btn-xs btn-danger">Supprimer</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>
</div>
