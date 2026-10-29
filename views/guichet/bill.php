<?php $pageTitle = 'Facture #' . $order['order_number']; ?>
<?php if (!isset($_GET['print'])): ?>
<a href="/guichet/factures" class="btn btn-outline" style="margin-bottom:1rem">&larr; Retour aux factures</a>
<?php endif; ?>

<style>
    .bill-paper {
        max-width: 600px;
        margin: 0 auto;
        background: #fff;
        padding: 2rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
    }
    .bill-header { text-align: center; border-bottom: 2px dashed #ccc; padding-bottom: 1rem; margin-bottom: 1rem; }
    .bill-header h2 { margin: 0; font-size: 1.3rem; }
    .bill-header p { margin: .25rem 0; color: #666; font-size: .85rem; }
    .bill-meta { display: flex; justify-content: space-between; font-size: .85rem; margin-bottom: 1rem; color: #555; }
    .bill-table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
    .bill-table th, .bill-table td { padding: .5rem .25rem; text-align: left; border-bottom: 1px dotted #ddd; font-size: .85rem; }
    .bill-table th { font-weight: 600; }
    .bill-table .text-right { text-align: right; }
    .bill-totals { border-top: 2px solid #333; padding-top: .75rem; }
    .bill-totals .bill-row { display: flex; justify-content: space-between; padding: .25rem 0; font-size: .9rem; }
    .bill-totals .bill-row.total { font-size: 1.1rem; font-weight: 700; border-top: 1px solid #333; margin-top: .25rem; padding-top: .5rem; }
    .bill-footer { text-align: center; border-top: 2px dashed #ccc; padding-top: 1rem; margin-top: 1rem; font-size: .8rem; color: #888; }
    .bill-paid-stamp { text-align: center; font-size: 2rem; font-weight: 900; color: #27ae60; border: 4px solid #27ae60; padding: .5rem; margin: 1rem 0; transform: rotate(-5deg); opacity: .7; }
    @media print {
        body { background: #fff !important; }
        .bill-paper { border: none; padding: 0; box-shadow: none; }
        .no-print { display: none !important; }
    }
</style>

<div class="bill-paper" id="billPaper">
    <div class="bill-header">
        <h2><?= htmlspecialchars($restaurant['name']) ?></h2>
        <p><?= htmlspecialchars($restaurant['address']) ?></p>
        <p>Tel: <?= htmlspecialchars($restaurant['phone']) ?></p>
    </div>

    <div class="bill-meta">
        <div>
            <strong>Facture:</strong> <?= htmlspecialchars($order['order_number']) ?><br>
            <strong>Type:</strong> <?= $order['type'] === 'dine_in' ? 'Sur place' : 'A emporter' ?>
            <?php if ($order['table_number']): ?><br><strong>Table:</strong> <?= $order['table_number'] ?><?php endif; ?>
        </div>
        <div style="text-align:right">
            <strong>Date:</strong> <?= date('d/m/Y', strtotime($order['created_at'])) ?><br>
            <strong>Heure:</strong> <?= date('H:i', strtotime($order['created_at'])) ?>
        </div>
    </div>

    <?php if ($order['status'] === 'paid'): ?>
        <div class="bill-paid-stamp">PAYE</div>
    <?php endif; ?>

    <table class="bill-table">
        <thead>
            <tr>
                <th>Article</th>
                <th class="text-right">Qte</th>
                <th class="text-right">Prix</th>
                <th class="text-right">Total</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($order['items'] as $item): ?>
                <tr>
                    <td>
                        <?= htmlspecialchars($item['product_name']) ?>
                        <?php if (!empty($item['notes'])): ?>
                            <br><small style="color:#888">(<?= htmlspecialchars($item['notes']) ?>)</small>
                        <?php endif; ?>
                    </td>
                    <td class="text-right"><?= $item['quantity'] ?></td>
                    <td class="text-right"><?= number_format($item['unit_price'], 0, ',', ' ') ?></td>
                    <td class="text-right"><?= number_format($item['total_price'], 0, ',', ' ') ?></td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>

    <div class="bill-totals">
        <div class="bill-row">
            <span>Sous-total</span>
            <span><?= number_format($order['subtotal'], 0, ',', ' ') ?> FCFA</span>
        </div>
        <?php if ($order['discount'] > 0): ?>
            <div class="bill-row" style="color:#27ae60">
                <span>Remise</span>
                <span>-<?= number_format($order['discount'], 0, ',', ' ') ?> FCFA</span>
            </div>
        <?php endif; ?>
        <div class="bill-row">
            <span>TVA (<?= \SettingModel::getValue('tax_rate', 18) ?>%)</span>
            <span><?= number_format($order['tax'], 0, ',', ' ') ?> FCFA</span>
        </div>
        <div class="bill-row total">
            <span>TOTAL A PAYER</span>
            <span><?= number_format($order['total'], 0, ',', ' ') ?> FCFA</span>
        </div>
    </div>

    <?php if (!empty($payments)): ?>
        <div style="margin-top:1rem;border-top:1px dashed #ccc;padding-top:.75rem">
            <strong style="font-size:.85rem">Paiements:</strong>
            <?php foreach ($payments as $pm): ?>
                <div style="font-size:.8rem;color:#555;padding:.25rem 0">
                    <?= date('H:i', strtotime($pm['created_at'])) ?> -
                    <?= ucfirst(str_replace('_', ' ', $pm['method'])) ?>:
                    <?= number_format($pm['amount'], 0, ',', ' ') ?> FCFA
                    <span class="badge badge-<?= $pm['status'] ?> badge-sm"><?= $pm['status'] ?></span>
                </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>

    <div class="bill-footer">
        <p>Merci pour votre visite!</p>
        <p><?= htmlspecialchars($restaurant['name']) ?> - <?= htmlspecialchars($restaurant['phone']) ?></p>
    </div>
</div>

<?php if ($order['status'] !== 'paid' && $order['status'] !== 'cancelled'): ?>
<div id="payer" style="max-width:600px;margin:1.5rem auto">
    <div class="card">
        <div class="card-header"><h3>Encaisser cette commande</h3></div>
        <div class="card-body">
            <?php
            $totalPaid = 0;
            foreach ($payments as $pm) {
                if ($pm['status'] === 'completed') $totalPaid += (float)$pm['amount'];
            }
            $due = (float)$order['total'] - $totalPaid;
            ?>
            <p style="font-size:1.1rem;font-weight:700;margin-bottom:1rem">
                Reste a payer: <span style="color:#e74c3c"><?= number_format($due, 0, ',', ' ') ?> FCFA</span>
            </p>
            <form method="POST" action="/guichet/payment/process" id="paymentForm">
                <?= csrf_field() ?>
                <input type="hidden" name="order_id" value="<?= $order['id'] ?>">
                <input type="hidden" name="amount" value="<?= $due ?>">
                <div class="form-group">
                    <label>Mode de paiement *</label>
                    <select name="method" id="payment_method" class="form-control" onchange="toggleGuichetPhone()">
                        <option value="cash">Especes</option>
                        <option value="mobile_money">Mobile Money</option>
                        <option value="card">Carte</option>
                    </select>
                </div>
                <div class="form-group" id="phone_group" style="display:none">
                    <label>Numero de telephone</label>
                    <input type="text" name="phone_number" class="form-control" placeholder="+225 XX XX XX XX">
                </div>
                <div class="form-group">
                    <label>Notes</label>
                    <input type="text" name="payment_notes" class="form-control" placeholder="Optionnel">
                </div>
                <button type="submit" class="btn btn-success btn-lg btn-block" onclick="return confirm('Confirmer l\'encaissement de <?= number_format($due, 0, ',', ' ') ?> FCFA ?')">
                    Encaisser <?= number_format($due, 0, ',', ' ') ?> FCFA
                </button>
            </form>
        </div>
    </div>
</div>
<?php endif; ?>

<?php if (!isset($_GET['print'])): ?>
<div style="max-width:600px;margin:1rem auto;text-align:center" class="no-print">
    <button onclick="window.print()" class="btn btn-outline btn-lg"><i data-lucide="printer"></i> Imprimer la facture</button>
</div>
<?php endif; ?>

<script>
function toggleGuichetPhone() {
    const m = document.getElementById('payment_method');
    const p = document.getElementById('phone_group');
    if (m && p) p.style.display = m.value === 'mobile_money' ? 'block' : 'none';
}
<?php if (isset($_GET['print'])): ?>
window.onload = function() { window.print(); };
<?php endif; ?>
</script>
