<?php

class AdminLoyaltyController extends Controller
{
    private LoyaltyCardModel $loyaltyModel;

    public function __construct()
    {
        parent::__construct();
        $this->loyaltyModel = new LoyaltyCardModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('loyalty');
        $cards = $this->loyaltyModel->getTopCustomers(50);
        $totalCards = $this->loyaltyModel->count();
        $totalPoints = $this->loyaltyModel->totalPoints();
        $this->view->renderAdmin('admin/loyalty/index', compact('cards', 'totalCards', 'totalPoints'));
    }

    public function createCard(): void
    {
        AuthMiddleware::can('loyalty');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'customer_name' => 'required|max:150',
            'customer_phone' => 'required|phone',
            'customer_email' => 'email',
        ]);

        $existing = $this->loyaltyModel->findByPhone($validated['customer_phone']);
        if ($existing) {
            $_SESSION['error'] = 'Un client avec ce numéro existe déjà';
            $this->redirect('/admin/loyalty');
        }

        $validated['code'] = $this->loyaltyModel->generateCode();
        $this->loyaltyModel->create($validated);

        $_SESSION['success'] = "Carte fidélité créée - Code: {$validated['code']}";
        $this->redirect('/admin/loyalty');
    }

    public function addPoints(): void
    {
        AuthMiddleware::can('loyalty');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'card_id' => 'required|integer',
            'points' => 'required|integer',
            'type' => 'required|in:earned,redeemed,adjustment',
            'description' => 'max:255',
        ]);

        $this->loyaltyModel->addPoints(
            (int)$validated['card_id'],
            (int)$validated['points'],
            $validated['type'],
            null,
            $validated['description'] ?? null
        );

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Points mis à jour';
        $this->redirect('/admin/loyalty');
    }
}
