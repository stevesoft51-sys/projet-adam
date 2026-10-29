<?php $pageTitle = 'Ticket de reservation'; ?>
<section class="section">
    <div class="container container-sm">
        <div class="ticket" id="reservationTicket">
            <div class="ticket-header">
                <div class="ticket-logo"><i data-lucide="utensils"></i> Restaurant ADAM</div>
                <div class="ticket-badge">CONFIRMEE</div>
            </div>
            <div class="ticket-code">
                <span class="ticket-code-label">Code de reservation</span>
                <span class="ticket-code-value"><?= htmlspecialchars($reservation['code']) ?></span>
            </div>
            <div class="ticket-details">
                <div class="ticket-row">
                    <span class="ticket-label">Nom</span>
                    <span class="ticket-value"><?= htmlspecialchars($reservation['customer_name']) ?></span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-label">Telephone</span>
                    <span class="ticket-value"><?= htmlspecialchars($reservation['customer_phone']) ?></span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-label">Date</span>
                    <span class="ticket-value"><?= View::date($reservation['date'], 'l d F Y') ?></span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-label">Heure</span>
                    <span class="ticket-value"><?= substr($reservation['time'], 0, 5) ?></span>
                </div>
                <div class="ticket-row">
                    <span class="ticket-label">Personnes</span>
                    <span class="ticket-value"><?= $reservation['guests'] ?></span>
                </div>
                <?php if ($reservation['table_id']): ?>
                    <div class="ticket-row">
                        <span class="ticket-label">Table</span>
                        <span class="ticket-value">Auto-assignee</span>
                    </div>
                <?php endif; ?>
            </div>
            <div class="ticket-footer">
                <p>Presentez ce code a l'arrivee</p>
                <p class="ticket-address"><?= htmlspecialchars($settings['restaurant_address'] ?? 'Abidjan, Cote d\'Ivoire') ?></p>
            </div>
        </div>

        <div class="ticket-actions">
            <button onclick="window.print()" class="btn btn-primary btn-lg">Imprimer le ticket</button>
            <a href="/" class="btn btn-outline btn-lg">Retour a l'accueil</a>
        </div>
    </div>
</section>

<style>
@media print {
    .client-header, .client-footer, .ticket-actions, .client-alert { display: none !important; }
    .ticket { box-shadow: none; border: 2px solid #000; }
    body { background: #fff; }
}
</style>
