<?php

class AdminStaffController extends Controller
{
    private UserModel $userModel;
    private ShiftModel $shiftModel;

    public function __construct()
    {
        parent::__construct();
        $this->userModel = new UserModel();
        $this->shiftModel = new ShiftModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('staff');
        $users = $this->userModel->getActive();
        $roleCounts = $this->userModel->countByRole();
        $this->view->renderAdmin('admin/staff/index', compact('users', 'roleCounts'));
    }

    public function schedule(): void
    {
        AuthMiddleware::can('staff');
        $weekStart = $this->get('week', date('Y-m-d', strtotime('monday this week')));
        $weekEnd = date('Y-m-d', strtotime($weekStart . ' +6 days'));
        $shifts = $this->shiftModel->getByWeek($weekStart);
        $users = $this->userModel->getActive();
        $nextWeek = date('Y-m-d', strtotime($weekStart . ' +7 days'));
        $prevWeek = date('Y-m-d', strtotime($weekStart . ' -7 days'));
        $this->view->renderAdmin('admin/staff/schedule', compact('shifts', 'users', 'weekStart', 'weekEnd', 'nextWeek', 'prevWeek'));
    }

    public function performance(): void
    {
        AuthMiddleware::can('staff');
        $from = $this->get('from', date('Y-m-d', strtotime('first day of this month')));
        $to = $this->get('to', date('Y-m-d'));
        $performance = $this->shiftModel->getPerformance($from, $to);

        foreach ($performance as &$emp) {
            $emp['hours_worked'] = round((float)$emp['hours_worked'], 1);
            $emp['absence_rate'] = $emp['shifts_count'] > 0 
                ? round(($emp['absences'] / $emp['shifts_count']) * 100, 1) 
                : 0;
        }

        $this->view->renderAdmin('admin/staff/performance', compact('performance', 'from', 'to'));
    }

    public function store(): void
    {
        AuthMiddleware::can('staff');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'name' => 'required|max:100|alpha',
            'email' => 'required|email|unique:users,email',
            'password' => 'required|min:6',
            'role' => 'required|in:admin,manager,serveur,cuisinier',
            'phone' => 'phone',
        ]);

        $this->userModel->create($validated);

        $_SESSION['success'] = 'Personnel ajouté';
        $this->redirect('/admin/staff');
    }

    public function update(): void
    {
        AuthMiddleware::can('staff');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $validated = $this->validate([
            'name' => 'required|max:100|alpha',
            'email' => 'required|email|unique:users,email,' . $id,
            'role' => 'required|in:admin,manager,serveur,cuisinier',
            'phone' => 'phone',
        ]);

        if (!empty($_POST['password'])) {
            $validated['password'] = $_POST['password'];
        }

        $validated['is_active'] = isset($_POST['is_active']) ? 1 : 0;

        $this->userModel->updateById($id, $validated);

        $_SESSION['success'] = 'Personnel mis à jour';
        $this->redirect('/admin/staff');
    }

    public function delete(): void
    {
        AuthMiddleware::can('staff');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        if ($id === $this->auth->id()) {
            $_SESSION['error'] = 'Vous ne pouvez pas supprimer votre propre compte';
            $this->redirect('/admin/staff');
        }

        $checks = [
            'commandes' => 'orders',
            'sessions de caisse' => 'cash_registers',
            'mouvements de caisse' => 'cash_movements',
            'mouvements d\'inventaire' => 'inventory_movements',
            'dépenses' => 'expenses',
        ];
        foreach ($checks as $label => $table) {
            $col = in_array($table, ['orders']) ? 'user_id' : 'created_by';
            $count = $this->db->count($table, "{$col} = ?", [$id]);
            if ($count > 0) {
                $_SESSION['error'] = "Cet employé a {$count} {$label} et ne peut pas être supprimé. Désactivez-le à la place.";
                $this->redirect('/admin/staff');
            }
        }

        $this->userModel->deleteById($id);
        $_SESSION['success'] = 'Personnel supprimé';
        $this->redirect('/admin/staff');
    }

    public function addShift(): void
    {
        AuthMiddleware::can('staff');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'user_id' => 'required|integer',
            'date' => 'required|date',
            'start_time' => 'required',
            'end_time' => 'required',
            'role_override' => 'in:admin,manager,serveur,cuisinier',
            'notes' => 'max:255',
        ]);

        $validated['created_by'] = $this->auth->id();

        $this->shiftModel->create($validated);

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Shift ajouté';
        $this->redirect('/admin/staff/schedule?week=' . $validated['date']);
    }
}
