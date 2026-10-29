<?php

class AdminCashController extends Controller
{
    private CashRegisterModel $cashModel;

    public function __construct()
    {
        parent::__construct();
        $this->cashModel = new CashRegisterModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('cash');
        $openRegister = $this->cashModel->getOpen();
        $movements = $openRegister ? $this->cashModel->getMovements($openRegister['id']) : [];
        $this->view->renderAdmin('admin/cash/register', compact('openRegister', 'movements'));
    }

    public function history(): void
    {
        AuthMiddleware::can('cash');
        $history = $this->cashModel->getHistory(30);
        $this->view->renderAdmin('admin/cash/history', compact('history'));
    }

    public function open(): void
    {
        AuthMiddleware::can('cash');
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

        $this->redirect('/admin/cash');
    }

    public function close(): void
    {
        AuthMiddleware::can('cash');
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
            $_SESSION['success'] = 'Caisse fermée';
        } catch (Exception $e) {
            $_SESSION['error'] = $e->getMessage();
        }

        $this->redirect('/admin/cash/history');
    }

    public function addMovement(): void
    {
        AuthMiddleware::can('cash');
        AuthMiddleware::csrf();

        $openRegister = $this->cashModel->getOpen();
        if (!$openRegister) {
            $_SESSION['error'] = 'Aucune caisse ouverte';
            $this->redirect('/admin/cash');
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

        $_SESSION['success'] = 'Mouvement enregistré';
        $this->redirect('/admin/cash');
    }

    public function processPayment(): void
    {
        AuthMiddleware::can('cash');
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
            $this->json(['success' => true, 'message' => 'Paiement enregistré']);
        }

        $_SESSION['success'] = 'Paiement enregistré';
        $this->redirect('/admin/orders');
    }
}
