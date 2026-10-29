<?php

class AuthMiddleware
{
    public static function check(): void
    {
        if (!Auth::getInstance()->check()) {
            if (Request::isAjax()) {
                Response::json(['error' => 'Non authentifié'], 401);
            } else {
                header('Location: /login');
                exit;
            }
        }
    }

    public static function role(string ...$roles): void
    {
        self::check();
        $userRole = Auth::getInstance()->role();
        if (!in_array($userRole, $roles)) {
            if (Request::isAjax()) {
                Response::json(['error' => 'Accès interdit'], 403);
            } else {
                http_response_code(403);
                echo 'Accès interdit - Permissions insuffisantes';
                exit;
            }
        }
    }

    public static function admin(): void
    {
        self::role('admin');
    }

    public static function manager(): void
    {
        self::role('admin', 'manager');
    }

    public static function can(string $resource): void
    {
        self::check();
        if (!Auth::getInstance()->canAccess($resource)) {
            if (Request::isAjax()) {
                Response::json(['error' => 'Accès interdit'], 403);
            } else {
                http_response_code(403);
                echo 'Accès interdit';
                exit;
            }
        }
    }

    public static function guest(): void
    {
        if (Auth::getInstance()->check()) {
            header('Location: /admin');
            exit;
        }
    }

    public static function csrf(): void
    {
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $token = $_POST['_token'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
            if (!hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
                if (Request::isAjax()) {
                    Response::json(['error' => 'Token CSRF invalide'], 419);
                } else {
                    http_response_code(419);
                    echo 'Session expirée. Veuillez rafraîchir la page.';
                    exit;
                }
            }
        }
    }
}
