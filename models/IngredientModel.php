<?php

class IngredientModel extends Model
{
    protected string $table = 'ingredients';

    public function getLowStock(): array
    {
        return $this->db->query(
            "SELECT * FROM {$this->table} WHERE current_stock <= min_stock AND min_stock > 0 ORDER BY current_stock ASC"
        )->fetchAll();
    }

    public function getAll(): array
    {
        return $this->db->findAll($this->table, 'name ASC', 500);
    }

    public function search(string $query): array
    {
        $q = "%{$query}%";
        return $this->db->query(
            "SELECT * FROM {$this->table} WHERE name LIKE ? ORDER BY name ASC LIMIT 20",
            [$q]
        )->fetchAll();
    }

    public function updateStock(int $id, float $quantity, string $type): int
    {
        $operator = $type === 'in' ? '+' : '-';
        if ($type === 'adjust') {
            return $this->db->update($this->table, ['current_stock' => $quantity], 'id = ?', [$id]);
        }
        return $this->db->query(
            "UPDATE {$this->table} SET current_stock = GREATEST(0, current_stock {$operator} ?) WHERE id = ?",
            [$quantity, $id]
        )->rowCount();
    }

    public function lowStockCount(): int
    {
        return $this->db->count($this->table, 'current_stock <= min_stock AND min_stock > 0');
    }
}
