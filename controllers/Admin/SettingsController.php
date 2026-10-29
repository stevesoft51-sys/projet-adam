<?php

class AdminSettingsController extends Controller
{
    public function index(): void
    {
        AuthMiddleware::admin();
        $settings = SettingModel::getAll();
        $this->view->renderAdmin('admin/settings/index', compact('settings'));
    }

    public function update(): void
    {
        AuthMiddleware::admin();
        AuthMiddleware::csrf();

        $settings = [
            'restaurant_name' => $_POST['restaurant_name'] ?? '',
            'restaurant_phone' => $_POST['restaurant_phone'] ?? '',
            'restaurant_address' => $_POST['restaurant_address'] ?? '',
            'tax_rate' => $_POST['tax_rate'] ?? '18',
            'opening_time' => $_POST['opening_time'] ?? '08:00',
            'closing_time' => $_POST['closing_time'] ?? '23:00',
            'reservation_duration' => $_POST['reservation_duration'] ?? '120',
            'loyalty_enabled' => isset($_POST['loyalty_enabled']) ? '1' : '0',
            'loyalty_points_per_fcfa' => $_POST['loyalty_points_per_fcfa'] ?? '1',
            'cinetpay_enabled' => isset($_POST['cinetpay_enabled']) ? '1' : '0',
            'cinetpay_api_key' => $_POST['cinetpay_api_key'] ?? '',
            'cinetpay_site_id' => $_POST['cinetpay_site_id'] ?? '',
            'cinetpay_secret_key' => $_POST['cinetpay_secret_key'] ?? '',
            'brevo_api_key' => $_POST['brevo_api_key'] ?? '',
            'restaurant_email' => $_POST['restaurant_email'] ?? '',
        ];

        SettingModel::updateMany($settings);

        $_SESSION['success'] = 'Paramètres mis à jour';
        $this->redirect('/admin/settings');
    }

    public function updatePassword(): void
    {
        AuthMiddleware::admin();
        AuthMiddleware::csrf();

        $userId = $this->auth->id();
        $user = $this->auth->user();

        $currentPassword = $_POST['current_password'] ?? '';
        $newPassword = $_POST['new_password'] ?? '';
        $confirmPassword = $_POST['new_password_confirmation'] ?? '';

        if (!password_verify($currentPassword, $user['password'])) {
            $_SESSION['error'] = 'Mot de passe actuel incorrect';
            $this->redirect('/admin/settings');
        }

        if ($newPassword !== $confirmPassword) {
            $_SESSION['error'] = 'Les mots de passe ne correspondent pas';
            $this->redirect('/admin/settings');
        }

        if (strlen($newPassword) < 6) {
            $_SESSION['error'] = 'Le mot de passe doit faire au moins 6 caractères';
            $this->redirect('/admin/settings');
        }

        (new UserModel())->updateById($userId, ['password' => $newPassword]);
        $_SESSION['success'] = 'Mot de passe mis à jour';
        $this->redirect('/admin/settings');
    }
}
