<?php

class Model
{
    protected Database $db;
    protected string $table = '';
    protected string $primaryKey = 'id';

    public function __construct()
    {
        $this->db = Database::getInstance();
    }

    public function find(int $id): ?array
    {
        return $this->db->find($this->table, "{$this->primaryKey} = ?", [$id]);
    }

    public function where(string $column, mixed $value, string $operator = '='): self
    {
        $this->wheres[] = "{$column} {$operator} ?";
        $this->whereValues[] = $value;
        return $this;
    }

    private array $wheres = [];
    private array $whereValues = [];
    private string $orderByClause = '';
    private int $limitClause = 100;

    public function orderBy(string $column, string $direction = 'ASC'): self
    {
        $this->orderByClause = "ORDER BY {$column} {$direction}";
        return $this;
    }

    public function limit(int $limit): self
    {
        $this->limitClause = $limit;
        return $this;
    }

    public function get(): array
    {
        $where = !empty($this->wheres) ? implode(' AND ', $this->wheres) : '1=1';
        $sql = "SELECT * FROM {$this->table} WHERE {$where} {$this->orderByClause} LIMIT {$this->limitClause}";
        $result = $this->db->query($sql, $this->whereValues)->fetchAll();
        $this->wheres = [];
        $this->whereValues = [];
        $this->orderByClause = '';
        $this->limitClause = 100;
        return $result;
    }

    public function first(): ?array
    {
        $this->limitClause = 1;
        $results = $this->get();
        return $results[0] ?? null;
    }

    public function create(array $data): int
    {
        $data['created_at'] = date('Y-m-d H:i:s');
        return $this->db->insert($this->table, $data);
    }

    public function updateById(int $id, array $data): int
    {
        $data['updated_at'] = date('Y-m-d H:i:s');
        return $this->db->update($this->table, $data, "{$this->primaryKey} = ?", [$id]);
    }

    public function deleteById(int $id): int
    {
        return $this->db->delete($this->table, "{$this->primaryKey} = ?", [$id]);
    }

    public function count(string $where = '1=1', array $params = []): int
    {
        return $this->db->count($this->table, $where, $params);
    }

    public function sum(string $column, string $where = '1=1', array $params = []): float
    {
        return $this->db->sum($this->table, $column, $where, $params);
    }

    public function all(string $orderBy = 'id DESC', int $limit = 100): array
    {
        return $this->db->findAll($this->table, $orderBy, $limit);
    }
}
