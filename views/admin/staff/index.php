<?php $pageTitle = 'Personnel'; ?>
<div class="page-header">
    <h2>Gestion du personnel</h2>
    <button class="btn btn-primary" onclick="document.getElementById('addStaffModal').classList.add('show')">+ Ajouter</button>
</div>
<div class="stats-grid stats-4">
    <div class="stat-card stat-primary"><div class="stat-body"><h3><?= $roleCounts['admin'] ?? 0 ?></h3><p>Admins</p></div></div>
    <div class="stat-card stat-info"><div class="stat-body"><h3><?= $roleCounts['manager'] ?? 0 ?></h3><p>Managers</p></div></div>
    <div class="stat-card stat-success"><div class="stat-body"><h3><?= $roleCounts['serveur'] ?? 0 ?></h3><p>Serveurs</p></div></div>
    <div class="stat-card stat-warning"><div class="stat-body"><h3><?= $roleCounts['cuisinier'] ?? 0 ?></h3><p>Cuisiniers</p></div></div>
</div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Nom</th><th>Email</th><th>Telephone</th><th>Role</th><th>Statut</th><th>Derniere connexion</th><th>Actions</th></tr></thead>
            <tbody>
                <?php foreach ($users as $u): ?>
                    <tr>
                        <td><strong><?= htmlspecialchars($u['name']) ?></strong></td>
                        <td><?= htmlspecialchars($u['email']) ?></td>
                        <td><?= htmlspecialchars($u['phone'] ?? '-') ?></td>
                        <td><span class="badge badge-<?= $u['role'] ?>"><?= ucfirst($u['role']) ?></span></td>
                        <td><span class="badge badge-<?= $u['is_active'] ? 'success' : 'danger' ?>"><?= $u['is_active'] ? 'Actif' : 'Inactif' ?></span></td>
                        <td class="text-muted"><?= $u['last_login'] ? View::timeAgo($u['last_login']) : 'Jamais' ?></td>
                        <td>
                            <div class="btn-group">
                                <button class="btn btn-xs btn-outline edit-staff-btn"
                                    data-id="<?= $u['id'] ?>"
                                    data-name="<?= htmlspecialchars($u['name']) ?>"
                                    data-email="<?= htmlspecialchars($u['email']) ?>"
                                    data-role="<?= $u['role'] ?>"
                                    data-phone="<?= htmlspecialchars($u['phone'] ?? '') ?>"
                                    data-active="<?= $u['is_active'] ?>"
                                    onclick="openEditStaff(this)">Modifier</button>
                                <?php if ($u['id'] != $auth->id()): ?>
                                    <form method="POST" action="/admin/staff/delete" class="inline" onsubmit="return confirm('Supprimer ce membre ?')">
                                        <?= csrf_field() ?>
                                        <input type="hidden" name="id" value="<?= $u['id'] ?>">
                                        <button class="btn btn-xs btn-danger">Supprimer</button>
                                    </form>
                                <?php endif; ?>
                            </div>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>

<div class="modal" id="addStaffModal">
    <div class="modal-content">
        <div class="modal-header"><h3>Ajouter un membre</h3><button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button></div>
        <form method="POST" action="/admin/staff">
            <?= csrf_field() ?>
            <div class="form-group"><label>Nom *</label><input type="text" name="name" required class="form-control"></div>
            <div class="form-group"><label>Email *</label><input type="email" name="email" required class="form-control"></div>
            <div class="form-group"><label>Mot de passe *</label><input type="password" name="password" required minlength="6" class="form-control"></div>
            <div class="form-row">
                <div class="form-col-2"><label>Role *</label>
                    <select name="role" class="form-control"><option value="serveur">Serveur</option><option value="cuisinier">Cuisinier</option><option value="manager">Manager</option><option value="admin">Admin</option></select>
                </div>
                <div class="form-col-2"><label>Telephone</label><input type="text" name="phone" class="form-control"></div>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Ajouter</button>
        </form>
    </div>
</div>

<div class="modal" id="editStaffModal">
    <div class="modal-content">
        <div class="modal-header"><h3>Modifier un membre</h3><button class="modal-close" onclick="this.closest('.modal').classList.remove('show')">&times;</button></div>
        <form method="POST" action="/admin/staff/update">
            <?= csrf_field() ?>
            <input type="hidden" name="id" id="edit_staff_id">
            <div class="form-group"><label>Nom *</label><input type="text" name="name" id="edit_staff_name" required class="form-control"></div>
            <div class="form-group"><label>Email *</label><input type="email" name="email" id="edit_staff_email" required class="form-control"></div>
            <div class="form-group"><label>Nouveau mot de passe (laisser vide pour garder)</label><input type="password" name="password" class="form-control" minlength="6"></div>
            <div class="form-row">
                <div class="form-col-2"><label>Role *</label>
                    <select name="role" id="edit_staff_role" class="form-control"><option value="serveur">Serveur</option><option value="cuisinier">Cuisinier</option><option value="manager">Manager</option><option value="admin">Admin</option></select>
                </div>
                <div class="form-col-2"><label>Telephone</label><input type="text" name="phone" id="edit_staff_phone" class="form-control"></div>
            </div>
            <div class="form-group">
                <label class="checkbox-label"><input type="checkbox" name="is_active" id="edit_staff_active" value="1"> Actif</label>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Mettre a jour</button>
        </form>
    </div>
</div>

<script>
function openEditStaff(btn) {
    document.getElementById('edit_staff_id').value = btn.dataset.id;
    document.getElementById('edit_staff_name').value = btn.dataset.name;
    document.getElementById('edit_staff_email').value = btn.dataset.email;
    document.getElementById('edit_staff_role').value = btn.dataset.role;
    document.getElementById('edit_staff_phone').value = btn.dataset.phone;
    document.getElementById('edit_staff_active').checked = btn.dataset.active === '1';
    document.getElementById('editStaffModal').classList.add('show');
}
</script>
