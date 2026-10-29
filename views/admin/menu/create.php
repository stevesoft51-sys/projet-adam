<?php $pageTitle = 'Ajouter un plat'; ?>
<div class="page-header"><h2>Ajouter un plat</h2></div>
<div class="card">
    <div class="card-body">
        <form method="POST" action="/admin/menu" enctype="multipart/form-data">
            <?= csrf_field() ?>
            <div class="form-row">
                <div class="form-group form-col-2">
                    <label>Nom du plat *</label>
                    <input type="text" name="name" required maxlength="150" class="form-control" value="<?= htmlspecialchars($_POST['name'] ?? '') ?>">
                </div>
                <div class="form-group form-col-2">
                    <label>Categorie *</label>
                    <select name="category_id" required class="form-control">
                        <option value="">Choisir...</option>
                        <?php foreach ($categories as $cat): ?>
                            <option value="<?= $cat['id'] ?>"><?= htmlspecialchars($cat['name']) ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group form-col-2">
                    <label>Prix (FCFA) *</label>
                    <input type="number" name="price" required min="0" step="50" class="form-control" value="<?= htmlspecialchars($_POST['price'] ?? '') ?>">
                </div>
                <div class="form-group form-col-2">
                    <label>Prix de revient (FCFA)</label>
                    <input type="number" name="cost_price" min="0" step="50" class="form-control" value="<?= htmlspecialchars($_POST['cost_price'] ?? '') ?>">
                </div>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" rows="3" class="form-control" maxlength="500"><?= htmlspecialchars($_POST['description'] ?? '') ?></textarea>
            </div>
            <div class="form-row">
                <div class="form-group form-col-3">
                    <label>Temps de preparation (min)</label>
                    <input type="number" name="preparation_time" min="0" class="form-control" value="<?= htmlspecialchars($_POST['preparation_time'] ?? '') ?>">
                </div>
                <div class="form-group form-col-3">
                    <label>Ordre d'affichage</label>
                    <input type="number" name="sort_order" min="0" class="form-control" value="<?= htmlspecialchars($_POST['sort_order'] ?? '0') ?>">
                </div>
                <div class="form-group form-col-3">
                    <label>Photo du plat</label>
                    <input type="file" name="image" accept="image/*" class="form-control">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_available" checked> Disponible a la vente
                    </label>
                </div>
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" name="is_featured"> Plat vedette
                    </label>
                </div>
            </div>

            <h3 class="section-title">Ingredients</h3>
            <div id="ingredients-list">
                <div class="ingredient-row form-row">
                    <div class="form-col-3">
                        <select name="ingredient_id[]" class="form-control">
                            <option value="">Choisir un ingredient...</option>
                            <?php foreach ($ingredients as $ing): ?>
                                <option value="<?= $ing['id'] ?>"><?= htmlspecialchars($ing['name']) ?> (<?= $ing['unit'] ?>)</option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    <div class="form-col-3">
                        <input type="number" name="ingredient_qty[]" placeholder="Quantite" min="0" step="0.1" class="form-control">
                    </div>
                    <div class="form-col-3">
                        <button type="button" class="btn btn-xs btn-danger remove-ingredient">Retirer</button>
                    </div>
                </div>
            </div>
            <button type="button" class="btn btn-sm btn-outline" onclick="addIngredientRow()">+ Ajouter un ingredient</button>

            <div class="form-actions">
                <a href="/admin/menu" class="btn btn-outline">Annuler</a>
                <button type="submit" class="btn btn-primary">Enregistrer</button>
            </div>
        </form>
    </div>
</div>
