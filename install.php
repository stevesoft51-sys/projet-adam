<?php
/**
 * RESTAURANT ADAM - Script d'installation
 * Supprimez ce fichier après installation !
 */
session_start();
$message = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $host = trim($_POST['host'] ?? '');
    $database = trim($_POST['database'] ?? '');
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    try {
        $dsn = "mysql:host={$host};charset=utf8mb4";
        $pdo = new PDO($dsn, $username, $password, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
        ]);

        // Create database if not exists
        $pdo->exec("CREATE DATABASE IF NOT EXISTS `{$database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
        $pdo->exec("USE `{$database}`");

        // Run schema
        $schema = file_get_contents(__DIR__ . '/database/schema.sql');
        $pdo->exec($schema);
        $message .= "Schema cree avec succes!<br>";

        // Run seed (without user inserts - we'll hash passwords properly)
        $seedContent = file_get_contents(__DIR__ . '/database/seed.sql');
        // Remove user INSERT from seed (multi-line safe)
        $seedContent = preg_replace('/INSERT INTO users.*?;/s', '-- users inserted below', $seedContent, 1);
        try {
            $pdo->exec($seedContent);
            $message .= "Donnees initiales inserees!<br>";
        } catch (PDOException $e) {
            $message .= "Seed deja applique ou erreur: " . $e->getMessage() . "<br>";
        }
        
        // Insert users with properly hashed passwords
        $defaultPass = password_hash('admin123', PASSWORD_BCRYPT);
        $users = [
            ['Administrateur', 'admin@adam.com', 'admin', '+225 01 02 03 04'],
            ['Manager Principal', 'manager@adam.com', 'manager', '+225 05 06 07 08'],
            ['Kofi Mensah', 'kofi@adam.com', 'serveur', '+225 11 12 13 14'],
            ['Aya Kouame', 'aya@adam.com', 'serveur', '+225 15 16 17 18'],
            ['Chef Moussa', 'moussa@adam.com', 'cuisinier', '+225 21 22 23 24'],
            ['Fatou Diallo', 'fatou@adam.com', 'guichet', '+225 31 32 33 34'],
        ];
        $stmt = $pdo->prepare("REPLACE INTO users (name, email, password, role, phone, is_active) VALUES (?, ?, ?, ?, ?, 1)");
        foreach ($users as $u) {
            $stmt->execute([$u[0], $u[1], $defaultPass, $u[2], $u[3]]);
        }
        $message .= "Utilisateurs crees (mot de passe: admin123)<br>";

        // Update config/database.php
        $configContent = "<?php

return [
";
        $configContent .= "    'host' => '" . addslashes($host) . "',
";
        $configContent .= "    'database' => '" . addslashes($database) . "',
";
        $configContent .= "    'username' => '" . addslashes($username) . "',
";
        $configContent .= "    'password' => '" . addslashes($password) . "',
";
        $configContent .= "    'charset' => 'utf8mb4',
";
        $configContent .= "    'options' => [
";
        $configContent .= "        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
";
        $configContent .= "        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
";
        $configContent .= "        PDO::ATTR_EMULATE_PREPARES => false,
";
        $configContent .= "    ],
";
        $configContent .= "];
";

        if (file_put_contents(__DIR__ . '/config/database.php', $configContent)) {
            $message .= "Configuration mise a jour!<br>";
        }

        $message .= "<br><strong>Installation terminee!</strong><br>";
        $message .= "Connectez-vous avec: admin@adam.com / admin123<br>";
        $message .= "<strong>IMPORTANT: Supprimez ce fichier install.php !</strong><br>";
        $message .= '<a href="/login" class="btn btn-primary">Se connecter</a>';

    } catch (PDOException $e) {
        $error = "Erreur de connexion: " . $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Installation - Restaurant ADAM</title>
    <link rel="stylesheet" href="/css/common.css">
    <style>
        body { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: #f8f9fa; }
        .install-card { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 2.5rem; width: 100%; max-width: 480px; }
        .install-card h1 { text-align: center; margin-bottom: 0.5rem; }
        .install-card p { text-align: center; color: #7f8c8d; margin-bottom: 2rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; font-weight: 600; margin-bottom: 0.375rem; font-size: 0.875rem; }
        .form-control { width: 100%; padding: 0.625rem 0.875rem; border: 1.5px solid #e0e0e0; border-radius: 8px; font-size: 0.875rem; }
        .btn { display: block; width: 100%; padding: 0.75rem; background: #e94560; color: #fff; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }
        .btn:hover { background: #c73650; }
        .alert { padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="install-card">
        <h1>🍽 Restaurant ADAM</h1>
        <p>Script d'installation</p>

        <?php if ($message): ?><div class="alert alert-success"><?= $message ?></div><?php endif; ?>
        <?php if ($error): ?><div class="alert alert-error"><?= $error ?></div><?php endif; ?>

        <form method="POST">
            <div class="form-group">
                <label>Host MySQL</label>
                <input type="text" name="host" class="form-control" value="<?= htmlspecialchars($_POST['host'] ?? 'sql.infinityfree.com') ?>" required>
            </div>
            <div class="form-group">
                <label>Nom de la base</label>
                <input type="text" name="database" class="form-control" value="<?= htmlspecialchars($_POST['database'] ?? '') ?>" required>
            </div>
            <div class="form-group">
                <label>Utilisateur MySQL</label>
                <input type="text" name="username" class="form-control" value="<?= htmlspecialchars($_POST['username'] ?? '') ?>" required>
            </div>
            <div class="form-group">
                <label>Mot de passe MySQL</label>
                <input type="password" name="password" class="form-control" value="" required>
            </div>
            <button type="submit" class="btn">Installer</button>
        </form>
    </div>
</body>
</html>
