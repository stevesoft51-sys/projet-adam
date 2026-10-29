<?php

class CategoryModel extends Model
{
    protected string $table = 'categories';

    public function getActive(): array
    {
        return $this->db->query(
            "SELECT c.*, COUNT(p.id) as product_count 
             FROM {$this->table} c 
             LEFT JOIN products p ON p.category_id = c.id AND p.is_available = 1 
             WHERE c.is_active = 1 
             GROUP BY c.id 
             ORDER BY c.sort_order ASC, c.name ASC"
        )->fetchAll();
    }

    public function getAll(): array
    {
        return $this->db->findAll($this->table, 'sort_order ASC, name ASC');
    }

    public function toggle(int $id): int
    {
        $cat = $this->find($id);
        if (!$cat) return 0;
        return $this->db->update($this->table, ['is_active' => $cat['is_active'] ? 0 : 1], 'id = ?', [$id]);
    }
}
