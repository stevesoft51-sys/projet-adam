<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="<?= htmlspecialchars($_SESSION['csrf_token'] ?? '') ?>">
    <title><?= $appName ?? 'Restaurant ADAM' ?> - <?= $pageTitle ?? 'Accueil' ?></title>
    <link rel="stylesheet" href="/css/common.css">
    <link rel="stylesheet" href="/css/client.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body class="client-body">
    <header class="client-header">
        <div class="container">
            <div class="header-inner">
                <a href="/" class="client-logo">
                    <span class="logo-icon"><i data-lucide="utensils"></i></span>
                    <span class="logo-text">ADAM</span>
                </a>
                <button class="mobile-menu-toggle" id="mobileMenuToggle"><i data-lucide="menu"></i></button>
                <nav class="client-nav" id="clientNav">
                    <a href="/" class="nav-link">Accueil</a>
                    <a href="/menu" class="nav-link">La Carte</a>
                    <a href="/reservation" class="nav-link">Réservation</a>
                    <a href="/menu" class="nav-link nav-cta">Commander</a>
                </nav>
            </div>
        </div>
    </header>

    <?php if (isset($_SESSION['success'])): ?>
        <div class="alert alert-success client-alert">
            <?= htmlspecialchars($_SESSION['success']) ?>
            <button class="alert-close" onclick="this.parentElement.remove()"><i data-lucide="x"></i></button>
        </div>
        <?php unset($_SESSION['success']); ?>
    <?php endif; ?>

    <?php if (isset($_SESSION['error'])): ?>
        <div class="alert alert-error client-alert">
            <?= htmlspecialchars($_SESSION['error']) ?>
            <button class="alert-close" onclick="this.parentElement.remove()"><i data-lucide="x"></i></button>
        </div>
        <?php unset($_SESSION['error']); ?>
    <?php endif; ?>

    <main class="client-main">
        <?= $content ?>
    </main>

    <footer class="client-footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-col">
                    <h3><i data-lucide="utensils" style="width:1em;height:1em;vertical-align:-0.15em;margin-right:0.3em"></i> Restaurant ADAM</h3>
                    <p><?= htmlspecialchars($settings['restaurant_address'] ?? 'Abidjan, Côte d\'Ivoire') ?></p>
                    <p><i data-lucide="phone" style="width:1em;height:1em;vertical-align:-0.15em;margin-right:0.3em"></i> <?= htmlspecialchars($settings['restaurant_phone'] ?? '+225 00 00 00 00') ?></p>
                </div>
                <div class="footer-col">
                    <h3>Horaires</h3>
                    <p>Lun - Dim</p>
                    <p><?= htmlspecialchars($settings['opening_time'] ?? '08:00') ?> - <?= htmlspecialchars($settings['closing_time'] ?? '23:00') ?></p>
                </div>
                <div class="footer-col">
                    <h3>Navigation</h3>
                    <a href="/">Accueil</a>
                    <a href="/menu">La Carte</a>
                    <a href="/reservation">Réservation</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; <?= date('Y') ?> Restaurant ADAM. Tous droits réservés.</p>
            </div>
        </div>
    </footer>

    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="/js/client.js"></script>
    <script>lucide.createIcons();</script>
</body>
</html>
