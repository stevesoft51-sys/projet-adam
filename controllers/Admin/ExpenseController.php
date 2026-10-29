<?php

class AdminExpenseController extends Controller
{
    private ExpenseModel $expenseModel;

    public function __construct()
    {
        parent::__construct();
        $this->expenseModel = new ExpenseModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('reports');

        $from = $this->get('from', date('Y-m-d', strtotime('first day of this month')));
        $to = $this->get('to', date('Y-m-d'));

        $expenses = $this->expenseModel->getByDateRange($from, $to);
        $total = array_sum(array_column($expenses, 'amount'));
        $byCategory = $this->expenseModel->sumByCategory($from, $to);

        $this->view->renderAdmin('admin/expenses/index', compact('expenses', 'total', 'from', 'to', 'byCategory'));
    }

    public function store(): void
    {
        AuthMiddleware::can('reports');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'category' => 'required|max:100',
            'description' => 'required|max:255',
            'amount' => 'required|numeric',
            'date' => 'required|date',
            'payment_method' => 'required|in:cash,mobile_money,card,transfer',
        ]);

        $validated['created_by'] = $this->auth->id();

        $this->expenseModel->create($validated);

        if (Request::isAjax()) {
            $this->json(['success' => true, 'message' => 'Dépense enregistrée']);
        }

        $_SESSION['success'] = 'Dépense enregistrée';
        $this->redirect('/admin/expenses');
    }

    public function delete(): void
    {
        AuthMiddleware::can('reports');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $this->expenseModel->deleteById($id);

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Dépense supprimée';
        $this->redirect('/admin/expenses');
    }
}
