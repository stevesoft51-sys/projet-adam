<?php

return [
    'name' => 'Restaurant ADAM',
    'tagline' => "L'art de la cuisine a chaque bouchee",
    'currency' => 'FCFA',
    'currency_symbol' => 'FCFA',
    'timezone' => 'Africa/Abidjan',
    'locale' => 'fr_FR',
    'admin_prefix' => 'admin',
    'upload_max_size' => 10 * 1024 * 1024,
    'allowed_image_types' => ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    'loyalty_points_per_fcfa' => 1,
    'loyalty_tiers' => [
        ['name' => 'Bronze', 'min_points' => 0, 'discount' => 0],
        ['name' => 'Argent', 'min_points' => 100, 'discount' => 5],
        ['name' => 'Or', 'min_points' => 300, 'discount' => 10],
        ['name' => 'Platine', 'min_points' => 500, 'discount' => 15],
    ],
    'reservation_slot_minutes' => 30,
    'max_reservation_advance_days' => 30,
];
