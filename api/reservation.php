<?php
session_start();
header('Content-Type: application/json; charset=utf-8');

require_once dirname(__DIR__) . '/core/Database.php';
require_once dirname(__DIR__) . '/core/Model.php';
require_once dirname(__DIR__) . '/core/Request.php';
require_once dirname(__DIR__) . '/core/Response.php';
require_once dirname(__DIR__) . '/models/ReservationModel.php';
require_once dirname(__DIR__) . '/models/RestaurantTableModel.php';
require_once dirname(__DIR__) . '/models/SettingModel.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true) ?: $_POST;

    $name = trim($input['customer_name'] ?? '');
    $phone = trim($input['customer_phone'] ?? '');
    $date = $input['date'] ?? '';
    $time = $input['time'] ?? '';
    $guests = (int)($input['guests'] ?? 2);

    if (empty($name) || empty($phone) || empty($date) || empty($time)) {
        http_response_code(422);
        echo json_encode(['error' => 'Champs obligatoires manquants']);
        exit;
    }

    $reservationModel = new ReservationModel();
    $availability = $reservationModel->checkAvailability($date, $time, $guests);

    $tableId = null;
    if ($availability['available'] && !empty($availability['tables'])) {
        $tableId = $availability['tables'][0]['id'];
    }

    $code = $reservationModel->generateCode();

    $reservationModel->create([
        'code' => $code,
        'customer_name' => $name,
        'customer_phone' => $phone,
        'customer_email' => $input['customer_email'] ?? null,
        'date' => $date,
        'time' => $time,
        'guests' => $guests,
        'duration' => (int)SettingModel::getValue('reservation_duration', 120),
        'table_id' => $tableId,
        'status' => 'confirmed',
        'notes' => $input['notes'] ?? null,
    ]);

    if ($tableId) {
        (new RestaurantTableModel())->updateStatus($tableId, 'reserved');
    }

    http_response_code(201);
    echo json_encode([
        'success' => true,
        'code' => $code,
        'message' => 'Réservation confirmée',
        'reservation' => [
            'code' => $code,
            'date' => $date,
            'time' => $time,
            'guests' => $guests,
            'table' => $tableId ? 'Table assignée' : 'À confirmer',
        ]
    ]);
    exit;
}

if ($method === 'GET' && isset($_GET['code'])) {
    $reservation = (new ReservationModel())->getByCode($_GET['code']);
    if ($reservation) {
        echo json_encode(['success' => true, 'reservation' => $reservation]);
    } else {
        http_response_code(404);
        echo json_encode(['error' => 'Réservation introuvable']);
    }
    exit;
}

http_response_code(405);
echo json_encode(['error' => 'Méthode non autorisée']);
