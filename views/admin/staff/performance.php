<?php $pageTitle = 'Performance du personnel'; ?>
<div class="page-header">
    <h2>Performance</h2>
    <form method="GET" class="inline-form">
        <input type="date" name="from" value="<?= $from ?>" class="form-control form-control-sm">
        <input type="date" name="to" value="<?= $to ?>" class="form-control form-control-sm">
        <button type="submit" class="btn btn-sm btn-primary">Filtrer</button>
    </form>
</div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Nom</th><th>Role</th><th>Heures travaillees</th><th>Shifts</th><th>Absences</th><th>Retards</th><th>Taux absence</th></tr></thead>
            <tbody>
                <?php foreach ($performance as $p): ?>
                    <tr>
                        <td><strong><?= htmlspecialchars($p['name']) ?></strong></td>
                        <td><span class="badge badge-<?= $p['role'] ?>"><?= ucfirst($p['role']) ?></span></td>
                        <td><?= $p['hours_worked'] ?>h</td>
                        <td><?= $p['shifts_count'] ?></td>
                        <td><?= $p['absences'] ?></td>
                        <td><?= $p['lates'] ?></td>
                        <td>
                            <?php $color = $p['absence_rate'] > 10 ? 'danger' : ($p['absence_rate'] > 5 ? 'warning' : 'success'); ?>
                            <span class="badge badge-<?= $color ?>"><?= $p['absence_rate'] ?>%</span>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
