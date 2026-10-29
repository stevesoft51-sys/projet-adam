<?php

class AdminStockController extends Controller
{
    private IngredientModel $ingredientModel;
    private InventoryModel $inventoryModel;

    public function __construct()
    {
        parent::__construct();
        $this->ingredientModel = new IngredientModel();
        $this->inventoryModel = new InventoryModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('stock');
        $ingredients = $this->ingredientModel->getAll();
        $lowStock = $this->ingredientModel->getLowStock();
        $lowStockCount = count($lowStock);
        $this->view->renderAdmin('admin/stock/index', compact('ingredients', 'lowStock', 'lowStockCount'));
    }

    public function inventory(): void
    {
        AuthMiddleware::can('stock');
        $ingredients = $this->ingredientModel->getAll();
        $this->view->renderAdmin('admin/stock/inventory', compact('ingredients'));
    }

    public function movements(): void
    {
        AuthMiddleware::can('stock');
        $movements = $this->inventoryModel->getRecent(100);
        $ingredients = $this->ingredientModel->getAll();
        $this->view->renderAdmin('admin/stock/movements', compact('movements', 'ingredients'));
    }

    public function addMovement(): void
    {
        AuthMiddleware::can('stock');
        AuthMiddleware::csrf();

        // Check if this is a new ingredient creation
        if (!empty($_POST['ingredient_name'])) {
            $this->storeIngredient();
            return;
        }

        $validated = $this->validate([
            'ingredient_id' => 'required|integer',
            'type' => 'required|in:in,out,adjust',
            'quantity' => 'required|numeric',
            'reason' => 'required|max:255',
        ]);

        $validated['created_by'] = $this->auth->id();
        $this->inventoryModel->addMovement($validated);

        if (Request::isAjax()) {
            $this->json(['success' => true, 'message' => 'Mouvement enregistré']);
        }

        $_SESSION['success'] = 'Mouvement de stock enregistré';
        $this->redirect('/admin/stock/movements');
    }

    private function storeIngredient(): void
    {
        $validated = $this->validate([
            'ingredient_name' => 'required|max:100',
            'quantity' => 'required|numeric',
            'unit' => 'required',
        ]);

        $ingredientData = [
            'name' => $validated['ingredient_name'],
            'unit' => $validated['unit'],
            'current_stock' => (float)$validated['quantity'],
            'min_stock' => (float)($_POST['min_stock'] ?? 0),
            'cost_per_unit' => (float)($_POST['cost_per_unit'] ?? 0),
            'supplier' => $_POST['supplier'] ?? null,
        ];

        $ingredientId = $this->ingredientModel->create($ingredientData);

        // Record the initial stock movement
        $this->inventoryModel->addMovement([
            'ingredient_id' => $ingredientId,
            'type' => 'in',
            'quantity' => (float)$validated['quantity'],
            'reason' => $_POST['reason'] ?? 'Stock initial',
            'created_by' => $this->auth->id(),
        ]);

        if (Request::isAjax()) {
            $this->json(['success' => true, 'message' => 'Ingredient ajouté']);
        }

        $_SESSION['success'] = 'Ingredient ajouté avec succès';
        $this->redirect('/admin/stock');
    }

    public function adjust(): void
    {
        AuthMiddleware::can('stock');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'ingredient_id' => 'required|integer',
            'quantity' => 'required|numeric',
        ]);

        $this->inventoryModel->addMovement([
            'ingredient_id' => $validated['ingredient_id'],
            'type' => 'adjust',
            'quantity' => $validated['quantity'],
            'reason' => 'Ajustement manuel d\'inventaire',
            'created_by' => $this->auth->id(),
        ]);

        if (Request::isAjax()) {
            $this->json(['success' => true, 'message' => 'Stock ajusté']);
        }

        $_SESSION['success'] = 'Stock ajusté';
        $this->redirect('/admin/stock/inventory');
    }
}
