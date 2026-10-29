<?php
session_start();

// Ensure CSRF token exists for the session
if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

define('ROOT_PATH', __DIR__);
define('CORE_PATH', ROOT_PATH . '/core');
define('CONFIG_PATH', ROOT_PATH . '/config');
define('MODELS_PATH', ROOT_PATH . '/models');
define('CONTROLLERS_PATH', ROOT_PATH . '/controllers');
define('VIEWS_PATH', ROOT_PATH . '/views');
define('PUBLIC_PATH', ROOT_PATH . '/public');

require_once CORE_PATH . '/Database.php';
require_once CORE_PATH . '/Router.php';
require_once CORE_PATH . '/Controller.php';
require_once CORE_PATH . '/Model.php';
require_once CORE_PATH . '/Auth.php';
require_once CORE_PATH . '/Request.php';
require_once CORE_PATH . '/Response.php';
require_once CORE_PATH . '/Validator.php';
require_once CORE_PATH . '/View.php';

function csrf_field(): string
{
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return '<input type="hidden" name="_token" value="' . htmlspecialchars($_SESSION['csrf_token']) . '">';
}

spl_autoload_register(function (string $class): void {
    // Try direct model file
    if (file_exists(MODELS_PATH . '/' . $class . '.php')) {
        require_once MODELS_PATH . '/' . $class . '.php';
        return;
    }
    // Try middleware
    if (file_exists(ROOT_PATH . '/middleware/' . $class . '.php')) {
        require_once ROOT_PATH . '/middleware/' . $class . '.php';
        return;
    }
    // Scan all controllers and match class name inside file
    foreach ([CONTROLLERS_PATH . '/Admin', CONTROLLERS_PATH . '/Client', CONTROLLERS_PATH] as $dir) {
        if (!is_dir($dir)) continue;
        foreach (glob($dir . '/*.php') as $file) {
            $content = file_get_contents($file);
            if (preg_match('/^\s*class\s+' . preg_quote($class) . '\s/m', $content)) {
                require_once $file;
                return;
            }
        }
    }
});

require_once CORE_PATH . '/App.php';

try {
    $app = new App();
    $app->run();
} catch (Throwable $e) {
    error_log('Application error: ' . $e->getMessage() . ' in ' . $e->getFile() . ':' . $e->getLine());
    http_response_code(500);
    if (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest') {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['error' => 'Erreur interne du serveur']);
    } else {
        echo '<h1>Erreur interne du serveur</h1>';
        echo '<p>Une erreur inattendue s\'est produite. Veuillez réessayer.</p>';
        echo '<p><a href="/">Retour à l\'accueil</a></p>';
    }
}
