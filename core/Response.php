<?php

class Response
{
    public static function json(mixed $data, int $code = 200): void
    {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit;
    }

    public static function redirect(string $url, int $code = 302): void
    {
        http_response_code($code);
        header("Location: {$url}");
        exit;
    }

    public static function html(string $content, int $code = 200): void
    {
        http_response_code($code);
        header('Content-Type: text/html; charset=utf-8');
        echo $content;
        exit;
    }

    public static function error(int $code, string $message = ''): void
    {
        http_response_code($code);
        if (Request::isAjax()) {
            self::json(['error' => true, 'message' => $message], $code);
        } else {
            echo $message ?: "Erreur {$code}";
        }
        exit;
    }

    public static function success(string $message = 'Succès'): void
    {
        self::json(['success' => true, 'message' => $message]);
    }
}
