<?php

class AdminDashboardController extends Controller
{
    public function index(): void
    {
        AuthMiddleware::can('dashboard');

        $today = date('Y-m-d');
        $month = date('Y-m');
        $weekStart = date('Y-m-d', strtotime('monday this week'));
        $weekEnd = date('Y-m-d', strtotime('sunday this week'));

        $orderModel = new OrderModel();
        $paymentModel = new PaymentModel();
        $reservationModel = new ReservationModel();
        $ingredientModel = new IngredientModel();
        $loyaltyModel = new LoyaltyCardModel();
        $expenseModel = new ExpenseModel();

        $data = [
            'todayOrders' => $orderModel->countToday(),
            'todayRevenue' => $orderModel->sumToday(),
            'todayPayments' => $paymentModel->sumToday(),
            'todayReservations' => $reservationModel->countToday(),
            'pendingReservations' => $reservationModel->countPending(),
            'lowStockCount' => $ingredientModel->lowStockCount(),
            'lowStockItems' => $ingredientModel->getLowStock(),
            'activeOrders' => $orderModel->getActive(),
            'recentOrders' => $orderModel->getRecent(8),
            'upcomingReservations' => $reservationModel->getUpcoming(),
            'loyaltyCardCount' => $loyaltyModel->count(),
            'totalLoyaltyPoints' => $loyaltyModel->totalPoints(),
            'monthExpenses' => $expenseModel->totalMonth(),
            'weekRevenue' => $this->db->sum('orders', 'total', "DATE(created_at) BETWEEN ? AND ? AND status = 'paid'", [$weekStart, $weekEnd]),
            'monthRevenue' => $this->db->sum('orders', 'total', "DATE_FORMAT(created_at, '%Y-%m') = ? AND status = 'paid'", [$month]),
        ];

        $this->view->renderAdmin('admin/dashboard', $data);
    }
}
