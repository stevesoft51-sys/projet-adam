<?php $pageTitle = 'Reservation'; ?>
<section class="reservation-hero">
    <div class="container">
        <h1>Reservez votre table</h1>
        <p>Assurez-vous d'avoir votre place a Restaurant ADAM</p>
    </div>
</section>

<section class="section">
    <div class="container container-sm">
        <?php if (!empty($errors)): ?>
            <div class="alert alert-error">
                <?php foreach ($errors as $field => $fieldErrors): ?>
                    <?php foreach ($fieldErrors as $err): ?>
                        <p><?= htmlspecialchars($err) ?></p>
                    <?php endforeach; ?>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <form method="POST" action="/reservation" class="reservation-form" id="reservationForm">
            <?= csrf_field() ?>
            <div class="form-row">
                <div class="form-group form-col-2">
                    <label>Votre nom *</label>
                    <input type="text" name="customer_name" required class="form-control" value="<?= htmlspecialchars($old['customer_name'] ?? '') ?>" placeholder="Jean Dupont">
                </div>
                <div class="form-group form-col-2">
                    <label>Telephone *</label>
                    <input type="text" name="customer_phone" required class="form-control" value="<?= htmlspecialchars($old['customer_phone'] ?? '') ?>" placeholder="+225 00 00 00 00">
                </div>
            </div>
            <div class="form-group">
                <label>Email (optionnel)</label>
                <input type="email" name="customer_email" class="form-control" value="<?= htmlspecialchars($old['customer_email'] ?? '') ?>" placeholder="jean@email.com">
            </div>
            <div class="form-row">
                <div class="form-group form-col-2">
                    <label>Date *</label>
                    <input type="date" name="date" required class="form-control" value="<?= htmlspecialchars($old['date'] ?? date('Y-m-d')) ?>" min="<?= date('Y-m-d') ?>">
                </div>
                <div class="form-group form-col-2">
                    <label>Heure *</label>
                    <select name="time" required class="form-control">
                        <option value="">Choisir l'heure</option>
                        <?php for ($h = 8; $h <= 22; $h++): ?>
                            <?php for ($m = 0; $m < 60; $m += 30): ?>
                                <?php $t = sprintf('%02d:%02d', $h, $m); ?>
                                <option value="<?= $t ?>" <?= ($old['time'] ?? '') === $t ? 'selected' : '' ?>><?= $t ?></option>
                            <?php endfor; ?>
                        <?php endfor; ?>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>Nombre de personnes *</label>
                <select name="guests" required class="form-control">
                    <?php for ($i = 1; $i <= 20; $i++): ?>
                        <option value="<?= $i ?>" <?= ($old['guests'] ?? '2') == $i ? 'selected' : '' ?>><?= $i ?> personne<?= $i > 1 ? 's' : '' ?></option>
                    <?php endfor; ?>
                </select>
            </div>
            <div class="form-group">
                <label>Notes speciales (optionnel)</label>
                <textarea name="notes" class="form-control" rows="3" placeholder="Allergies, occasion speciale, etc."><?= htmlspecialchars($old['notes'] ?? '') ?></textarea>
            </div>
            <button type="submit" class="btn btn-primary btn-lg btn-block">Confirmer la reservation</button>
            <p class="form-note">Vous recevrez un code de reservation unique</p>
        </form>
    </div>
</section>
