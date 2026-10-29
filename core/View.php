<?php

class View
{
    private array $shareData = [];

    public function share(string $key, mixed $value): void
    {
        $this->shareData[$key] = $value;
    }

    public function render(string $view, array $data = [], ?string $layout = null): void
    {
        $data = array_merge($this->shareData, $data);
        extract($data);

        $viewPath = VIEWS_PATH . '/' . str_replace('.', '/', $view) . '.php';
        if (!file_exists($viewPath)) {
            http_response_code(500);
            echo "Vue introuvable: {$view}";
            return;
        }

        ob_start();
        require $viewPath;
        $content = ob_get_clean();

        if ($layout) {
            $layoutPath = VIEWS_PATH . '/layouts/' . $layout . '.php';
            if (file_exists($layoutPath)) {
                require $layoutPath;
            } else {
                echo $content;
            }
        } else {
            echo $content;
        }
    }

    public function renderAdmin(string $view, array $data = []): void
    {
        $data['auth'] = Auth::getInstance();
        $data['appName'] = (require CONFIG_PATH . '/app.php')['name'];
        $data['currentPage'] = $view;
        $this->render($view, $data, 'admin');
    }

    public function renderGuichet(string $view, array $data = []): void
    {
        $data['auth'] = Auth::getInstance();
        $data['appName'] = (require CONFIG_PATH . '/app.php')['name'];
        $data['currentPage'] = $view;
        $this->render($view, $data, 'guichet');
    }

    public function renderClient(string $view, array $data = []): void
    {
        $data['appName'] = (require CONFIG_PATH . '/app.php')['name'];
        $this->render($view, $data, 'client');
    }

    public function partial(string $partial, array $data = []): void
    {
        $data = array_merge($this->shareData, $data);
        extract($data);
        $partialPath = VIEWS_PATH . '/partials/' . str_replace('.', '/', $partial) . '.php';
        if (file_exists($partialPath)) {
            require $partialPath;
        }
    }

    public static function e(string $value): string
    {
        return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
    }

    public static function money(float $amount): string
    {
        return number_format($amount, 0, ',', ' ') . ' FCFA';
    }

    public static function date(string $date, string $format = 'd/m/Y'): string
    {
        return date($format, strtotime($date));
    }

    public static function datetime(string $datetime): string
    {
        return date('d/m/Y H:i', strtotime($datetime));
    }

    public static function timeAgo(string $datetime): string
    {
        $now = new DateTime();
        $past = new DateTime($datetime);
        $diff = $now->diff($past);

        if ($diff->y > 0) return "il y a {$diff->y} an" . ($diff->y > 1 ? 's' : '');
        if ($diff->m > 0) return "il y a {$diff->m} mois";
        if ($diff->d > 0) return "il y a {$diff->d} jour" . ($diff->d > 1 ? 's' : '');
        if ($diff->h > 0) return "il y a {$diff->h} heure" . ($diff->h > 1 ? 's' : '');
        if ($diff->i > 0) return "il y a {$diff->i} minute" . ($diff->i > 1 ? 's' : '');
        return "à l'instant";
    }
}
