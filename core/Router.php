<?php

class Router
{
    private array $routes = [];
    private array $middleware = [];

    public function get(string $path, string $controller, string $method): self
    {
        $this->routes['GET'][$path] = ['controller' => $controller, 'method' => $method];
        return $this;
    }

    public function post(string $path, string $controller, string $method): self
    {
        $this->routes['POST'][$path] = ['controller' => $controller, 'method' => $method];
        return $this;
    }

    public function middleware(string $name, array $params = []): self
    {
        $this->middleware[$name] = $params;
        return $this;
    }

    public function dispatch(string $method, string $uri): void
    {
        $uri = parse_url($uri, PHP_URL_PATH);
        $uri = rtrim($uri, '/') ?: '/';

        if (!isset($this->routes[$method][$uri])) {
            http_response_code(404);
            require VIEWS_PATH . '/errors/404.php';
            return;
        }

        $route = $this->routes[$method][$uri];

        if (isset($this->middleware['auth'])) {
            $role = $this->middleware['auth']['role'] ?? null;
            $auth = Auth::getInstance();
            if (!$auth->check()) {
                header('Location: /login');
                exit;
            }
            if ($role && $auth->user()['role'] !== $role && $auth->user()['role'] !== 'admin') {
                http_response_code(403);
                echo 'Accès interdit';
                exit;
            }
        }

        $controllerClass = $route['controller'];
        $method = $route['method'];

        if (!class_exists($controllerClass)) {
            http_response_code(500);
            echo "Controller {$controllerClass} introuvable";
            return;
        }

        $controller = new $controllerClass();
        if (!method_exists($controller, $method)) {
            http_response_code(500);
            echo "Méthode {$method} introuvable dans {$controllerClass}";
            return;
        }

        $controller->$method();
    }
}
