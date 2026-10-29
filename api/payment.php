<?php
session_start();
header('Content-Type: application/json; charset=utf-8');

require_once dirname(__DIR__) . '/core/Database.php';
require_once dirname(__DIR__) . '/core/Model.php';
require_once dirname(__DIR__) . '/core/Request.php';
require_once dirname(__DIR__) . '/core/Response.php';
require_once dirname(__DIR__) . '/models/PaymentModel.php';
require_once dirname(__DIR__) . '/models/OrderModel.php';
require_once dirname(__DIR__) . '/models/CashRegisterModel.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    $contentType = $_SERVER['CONTENT_TYPE'] ?? '';

    if (str_contains($contentType, 'application/json')) {
        $input = json_decode(file_get_contents('php://input'), true);
    } else {
        $input = $_POST;
    }

    if (isset($input['cpm_ipn'])) {
        processCinetPayWebhook($input);
        exit;
    }

    http_response_code(400);
    echo json_encode(['error' => 'Requête invalide']);
    exit;
}

function processCinetPayWebhook(array $data): void
{
    $config = require dirname(__DIR__) . '/config/cinetpay.php';

    $token = $data['cpm_trans_token'] ?? '';
    $orderId = $data['cpm_order_id'] ?? '';
    $amount = (float)($data['cpm_amount'] ?? 0);
    $status = $data['cpm_result'] ?? '';

    $validSign = hash_hmac('sha256', "{$config['site_id']}|{$orderId}|{$amount}|{$token}", $config['secret_key']);
    $receivedSign = $data['cpm_hash'] ?? '';

    if ($validSign !== $receivedSign) {
        http_response_code(403);
        echo json_encode(['error' => 'Signature invalide']);
        return;
    }

    $paymentModel = new PaymentModel();
    $orderModel = new OrderModel();

    $existing = $paymentModel->findByRef($token);
    if ($existing) {
        echo json_encode(['status' => 'already_processed']);
        return;
    }

    $orderNumber = str_replace('ORD-', '', $orderId);
    $order = $orderModel->db->find('orders', 'order_number = ?', [$orderId]);

    $paymentStatus = ($status === '001') ? 'completed' : 'failed';

    $paymentData = [
        'order_id' => $order ? $order['id'] : null,
        'amount' => $amount,
        'method' => 'mobile_money',
        'status' => $paymentStatus,
        'reference' => $token,
        'phone_number' => $data['cpm_phone_number'] ?? null,
        'notes' => 'Paiement CinetPay',
    ];

    $paymentModel->processPayment($paymentData);

    echo json_encode(['status' => 'ok']);
}
