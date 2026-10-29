<?php

class LoyaltyCardModel extends Model
{
    protected string $table = 'loyalty_cards';

    public function generateCode(): string
    {
        do {
            $code = 'ADAM-' . str_pad(mt_rand(1, 99999), 5, '0', STR_PAD_LEFT);
            $exists = $this->db->count($this->table, 'code = ?', [$code]);
        } while ($exists > 0);
        return $code;
    }

    public function findByPhone(string $phone): ?array
    {
        return $this->db->find($this->table, 'customer_phone = ? AND is_active = 1', [$phone]);
    }

    public function findByCode(string $code): ?array
    {
        return $this->db->find($this->table, 'code = ? AND is_active = 1', [$code]);
    }

    public function addPoints(int $cardId, int $points, string $type, ?int $orderId = null, ?string $description = null): void
    {
        $this->db->beginTransaction();
        try {
            $this->db->insert('loyalty_points', [
                'loyalty_card_id' => $cardId,
                'points' => $points,
                'type' => $type,
                'order_id' => $orderId,
                'description' => $description,
            ]);

            if ($type === 'earned') {
                $this->db->query(
                    "UPDATE {$this->table} SET points = points + ? WHERE id = ?",
                    [$points, $cardId]
                );
            } elseif ($type === 'redeemed') {
                $this->db->query(
                    "UPDATE {$this->table} SET points = GREATEST(0, points - ?) WHERE id = ?",
                    [abs($points), $cardId]
                );
            } else {
                $this->db->query(
                    "UPDATE {$this->table} SET points = GREATEST(0, points + ?) WHERE id = ?",
                    [$points, $cardId]
                );
            }

            $this->updateTier($cardId);
            $this->db->commit();
        } catch (Exception $e) {
            $this->db->rollBack();
            throw $e;
        }
    }

    private function updateTier(int $cardId): void
    {
        $card = $this->find($cardId);
        if (!$card) return;

        $config = require CONFIG_PATH . '/app.php';
        $tier = 'bronze';
        foreach (array_reverse($config['loyalty_tiers']) as $t) {
            if ($card['points'] >= $t['min_points']) {
                $tier = strtolower($t['name']);
                break;
            }
        }

        if ($card['tier'] !== $tier) {
            $this->db->update($this->table, ['tier' => $tier], 'id = ?', [$cardId]);
        }
    }

    public function addSpent(int $cardId, float $amount): void
    {
        $this->db->query(
            "UPDATE {$this->table} SET total_spent = total_spent + ? WHERE id = ?",
            [$amount, $cardId]
        );
    }

    public function getPointsHistory(int $cardId): array
    {
        return $this->db->query(
            "SELECT lp.*, o.order_number
             FROM loyalty_points lp
             LEFT JOIN orders o ON lp.order_id = o.id
             WHERE lp.loyalty_card_id = ?
             ORDER BY lp.created_at DESC
             LIMIT 50",
            [$cardId]
        )->fetchAll();
    }

    public function getTopCustomers(int $limit = 20): array
    {
        return $this->db->query(
            "SELECT * FROM {$this->table} WHERE is_active = 1 ORDER BY total_spent DESC LIMIT ?",
            [$limit]
        )->fetchAll();
    }

    public function count(string $where = '1=1', array $params = []): int
    {
        return parent::count("is_active = 1 AND {$where}", $params);
    }

    public function totalPoints(): int
    {
        return (int)$this->db->sum($this->table, 'points', 'is_active = 1');
    }

    public function search(string $query): array
    {
        $q = "%{$query}%";
        return $this->db->query(
            "SELECT * FROM {$this->table} 
             WHERE code LIKE ? OR customer_name LIKE ? OR customer_phone LIKE ?
             ORDER BY customer_name ASC LIMIT 20",
            [$q, $q, $q]
        )->fetchAll();
    }
}
