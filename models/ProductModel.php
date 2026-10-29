<?php

class ProductModel extends Model
{
    protected string $table = 'products';

    public function getAvailable(): array
    {
        return $this->db->query(
            "SELECT p.*, c.name as category_name 
             FROM {$this->table} p 
             JOIN categories c ON p.category_id = c.id 
             WHERE p.is_available = 1 AND c.is_active = 1 
             ORDER BY c.sort_order ASC, p.sort_order ASC, p.name ASC"
        )->fetchAll();
    }

    public function getByCategory(int $categoryId): array
    {
        return $this->db->query(
            "SELECT * FROM {$this->table} WHERE category_id = ? AND is_available = 1 ORDER BY sort_order ASC, name ASC",
            [$categoryId]
        )->fetchAll();
    }

    public function getFeatured(): array
    {
        return $this->db->query(
            "SELECT p.*, c.name as category_name 
             FROM {$this->table} p 
             JOIN categories c ON p.category_id = c.id 
             WHERE p.is_featured = 1 AND p.is_available = 1 
             ORDER BY p.sort_order ASC"
        )->fetchAll();
    }

    public function getAdmin(): array
    {
        return $this->db->query(
            "SELECT p.*, c.name as category_name 
             FROM {$this->table} p 
             JOIN categories c ON p.category_id = c.id 
             ORDER BY c.sort_order ASC, p.sort_order ASC, p.name ASC"
        )->fetchAll();
    }

    public function getWithIngredients(int $id): array
    {
        $product = $this->find($id);
        if (!$product) return [];

        $product['ingredients'] = $this->db->query(
            "SELECT pi.*, i.name as ingredient_name, i.unit 
             FROM product_ingredients pi 
             JOIN ingredients i ON pi.ingredient_id = i.id 
             WHERE pi.product_id = ?",
            [$id]
        )->fetchAll();

        return $product;
    }

    public function toggle(int $id): int
    {
        $product = $this->find($id);
        if (!$product) return 0;
        return $this->db->update($this->table, ['is_available' => $product['is_available'] ? 0 : 1], 'id = ?', [$id]);
    }

    public function updateIngredients(int $productId, array $ingredients): void
    {
        $this->db->delete('product_ingredients', 'product_id = ?', [$productId]);
        foreach ($ingredients as $ing) {
            if (!empty($ing['ingredient_id']) && !empty($ing['quantity'])) {
                $this->db->insert('product_ingredients', [
                    'product_id' => $productId,
                    'ingredient_id' => (int)$ing['ingredient_id'],
                    'quantity' => (float)$ing['quantity'],
                ]);
            }
        }
    }

    public function deductIngredients(int $orderId): void
    {
        $items = $this->db->query(
            "SELECT oi.product_id, oi.quantity as order_qty 
             FROM order_items oi 
             WHERE oi.order_id = ? AND oi.status != 'cancelled'",
            [$orderId]
        )->fetchAll();

        foreach ($items as $item) {
            $ingredients = $this->db->query(
                "SELECT pi.ingredient_id, pi.quantity 
                 FROM product_ingredients pi 
                 WHERE pi.product_id = ?",
                [$item['product_id']]
            )->fetchAll();

            foreach ($ingredients as $ing) {
                $deduction = $ing['quantity'] * $item['order_qty'];
                $this->db->query(
                    "UPDATE ingredients SET current_stock = GREATEST(0, current_stock - ?) WHERE id = ?",
                    [$deduction, $ing['ingredient_id']]
                );
            }
        }
    }

    public function count(string $where = '1=1', array $params = []): int
    {
        return parent::count($where, $params);
    }

    public function search(string $query): array
    {
        $q = "%{$query}%";
        return $this->db->query(
            "SELECT p.*, c.name as category_name 
             FROM {$this->table} p 
             JOIN categories c ON p.category_id = c.id 
             WHERE (p.name LIKE ? OR p.description LIKE ?) 
             ORDER BY p.name ASC LIMIT 20",
            [$q, $q]
        )->fetchAll();
    }
}
