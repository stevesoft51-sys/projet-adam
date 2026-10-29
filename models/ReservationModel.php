<?php

class ReservationModel extends Model
{
    protected string $table = 'reservations';

    public function generateCode(): string
    {
        do {
            $code = strtoupper(substr(md5(uniqid(mt_rand(), true)), 0, 8));
            $exists = $this->db->count($this->table, 'code = ?', [$code]);
        } while ($exists > 0);
        return $code;
    }

    public function getByDate(string $date): array
    {
        return $this->db->query(
            "SELECT r.*, t.number as table_number, u.name as creator_name
             FROM {$this->table} r
             LEFT JOIN tables_restaurant t ON r.table_id = t.id
             LEFT JOIN users u ON r.created_by = u.id
             WHERE r.date = ?
             ORDER BY r.time ASC",
            [$date]
        )->fetchAll();
    }

    public function getUpcoming(): array
    {
        return $this->db->query(
            "SELECT r.*, t.number as table_number
             FROM {$this->table} r
             LEFT JOIN tables_restaurant t ON r.table_id = t.id
             WHERE r.date >= CURDATE() 
                AND r.status IN ('pending', 'confirmed')
             ORDER BY r.date ASC, r.time ASC
             LIMIT 50"
        )->fetchAll();
    }

    public function getByCode(string $code): ?array
    {
        return $this->db->find($this->table, 'code = ?', [$code]);
    }

    public function checkAvailability(string $date, string $time, int $guests): array
    {
        $availableTables = $this->db->query(
            "SELECT t.* FROM tables_restaurant t
             WHERE t.is_active = 1 
                AND t.capacity >= ?
                AND t.status NOT IN ('maintenance')
                AND t.id NOT IN (
                    SELECT r.table_id FROM reservations r 
                    WHERE r.date = ? 
                    AND r.status IN ('pending', 'confirmed')
                    AND r.table_id IS NOT NULL
                )
             ORDER BY t.capacity ASC",
            [$guests, $date]
        )->fetchAll();

        return [
            'available' => count($availableTables) > 0,
            'tables' => $availableTables,
            'count' => count($availableTables),
        ];
    }

    public function countToday(): int
    {
        return $this->count("date = CURDATE() AND status NOT IN ('cancelled', 'no_show')");
    }

    public function countPending(): int
    {
        return $this->count("status = 'pending'");
    }

    public function updateStatus(int $id, string $status): int
    {
        return $this->db->update($this->table, ['status' => $status], 'id = ?', [$id]);
    }
}
