<?php

class SettingModel extends Model
{
    protected string $table = 'settings';

    public static function getValue(string $key, mixed $default = null): mixed
    {
        $db = Database::getInstance();
        $row = $db->find('settings', 'setting_key = ?', [$key]);
        if (!$row) return $default;

        return match ($row['setting_type']) {
            'int' => (int)$row['setting_value'],
            'float' => (float)$row['setting_value'],
            'bool' => (bool)$row['setting_value'],
            'json' => json_decode($row['setting_value'], true),
            default => $row['setting_value'],
        };
    }

    public static function set(string $key, mixed $value, string $type = 'string'): void
    {
        $db = Database::getInstance();
        $exists = $db->count('settings', 'setting_key = ?', [$key]);
        $val = is_array($value) ? json_encode($value) : (string)$value;

        if ($exists) {
            $db->update('settings', ['setting_value' => $val, 'setting_type' => $type], 'setting_key = ?', [$key]);
        } else {
            $db->insert('settings', ['setting_key' => $key, 'setting_value' => $val, 'setting_type' => $type]);
        }
    }

    public static function getAll(): array
    {
        $db = Database::getInstance();
        $rows = $db->findAll('settings', 'id ASC');
        $settings = [];
        foreach ($rows as $row) {
            $settings[$row['setting_key']] = match ($row['setting_type']) {
                'int' => (int)$row['setting_value'],
                'float' => (float)$row['setting_value'],
                'bool' => (bool)$row['setting_value'],
                'json' => json_decode($row['setting_value'], true),
                default => $row['setting_value'],
            };
        }
        return $settings;
    }

    public static function updateMany(array $data): void
    {
        foreach ($data as $key => $value) {
            self::set($key, $value);
        }
    }
}
