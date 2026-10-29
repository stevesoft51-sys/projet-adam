<?php

class OrderModel extends Model
{
    protected string $table = 'orders';

    public function generateNumber(): string
    {
        $date = date('Ymd');
        $lastOrder = $this->db->query(
            "SELECT order_number FROM {$this->table} WHERE order_number LIKE ? ORDER BY id DESC LIMIT 1",
            ["ORD-{$date}%"]
        )->fetch();

        if ($lastOrder) {
            $seq = (int)substr($lastOrder['order_number'], -4) + 1;
        } else {
            $seq = 1;
        }

        return 'ORD-' . $date . '-' . str_pad($seq, 4, '0', STR_PAD_LEFT);
    }

    public function getActive(): array
    {
        return $this->db->query(
            "SELECT o.*, t.number as table_number, u.name as server_name,
                    (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.id AND oi.status != 'cancelled') as items_count
             FROM {$this->table} o
             LEFT JOIN tables_restaurant t ON o.table_id = t.id
             LEFT JOIN users u ON o.user_id = u.id
             WHERE o.status NOT IN ('paid', 'cancelled')
             ORDER BY 
                CASE o.status 
                    WHEN 'pending' THEN 1 
                    WHEN 'confirmed' THEN 2 
                    WHEN 'preparing' THEN 3 
                    WHEN 'ready' THEN 4 
                    WHEN 'served' THEN 5 
                    ELSE 6 
                END ASC,
                o.created_at ASC"
        )->fetchAll();
    }

    public function getForKitchen(): array
    {
        return $this->db->query(
            "SELECT o.*, t.number as table_number
             FROM {$this->table} o
             LEFT JOIN tables_restaurant t ON o.table_id = t.id
             WHERE o.status IN ('confirmed', 'preparing')
             ORDER BY o.created_at ASC"
        )->fetchAll();
    }

    public function getWithItems(int $id): ?array
    {
        $order = $this->find($id);
        if (!$order) return null;

        $order['items'] = $this->db->query(
            "SELECT oi.*, p.name as product_name, p.image as product_image
             FROM order_items oi
             JOIN products p ON oi.product_id = p.id
             WHERE oi.order_id = ?",
            [$id]
        )->fetchAll();

        $order['payments'] = $this->db->query(
            "SELECT * FROM payments WHERE order_id = ? ORDER BY created_at DESC",
            [$id]
        )->fetchAll();

        return $order;
    }

    public function createWithItems(array $orderData, array $items): int
    {
        $this->db->beginTransaction();
        try {
            $subtotal = 0;
            foreach ($items as $item) {
                $subtotal += $item['unit_price'] * $item['quantity'];
            }

            $settings = $this->db->query("SELECT setting_value FROM settings WHERE setting_key = 'tax_rate'")->fetch();
            $taxRate = $settings ? (float)$settings['setting_value'] : 18;
            $tax = $subtotal * ($taxRate / 100);
            $total = $subtotal + $tax;

            $orderData['subtotal'] = $subtotal;
            $orderData['tax'] = $tax;
            $orderData['total'] = $total;
            $orderData['order_number'] = $this->generateNumber();
            $orderData['status'] = 'confirmed';

            $orderId = $this->db->insert($this->table, $orderData);

            foreach ($items as $item) {
                $this->db->insert('order_items', [
                    'order_id' => $orderId,
                    'product_id' => $item['product_id'],
                    'quantity' => $item['quantity'],
                    'unit_price' => $item['unit_price'],
                    'total_price' => $item['unit_price'] * $item['quantity'],
                    'notes' => $item['notes'] ?? null,
                ]);
            }

            $this->db->commit();
            return $orderId;
        } catch (Exception $e) {
            $this->db->rollBack();
            throw $e;
        }
    }

    public function updateStatus(int $id, string $status): int
    {
        $data = ['status' => $status];
        if ($status === 'paid') {
            $data['paid_at'] = date('Y-m-d H:i:s');
        }
        return $this->db->update($this->table, $data, 'id = ?', [$id]);
    }

    public function addItem(int $orderId, array $itemData): int
    {
        $itemData['order_id'] = $orderId;
        $itemData['total_price'] = $itemData['unit_price'] * $itemData['quantity'];

        $itemId = $this->db->insert('order_items', $itemData);

        $this->recalculateTotal($orderId);
        return $itemId;
    }

    public function removeItem(int $itemId): int
    {
        $item = $this->db->find('order_items', 'id = ?', [$itemId]);
        if (!$item) return 0;

        $result = $this->db->delete('order_items', 'id = ?', [$itemId]);
        $this->recalculateTotal($item['order_id']);
        return $result;
    }

    private function recalculateTotal(int $orderId): void
    {
        $subtotal = (float)$this->db->sum('order_items', 'total_price', 'order_id = ? AND status != "cancelled"', [$orderId]);
        $settings = $this->db->query("SELECT setting_value FROM settings WHERE setting_key = 'tax_rate'")->fetch();
        $taxRate = $settings ? (float)$settings['setting_value'] : 18;
        $tax = $subtotal * ($taxRate / 100);
        $order = $this->find($orderId);
        $discount = $order ? (float)$order['discount'] : 0;
        $total = $subtotal + $discount + $tax;

        $this->db->update($this->table, [
            'subtotal' => $subtotal,
            'tax' => $tax,
            'total' => $total,
        ], 'id = ?', [$orderId]);
    }

    public function countToday(): int
    {
        return $this->count("DATE(created_at) = CURDATE() AND status != 'cancelled'");
    }

    public function sumToday(): float
    {
        return $this->db->sum($this->table, 'total', "DATE(created_at) = CURDATE() AND status = 'paid'");
    }

    public function getRecent(int $limit = 10): array
    {
        return $this->db->query(
            "SELECT o.*, t.number as table_number, u.name as server_name
             FROM {$this->table} o
             LEFT JOIN tables_restaurant t ON o.table_id = t.id
             LEFT JOIN users u ON o.user_id = u.id
             ORDER BY o.created_at DESC
             LIMIT ?",
            [$limit]
        )->fetchAll();
    }
}
