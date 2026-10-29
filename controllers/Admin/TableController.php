<?php

class AdminTableController extends Controller
{
    private RestaurantTableModel $tableModel;

    public function __construct()
    {
        parent::__construct();
        $this->tableModel = new RestaurantTableModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('tables');
        $date = $this->get('date', date('Y-m-d'));
        $tables = $this->tableModel->getForDate($date);
        $this->view->renderAdmin('admin/tables/floorplan', compact('tables', 'date'));
    }

    public function store(): void
    {
        AuthMiddleware::can('tables');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'number' => 'required|integer|unique:tables_restaurant,number',
            'capacity' => 'required|integer',
            'shape' => 'in:square,round,rectangle',
            'zone' => 'max:50',
            'name' => 'max:50',
        ]);

        $validated['pos_x'] = (int)($_POST['pos_x'] ?? 0);
        $validated['pos_y'] = (int)($_POST['pos_y'] ?? 0);

        $this->tableModel->create($validated);

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Table ajoutée';
        $this->redirect('/admin/tables');
    }

    public function update(): void
    {
        AuthMiddleware::can('tables');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $validated = $this->validate([
            'number' => 'required|integer',
            'capacity' => 'required|integer',
            'shape' => 'in:square,round,rectangle',
            'zone' => 'max:50',
            'name' => 'max:50',
        ]);

        $validated['pos_x'] = (int)($_POST['pos_x'] ?? 0);
        $validated['pos_y'] = (int)($_POST['pos_y'] ?? 0);

        $this->tableModel->updateById($id, $validated);

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Table mise à jour';
        $this->redirect('/admin/tables');
    }

    public function delete(): void
    {
        AuthMiddleware::can('tables');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $this->tableModel->deleteById($id);

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Table supprimée';
        $this->redirect('/admin/tables');
    }

    public function updateStatus(): void
    {
        AuthMiddleware::can('tables');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $status = $_POST['status'] ?? 'free';

        $validStatuses = ['free', 'reserved', 'occupied', 'maintenance'];
        if (!in_array($status, $validStatuses)) {
            $this->json(['error' => 'Statut invalide'], 400);
        }

        $this->tableModel->updateStatus($id, $status);
        $this->json(['success' => true]);
    }
}
