<?php $pageTitle = 'Historique de caisse'; ?>
<div class="page-header"><h2>Historique des caisses</h2></div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>#</th><th>Caissier</th><th>Ouverture</th><th>Fermeture</th><th>Entrees</th><th>Sorties</th><th>Attendu</th><th>Reel</th><th>Ecart</th><th>Statut</th></tr></thead>
            <tbody>
                <?php foreach ($history as $h): ?>
                    <tr>
                        <td><?= $h['id'] ?></td>
                        <td><?= htmlspecialchars($h['user_name']) ?></td>
                        <td><?= View::money($h['opening_amount']) ?></td>
                        <td><?= $h['closing_amount'] !== null ? View::money($h['closing_amount']) : '<em>En cours</em>' ?></td>
                        <td><?= View::money($h['total_cash_in']) ?></td>
                        <td><?= View::money($h['total_cash_out']) ?></td>
                        <td><?= $h['expected_amount'] !== null ? View::money($h['expected_amount']) : '-' ?></td>
                        <td><?= $h['closing_amount'] !== null ? View::money($h['closing_amount']) : '-' ?></td>
                        <td>
                            <?php if ($h['expected_amount'] !== null && $h['closing_amount'] !== null): ?>
                                <?php $diff = $h['closing_amount'] - $h['expected_amount']; ?>
                                <span class="<?= $diff != 0 ? 'text-danger' : 'text-success' ?>"><?= $diff >= 0 ? '+' : '' ?><?= View::money($diff) ?></span>
                            <?php else: ?>-<?php endif; ?>
                        </td>
                        <td><span class="badge badge-<?= $h['status'] ?>"><?= $h['status']==='open'?'Ouverte':'Fermee' ?></span></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
