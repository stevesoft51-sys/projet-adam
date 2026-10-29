<?php

class ShiftModel extends Model
{
    protected string $table = 'shifts';

    public function getByWeek(string $startDate): array
    {
        $endDate = date('Y-m-d', strtotime($startDate . ' +6 days'));
        return $this->db->query(
            "SELECT s.*, u.name as user_name, u.role as user_role
             FROM {$this->table} s
             JOIN users u ON s.user_id = u.id
             WHERE s.date BETWEEN ? AND ?
             ORDER BY s.date ASC, s.start_time ASC",
            [$startDate, $endDate]
        )->fetchAll();
    }

    public function getByDate(string $date): array
    {
        return $this->db->query(
            "SELECT s.*, u.name as user_name, u.role as user_role
             FROM {$this->table} s
             JOIN users u ON s.user_id = u.id
             WHERE s.date = ?
             ORDER BY s.start_time ASC",
            [$date]
        )->fetchAll();
    }

    public function getUserHours(int $userId, string $from, string $to): float
    {
        $result = $this->db->query(
            "SELECT 
                SUM(TIMESTAMPDIFF(MINUTE, start_time, end_time)) as total_minutes
             FROM {$this->table}
             WHERE user_id = ? AND date BETWEEN ? AND ? AND status != 'absent'",
            [$userId, $from, $to]
        )->fetch();

        return $result ? (float)$result['total_minutes'] / 60 : 0;
    }

    public function updateStatus(int $id, string $status): int
    {
        return $this->db->update($this->table, ['status' => $status], 'id = ?', [$id]);
    }

    public function getPerformance(string $from, string $to): array
    {
        return $this->db->query(
            "SELECT u.id, u.name, u.role,
                SUM(TIMESTAMPDIFF(MINUTE, s.start_time, s.end_time)) / 60 as hours_worked,
                COUNT(s.id) as shifts_count,
                SUM(CASE WHEN s.status = 'absent' THEN 1 ELSE 0 END) as absences,
                SUM(CASE WHEN s.status = 'late' THEN 1 ELSE 0 END) as lates
             FROM users u
             LEFT JOIN {$this->table} s ON s.user_id = u.id AND s.date BETWEEN ? AND ?
             WHERE u.is_active = 1
             GROUP BY u.id
             ORDER BY u.name ASC",
            [$from, $to]
        )->fetchAll();
    }
}
