<?php

class PaymentModel extends Model
{
    protected string $table = 'payments';

    public function getByDateRange(string $from, string $to): array
    {
        return $this->db->query(
            "SELECT p.*, o.order_number, u.name as received_by_name
             FROM {$this->table} p
             LEFT JOIN orders o ON p.order_id = o.id
             LEFT JOIN users u ON p.received_by = u.id
             WHERE DATE(p.created_at) BETWEEN ? AND ?
             ORDER BY p.created_at DESC",
            [$from, $to]
        )->fetchAll();
    }

    public function sumByMethod(string $where = '1=1', array $params = []): array
    {
        return $this->db->query(
            "SELECT method, SUM(amount) as total, COUNT(*) as count 
             FROM {$this->table} WHERE status = 'completed' AND {$where} 
             GROUP BY method",
            $params
        )->fetchAll();
    }

    public function sumToday(): float
    {
        return $this->db->sum($this->table, 'amount', "DATE(created_at) = CURDATE() AND status = 'completed'");
    }

    public function getByOrder(int $orderId): array
    {
        return $this->db->query(
            "SELECT * FROM {$this->table} WHERE order_id = ? ORDER BY created_at DESC",
            [$orderId]
        )->fetchAll();
    }

    public function processPayment(array $data): int
    {
        $this->db->beginTransaction();
        try {
            $paymentId = $this->db->insert($this->table, $data);

            if ($data['order_id'] && $data['status'] === 'completed') {
                $order = (new OrderModel())->find($data['order_id']);
                if ($order) {
                    $totalPaid = $this->db->sum(
                        $this->table, 'amount',
                        "order_id = ? AND status = 'completed'",
                        [$data['order_id']]
                    );

                    if ($totalPaid >= $order['total']) {
                        (new OrderModel())->updateStatus($data['order_id'], 'paid');

                        if ($order['table_id']) {
                            (new RestaurantTableModel())->updateStatus((int)$order['table_id'], 'free');
                        }
                    }
                }
            }

            if ($data['cash_register_id'] && $data['status'] === 'completed') {
                $this->db->query(
                    "UPDATE cash_registers SET total_cash_in = total_cash_in + ? WHERE id = ?",
                    [$data['amount'], $data['cash_register_id']]
                );

                $orderNum = '';
                if ($data['order_id']) {
                    $o = (new OrderModel())->find($data['order_id']);
                    $orderNum = $o ? $o['order_number'] : '#' . $data['order_id'];
                }

                $methodLabel = match($data['method']) {
                    'cash' => 'Especes',
                    'mobile_money' => 'Mobile Money',
                    'card' => 'Carte',
                    default => ucfirst($data['method']),
                };

                $this->db->insert('cash_movements', [
                    'cash_register_id' => $data['cash_register_id'],
                    'type' => 'in',
                    'amount' => $data['amount'],
                    'reason' => "Paiement {$methodLabel} - {$orderNum}" . ($data['notes'] ? " ({$data['notes']})" : ''),
                    'created_by' => $data['received_by'] ?? 1,
                ]);
            }

            $this->db->commit();
            return $paymentId;
        } catch (Exception $e) {
            $this->db->rollBack();
            throw $e;
        }
    }

    public function findByRef(string $reference): ?array
    {
        return $this->db->find($this->table, 'reference = ?', [$reference]);
    }

    public function getDailyStats(string $date): array
    {
        $row = $this->db->query(
            "SELECT 
                COUNT(*) as total_transactions,
                COALESCE(SUM(amount), 0) as total_amount,
                SUM(CASE WHEN method = 'cash' THEN amount ELSE 0 END) as cash_amount,
                SUM(CASE WHEN method = 'mobile_money' THEN amount ELSE 0 END) as mobile_amount,
                SUM(CASE WHEN method = 'card' THEN amount ELSE 0 END) as card_amount
             FROM {$this->table} 
             WHERE DATE(created_at) = ? AND status = 'completed'",
            [$date]
        )->fetch();

        return $row ?: [
            'total_transactions' => 0,
            'total_amount' => 0,
            'cash_amount' => 0,
            'mobile_amount' => 0,
            'card_amount' => 0,
        ];
    }
}
