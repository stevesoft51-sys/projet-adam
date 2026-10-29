-- ====================================
-- RESTAURANT ADAM - Seed Data
-- Run AFTER schema.sql
-- Default password for all users: admin123
-- (If using install.php, this is already hashed)
-- ====================================

-- Admin user (password: admin123)
INSERT INTO users (name, email, password, role, phone, is_active) VALUES
('Administrateur', 'admin@adam.com', '$2y$12$ANLXPoAybdC2oTnXgLgYaOw0vhHLXCAzyKm3PQ9qRy4du.aFaF9PK', 'admin', '+225 01 02 03 04', 1),
('Manager Principal', 'manager@adam.com', '$2y$12$ANLXPoAybdC2oTnXgLgYaOw0vhHLXCAzyKm3PQ9qRy4du.aFaF9PK', 'manager', '+225 05 06 07 08', 1),
('Kofi Mensah', 'kofi@adam.com', '$2y$12$ANLXPoAybdC2oTnXgLgYaOw0vhHLXCAzyKm3PQ9qRy4du.aFaF9PK', 'serveur', '+225 11 12 13 14', 1),
('Aya Kouame', 'aya@adam.com', '$2y$12$ANLXPoAybdC2oTnXgLgYaOw0vhHLXCAzyKm3PQ9qRy4du.aFaF9PK', 'serveur', '+225 15 16 17 18', 1),
('Chef Moussa', 'moussa@adam.com', '$2y$12$ANLXPoAybdC2oTnXgLgYaOw0vhHLXCAzyKm3PQ9qRy4du.aFaF9PK', 'cuisinier', '+225 21 22 23 24', 1),
('Fatou Diallo', 'fatou@adam.com', '$2y$12$ANLXPoAybdC2oTnXgLgYaOw0vhHLXCAzyKm3PQ9qRy4du.aFaF9PK', 'guichet', '+225 31 32 33 34', 1);

-- Categories
INSERT INTO categories (name, description, sort_order, is_active) VALUES
('Entrees', 'Nos entrees et appetizers', 1, 1),
('Plats principaux', 'Les plats signatures du Chef', 2, 1),
('Grillades', 'Viandes et poissons grillés', 3, 1),
('Accompagnements', 'Riz, légumes, tubercules', 4, 1),
('Boissons', 'Boissons fraîches et chaudes', 5, 1),
('Desserts', 'Nos douceurs finales', 6, 1);

-- Products
INSERT INTO products (category_id, name, description, price, cost_price, is_available, is_featured, preparation_time) VALUES
(1, 'Salade d''avocat', 'Avocat frais, tomates cerises, vinaigrette maison', 2500, 800, 1, 1, 10),
(1, 'Brochettes de crevettes', 'Crevettes marinées, grillées à la perfection', 3500, 1200, 1, 1, 15),
(1, 'Samoussas au poulet', '6 pièces croustillantes, sauce épicée', 2000, 600, 1, 0, 12),
(2, 'Poulet yassa', 'Poulet mariné aux oignons et citron, riz', 5000, 1800, 1, 1, 25),
(2, 'Poisson braisé', 'Poisson entier braisé, garniture de légumes', 6000, 2200, 1, 1, 30),
(2, 'Thiéboudienne', 'Riz au poisson à l''ivoriane, légumes', 4500, 1500, 1, 1, 35),
(2, 'Poulet braisé', 'Poulet braisé aux épices, attiéké', 4000, 1400, 1, 0, 25),
(3, 'Côtelettes d''agneau', 'Agneau grillé, jus de romarin', 8000, 3000, 1, 1, 20),
(3, 'Brochettes de bœuf', 'Bœuf tendre grillé, sauce piquante', 5500, 2000, 1, 0, 18),
(4, 'Riz basmati', 'Riz basmati parfumé', 1000, 300, 1, 0, 15),
(4, 'Frites de patates douces', 'Patates douces croustillantes', 1500, 500, 1, 0, 12),
(5, 'Jus de bissap', 'Jus d''hibiscus frais, fait maison', 1000, 200, 1, 1, 5),
(5, 'Jus de gingembre', 'Gingembre frais pressé, citron vert', 1000, 250, 1, 0, 5),
(5, 'Bière flag', 'Bière locale servie bien fraîche', 1000, 400, 1, 0, 2),
(6, 'Salade de fruits', 'Fruits de saison, miel, menthe', 1500, 500, 1, 0, 8),
(6, 'Flan à la vanille', 'Flan maison à la vanille de Madagascar', 1200, 350, 1, 1, 10);

