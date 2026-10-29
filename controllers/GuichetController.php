<?php

class GuichetController extends Controller
{
    private OrderModel $orderModel;
    private CashRegisterModel $cashModel;

    public function __construct()
    {
        parent::__construct();
        $this->orderModel = new OrderModel();
        $this->cashModel = new CashRegisterModel();
    }

    public function dashboard(): void
    {
        AuthMiddleware::role('guichet');
        $today = date('Y-m-d');
        $orderModel = $this->orderModel;
        $paymentModel = new PaymentModel();

        $data = [
            'todayOrders' => $orderModel->countToday(),
            'todayRevenue' => $paymentModel->sumToday(),
            'activeOrders' => $orderModel->getActive(),
            'recentOrders' => $orderModel->getRecent(10),
            'openRegister' => $this->cashModel->getOpen(),
            'todayPaymentsCash' => (float)$this->db->query(
                "SELECT COALESCE(SUM(amount),0) FROM payments WHERE DATE(created_at) = ? AND status = 'completed' AND method = 'cash'",
                [$today]
            )->fetchColumn(),
            'todayPaymentsMobile' => (float)$this->db->query(
                "SELECT COALESCE(SUM(amount),0) FROM payments WHERE DATE(created_at) = ? AND status = 'completed' AND method = 'mobile_money'",
                [$today]
            )->fetchColumn(),
            'todayPaymentsCard' => (float)$this->db->query(
                "SELECT COALESCE(SUM(amount),0) FROM payments WHERE DATE(created_at) = ? AND status = 'completed' AND method = 'card'",
                [$today]
            )->fetchColumn(),
        ];

        $this->view->renderGuichet('guichet/dashboard', $data);
    }

    public function pos(): void
    {
        AuthMiddleware::role('guichet');
        $categories = (new CategoryModel())->getActive();
        $products = (new ProductModel())->getAvailable();
        $tables = (new RestaurantTableModel())->getAvailable();
        $cashRegister = $this->cashModel->getOpen();
        $activeOrders = $this->orderModel->getActive();
        $this->view->renderGuichet('guichet/pos', compact('categories', 'products', 'tables', 'cashRegister', 'activeOrders'));
    }

    public function createOrder(): void
    {
        AuthMiddleware::role('guichet');
        AuthMiddleware::csrf();

        $items = json_decode($_POST['items'] ?? '[]', true);
        if (empty($items)) {
            $_SESSION['error'] = 'Aucun produit selectionne';
            $this->redirect('/guichet/pos');
        }

        $orderData = [
            'table_id' => !empty($_POST['table_id']) ? (int)$_POST['table_id'] : null,
            'user_id' => $this->auth->id(),
            'type' => $_POST['order_type'] ?? 'dine_in',
            'notes' => $_POST['notes'] ?? null,
        ];

        $orderId = $this->orderModel->createWithItems($orderData, $items);

        if (!empty($_POST['table_id'])) {
            (new RestaurantTableModel())->updateStatus((int)$_POST['table_id'], 'occupied');
        }

        if (Request::isAjax()) {
            $order = $this->orderModel->getWithItems($orderId);
            $this->json(['success' => true, 'order' => $order]);
        }

        $_SESSION['success'] = 'Commande #' . $orderId . ' creee';
        $this->redirect('/guichet/pos');
    }

    public function addItem(): void
    {
        AuthMiddleware::role('guichet');
        AuthMiddleware::csrf();

        $orderId = (int)($_POST['order_id'] ?? 0);
        $productId = (int)($_POST['product_id'] ?? 0);
        $quantity = (int)($_POST['quantity'] ?? 1);

        $product = (new ProductModel())->find($productId);
        if (!$product) {
            $this->json(['error' => 'Produit introuvable'], 404);
        }

        $this->orderModel->addItem($orderId, [
            'product_id' => $productId,
            'quantity' => $quantity,
            'unit_price' => $product['price'],
            'notes' => $_POST['notes'] ?? null,
        ]);

        $order = $this->orderModel->getWithItems($orderId);
        $this->json(['success' => true, 'order' => $order]);
    }

    public function removeItem(): void
    {
        AuthMiddleware::role('guichet');
        AuthMiddleware::csrf();

        $itemId = (int)($_POST['item_id'] ?? 0);
        $this->orderModel->removeItem($itemId);

        $orderId = (int)($_POST['order_id'] ?? 0);
        $order = $this->orderModel->getWithItems($orderId);
        $this->json(['success' => true, 'order' => $order]);
    }

    public function updateStatus(): void
    {
        AuthMiddleware::role('guichet');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $status = $_POST['status'] ?? '';

        $validStatuses = ['pending', 'confirmed', 'preparing', 'ready', 'served', 'paid', 'cancelled'];
        if (!in_array($status, $validStatuses)) {
            $this->json(['error' => 'Statut invalide'], 400);
        }

        $this->orderModel->updateStatus($id, $status);

        $order = $this->orderModel->find($id);
        if ($order && $order['table_id']) {
            if ($status === 'paid' || $status === 'cancelled') {
                (new RestaurantTableModel())->updateStatus($order['table_id'], 'free');
            }
        }

        if (Request::isAjax()) {
            $this->json(['success' => true, 'message' => 'Statut mis a jour']);
        }

        $_SESSION['success'] = 'Statut mis a jour';
        $this->redirect('/guichet/factures');
    }

