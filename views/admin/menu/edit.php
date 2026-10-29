<?php $pageTitle = 'Modifier: ' . $product['name']; ?>
<div class="page-header"><h2>Modifier: <?= htmlspecialchars($product['name']) ?></h2></div>
<div class="card">
    <div class="card-body">
        <form method="POST" action="/admin/menu/update" enctype="multipart/form-data">
            <?= csrf_field() ?>
            <input type="hidden" name="id" value="<?= $product['id'] ?>">
            <div class="form-row">
                <div class="form-group form-col-2">
                    <label>Nom du plat *</label>
                    <input type="text" name="name" required maxlength="150" class="form-control" value="<?= htmlspecialchars($product['name']) ?>">
                </div>
                <div class="form-group form-col-2">
                    <label>Categorie *</label>
                    <select name="category_id" required class="form-control">
                        <?php foreach ($categories as $cat): ?>
                            <option value="<?= $cat['id'] ?>" <?= $cat['id'] == $product['category_id'] ? 'selected' : '' ?>><?= htmlspecialchars($cat['name']) ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group form-col-2">
                    <label>Prix (FCFA) *</label>
                    <input type="number" name="price" required min="0" step="50" class="form-control" value="<?= $product['price'] ?>">
                </div>
                <div class="form-group form-col-2">
                    <label>Prix de revient (FCFA)</label>
                    <input type="number" name="cost_price" min="0" step="50" class="form-control" value="<?= $product['cost_price'] ?>">
                </div>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" rows="3" class="form-control"><?= htmlspecialchars($product['description'] ?? '') ?></textarea>
            </div>
            <div class="form-row">
                <div class="form-group form-col-3">
                    <label>Temps de preparation (min)</label>
                    <input type="number" name="preparation_time" min="0" class="form-control" value="<?= $product['preparation_time'] ?? '' ?>">
                </div>
                <div class="form-group form-col-3">
                    <label>Ordre d'affichage</label>
                    <input type="number" name="sort_order" min="0" class="form-control" value="<?= $product['sort_order'] ?>">
                </div>
                <div class="form-group form-col-3">
                    <label>Photo</label>
                    <?php if ($product['image']): ?>
                        <div class="current-image"><img src="<?= htmlspecialchars($product['image']) ?>" alt="" style="max-height:80px"></div>
                    <?php endif; ?>
                    <input type="file" name="image" accept="image/*" class="form-control">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="checkbox-label"><input type="checkbox" name="is_available" <?= $product['is_available'] ? 'checked' : '' ?>> Disponible</label>
                </div>
                <div class="form-group">
                    <label class="checkbox-label"><input type="checkbox" name="is_featured" <?= $product['is_featured'] ? 'checked' : '' ?>> Vedette</label>
                </div>
            </div>

            <h3 class="section-title">Ingredients</h3>
            <div id="ingredients-list">
                <?php if (!empty($product['ingredients'])): ?>
                    <?php foreach ($product['ingredients'] as $ing): ?>
                        <div class="ingredient-row form-row">
                            <div class="form-col-3">
                                <select name="ingredient_id[]" class="form-control">
                                    <option value="">Choisir...</option>
                                    <?php foreach ($ingredients as $i): ?>
                                        <option value="<?= $i['id'] ?>" <?= $i['id'] == $ing['ingredient_id'] ? 'selected' : '' ?>><?= htmlspecialchars($i['name']) ?> (<?= $i['unit'] ?>)</option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                            <div class="form-col-3">
                                <input type="number" name="ingredient_qty[]" value="<?= $ing['quantity'] ?>" min="0" step="0.1" class="form-control">
                            </div>
                            <div class="form-col-3">
                                <button type="button" class="btn btn-xs btn-danger remove-ingredient">Retirer</button>
                            </div>
                        </div>
                    <?php endforeach; ?>
                <?php endif; ?>
            </div>
            <button type="button" class="btn btn-sm btn-outline" onclick="addIngredientRow()">+ Ingredient</button>

            <div class="form-actions">
                <a href="/admin/menu" class="btn btn-outline">Annuler</a>
                <button type="submit" class="btn btn-primary">Mettre a jour</button>
            </div>
        </form>
    </div>
</div>
