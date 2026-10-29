<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="<?= htmlspecialchars($_SESSION['csrf_token'] ?? '') ?>">
    <title><?= $appName ?? 'Restaurant ADAM' ?> - Administration</title>
    <link rel="stylesheet" href="/css/common.css">
    <link rel="stylesheet" href="/css/admin.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="admin-body">
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-logo">
                <span class="logo-icon"><i data-lucide="utensils"></i></span>
                <span class="logo-text">ADAM</span>
            </div>
            <button class="sidebar-close" id="sidebarClose"><i data-lucide="x"></i></button>
        </div>
        <nav class="sidebar-nav">
            <a href="/admin/dashboard" class="nav-item <?= str_contains($currentPage ?? '', 'dashboard') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="layout-dashboard"></i></span>
                <span class="nav-label">Dashboard</span>
            </a>
            <a href="/admin/menu" class="nav-item <?= str_contains($currentPage ?? '', 'menu') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="clipboard-list"></i></span>
                <span class="nav-label">Menu</span>
            </a>
            <a href="/admin/categories" class="nav-item <?= str_contains($currentPage ?? '', 'categories') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="tag"></i></span>
                <span class="nav-label">Catégories</span>
            </a>
            <a href="/admin/orders/pos" class="nav-item <?= str_contains($currentPage ?? '', 'pos') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="shopping-cart"></i></span>
                <span class="nav-label">POS</span>
            </a>
            <a href="/admin/orders" class="nav-item <?= str_contains($currentPage ?? '', 'orders') && !str_contains($currentPage ?? '', 'pos') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="receipt"></i></span>
                <span class="nav-label">Commandes</span>
            </a>
            <a href="/admin/orders/kitchen" class="nav-item <?= str_contains($currentPage ?? '', 'kitchen') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="chef-hat"></i></span>
                <span class="nav-label">Cuisine</span>
            </a>
            <a href="/admin/tables" class="nav-item <?= str_contains($currentPage ?? '', 'tables') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="armchair"></i></span>
                <span class="nav-label">Plan de salle</span>
            </a>
            <a href="/admin/reservations" class="nav-item <?= str_contains($currentPage ?? '', 'reservations') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="calendar"></i></span>
                <span class="nav-label">Réservations</span>
            </a>
            <a href="/admin/cash" class="nav-item <?= str_contains($currentPage ?? '', 'cash') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="wallet"></i></span>
                <span class="nav-label">Caisse</span>
            </a>
            <a href="/admin/stock" class="nav-item <?= str_contains($currentPage ?? '', 'stock') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="package"></i></span>
                <span class="nav-label">Stock</span>
            </a>
            <a href="/admin/expenses" class="nav-item <?= str_contains($currentPage ?? '', 'expenses') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="banknote"></i></span>
                <span class="nav-label">Depenses</span>
            </a>
            <?php if ($auth && in_array($auth->role(), ['admin', 'manager'])): ?>
            <a href="/admin/staff" class="nav-item <?= str_contains($currentPage ?? '', 'staff') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="users"></i></span>
                <span class="nav-label">Personnel</span>
            </a>
            <a href="/admin/loyalty" class="nav-item <?= str_contains($currentPage ?? '', 'loyalty') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="star"></i></span>
                <span class="nav-label">Fidélité</span>
            </a>
            <a href="/admin/reports" class="nav-item <?= str_contains($currentPage ?? '', 'reports') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="trending-up"></i></span>
                <span class="nav-label">Rapports</span>
            </a>
            <?php endif; ?>
            <?php if ($auth && $auth->role() === 'admin'): ?>
            <a href="/admin/settings" class="nav-item <?= str_contains($currentPage ?? '', 'settings') ? 'active' : '' ?>">
                <span class="nav-icon"><i data-lucide="settings"></i></span>
                <span class="nav-label">Paramètres</span>
            </a>
            <?php endif; ?>
        </nav>
        <div class="sidebar-footer">
            <div class="sidebar-user">
                <span class="user-avatar"><?= strtoupper(substr($auth->name() ?? 'A', 0, 1)) ?></span>
                <div class="user-info">
                    <span class="user-name"><?= htmlspecialchars($auth->name() ?? '') ?></span>
                    <span class="user-role"><?= htmlspecialchars($auth->role() ?? '') ?></span>
                </div>
            </div>
            <a href="/logout" class="nav-item logout-link">
                <span class="nav-icon"><i data-lucide="log-out"></i></span>
                <span class="nav-label">Déconnexion</span>
            </a>
        </div>
    </aside>

    <main class="admin-main" id="mainContent">
        <header class="admin-header">
            <button class="sidebar-toggle" id="sidebarToggle"><i data-lucide="menu"></i></button>
            <h1 class="page-title"><?= $pageTitle ?? 'Dashboard' ?></h1>
            <div class="header-actions">
                <span class="header-date"><?= date('d/m/Y H:i') ?></span>
                <a href="/logout" class="btn btn-sm btn-outline" style="margin-left:.75rem" onclick="return confirm('Deconnexion ?')">Deconnexion</a>
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

        <div class="admin-content">
            <?= $content ?>
        </div>
    </main>

    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="/js/admin.js"></script>
    <script>
        lucide.createIcons();
        if (typeof autoCloseAlerts === 'function') autoCloseAlerts();
    </script>
</body>
</html>
