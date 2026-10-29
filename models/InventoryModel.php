<?php

class InventoryModel extends Model
{
    protected string $table = 'inventory_movements';

    public function addMovement(array $data): int
    {
        $this->db->beginTransaction();
        try {
            $movementId = $this->db->insert($this->table, $data);

            $ingredient = (new IngredientModel())->find($data['ingredient_id']);
            if (!$ingredient) throw new \Exception('Ingrédient introuvable');

            if ($data['type'] === 'in') {
                $newStock = (float)$ingredient['current_stock'] + (float)$data['quantity'];
            } elseif ($data['type'] === 'out') {
                $newStock = max(0, (float)$ingredient['current_stock'] - (float)$data['quantity']);
            } else {
                $newStock = (float)$data['quantity'];
            }

            $this->db->update('ingredients', ['current_stock' => $newStock], 'id = ?', [$data['ingredient_id']]);

            $this->db->commit();
            return $movementId;
        } catch (Exception $e) {
            $this->db->rollBack();
            throw $e;
        }
    }

    public function getByIngredient(int $ingredientId, int $limit = 50): array
    {
        return $this->db->query(
            "SELECT im.*, u.name as creator_name, i.name as ingredient_name, i.unit
             FROM {$this->table} im
             JOIN users u ON im.created_by = u.id
             JOIN ingredients i ON im.ingredient_id = i.id
             WHERE im.ingredient_id = ?
             ORDER BY im.created_at DESC
             LIMIT ?",
            [$ingredientId, $limit]
        )->fetchAll();
    }

    public function getRecent(int $limit = 50): array
    {
        return $this->db->query(
            "SELECT im.*, u.name as creator_name, i.name as ingredient_name, i.unit
             FROM {$this->table} im
             JOIN users u ON im.created_by = u.id
             JOIN ingredients i ON im.ingredient_id = i.id
             ORDER BY im.created_at DESC
             LIMIT ?",
            [$limit]
        )->fetchAll();
    }

    public function getMovementsByDate(string $from, string $to): array
    {
        return $this->db->query(
            "SELECT im.*, u.name as creator_name, i.name as ingredient_name, i.unit
             FROM {$this->table} im
             JOIN users u ON im.created_by = u.id
             JOIN ingredients i ON im.ingredient_id = i.id
             WHERE DATE(im.created_at) BETWEEN ? AND ?
             ORDER BY im.created_at DESC",
            [$from, $to]
        )->fetchAll();
    }
}
