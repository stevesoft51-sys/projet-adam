<?php

class Database
{
    private static ?Database $instance = null;
    private PDO $pdo;

    private function __construct()
    {
        $config = require CONFIG_PATH . '/database.php';
        $dsn = "mysql:host={$config['host']};dbname={$config['database']};charset={$config['charset']}";
        try {
            $this->pdo = new PDO($dsn, $config['username'], $config['password'], $config['options']);
        } catch (PDOException $e) {
            error_log('Database connection failed: ' . $e->getMessage());
            if (php_sapi_name() === 'cli' || (isset($_SERVER['HTTP_HOST']) && false !== strpos($_SERVER['HTTP_HOST'], '127.0.0.1'))) {
                http_response_code(500);
                echo '<h1>Erreur de connexion à la base de données</h1>';
                echo '<p>Vérifiez que MySQL est démarré et que la configuration dans <code>config/database.php</code> est correcte.</p>';
                echo '<p><a href="/install.php">Lancer l\'installation</a></p>';
            } else {
                http_response_code(500);
                echo 'Erreur de connexion à la base de données.';
            }
            exit;
        }
    }

    public static function getInstance(): self
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    public function getConnection(): PDO
    {
        return $this->pdo;
    }

    public function query(string $sql, array $params = []): PDOStatement
    {
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);
        return $stmt;
    }

    public function insert(string $table, array $data): int
    {
        $columns = implode(', ', array_keys($data));
        $placeholders = implode(', ', array_fill(0, count($data), '?'));
        $sql = "INSERT INTO {$table} ({$columns}) VALUES ({$placeholders})";
        $this->query($sql, array_values($data));
        return (int) $this->pdo->lastInsertId();
    }

    public function update(string $table, array $data, string $where, array $whereParams = []): int
    {
        $set = implode(', ', array_map(fn($col) => "{$col} = ?", array_keys($data)));
        $sql = "UPDATE {$table} SET {$set} WHERE {$where}";
        $stmt = $this->query($sql, array_merge(array_values($data), $whereParams));
        return $stmt->rowCount();
    }

    public function delete(string $table, string $where, array $params = []): int
    {
        $sql = "DELETE FROM {$table} WHERE {$where}";
        $stmt = $this->query($sql, $params);
        return $stmt->rowCount();
    }

    public function find(string $table, string $where, array $params = []): ?array
    {
        $sql = "SELECT * FROM {$table} WHERE {$where} LIMIT 1";
        $stmt = $this->query($sql, $params);
        return $stmt->fetch() ?: null;
    }

    public function findAll(string $table, string $orderBy = 'id DESC', int $limit = 100): array
    {
        $sql = "SELECT * FROM {$table} ORDER BY {$orderBy} LIMIT {$limit}";
        return $this->query($sql)->fetchAll();
    }

    public function count(string $table, string $where = '1=1', array $params = []): int
    {
        $sql = "SELECT COUNT(*) as total FROM {$table} WHERE {$where}";
        $stmt = $this->query($sql, $params);
        return (int) $stmt->fetch()['total'];
    }

    public function sum(string $table, string $column, string $where = '1=1', array $params = []): float
    {
        $sql = "SELECT COALESCE(SUM({$column}), 0) as total FROM {$table} WHERE {$where}";
        $stmt = $this->query($sql, $params);
        return (float) $stmt->fetch()['total'];
    }

    public function beginTransaction(): void { $this->pdo->beginTransaction(); }
    public function commit(): void { $this->pdo->commit(); }
    public function rollBack(): void { $this->pdo->rollBack(); }
}
