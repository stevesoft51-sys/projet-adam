<?php $pageTitle = 'Commandes'; ?>
<div class="page-header">
    <h2>Commandes actives</h2>
    <a href="/admin/orders/pos" class="btn btn-primary">Nouvelle commande (POS)</a>
</div>
<div class="card">
    <div class="card-body">
        <?php if (empty($orders)): ?>
            <p class="text-muted">Aucune commande active</p>
        <?php else: ?>
            <div class="table-responsive">
                <table class="table">
                    <thead><tr><th>#</th><th>Table</th><th>Type</th><th>Serveur</th><th>Items</th><th>Total</th><th>Statut</th><th>Date</th><th>Actions</th></tr></thead>
                    <tbody>
                        <?php foreach ($orders as $o): ?>
                            <tr class="row-<?= $o['status'] ?>">
                                <td><strong><?= htmlspecialchars($o['order_number']) ?></strong></td>
                                <td><?= $o['table_number'] ? 'T'.$o['table_number'] : '<em>A emporter</em>' ?></td>
                                <td><?= $o['type'] === 'dine_in' ? 'Sur place' : 'A emporter' ?></td>
                                <td><?= htmlspecialchars($o['server_name']) ?></td>
                                <td><span class="badge badge-info"><?= $o['items_count'] ?? '-' ?></span></td>
                                <td><strong><?= View::money($o['total']) ?></strong></td>
                                <td><span class="badge badge-<?= $o['status'] ?>"><?php $statusLabels = ['pending'=>'En attente','confirmed'=>'Confirmee','preparing'=>'En prep.','ready'=>'Prete','served'=>'Servie','paid'=>'Payee']; echo $statusLabels[$o['status']] ?? $o['status']; ?></span></td>
                                <td class="text-muted"><?= View::datetime($o['created_at']) ?></td>
                                <td>
                                    <div class="btn-group">
                                        <?php if ($o['status']==='confirmed'): ?><button class="btn btn-xs btn-warning update-order-status" data-id="<?=$o['id']?>" data-status="preparing">Prep.</button><?php endif; ?>
                                        <?php if ($o['status']==='preparing'): ?><button class="btn btn-xs btn-success update-order-status" data-id="<?=$o['id']?>" data-status="ready">Prete</button><?php endif; ?>
                                        <?php if ($o['status']==='ready'): ?><button class="btn btn-xs btn-info update-order-status" data-id="<?=$o['id']?>" data-status="served">Servie</button><?php endif; ?>
                                        <?php if (in_array($o['status'],['served','confirmed','preparing','ready'])): ?>
                                            <button class="btn btn-xs btn-primary show-payment-modal" data-id="<?=$o['id']?>" data-total="<?=$o['total']?>">Payer</button>
                                        <?php endif; ?>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>
</div>

<div class="modal" id="paymentModal">
    <div class="modal-content modal-sm">
        <div class="modal-header"><h3>Enregistrer le paiement</h3><button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button></div>
        <form method="POST" action="/admin/cash/payment">
            <?= csrf_field() ?>
            <input type="hidden" name="order_id" id="payment_order_id">
            <div class="form-group"><label>Montant (FCFA) *</label><input type="number" name="amount" id="payment_amount" step="50" min="0" required class="form-control"></div>
            <div class="form-group"><label>Moyen de paiement *</label>
                <select name="method" required class="form-control" id="payment_method" onchange="togglePhoneField()">
                    <option value="cash">Especes</option>
                    <option value="mobile_money">Mobile Money</option>
                    <option value="card">Carte</option>
                </select>
            </div>
            <div class="form-group" id="phone_group" style="display:none"><label>Numero Mobile Money</label><input type="text" name="phone_number" class="form-control" placeholder="+225..."></div>
            <div class="form-group"><label>Notes</label><textarea name="payment_notes" class="form-control" rows="2"></textarea></div>
            <button type="submit" class="btn btn-primary btn-block">Confirmer le paiement</button>
        </form>
    </div>
</div>
