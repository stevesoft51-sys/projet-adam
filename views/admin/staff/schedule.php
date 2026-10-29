<?php $pageTitle = 'Planning du personnel'; ?>
<div class="page-header">
    <h2>Planning</h2>
    <div class="page-actions">
        <a href="/admin/staff/schedule?week=<?= $prevWeek ?>" class="btn btn-outline">&laquo; Semaine precedente</a>
        <span class="current-week"><?= View::date($weekStart) ?> - <?= View::date($weekEnd) ?></span>
        <a href="/admin/staff/schedule?week=<?= $nextWeek ?>" class="btn btn-outline">Semaine suivante &raquo;</a>
        <button class="btn btn-primary" onclick="document.getElementById('addShiftModal').classList.add('show')">+ Ajouter shift</button>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-schedule">
                <thead>
                    <tr>
                        <th>Personnel</th>
                        <?php for ($i = 0; $i < 7; $i++): ?>
                            <?php $d = date('Y-m-d', strtotime($weekStart . " +{$i} days")); ?>
                            <th class="<?= $d === date('Y-m-d') ? 'today-col' : '' ?>">
                                <?= date('d/m', strtotime($d)) ?>
                            </th>
                        <?php endfor; ?>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($users as $u): ?>
                        <tr>
                            <td><strong><?= htmlspecialchars($u['name']) ?></strong><br><small class="text-muted"><?= $u['role'] ?></small></td>
                            <?php for ($i = 0; $i < 7; $i++): ?>
                                <?php $d = date('Y-m-d', strtotime($weekStart . " +{$i} days")); ?>
                                <td>
                                    <?php foreach ($shifts as $s): ?>
                                        <?php if ($s['user_id'] == $u['id'] && $s['date'] === $d): ?>
                                            <div class="shift-card shift-<?= $s['status'] ?>">
                                                <strong><?= substr($s['start_time'],0,5) ?> - <?= substr($s['end_time'],0,5) ?></strong>
                                                <?php if ($s['role_override']): ?><small><?= $s['role_override'] ?></small><?php endif; ?>
                                                <span class="badge badge-sm badge-<?= $s['status'] ?>"><?= $s['status'] ?></span>
                                            </div>
                                        <?php endif; ?>
                                    <?php endforeach; ?>
                                </td>
                            <?php endfor; ?>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="modal" id="addShiftModal">
    <div class="modal-content">
        <div class="modal-header"><h3>Ajouter un shift</h3><button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button></div>
        <form method="POST" action="/admin/staff/shift">
            <?= csrf_field() ?>
            <div class="form-group"><label>Personnel *</label>
                <select name="user_id" required class="form-control">
                    <?php foreach ($users as $u): ?>
                        <option value="<?= $u['id'] ?>"><?= htmlspecialchars($u['name']) ?> (<?= $u['role'] ?>)</option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="form-group"><label>Date *</label><input type="date" name="date" required class="form-control" value="<?= $weekStart ?>"></div>
            <div class="form-row">
                <div class="form-col-2"><label>Debut *</label><input type="time" name="start_time" required class="form-control" value="08:00"></div>
                <div class="form-col-2"><label>Fin *</label><input type="time" name="end_time" required class="form-control" value="16:00"></div>
            </div>
            <div class="form-group"><label>Notes</label><input type="text" name="notes" class="form-control"></div>
            <button type="submit" class="btn btn-primary btn-block">Ajouter</button>
        </form>
    </div>
</div>
