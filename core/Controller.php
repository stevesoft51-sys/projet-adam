<?php

class Controller
{
    protected Database $db;
    protected Auth $auth;
    protected View $view;

    public function __construct()
    {
        $this->db = Database::getInstance();
        $this->auth = Auth::getInstance();
        $this->view = new View();
    }

    protected function redirect(string $url): void
    {
        header("Location: {$url}");
        exit;
    }

    protected function json(mixed $data, int $code = 200): void
    {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($data, JSON_UNESCAPED_UNICODE);
        exit;
    }

    protected function input(): array
    {
        return Request::all();
    }

    protected function post(string $key, mixed $default = null): mixed
    {
        return Request::post($key, $default);
    }

    protected function get(string $key, mixed $default = null): mixed
    {
        return Request::get($key, $default);
    }

    protected function validate(array $rules): array
    {
        $validator = new Validator();
        return $validator->validate($rules);
    }

    protected function csrfToken(): string
    {
        if (empty($_SESSION['csrf_token'])) {
            $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
        }
        return $_SESSION['csrf_token'];
    }

    protected function csrfField(): string
    {
        return '<input type="hidden" name="_token" value="' . $this->csrfToken() . '">';
    }

    protected function verifyCsrf(): bool
    {
        $token = $_POST['_token'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
        return hash_equals($this->csrfToken(), $token);
    }

    protected function uploadImage(string $inputName, string $destination): ?string
    {
        if (!isset($_FILES[$inputName]) || $_FILES[$inputName]['error'] !== UPLOAD_ERR_OK) {
            return null;
        }

        $file = $_FILES[$inputName];
        $config = require CONFIG_PATH . '/app.php';

        if ($file['size'] > $config['upload_max_size']) {
            return null;
        }

        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $mime = finfo_file($finfo, $file['tmp_name']);
        finfo_close($finfo);

        if (!in_array($mime, $config['allowed_image_types'])) {
            return null;
        }

        $extension = match($mime) {
            'image/jpeg' => 'jpg',
            'image/png' => 'png',
            'image/webp' => 'webp',
            'image/gif' => 'gif',
            default => 'jpg',
        };

        $filename = uniqid('img_', true) . '.' . $extension;
        $uploadPath = PUBLIC_PATH . '/images/uploads/' . $destination;

        if (!is_dir($uploadPath)) {
            mkdir($uploadPath, 0755, true);
        }

        $fullPath = $uploadPath . '/' . $filename;

        if (!move_uploaded_file($file['tmp_name'], $fullPath)) {
            return null;
        }

        return '/images/uploads/' . $destination . '/' . $filename;
    }

    protected function deleteImage(string $path): bool
    {
        if (empty($path)) return true;
        $fullPath = PUBLIC_PATH . $path;
        if (file_exists($fullPath)) {
            return unlink($fullPath);
        }
        return true;
    }

    protected function formatCurrency(float $amount): string
    {
        return number_format($amount, 0, ',', ' ') . ' FCFA';
    }

    protected function paginate(string $table, string $where = '1=1', array $params = [], int $perPage = 15): array
    {
        $page = max(1, (int)($this->get('page', 1)));
        $total = $this->db->count($table, $where, $params);
        $totalPages = max(1, ceil($total / $perPage));
        $page = min($page, $totalPages);
        $offset = ($page - 1) * $perPage;

        $sql = "SELECT * FROM {$table} WHERE {$where} ORDER BY id DESC LIMIT {$perPage} OFFSET {$offset}";
        $items = $this->db->query($sql, $params)->fetchAll();

        return [
            'items' => $items,
            'page' => $page,
            'per_page' => $perPage,
            'total' => $total,
            'total_pages' => $totalPages,
        ];
    }
}
