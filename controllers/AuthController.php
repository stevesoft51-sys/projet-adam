<?php

class AuthController extends Controller
{
    public function showLogin(): void
    {
        if ($this->auth->check()) {
            $this->redirect('/admin');
        }

        $config = require CONFIG_PATH . '/app.php';
        require VIEWS_PATH . '/auth/login.php';
    }

    public function login(): void
    {
        AuthMiddleware::csrf();

        $email = Request::post('email', '');
        $password = Request::post('password', '');

        if (empty($email) || empty($password)) {
            $_SESSION['login_error'] = 'Veuillez remplir tous les champs';
            header('Location: /login');
            exit;
        }

        if ($this->auth->attempt($email, $password)) {
            unset($_SESSION['login_error']);
            $role = $this->auth->role();
            $redirects = [
                'cuisinier' => '/admin/orders/kitchen',
                'guichet' => '/guichet',
            ];
            $this->redirect($redirects[$role] ?? '/admin');
        } else {
            $_SESSION['login_error'] = 'Email ou mot de passe incorrect';
            header('Location: /login');
            exit;
        }
    }

    public function logout(): void
    {
        $this->auth->logout();
        header('Location: /login');
        exit;
    }
}