-- Ingredients
INSERT INTO ingredients (name, unit, current_stock, min_stock, cost_per_unit, supplier) VALUES
('Riz', 'kg', 50, 10, 800, 'Fournisseur Abidjan'),
('Poulet entier', 'kg', 30, 5, 2500, 'Ferme Locale'),
('Poisson', 'kg', 20, 5, 3000, 'Marché maritime'),
('Bœuf', 'kg', 15, 5, 3500, 'Boucherie Centrale'),
('Agneau', 'kg', 8, 3, 5000, 'Boucherie Premium'),
('Tomates', 'kg', 25, 5, 500, 'Marché central'),
('Oignons', 'kg', 15, 5, 400, 'Marché central'),
('Avocats', 'pièce', 30, 10, 300, 'Fruitier Local'),
('Citron', 'pièce', 40, 10, 100, 'Fruitier Local'),
('Huile d''arachide', 'L', 10, 2, 2000, 'Fournisseur Huiles'),
('Sel', 'kg', 5, 1, 500, 'Fournisseur Général'),
('Poivre', 'kg', 1, 0.5, 3000, 'Épicerie Fine'),
('Bissap séché', 'kg', 5, 1, 1500, 'Marché Adjamé'),
('Gingembre', 'kg', 3, 1, 1000, 'Marché Adjamé'),
('Sucre', 'kg', 10, 2, 600, 'Fournisseur Général'),
('Huile végétale', 'L', 15, 3, 1200, 'Fournisseur Huiles');

-- Tables
INSERT INTO tables_restaurant (number, name, capacity, status, pos_x, pos_y, shape, zone) VALUES
(1, NULL, 2, 'free', 50, 50, 'round', 'salle'),
(2, NULL, 2, 'free', 150, 50, 'round', 'salle'),
(3, NULL, 4, 'free', 50, 150, 'square', 'salle'),
(4, NULL, 4, 'free', 150, 150, 'square', 'salle'),
(5, 'Famille', 6, 'free', 250, 50, 'rectangle', 'salle'),
(6, 'VIP', 8, 'free', 250, 150, 'rectangle', 'salle'),
(7, NULL, 4, 'free', 50, 250, 'square', 'terrasse'),
(8, NULL, 4, 'free', 150, 250, 'square', 'terrasse'),
(9, NULL, 2, 'free', 250, 250, 'round', 'bar'),
(10, NULL, 2, 'free', 350, 50, 'round', 'bar');

-- Settings
INSERT INTO settings (setting_key, setting_value, setting_type) VALUES
('restaurant_name', 'Restaurant ADAM', 'string'),
('restaurant_phone', '+225 01 02 03 04', 'string'),
('restaurant_email', 'contact@adam.com', 'string'),
('restaurant_address', 'Boulevard de la République, Abidjan, Côte d''Ivoire', 'string'),
('tax_rate', '18', 'float'),
('currency', 'FCFA', 'string'),
('opening_time', '08:00', 'string'),
('closing_time', '23:00', 'string'),
('reservation_duration', '120', 'int'),
('max_guests_per_table', '10', 'int'),
('loyalty_enabled', '1', 'bool'),
('loyalty_points_per_fcfa', '1', 'int'),
('cinetpay_enabled', '0', 'bool');
