<?php

class ExpenseModel extends Model
{
    protected string $table = 'expenses';

    public function getByDateRange(string $from, string $to): array
    {
        return $this->db->query(
            "SELECT e.*, u.name as creator_name
             FROM {$this->table} e
             JOIN users u ON e.created_by = u.id
             WHERE e.date BETWEEN ? AND ?
             ORDER BY e.date DESC",
            [$from, $to]
        )->fetchAll();
    }

    public function sumByCategory(string $from, string $to): array
    {
        return $this->db->query(
            "SELECT category, SUM(amount) as total, COUNT(*) as count
             FROM {$this->table}
             WHERE date BETWEEN ? AND ?
             GROUP BY category
             ORDER BY total DESC",
            [$from, $to]
        )->fetchAll();
    }

    public function totalMonth(): float
    {
        $month = date('Y-m');
        return $this->db->sum($this->table, 'amount', "DATE_FORMAT(date, '%Y-%m') = ?", [$month]);
    }
}
