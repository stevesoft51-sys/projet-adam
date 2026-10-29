<?php

class AdminReportsController extends Controller
{
    public function index(): void
    {
        AuthMiddleware::can('reports');
        $this->sales();
    }

    public function sales(): void
    {
        AuthMiddleware::can('reports');

        $from = $this->get('from', date('Y-m-d', strtotime('first day of this month')));
        $to = $this->get('to', date('Y-m-d'));

        $totalSales = $this->db->sum('orders', 'total', "DATE(created_at) BETWEEN ? AND ? AND status = 'paid'", [$from, $to]);
        $totalOrders = $this->db->count('orders', "DATE(created_at) BETWEEN ? AND ? AND status = 'paid'", [$from, $to]);
        $avgOrder = $totalOrders > 0 ? $totalSales / $totalOrders : 0;

        $salesByDay = $this->db->query(
            "SELECT DATE(created_at) as date, SUM(total) as amount, COUNT(*) as count
             FROM orders WHERE DATE(created_at) BETWEEN ? AND ? AND status = 'paid'
             GROUP BY DATE(created_at) ORDER BY date ASC",
            [$from, $to]
        )->fetchAll();

        $salesByCategory = $this->db->query(
            "SELECT c.name as category, SUM(oi.total_price) as amount, COUNT(DISTINCT oi.order_id) as orders
             FROM order_items oi
             JOIN products p ON oi.product_id = p.id
             JOIN categories c ON p.category_id = c.id
             JOIN orders o ON oi.order_id = o.id
             WHERE DATE(o.created_at) BETWEEN ? AND ? AND o.status = 'paid'
             GROUP BY c.id ORDER BY amount DESC",
            [$from, $to]
        )->fetchAll();

        $topProducts = $this->db->query(
            "SELECT p.name, SUM(oi.quantity) as qty, SUM(oi.total_price) as revenue
             FROM order_items oi
             JOIN products p ON oi.product_id = p.id
             JOIN orders o ON oi.order_id = o.id
             WHERE DATE(o.created_at) BETWEEN ? AND ? AND o.status = 'paid'
             GROUP BY p.id ORDER BY revenue DESC LIMIT 10",
            [$from, $to]
        )->fetchAll();

        $payments = (new PaymentModel())->sumByMethod("DATE(created_at) BETWEEN ? AND ?", [$from, $to]);

        $this->view->renderAdmin('admin/reports/sales', compact(
            'from', 'to', 'totalSales', 'totalOrders', 'avgOrder',
            'salesByDay', 'salesByCategory', 'topProducts', 'payments'
        ));
    }

    public function analytics(): void
    {
        AuthMiddleware::can('reports');

        $today = date('Y-m-d');
        $month = date('Y-m');

        $peakHours = $this->db->query(
            "SELECT HOUR(created_at) as hour, COUNT(*) as count
             FROM orders WHERE DATE_FORMAT(created_at, '%Y-%m') = ? AND status = 'paid'
             GROUP BY HOUR(created_at) ORDER BY count DESC",
            [$month]
        )->fetchAll();

        $diningVsTakeaway = $this->db->query(
            "SELECT type, COUNT(*) as count, SUM(total) as revenue
             FROM orders WHERE DATE_FORMAT(created_at, '%Y-%m') = ? AND status = 'paid'
             GROUP BY type",
            [$month]
        )->fetchAll();

        $weeklyTrend = $this->db->query(
            "SELECT DAYNAME(created_at) as day_name, AVG(total) as avg_order, COUNT(*) as count
             FROM orders WHERE DATE_FORMAT(created_at, '%Y-%m') = ? AND status = 'paid'
             GROUP BY DAYOFWEEK(created_at), DAYNAME(created_at)
             ORDER BY DAYOFWEEK(created_at)",
            [$month]
        )->fetchAll();

        $expenses = (new ExpenseModel())->sumByCategory(
            date('Y-m-01'),
            $today
        );

        $this->view->renderAdmin('admin/reports/analytics', compact(
            'peakHours', 'diningVsTakeaway', 'weeklyTrend', 'expenses'
        ));
    }

    public function export(): void
    {
        AuthMiddleware::can('reports');

        $from = $this->get('from', date('Y-m-d', strtotime('first day of this month')));
        $to = $this->get('to', date('Y-m-d'));

        $orders = $this->db->query(
            "SELECT o.order_number, o.created_at, o.type, o.subtotal, o.tax, o.total,
                    t.number as table_number, u.name as server_name, o.status
             FROM orders o
             LEFT JOIN tables_restaurant t ON o.table_id = t.id
             LEFT JOIN users u ON o.user_id = u.id
             WHERE DATE(o.created_at) BETWEEN ? AND ?
             ORDER BY o.created_at ASC",
            [$from, $to]
        )->fetchAll();

        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename=ventes_' . $from . '_' . $to . '.csv');

        $output = fopen('php://output', 'w');
        fputcsv($output, ['Numéro', 'Date', 'Type', 'Sous-total', 'Taxe', 'Total', 'Table', 'Serveur', 'Statut']);

        foreach ($orders as $order) {
            fputcsv($output, [
                $order['order_number'],
                $order['created_at'],
                $order['type'],
                $order['subtotal'],
                $order['tax'],
                $order['total'],
                $order['table_number'] ?? 'N/A',
                $order['server_name'],
                $order['status'],
            ]);
        }

        fclose($output);
        exit;
    }
}
