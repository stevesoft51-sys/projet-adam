<?php $pageTitle = 'Depenses'; ?>
<div class="page-header">
    <h2>Gestion des depenses</h2>
    <button class="btn btn-primary" onclick="document.getElementById('addExpenseModal').classList.add('show')">+ Ajouter une depense</button>
</div>

<div class="card">
    <div class="card-header">
        <h3>Filtrer par periode</h3>
    </div>
    <div class="card-body">
        <form method="GET" action="/admin/expenses" class="form-row" style="align-items:flex-end">
            <div class="form-group form-col-3">
                <label>Du</label>
                <input type="date" name="from" value="<?= htmlspecialchars($from) ?>" class="form-control">
            </div>
            <div class="form-group form-col-3">
                <label>Au</label>
                <input type="date" name="to" value="<?= htmlspecialchars($to) ?>" class="form-control">
            </div>
            <div class="form-group form-col-3">
                <button type="submit" class="btn btn-primary">Filtrer</button>
            </div>
        </form>
    </div>
</div>

<div class="stats-grid">
    <div class="stat-card stat-warning">
        <div class="stat-icon"><i data-lucide="banknote"></i></div>
        <div class="stat-body">
            <h3><?= View::money($total) ?></h3>
            <p>Total depenses</p>
        </div>
    </div>
    <div class="stat-card stat-info">
        <div class="stat-icon"><i data-lucide="bar-chart"></i></div>
        <div class="stat-body">
            <h3><?= count($byCategory) ?></h3>
            <p>Categories</p>
        </div>
    </div>
    <div class="stat-card stat-primary">
        <div class="stat-icon"><i data-lucide="file-text"></i></div>
        <div class="stat-body">
            <h3><?= count($expenses) ?></h3>
            <p>Depenses</p>
        </div>
    </div>
</div>

<?php if (!empty($byCategory)): ?>
<div class="card">
    <div class="card-header"><h3>Par categorie</h3></div>
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Categorie</th><th>Nombre</th><th>Total</th></tr></thead>
            <tbody>
                <?php foreach ($byCategory as $cat): ?>
                    <tr>
                        <td><strong><?= htmlspecialchars($cat['category']) ?></strong></td>
                        <td><?= $cat['count'] ?></td>
                        <td><?= View::money($cat['total']) ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
<?php endif; ?>

<div class="card">
    <div class="card-header"><h3>Liste des depenses</h3></div>
    <div class="card-body">
        <?php if (empty($expenses)): ?>
            <p class="text-muted">Aucune depense sur cette periode</p>
        <?php else: ?>
            <div class="table-responsive">
                <table class="table">
                    <thead><tr><th>Date</th><th>Categorie</th><th>Description</th><th>Montant</th><th>Paiement</th><th>Actions</th></tr></thead>
                    <tbody>
                        <?php foreach ($expenses as $exp): ?>
                            <tr>
                                <td><?= View::date($exp['date']) ?></td>
                                <td><span class="badge badge-info"><?= htmlspecialchars($exp['category']) ?></span></td>
                                <td><?= htmlspecialchars($exp['description']) ?></td>
                                <td><strong><?= View::money($exp['amount']) ?></strong></td>
                                <td><?= ucfirst(str_replace('_', ' ', $exp['payment_method'])) ?></td>
                                <td>
                                    <form method="POST" action="/admin/expenses/delete" class="inline" onsubmit="return confirm('Supprimer cette depense ?')">
                                        <?= csrf_field() ?>
                                        <input type="hidden" name="id" value="<?= $exp['id'] ?>">
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

<div class="modal" id="addExpenseModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Ajouter une depense</h3>
            <button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button>
        </div>
        <form method="POST" action="/admin/expenses">
            <?= csrf_field() ?>
            <div class="form-row">
                <div class="form-col-2 form-group">
                    <label>Categorie *</label>
                    <select name="category" required class="form-control">
                        <option value="">Choisir...</option>
                        <option value="Alimentation">Alimentation</option>
                        <option value="Boissons">Boissons</option>
                        <option value="Fournitures">Fournitures</option>
                        <option value="Entretien">Entretien</option>
                        <option value="Salaires">Salaires</option>
                        <option value="Loyer">Loyer</option>
                        <option value="Eau/Electricite">Eau / Electricite</option>
                        <option value="Transport">Transport</option>
                        <option value="Marketing">Marketing</option>
                        <option value="Autre">Autre</option>
                    </select>
                </div>
                <div class="form-col-2 form-group">
                    <label>Montant (FCFA) *</label>
                    <input type="number" name="amount" required min="0" step="50" class="form-control">
                </div>
            </div>
            <div class="form-group">
                <label>Description *</label>
                <input type="text" name="description" required maxlength="255" class="form-control" placeholder="Ex: Achat huile d'arachide">
            </div>
            <div class="form-row">
                <div class="form-col-2 form-group">
                    <label>Date *</label>
                    <input type="date" name="date" required class="form-control" value="<?= date('Y-m-d') ?>">
                </div>
                <div class="form-col-2 form-group">
                    <label>Mode de paiement *</label>
                    <select name="payment_method" required class="form-control">
                        <option value="cash">Especes</option>
                        <option value="mobile_money">Mobile Money</option>
                        <option value="card">Carte</option>
                        <option value="transfer">Virement</option>
                    </select>
                </div>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-outline" onclick="this.closest('.modal').classList.remove('show')">Annuler</button>
                <button type="submit" class="btn btn-primary">Enregistrer</button>
            </div>
        </form>
    </div>
</div>
