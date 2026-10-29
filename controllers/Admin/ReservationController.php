<?php

class AdminReservationController extends Controller
{
    private ReservationModel $reservationModel;

    public function __construct()
    {
        parent::__construct();
        $this->reservationModel = new ReservationModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('reservations');
        $date = $this->get('date', date('Y-m-d'));
        $reservations = $this->reservationModel->getByDate($date);
        $upcoming = $this->reservationModel->getUpcoming();
        $this->view->renderAdmin('admin/reservations/index', compact('reservations', 'upcoming', 'date'));
    }

    public function store(): void
    {
        AuthMiddleware::can('reservations');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'customer_name' => 'required|max:150',
            'customer_phone' => 'required|phone',
            'customer_email' => 'email',
            'date' => 'required|date',
            'time' => 'required',
            'guests' => 'required|integer',
            'notes' => 'max:500',
        ]);

        $validated['table_id'] = !empty($_POST['table_id']) ? (int)$_POST['table_id'] : null;
        $validated['code'] = $this->reservationModel->generateCode();
        $validated['created_by'] = $this->auth->id();
        $validated['duration'] = (int)($_POST['duration'] ?? 120);
        $validated['status'] = 'confirmed';

        $this->reservationModel->create($validated);

        if ($validated['table_id']) {
            (new RestaurantTableModel())->updateStatus($validated['table_id'], 'reserved');
        }

        if (Request::isAjax()) {
            $this->json(['success' => true, 'code' => $validated['code']]);
        }

        $_SESSION['success'] = "Réservation créée - Code: {$validated['code']}";
        $this->redirect('/admin/reservations');
    }

    public function update(): void
    {
        AuthMiddleware::can('reservations');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $validated = $this->validate([
            'customer_name' => 'required|max:150',
            'customer_phone' => 'required|phone',
            'date' => 'required|date',
            'time' => 'required',
            'guests' => 'required|integer',
        ]);

        $validated['table_id'] = !empty($_POST['table_id']) ? (int)$_POST['table_id'] : null;
        $validated['duration'] = (int)($_POST['duration'] ?? 120);

        $this->reservationModel->updateById($id, $validated);

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Réservation mise à jour';
        $this->redirect('/admin/reservations');
    }

    public function delete(): void
    {
        AuthMiddleware::can('reservations');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $reservation = $this->reservationModel->find($id);

        if ($reservation && $reservation['table_id']) {
            (new RestaurantTableModel())->updateStatus($reservation['table_id'], 'free');
        }

        $this->reservationModel->deleteById($id);

        if (Request::isAjax()) {
            $this->json(['success' => true]);
        }

        $_SESSION['success'] = 'Réservation supprimée';
        $this->redirect('/admin/reservations');
    }

    public function updateStatus(): void
    {
        AuthMiddleware::can('reservations');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $status = $_POST['status'] ?? '';

        $validStatuses = ['pending', 'confirmed', 'seated', 'completed', 'cancelled', 'no_show'];
        if (!in_array($status, $validStatuses)) {
            $this->json(['error' => 'Statut invalide'], 400);
        }

        $reservation = $this->reservationModel->find($id);
        $this->reservationModel->updateStatus($id, $status);

        if ($reservation && $reservation['table_id']) {
            if ($status === 'cancelled' || $status === 'completed' || $status === 'no_show') {
                (new RestaurantTableModel())->updateStatus($reservation['table_id'], 'free');
            } elseif ($status === 'seated') {
                (new RestaurantTableModel())->updateStatus($reservation['table_id'], 'occupied');
            }
        }

        $this->json(['success' => true, 'message' => 'Statut mis à jour']);
    }
}
