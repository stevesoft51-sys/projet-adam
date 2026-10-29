<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="<?= htmlspecialchars($_SESSION['csrf_token'] ?? '') ?>">
    <title><?= $appName ?? 'Restaurant ADAM' ?> - Guichet</title>
    <link rel="stylesheet" href="/css/common.css">
    <link rel="stylesheet" href="/css/admin.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        .guichet-body { display: flex; min-height: 100vh; }
        .guichet-sidebar {
            width: 240px;
            background: #1a1d29;
            color: #fff;
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0; left: 0; bottom: 0;
            z-index: 100;
            transition: transform .3s;
        }
        .guichet-sidebar-header {
            padding: 1.25rem;
            display: flex;
            align-items: center;
            gap: .75rem;
            border-bottom: 1px solid rgba(255,255,255,.08);
        }
        .guichet-sidebar-header .logo-icon { font-size: 1.5rem; }
        .guichet-sidebar-header .logo-text { font-size: 1.1rem; font-weight: 700; letter-spacing: .5px; }
        .guichet-nav { flex: 1; padding: .5rem 0; overflow-y: auto; }
        .guichet-nav .nav-item {
            display: flex; align-items: center; gap: .75rem;
            padding: .75rem 1.25rem;
            color: rgba(255,255,255,.65);
            text-decoration: none;
            font-size: .9rem;
            transition: all .2s;
            border-left: 3px solid transparent;
        }
        .guichet-nav .nav-item:hover { background: rgba(255,255,255,.06); color: #fff; }
        .guichet-nav .nav-item.active {
            background: rgba(255,255,255,.1);
            color: #fff;
            border-left-color: #6c5ce7;
        }
        .guichet-nav .nav-icon { font-size: 1.15rem; width: 24px; text-align: center; }
        .guichet-sidebar-footer {
            padding: 1rem 1.25rem;
            border-top: 1px solid rgba(255,255,255,.08);
        }
        .guichet-user {
            display: flex; align-items: center; gap: .75rem; margin-bottom: .75rem;
        }
        .guichet-user .user-avatar {
            width: 36px; height: 36px; border-radius: 50%;
            background: #6c5ce7; color: #fff;
            display: flex; align-items: center; justify-content: center;
            font-weight: 600; font-size: .85rem;
        }
        .guichet-user .user-name { font-size: .85rem; font-weight: 500; color: #fff; }
        .guichet-user .user-role { font-size: .75rem; color: rgba(255,255,255,.45); text-transform: uppercase; letter-spacing: .5px; }
        .guichet-main {
            flex: 1;
            margin-left: 240px;
            display: flex; flex-direction: column;
            min-height: 100vh;
        }
        .guichet-header {
            background: #fff;
            padding: .75rem 1.5rem;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid #eee;
            position: sticky; top: 0; z-index: 50;
        }
        .guichet-header h1 { font-size: 1.15rem; font-weight: 600; color: #1a1d29; margin: 0; }
        .guichet-header .header-date { font-size: .85rem; color: #666; }
        .guichet-content { flex: 1; padding: 1.5rem; background: #f5f6fa; }
        .sidebar-close { display: none; background: none; border: none; color: rgba(255,255,255,.6); font-size: 1.2rem; cursor: pointer; position: absolute; top: .75rem; right: .75rem; }
        .sidebar-toggle { display: none; background: none; border: none; font-size: 1.3rem; cursor: pointer; color: #333; }
        @media (max-width: 768px) {
            .guichet-sidebar { transform: translateX(-100%); }
            .guichet-sidebar.open { transform: translateX(0); }
            .guichet-main { margin-left: 0; }
            .sidebar-toggle { display: block; }
            .sidebar-close { display: block; }
        }
        .logout-link { color: rgba(255,255,255,.45) !important; font-size: .85rem; }
        .logout-link:hover { color: #e74c3c !important; }
    </style>
</head>
<body class="guichet-body">
    <aside class="guichet-sidebar" id="sidebar">
        <div class="guichet-sidebar-header">
            <span class="logo-icon"><i data-lucide="utensils"></i></span>
            <span class="logo-text">ADAM</span>
            <button class="sidebar-close" id="sidebarClose"><i data-lucide="x"></i></button>
        </div>
        <nav class="guichet-nav">
            <a href="/guichet" class="nav-item <?= ($currentPage ?? '') === 'guichet/dashboard' ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="layout-dashboard"></i></span>
                <span>Tableau de bord</span>
            </a>
            <a href="/guichet/pos" class="nav-item <?= str_contains($currentPage ?? '', 'pos') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="shopping-cart"></i></span>
                <span>Nouvelle commande</span>
            </a>
            <a href="/guichet/factures" class="nav-item <?= str_contains($currentPage ?? '', 'factures') || str_contains($currentPage ?? '', 'bill') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="receipt"></i></span>
                <span>Factures</span>
            </a>
            <a href="/guichet/caisse" class="nav-item <?= str_contains($currentPage ?? '', 'caisse') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="wallet"></i></span>
                <span>Caisse</span>
            </a>
        </nav>
        <div class="guichet-sidebar-footer">
            <div class="guichet-user">
                <span class="user-avatar"><?= strtoupper(substr($auth->name() ?? 'G', 0, 1)) ?></span>
                <div>
                    <div class="user-name"><?= htmlspecialchars($auth->name() ?? '') ?></div>
                    <div class="user-role">Guichet</div>
                </div>
            </div>
            <a href="/logout" class="nav-item logout-link">
                <span class="nav-icon"><i data-lucide="log-out"></i></span>
                <span>Deconnexion</span>
            </a>
        </div>
    </aside>

    <main class="guichet-main" id="mainContent">
        <header class="guichet-header">
            <button class="sidebar-toggle" id="sidebarToggle"><i data-lucide="menu"></i></button>
            <h1><?= $pageTitle ?? 'Guichet' ?></h1>
            <div class="header-actions">
                <span class="header-date"><?= date('d/m/Y H:i') ?></span>
            </div>
        </header>

        <?php if (isset($_SESSION['success'])): ?>
            <div class="alert alert-success" id="alertSuccess">
                <?= htmlspecialchars($_SESSION['success']) ?>
                <button class="alert-close" onclick="this.parentElement.remove()"><i data-lucide="x"></i></button>
            </div>
            <?php unset($_SESSION['success']); ?>
        <?php endif; ?>

        <?php if (isset($_SESSION['error'])): ?>
            <div class="alert alert-error" id="alertError">
                <?= htmlspecialchars($_SESSION['error']) ?>
                <button class="alert-close" onclick="this.parentElement.remove()"><i data-lucide="x"></i></button>
            </div>
            <?php unset($_SESSION['error']); ?>
        <?php endif; ?>

        <div class="guichet-content">
            <?= $content ?>
        </div>
    </main>

    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="/js/admin.js"></script>
    <script>
        lucide.createIcons();
        // Sidebar toggle
        const sidebar = document.getElementById('sidebar');
        const toggle = document.getElementById('sidebarToggle');
        const close = document.getElementById('sidebarClose');
        if (toggle) toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
        if (close) close.addEventListener('click', () => sidebar.classList.remove('open'));
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== toggle) {
                sidebar.classList.remove('open');
            }
        });
        if (typeof autoCloseAlerts === 'function') autoCloseAlerts();
    </script>
</body>
</html>