    public function caisse(): void
    {
        AuthMiddleware::role('guichet');
        $openRegister = $this->cashModel->getOpen();
        $movements = $openRegister ? $this->cashModel->getMovements($openRegister['id']) : [];
        $this->view->renderGuichet('guichet/caisse', compact('openRegister', 'movements'));
    }

    public function openCash(): void
    {
        AuthMiddleware::role('guichet');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'opening_amount' => 'required|numeric',
            'notes' => 'max:500',
        ]);

        try {
            $this->cashModel->open(
                $this->auth->id(),
                (float)$validated['opening_amount'],
                $validated['notes'] ?? null
            );
            $_SESSION['success'] = 'Caisse ouverte';
        } catch (Exception $e) {
            $_SESSION['error'] = $e->getMessage();
        }

        $this->redirect('/guichet/caisse');
    }

    public function closeCash(): void
    {
        AuthMiddleware::role('guichet');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $validated = $this->validate([
            'closing_amount' => 'required|numeric',
            'notes' => 'max:500',
        ]);

        try {
            $this->cashModel->close(
                $id,
                (float)$validated['closing_amount'],
                $validated['notes'] ?? null
            );
            $_SESSION['success'] = 'Caisse fermee';
        } catch (Exception $e) {
            $_SESSION['error'] = $e->getMessage();
        }

        $this->redirect('/guichet/caisse');
    }

    public function addMovement(): void
    {
        AuthMiddleware::role('guichet');
        AuthMiddleware::csrf();

        $openRegister = $this->cashModel->getOpen();
        if (!$openRegister) {
            $_SESSION['error'] = 'Aucune caisse ouverte';
            $this->redirect('/guichet/caisse');
        }

        $validated = $this->validate([
            'type' => 'required|in:in,out',
            'amount' => 'required|numeric',
            'reason' => 'required|max:255',
        ]);

        $this->cashModel->addMovement(
            $openRegister['id'],
            $validated['type'],
            (float)$validated['amount'],
            $validated['reason'],
            $this->auth->id()
        );

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Mouvement enregistre';
        $this->redirect('/guichet/caisse');
    }

    public function processPayment(): void
    {
        AuthMiddleware::role('guichet');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'order_id' => 'required|integer',
            'amount' => 'required|numeric',
            'method' => 'required|in:cash,mobile_money,card',
        ]);

        $openRegister = $this->cashModel->getOpen();

        $paymentData = [
            'order_id' => (int)$validated['order_id'],
            'amount' => (float)$validated['amount'],
            'method' => $validated['method'],
            'status' => 'completed',
            'received_by' => $this->auth->id(),
            'cash_register_id' => $openRegister ? $openRegister['id'] : null,
            'phone_number' => $_POST['phone_number'] ?? null,
            'notes' => $_POST['payment_notes'] ?? null,
        ];

        (new PaymentModel())->processPayment($paymentData);

        if (Request::isAjax()) {
            $this->json(['success' => true, 'message' => 'Paiement enregistre']);
        }

        $_SESSION['success'] = 'Paiement enregistre';
        $this->redirect('/guichet/factures');
    }

    public function factures(): void
    {
        AuthMiddleware::role('guichet');
        $today = date('Y-m-d');
        $dateFrom = $_GET['date_from'] ?? $today;
        $dateTo = $_GET['date_to'] ?? $today;
        $statusFilter = $_GET['status'] ?? '';

        $sql = "SELECT o.*, t.number as table_number, u.name as server_name,
                       (SELECT COALESCE(SUM(amount),0) FROM payments WHERE order_id = o.id AND status = 'completed') as amount_paid
                FROM orders o
                LEFT JOIN tables_restaurant t ON o.table_id = t.id
                LEFT JOIN users u ON o.user_id = u.id
                WHERE DATE(o.created_at) BETWEEN ? AND ?";
        $params = [$dateFrom, $dateTo];

        if ($statusFilter) {
            $sql .= " AND o.status = ?";
            $params[] = $statusFilter;
        }
        $sql .= " ORDER BY o.created_at DESC";

        $orders = $this->db->query($sql, $params)->fetchAll();

        $this->view->renderGuichet('guichet/factures', compact('orders', 'dateFrom', 'dateTo', 'statusFilter'));
    }

    public function bill(): void
    {
        AuthMiddleware::role('guichet');
        $id = (int)($_GET['id'] ?? 0);
        $order = $this->orderModel->getWithItems($id);

        if (!$order) {
            $_SESSION['error'] = 'Commande introuvable';
            $this->redirect('/guichet/factures');
        }

        $payments = (new PaymentModel())->getByOrder($id);
        $restaurant = [
            'name' => SettingModel::getValue('restaurant_name', 'Restaurant ADAM'),
            'phone' => SettingModel::getValue('restaurant_phone', ''),
            'address' => SettingModel::getValue('restaurant_address', ''),
        ];

        $this->view->renderGuichet('guichet/bill', compact('order', 'payments', 'restaurant'));
    }

    public function printBill(): void
    {
        AuthMiddleware::role('guichet');
        $this->bill();
    }
}
