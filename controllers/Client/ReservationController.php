<?php

class ClientReservationController extends Controller
{
    public function index(): void
    {
        $config = require CONFIG_PATH . '/app.php';
        $settings = SettingModel::getAll();
        $errors = $_SESSION['errors'] ?? [];
        $old = $_SESSION['old'] ?? [];
        unset($_SESSION['errors'], $_SESSION['old']);

        $data = compact('config', 'settings', 'errors', 'old');
        $this->view->renderClient('client/reservation', $data);
    }

    public function store(): void
    {
        $validated = $this->validate([
            'customer_name' => 'required|max:150',
            'customer_phone' => 'required|phone',
            'customer_email' => 'email',
            'date' => 'required|date',
            'time' => 'required',
            'guests' => 'required|integer',
            'notes' => 'max:500',
        ]);

        $date = $validated['date'];
        $today = date('Y-m-d');
        if ($date < $today) {
            $_SESSION['errors'] = ['date' => ['La date ne peut pas être dans le passé']];
            $_SESSION['old'] = $validated;
            header('Location: /reservation');
            exit;
        }

        $maxAdvance = SettingModel::getValue('max_reservation_advance_days', 30);
        $maxDate = date('Y-m-d', strtotime("+{$maxAdvance} days"));
        if ($date > $maxDate) {
            $_SESSION['errors'] = ['date' => ['Réservation impossible plus de ' . $maxAdvance . ' jours à l\'avance']];
            $_SESSION['old'] = $validated;
            header('Location: /reservation');
            exit;
        }

        $reservationModel = new ReservationModel();
        $availability = $reservationModel->checkAvailability(
            $validated['date'],
            $validated['time'],
            (int)$validated['guests']
        );

        $tableId = null;
        if ($availability['available'] && !empty($availability['tables'])) {
            $tableId = $availability['tables'][0]['id'];
        }

        $code = $reservationModel->generateCode();

        $reservationData = [
            'code' => $code,
            'customer_name' => $validated['customer_name'],
            'customer_phone' => $validated['customer_phone'],
            'customer_email' => $validated['customer_email'] ?? null,
            'date' => $validated['date'],
            'time' => $validated['time'],
            'guests' => (int)$validated['guests'],
            'duration' => (int)SettingModel::getValue('reservation_duration', 120),
            'table_id' => $tableId,
            'status' => 'confirmed',
            'notes' => $validated['notes'] ?? null,
        ];

        $reservationModel->create($reservationData);

        if ($tableId) {
            (new RestaurantTableModel())->updateStatus($tableId, 'reserved');
        }

        $_SESSION['reservation_code'] = $code;
        header('Location: /reservation/ticket');
        exit;
    }

    public function ticket(): void
    {
        $code = $_SESSION['reservation_code'] ?? $this->get('code');
        unset($_SESSION['reservation_code']);

        if (!$code) {
            header('Location: /reservation');
            exit;
        }

        $reservation = (new ReservationModel())->getByCode($code);
        if (!$reservation) {
            $_SESSION['error'] = 'Réservation introuvable';
            header('Location: /reservation');
            exit;
        }

        $config = require CONFIG_PATH . '/app.php';
        $settings = SettingModel::getAll();

        $data = compact('config', 'settings', 'reservation');
        $this->view->renderClient('client/ticket', $data);
    }
}
