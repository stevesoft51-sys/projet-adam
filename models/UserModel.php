<?php

class UserModel extends Model
{
    protected string $table = 'users';

    public function findByEmail(string $email): ?array
    {
        return $this->db->find($this->table, 'email = ?', [$email]);
    }

    public function create(array $data): int
    {
        $data['password'] = password_hash($data['password'], PASSWORD_BCRYPT);
        return parent::create($data);
    }

    public function updateById(int $id, array $data): int
    {
        if (isset($data['password'])) {
            if (empty($data['password'])) {
                unset($data['password']);
            } else {
                $data['password'] = password_hash($data['password'], PASSWORD_BCRYPT);
            }
        }
        return parent::updateById($id, $data);
    }

    public function getActive(): array
    {
        return $this->db->findAll($this->table, 'name ASC', 200);
    }

    public function getByRole(string $role): array
    {
        return $this->db->query(
            "SELECT * FROM {$this->table} WHERE role = ? AND is_active = 1 ORDER BY name ASC",
            [$role]
        )->fetchAll();
    }

    public function countByRole(): array
    {
        $results = $this->db->query(
            "SELECT role, COUNT(*) as count FROM {$this->table} WHERE is_active = 1 GROUP BY role"
        )->fetchAll();
        $counted = [];
        foreach ($results as $r) {
            $counted[$r['role']] = (int)$r['count'];
        }
        return $counted;
    }

    public function toggle(int $id): int
    {
        $user = $this->find($id);
        if (!$user) return 0;
        return $this->db->update($this->table, ['is_active' => $user['is_active'] ? 0 : 1], 'id = ?', [$id]);
    }
}
