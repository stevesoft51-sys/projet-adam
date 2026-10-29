<?php $pageTitle = 'Parametres'; ?>
<div class="page-header"><h2>Parametres du restaurant</h2></div>
<form method="POST" action="/admin/settings">
    <?= csrf_field() ?>
    <div class="form-row">
        <div class="card" style="flex:1">
            <div class="card-header"><h3>Informations</h3></div>
            <div class="card-body">
                <div class="form-group"><label>Nom du restaurant</label><input type="text" name="restaurant_name" class="form-control" value="<?= htmlspecialchars($settings['restaurant_name'] ?? '') ?>"></div>
                <div class="form-group"><label>Telephone</label><input type="text" name="restaurant_phone" class="form-control" value="<?= htmlspecialchars($settings['restaurant_phone'] ?? '') ?>"></div>
                <div class="form-group"><label>Email</label><input type="email" name="restaurant_email" class="form-control" value="<?= htmlspecialchars($settings['restaurant_email'] ?? '') ?>"></div>
                <div class="form-group"><label>Adresse</label><textarea name="restaurant_address" class="form-control" rows="2"><?= htmlspecialchars($settings['restaurant_address'] ?? '') ?></textarea></div>
                <div class="form-group"><label>Taux de TVA (%)</label><input type="number" name="tax_rate" step="0.1" min="0" class="form-control" value="<?= $settings['tax_rate'] ?? '18' ?>"></div>
            </div>
        </div>
        <div class="card" style="flex:1">
            <div class="card-header"><h3>Horaires</h3></div>
            <div class="card-body">
                <div class="form-row">
                    <div class="form-col-2"><label>Heure d'ouverture</label><input type="time" name="opening_time" class="form-control" value="<?= $settings['opening_time'] ?? '08:00' ?>"></div>
                    <div class="form-col-2"><label>Heure de fermeture</label><input type="time" name="closing_time" class="form-control" value="<?= $settings['closing_time'] ?? '23:00' ?>"></div>
                </div>
                <div class="form-group"><label>Duree par defaut reservation (min)</label><input type="number" name="reservation_duration" class="form-control" value="<?= $settings['reservation_duration'] ?? '120' ?>"></div>
            </div>
        </div>
    </div>
    <div class="form-row">
        <div class="card" style="flex:1">
            <div class="card-header"><h3>Programme de fidelite</h3></div>
            <div class="card-body">
                <div class="form-group">
                    <label class="checkbox-label"><input type="checkbox" name="loyalty_enabled" <?= ($settings['loyalty_enabled'] ?? 1) ? 'checked' : '' ?>> Activer la fidelite</label>
                </div>
                <div class="form-group"><label>Points par FCFA</label><input type="number" name="loyalty_points_per_fcfa" class="form-control" value="<?= $settings['loyalty_points_per_fcfa'] ?? '1' ?>"></div>
            </div>
        </div>
        <div class="card" style="flex:1">
            <div class="card-header"><h3>CinetPay (Mobile Money)</h3></div>
            <div class="card-body">
                <div class="form-group">
                    <label class="checkbox-label"><input type="checkbox" name="cinetpay_enabled" <?= ($settings['cinetpay_enabled'] ?? 0) ? 'checked' : '' ?>> Activer CinetPay</label>
                </div>
                <div class="form-group"><label>API Key</label><input type="text" name="cinetpay_api_key" class="form-control" value="<?= htmlspecialchars($settings['cinetpay_api_key'] ?? '') ?>"></div>
                <div class="form-group"><label>Site ID</label><input type="text" name="cinetpay_site_id" class="form-control" value="<?= htmlspecialchars($settings['cinetpay_site_id'] ?? '') ?>"></div>
                <div class="form-group"><label>Secret Key</label><input type="password" name="cinetpay_secret_key" class="form-control" value="<?= htmlspecialchars($settings['cinetpay_secret_key'] ?? '') ?>"></div>
            </div>
        </div>
    </div>
    <div class="card" style="max-width:600px">
        <div class="card-header"><h3>Mot de passe</h3></div>
        <div class="card-body">
            <form method="POST" action="/admin/settings/password">
                <?= csrf_field() ?>
                <div class="form-group"><label>Mot de passe actuel</label><input type="password" name="current_password" class="form-control" required></div>
                <div class="form-group"><label>Nouveau mot de passe</label><input type="password" name="new_password" class="form-control" required minlength="6"></div>
                <div class="form-group"><label>Confirmer</label><input type="password" name="new_password_confirmation" class="form-control" required></div>
                <button type="submit" class="btn btn-warning">Changer le mot de passe</button>
            </form>
        </div>
    </div>
    <div class="form-actions">
        <button type="submit" class="btn btn-primary btn-lg">Enregistrer les parametres</button>
    </div>
</form>

<div class="card" style="max-width:600px;margin-top:2rem;border-color:#e74c3c">
    <div class="card-header" style="background:#e74c3c;color:#fff"><h3>Session</h3></div>
    <div class="card-body" style="text-align:center;padding:2rem">
        <p>Connecte en tant que <strong><?= htmlspecialchars($auth->name() ?? '') ?></strong> (<?= htmlspecialchars($auth->role() ?? '') ?>)</p>
        <a href="/logout" class="btn btn-danger btn-lg" onclick="return confirm('Voulez-vous vraiment vous deconnecter ?')">Deconnexion</a>
    </div>
</div>
