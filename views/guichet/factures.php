<?php $pageTitle = 'Factures'; ?>
<div class="page-header"><h2>Factures & Additions</h2></div>

<div class="card" style="margin-bottom:1.5rem">
    <div class="card-body">
        <form method="GET" action="/guichet/factures" style="display:flex;gap:1rem;align-items:flex-end;flex-wrap:wrap">
            <div class="form-group" style="margin:0">
                <label>Du</label>
                <input type="date" name="date_from" class="form-control form-control-sm" value="<?= htmlspecialchars($dateFrom) ?>">
            </div>
            <div class="form-group" style="margin:0">
                <label>Au</label>
                <input type="date" name="date_to" class="form-control form-control-sm" value="<?= htmlspecialchars($dateTo) ?>">
            </div>
            <div class="form-group" style="margin:0">
                <label>Statut</label>
                <select name="status" class="form-control form-control-sm">
                    <option value="">Tous</option>
                    <option value="pending" <?= $statusFilter === 'pending' ? 'selected' : '' ?>>En attente</option>
                    <option value="confirmed" <?= $statusFilter === 'confirmed' ? 'selected' : '' ?>>Confirme</option>
                    <option value="preparing" <?= $statusFilter === 'preparing' ? 'selected' : '' ?>>En preparation</option>
                    <option value="ready" <?= $statusFilter === 'ready' ? 'selected' : '' ?>>Pret</option>
                    <option value="served" <?= $statusFilter === 'served' ? 'selected' : '' ?>>Servi</option>
                    <option value="paid" <?= $statusFilter === 'paid' ? 'selected' : '' ?>>Paye</option>
                    <option value="cancelled" <?= $statusFilter === 'cancelled' ? 'selected' : '' ?>>Annule</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary btn-sm">Filtrer</button>
        </form>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <?php if (empty($orders)): ?>
            <p class="text-muted" style="text-align:center;padding:2rem">Aucune facture pour cette periode</p>
        <?php else: ?>
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Commande</th>
                            <th>Table</th>
                            <th>Articles</th>
                            <th>Total</th>
                            <th>Paye</th>
                            <th>Reste</th>
                            <th>Statut</th>
                            <th>Heure</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php
                        $totalJour = 0;
                        $totalPaye = 0;
                        foreach ($orders as $o):
                            $restant = (float)$o['total'] - (float)$o['amount_paid'];
                            $totalJour += (float)$o['total'];
                            $totalPaye += (float)$o['amount_paid'];
                        ?>
                            <tr>
                                <td><strong><?= htmlspecialchars($o['order_number']) ?></strong></td>
                                <td><?= $o['table_number'] ? 'T'.$o['table_number'] : 'A emporter' ?></td>
                                <td><?= $o['items_count'] ?? '' ?></td>
                                <td><?= View::money($o['total']) ?></td>
                                <td><?= View::money($o['amount_paid']) ?></td>
                                <td style="color:<?= $restant > 0 ? '#e74c3c' : '#27ae60' ?>;font-weight:600"><?= View::money($restant) ?></td>
                                <td><span class="badge badge-<?= $o['status'] ?>"><?php
                                    $sl = ['pending'=>'En attente','confirmed'=>'Confirmee','preparing'=>'En preparation','ready'=>'Prete','served'=>'Servie','paid'=>'Paye','cancelled'=>'Annule'];
                                    echo $sl[$o['status']] ?? $o['status'];
                                ?></span></td>
                                <td><?= date('H:i', strtotime($o['created_at'])) ?></td>
                                <td>
                                    <div style="display:flex;gap:.25rem">
                                        <a href="/guichet/bill?id=<?= $o['id'] ?>" class="btn btn-xs btn-primary" title="Voir la facture"><i data-lucide="eye"></i></a>
                                        <?php if ($restant > 0 && $o['status'] !== 'cancelled'): ?>
                                            <a href="/guichet/bill?id=<?= $o['id'] ?>#payer" class="btn btn-xs btn-success" title="Encaisser"><i data-lucide="credit-card"></i></a>
                                        <?php endif; ?>
                                        <a href="/guichet/bill?id=<?= $o['id'] ?>&print=1" class="btn btn-xs btn-outline" target="_blank" title="Imprimer"><i data-lucide="printer"></i></a>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                    <tfoot>
                        <tr style="font-weight:700;background:#f8f9fa">
                            <td colspan="3">TOTAUX (<?= count($orders) ?> commandes)</td>
                            <td><?= View::money($totalJour) ?></td>
                            <td><?= View::money($totalPaye) ?></td>
                            <td style="color:#e74c3c"><?= View::money($totalJour - $totalPaye) ?></td>
                            <td colspan="3"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        <?php endif; ?>
    </div>
</div>
