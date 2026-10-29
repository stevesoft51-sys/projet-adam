<?php

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$uri = rtrim($uri, '/') ?: '/';

// Serve static assets from public/ directory
if (preg_match('/\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/', $uri)) {
    $file = __DIR__ . '/public' . $uri;
    if (file_exists($file)) {
        $mimeTypes = [
            'css' => 'text/css', 'js' => 'application/javascript',
            'png' => 'image/png', 'jpg' => 'image/jpeg', 'jpeg' => 'image/jpeg',
            'gif' => 'image/gif', 'svg' => 'image/svg+xml', 'ico' => 'image/x-icon',
            'woff' => 'font/woff', 'woff2' => 'font/woff2', 'ttf' => 'font/ttf',
            'eot' => 'application/vnd.ms-fontobject', 'webp' => 'image/webp',
        ];
        $ext = pathinfo($file, PATHINFO_EXTENSION);
        header('Content-Type: ' . ($mimeTypes[$ext] ?? 'application/octet-stream'));
        readfile($file);
        return true;
    }
}

// Serve API standalone files directly
if (strpos($uri, '/api/') === 0) {
    $file = __DIR__ . $uri . '.php';
    if (file_exists($file)) {
        require $file;
        return true;
    }
}

// Serve install.php directly
if ($uri === '/install.php') {
    require __DIR__ . '/install.php';
    return true;
}

// Block access to sensitive directories
if (preg_match('#^/(config|core|models|middleware|database)/#', $uri)) {
    http_response_code(403);
    echo 'Forbidden';
    return true;
}

// Route everything else through the MVC front controller
require __DIR__ . '/index.php';
return true;
