<?php

class AdminOrderController extends Controller
{
    private OrderModel $orderModel;

    public function __construct()
    {
        parent::__construct();
        $this->orderModel = new OrderModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('orders');
        $orders = $this->orderModel->getActive();
        $this->view->renderAdmin('admin/orders/index', compact('orders'));
    }

    public function pos(): void
    {
        AuthMiddleware::can('orders');
        $categories = (new CategoryModel())->getActive();
        $products = (new ProductModel())->getAvailable();
        $tables = (new RestaurantTableModel())->getAvailable();
        $cashRegister = (new CashRegisterModel())->getOpen();
        $activeOrders = $this->orderModel->getActive();
        $this->view->renderAdmin('admin/orders/pos', compact('categories', 'products', 'tables', 'cashRegister', 'activeOrders'));
    }

    public function create(): void
    {
        AuthMiddleware::can('orders');
        AuthMiddleware::csrf();

        $items = json_decode($_POST['items'] ?? '[]', true);
        if (empty($items)) {
            $_SESSION['error'] = 'Aucun produit sélectionné';
            $this->redirect('/admin/orders/pos');
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

        $_SESSION['success'] = 'Commande créée';
        $this->redirect('/admin/orders');
    }

    public function updateStatus(): void
    {
        AuthMiddleware::can('orders');
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
            } elseif ($status === 'served') {
                (new RestaurantTableModel())->updateStatus($order['table_id'], 'occupied');
            }
        }

        if ($status === 'confirmed') {
            $productModel = new ProductModel();
            $productModel->deductIngredients($id);
        }

        if (Request::isAjax()) {
            $this->json(['success' => true, 'message' => 'Statut mis à jour']);
        }

        $_SESSION['success'] = 'Statut mis à jour';
        $this->redirect('/admin/orders');
    }

    public function kitchen(): void
    {
        AuthMiddleware::can('orders');
        $orders = $this->orderModel->getForKitchen();
        $this->view->renderAdmin('admin/orders/kitchen', compact('orders'));
    }

    public function addItem(): void
    {
        AuthMiddleware::can('orders');
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
        AuthMiddleware::can('orders');
        AuthMiddleware::csrf();

        $itemId = (int)($_POST['item_id'] ?? 0);
        $this->orderModel->removeItem($itemId);

        $orderId = (int)($_POST['order_id'] ?? 0);
        $order = $this->orderModel->getWithItems($orderId);
        $this->json(['success' => true, 'order' => $order]);
    }
}
