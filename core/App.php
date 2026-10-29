<?php

class App
{
    private Router $router;
    private array $config;

    public function __construct()
    {
        $this->router = new Router();
        $this->config = require CONFIG_PATH . '/app.php';
        date_default_timezone_set($this->config['timezone']);
    }

    public function run(): void
    {
        $this->registerRoutes();
        $method = Request::method();
        $uri = Request::uri();
        $this->router->dispatch($method, $uri);
    }

    private function registerRoutes(): void
    {
        $r = $this->router;

        // Auth routes
        $r->get('/login', AuthController::class, 'showLogin');
        $r->post('/login', AuthController::class, 'login');
        $r->get('/logout', AuthController::class, 'logout');

        // Client routes (public)
        $r->get('/', HomeController::class, 'index');
        $r->get('/menu', ClientMenuController::class, 'index');
        $r->get('/reservation', ClientReservationController::class, 'index');
        $r->post('/reservation', ClientReservationController::class, 'store');
        $r->get('/reservation/ticket', ClientReservationController::class, 'ticket');

        // Admin routes
        $r->get('/admin', AdminDashboardController::class, 'index');
        $r->get('/admin/dashboard', AdminDashboardController::class, 'index');

        // Menu management
        $r->get('/admin/menu', AdminMenuController::class, 'index');
        $r->get('/admin/menu/create', AdminMenuController::class, 'create');
        $r->post('/admin/menu', AdminMenuController::class, 'store');
        $r->get('/admin/menu/edit', AdminMenuController::class, 'edit');
        $r->post('/admin/menu/update', AdminMenuController::class, 'update');
        $r->post('/admin/menu/delete', AdminMenuController::class, 'delete');
        $r->post('/admin/menu/toggle', AdminMenuController::class, 'toggle');

        // Categories
        $r->get('/admin/categories', AdminMenuController::class, 'categories');
        $r->post('/admin/categories', AdminMenuController::class, 'storeCategory');
        $r->post('/admin/categories/delete', AdminMenuController::class, 'deleteCategory');

        // Stock management
        $r->get('/admin/stock', AdminStockController::class, 'index');
        $r->get('/admin/stock/inventory', AdminStockController::class, 'inventory');
        $r->get('/admin/stock/movements', AdminStockController::class, 'movements');
        $r->post('/admin/stock/movement', AdminStockController::class, 'addMovement');
        $r->post('/admin/stock/adjust', AdminStockController::class, 'adjust');

        // Orders & POS
        $r->get('/admin/orders', AdminOrderController::class, 'index');
        $r->get('/admin/orders/pos', AdminOrderController::class, 'pos');
        $r->post('/admin/orders/create', AdminOrderController::class, 'create');
        $r->post('/admin/orders/update-status', AdminOrderController::class, 'updateStatus');
        $r->get('/admin/orders/kitchen', AdminOrderController::class, 'kitchen');
        $r->post('/admin/orders/add-item', AdminOrderController::class, 'addItem');
        $r->post('/admin/orders/remove-item', AdminOrderController::class, 'removeItem');

        // Tables & Floor plan
        $r->get('/admin/tables', AdminTableController::class, 'index');
        $r->post('/admin/tables', AdminTableController::class, 'store');
        $r->post('/admin/tables/update', AdminTableController::class, 'update');
        $r->post('/admin/tables/delete', AdminTableController::class, 'delete');
        $r->post('/admin/tables/status', AdminTableController::class, 'updateStatus');

        // Reservations
        $r->get('/admin/reservations', AdminReservationController::class, 'index');
        $r->post('/admin/reservations', AdminReservationController::class, 'store');
        $r->post('/admin/reservations/update', AdminReservationController::class, 'update');
        $r->post('/admin/reservations/delete', AdminReservationController::class, 'delete');
        $r->post('/admin/reservations/status', AdminReservationController::class, 'updateStatus');

        // Cash register
        $r->get('/admin/cash', AdminCashController::class, 'index');
        $r->get('/admin/cash/history', AdminCashController::class, 'history');
        $r->post('/admin/cash/open', AdminCashController::class, 'open');
        $r->post('/admin/cash/close', AdminCashController::class, 'close');
        $r->post('/admin/cash/movement', AdminCashController::class, 'addMovement');
        $r->post('/admin/cash/payment', AdminCashController::class, 'processPayment');

        // Staff management
        $r->get('/admin/staff', AdminStaffController::class, 'index');
        $r->get('/admin/staff/schedule', AdminStaffController::class, 'schedule');
        $r->get('/admin/staff/performance', AdminStaffController::class, 'performance');
        $r->post('/admin/staff', AdminStaffController::class, 'store');
        $r->post('/admin/staff/update', AdminStaffController::class, 'update');
        $r->post('/admin/staff/delete', AdminStaffController::class, 'delete');
        $r->post('/admin/staff/shift', AdminStaffController::class, 'addShift');

        // Loyalty
        $r->get('/admin/loyalty', AdminLoyaltyController::class, 'index');
        $r->post('/admin/loyalty/card', AdminLoyaltyController::class, 'createCard');
        $r->post('/admin/loyalty/points', AdminLoyaltyController::class, 'addPoints');

        // Reports & Analytics
        $r->get('/admin/reports', AdminReportsController::class, 'index');
        $r->get('/admin/reports/sales', AdminReportsController::class, 'sales');
        $r->get('/admin/reports/analytics', AdminReportsController::class, 'analytics');
        $r->get('/admin/reports/export', AdminReportsController::class, 'export');

        // Settings
        $r->get('/admin/settings', AdminSettingsController::class, 'index');
        $r->post('/admin/settings', AdminSettingsController::class, 'update');
        $r->post('/admin/settings/password', AdminSettingsController::class, 'updatePassword');

        // Expenses
        $r->get('/admin/expenses', AdminExpenseController::class, 'index');
        $r->post('/admin/expenses', AdminExpenseController::class, 'store');
        $r->post('/admin/expenses/delete', AdminExpenseController::class, 'delete');

        // Guichet routes
        $r->get('/guichet', GuichetController::class, 'dashboard');
        $r->get('/guichet/dashboard', GuichetController::class, 'dashboard');
        $r->get('/guichet/pos', GuichetController::class, 'pos');
        $r->post('/guichet/orders/create', GuichetController::class, 'createOrder');
        $r->post('/guichet/orders/add-item', GuichetController::class, 'addItem');
        $r->post('/guichet/orders/remove-item', GuichetController::class, 'removeItem');
        $r->post('/guichet/orders/update-status', GuichetController::class, 'updateStatus');
        $r->get('/guichet/caisse', GuichetController::class, 'caisse');
        $r->post('/guichet/caisse/open', GuichetController::class, 'openCash');
        $r->post('/guichet/caisse/close', GuichetController::class, 'closeCash');
        $r->post('/guichet/caisse/movement', GuichetController::class, 'addMovement');
        $r->post('/guichet/payment/process', GuichetController::class, 'processPayment');
        $r->get('/guichet/factures', GuichetController::class, 'factures');
        $r->get('/guichet/bill', GuichetController::class, 'bill');
    }
}
