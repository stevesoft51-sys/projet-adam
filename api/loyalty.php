<?php
session_start();
header('Content-Type: application/json; charset=utf-8');

require_once dirname(__DIR__) . '/core/Database.php';
require_once dirname(__DIR__) . '/core/Model.php';
require_once dirname(__DIR__) . '/core/Request.php';
require_once dirname(__DIR__) . '/core/Response.php';
require_once dirname(__DIR__) . '/models/LoyaltyCardModel.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $query = trim($_GET['q'] ?? '');

    if (empty($query)) {
        echo json_encode(['success' => true, 'cards' => []]);
        exit;
    }

    $loyaltyModel = new LoyaltyCardModel();
    $cards = $loyaltyModel->search($query);

    echo json_encode(['success' => true, 'cards' => $cards]);
    exit;
}

if ($method === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true) ?: $_POST;

    $code = trim($input['code'] ?? '');
    $loyaltyModel = new LoyaltyCardModel();
    $card = $loyaltyModel->findByCode($code);

    if (!$card) {
        http_response_code(404);
        echo json_encode(['error' => 'Carte introuvable']);
        exit;
    }

    echo json_encode([
        'success' => true,
        'card' => $card,
    ]);
    exit;
}

http_response_code(405);
echo json_encode(['error' => 'Méthode non autorisée']);
