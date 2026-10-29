<?php

class RestaurantTableModel extends Model
{
    protected string $table = 'tables_restaurant';

    public function getAll(): array
    {
        return $this->db->findAll($this->table, 'number ASC');
    }

    public function getAvailable(): array
    {
        return $this->db->query(
            "SELECT * FROM {$this->table} WHERE status = 'free' AND is_active = 1 ORDER BY number ASC"
        )->fetchAll();
    }

    public function getByStatus(string $status): array
    {
        return $this->db->query(
            "SELECT * FROM {$this->table} WHERE status = ? AND is_active = 1 ORDER BY number ASC",
            [$status]
        )->fetchAll();
    }

    public function getForDate(string $date): array
    {
        return $this->db->query(
            "SELECT t.*,
                CASE WHEN r.id IS NOT NULL THEN 'reserved' ELSE t.status END as display_status,
                r.customer_name, r.time as reservation_time, r.guests as reservation_guests
             FROM {$this->table} t
             LEFT JOIN reservations r ON r.table_id = t.id 
                AND r.date = ? 
                AND r.status IN ('pending', 'confirmed')
             WHERE t.is_active = 1
             ORDER BY t.number ASC",
            [$date]
        )->fetchAll();
    }

    public function updateStatus(int $id, string $status): int
    {
        return $this->db->update($this->table, ['status' => $status], 'id = ?', [$id]);
    }

    public function getAvailableForDateTime(string $date, string $time, int $guests): array
    {
        return $this->db->query(
            "SELECT t.* FROM {$this->table} t
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
    }
}
