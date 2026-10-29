# Restaurant ADAM — version web (PHP 8.3 / MySQL)
1. Éditez `config.php` (accès MySQL).
2. Placez le dossier sur Apache/Nginx+PHP (ou `php -S localhost:8000`).
3. Ouvrez `/install.php` (crée base, tables, données, 6 comptes `@adam.com` / `admin123`), puis **supprimez install.php**.
4. Site public : `/` — équipe : `/?p=login`. API : `POST /api/reservation.php`, `GET /api/reservation.php?code=...`.
Règles reproduites : commande créée en `confirmed` sans déduction de stock ; déduction au passage à `confirmed` (répétable) ; taxe 18 % ; paiement partiel/complet ; tout paiement alimente la caisse ouverte ; caisse attendue = fond + entrées − sorties.
