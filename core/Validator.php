<?php

class Validator
{
    private array $errors = [];

    public function validate(array $rules): array
    {
        $this->errors = [];
        $data = Request::all();
        $validated = [];

        foreach ($rules as $field => $fieldRules) {
            $ruleList = is_string($fieldRules) ? explode('|', $fieldRules) : $fieldRules;
            $value = $data[$field] ?? null;

            foreach ($ruleList as $rule) {
                $params = [];
                if (str_contains($rule, ':')) {
                    [$rule, $paramStr] = explode(':', $rule, 2);
                    $params = explode(',', $paramStr);
                }

                match ($rule) {
                    'required' => $this->required($field, $value),
                    'email' => $this->email($field, $value),
                    'min' => $this->min($field, $value, (int)$params[0]),
                    'max' => $this->max($field, $value, (int)$params[0]),
                    'numeric' => $this->numeric($field, $value),
                    'integer' => $this->integer($field, $value),
                    'date' => $this->date($field, $value),
                    'in' => $this->in($field, $value, $params),
                    'confirmed' => $this->confirmed($field, $value),
                    'unique' => $this->unique($field, $value, $params),
                    'alpha' => $this->alpha($field, $value),
                    'phone' => $this->phone($field, $value),
                    default => null,
                };
            }

            $validated[$field] = $value;
        }

        if (!empty($this->errors)) {
            if (Request::isAjax()) {
                Response::json(['errors' => $this->errors], 422);
            } else {
                $_SESSION['errors'] = $this->errors;
                $_SESSION['old'] = $data;
                header('Location: ' . ($_SERVER['HTTP_REFERER'] ?? '/'));
                exit;
            }
        }

        return $validated;
    }

    private function required(string $field, mixed $value): void
    {
        if ($value === null || $value === '') {
            $this->errors[$field][] = "Le champ {$field} est obligatoire.";
        }
    }

    private function email(string $field, mixed $value): void
    {
        if ($value && !filter_var($value, FILTER_VALIDATE_EMAIL)) {
            $this->errors[$field][] = "Le champ {$field} doit être un email valide.";
        }
    }

    private function min(string $field, mixed $value, int $min): void
    {
        if (is_string($value) && strlen($value) < $min) {
            $this->errors[$field][] = "Le champ {$field} doit contenir au moins {$min} caractères.";
        }
    }

    private function max(string $field, mixed $value, int $max): void
    {
        if (is_string($value) && strlen($value) > $max) {
            $this->errors[$field][] = "Le champ {$field} ne doit pas dépasser {$max} caractères.";
        }
    }

    private function numeric(string $field, mixed $value): void
    {
        if ($value !== null && $value !== '' && !is_numeric($value)) {
            $this->errors[$field][] = "Le champ {$field} doit être numérique.";
        }
    }

    private function integer(string $field, mixed $value): void
    {
        if ($value !== null && $value !== '' && !ctype_digit((string)$value)) {
            $this->errors[$field][] = "Le champ {$field} doit être un entier.";
        }
    }

    private function date(string $field, mixed $value): void
    {
        if ($value && !strtotime($value)) {
            $this->errors[$field][] = "Le champ {$field} doit être une date valide.";
        }
    }

    private function in(string $field, mixed $value, array $allowed): void
    {
        if ($value && !in_array($value, $allowed)) {
            $this->errors[$field][] = "Le champ {$field} n'est pas valide.";
        }
    }

    private function confirmed(string $field, mixed $value): void
    {
        $confirmField = $field . '_confirmation';
        $confirmValue = Request::post($confirmField);
        if ($value !== $confirmValue) {
            $this->errors[$field][] = "La confirmation du champ {$field} ne correspond pas.";
        }
    }

    private function unique(string $field, mixed $value, array $params): void
    {
        if (!$value) return;
        $table = $params[0] ?? '';
        $exceptId = $params[1] ?? null;
        $db = Database::getInstance();
        $where = "{$field} = ?";
        $params_arr = [$value];
        if ($exceptId) {
            $where .= " AND id != ?";
            $params_arr[] = $exceptId;
        }
        $exists = $db->count($table, $where, $params_arr);
        if ($exists > 0) {
            $this->errors[$field][] = "Ce {$field} existe déjà.";
        }
    }

    private function alpha(string $field, mixed $value): void
    {
        if ($value && !preg_match('/^[a-zA-ZÀ-ÿ\s\'-]+$/', $value)) {
            $this->errors[$field][] = "Le champ {$field} ne doit contenir que des lettres.";
        }
    }

    private function phone(string $field, mixed $value): void
    {
        if ($value && !preg_match('/^[\+]?[0-9\s\-\(\)]{8,15}$/', $value)) {
            $this->errors[$field][] = "Le champ {$field} doit être un numéro de téléphone valide.";
        }
    }

    public function getErrors(): array
    {
        return $this->errors;
    }

    public function hasErrors(): bool
    {
        return !empty($this->errors);
    }

    public function firstError(string $field): ?string
    {
        return $this->errors[$field][0] ?? null;
    }
}
