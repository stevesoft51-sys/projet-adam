<?php

class CashRegisterModel extends Model
{
    protected string $table = 'cash_registers';

    public function getOpen(): ?array
    {
        return $this->db->query(
            "SELECT cr.*, u.name as user_name
             FROM {$this->table} cr
             JOIN users u ON cr.user_id = u.id
             WHERE cr.status = 'open'
             ORDER BY cr.opened_at DESC
             LIMIT 1"
        )->fetch() ?: null;
    }

    public function open(int $userId, float $amount, ?string $notes = null): int
    {
        $open = $this->getOpen();
        if ($open) {
            throw new \Exception('Une caisse est déjà ouverte (#' . $open['id'] . ')');
        }

        return $this->db->insert($this->table, [
            'user_id' => $userId,
            'opening_amount' => $amount,
            'notes' => $notes,
        ]);
    }

    public function close(int $id, float $closingAmount, ?string $notes = null): int
    {
        $register = $this->find($id);
        if (!$register || $register['status'] !== 'open') {
            throw new \Exception('Caisse introuvable ou déjà fermée');
        }

        $expectedAmount = (float)$register['opening_amount'] 
            + (float)$register['total_cash_in'] 
            - (float)$register['total_cash_out'];

        $data = [
            'closing_amount' => $closingAmount,
            'expected_amount' => $expectedAmount,
            'status' => 'closed',
            'closed_at' => date('Y-m-d H:i:s'),
        ];
        if ($notes) {
            $data['notes'] = ($data['notes'] ?? '') . "\n" . $notes;
        }

        return $this->db->update($this->table, $data, 'id = ?', [$id]);
    }

    public function addMovement(int $registerId, string $type, float $amount, string $reason, int $userId): int
    {
        $movementId = $this->db->insert('cash_movements', [
            'cash_register_id' => $registerId,
            'type' => $type,
            'amount' => $amount,
            'reason' => $reason,
            'created_by' => $userId,
        ]);

        $column = $type === 'in' ? 'total_cash_in' : 'total_cash_out';
        $this->db->query(
            "UPDATE {$this->table} SET {$column} = {$column} + ? WHERE id = ?",
            [$amount, $registerId]
        );

        return $movementId;
    }

    public function getMovements(int $registerId): array
    {
        return $this->db->query(
            "SELECT cm.*, u.name as creator_name
             FROM cash_movements cm
             JOIN users u ON cm.created_by = u.id
             WHERE cm.cash_register_id = ?
             ORDER BY cm.created_at DESC",
            [$registerId]
        )->fetchAll();
    }

    public function getHistory(int $limit = 30): array
    {
        return $this->db->query(
            "SELECT cr.*, u.name as user_name
             FROM {$this->table} cr
             JOIN users u ON cr.user_id = u.id
             ORDER BY cr.opened_at DESC
             LIMIT ?",
            [$limit]
        )->fetchAll();
    }

    public function getDailySummary(string $date): array
    {
        $payments = (new PaymentModel())->getDailyStats($date);
        $movements = $this->db->query(
            "SELECT 
                SUM(CASE WHEN type = 'in' THEN amount ELSE 0 END) as total_in,
                SUM(CASE WHEN type = 'out' THEN amount ELSE 0 END) as total_out
             FROM cash_movements cm
             JOIN {$this->table} cr ON cm.cash_register_id = cr.id
             WHERE DATE(cr.opened_at) = ? OR DATE(cm.created_at) = ?",
            [$date, $date]
        )->fetch();

        return array_merge($payments, $movements ?: ['total_in' => 0, 'total_out' => 0]);
    }
}
