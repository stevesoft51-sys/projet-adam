<?php

class Auth
{
    private static ?Auth $instance = null;
    private Database $db;

    private function __construct()
    {
        $this->db = Database::getInstance();
    }

    public static function getInstance(): self
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public function attempt(string $email, string $password): bool
    {
        $user = $this->db->find('users', 'email = ? AND is_active = 1', [$email]);

        if (!$user || !password_verify($password, $user['password'])) {
            return false;
        }

        $_SESSION['user_id'] = $user['id'];
        $_SESSION['user_role'] = $user['role'];
        $_SESSION['user_name'] = $user['name'];
        $_SESSION['user_email'] = $user['email'];

        $this->db->update('users', ['last_login' => date('Y-m-d H:i:s')], 'id = ?', [$user['id']]);

        return true;
    }

    public function logout(): void
    {
        session_destroy();
        session_start();
    }

    public function check(): bool
    {
        return isset($_SESSION['user_id']);
    }

    public function user(): array
    {
        if (!$this->check()) {
            return [];
        }

        if (!isset($_SESSION['user_full'])) {
            $_SESSION['user_full'] = $this->db->find('users', 'id = ?', [$_SESSION['user_id']]);
        }

        return $_SESSION['user_full'] ?? [];
    }

    public function id(): ?int
    {
        return $_SESSION['user_id'] ?? null;
    }

    public function role(): ?string
    {
        return $_SESSION['user_role'] ?? null;
    }

    public function name(): string
    {
        return $_SESSION['user_name'] ?? 'Invité';
    }

    public function isAdmin(): bool
    {
        return $this->role() === 'admin';
    }

    public function isManager(): bool
    {
        return in_array($this->role(), ['admin', 'manager']);
    }

    public function canAccess(string $resource): bool
    {
        $permissions = [
            'admin' => ['*'],
            'manager' => ['dashboard', 'menu', 'stock', 'orders', 'tables', 'reservations', 'cash', 'staff', 'loyalty', 'reports'],
            'serveur' => ['orders', 'tables', 'reservations', 'cash'],
            'cuisinier' => ['orders'],
            'guichet' => ['pos', 'cash', 'orders', 'factures'],
        ];

        $role = $this->role();
        if (!isset($permissions[$role])) return false;
        if (in_array('*', $permissions[$role])) return true;
        return in_array($resource, $permissions[$role]);
    }

    public function isGuichet(): bool
    {
        return $this->role() === 'guichet';
    }
}
