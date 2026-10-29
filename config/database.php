<?php

return [
    'host' => '127.0.0.1',
    'database' => 'adam_restaurant',
    'username' => 'adam_user',
    'password' => 'adam_pass',
    'charset' => 'utf8mb4',
    'options' => [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ],
];
