# Restaurant ADAM - Systeme de Gestion

## Installation

1. Uploadez tous les fichiers via FTP dans le dossier `htdocs/`
2. Accédez à `votredomaine.com/install.php`
3. Entrez vos identifiants MySQL InfinityFree
4. Cliquez sur "Installer"
5. **Supprimez install.php après l'installation**
6. Connectez-vous: `admin@adam.com` / `admin123`

## Acces

- **Administration**: `/admin`
- **Client public**: `/`

## Roles

| Role | Acces |
|------|-------|
| Admin | Tout |
| Manager | Sauf paramètres |
| Serveur | Commandes, tables, réservations, caisse |
| Cuisinier | Commandes (cuisine) |

## Modules

1. **Dashboard** - Vue d'ensemble avec KPIs
2. **Menu** - Gestion des plats et catégories
3. **Stock** - Ingrédients et inventaire
4. **POS** - Point de vente tactile
5. **Commandes** - Suivi des commandes
6. **Cuisine** - Affichage cuisine
7. **Plan de salle** - Gestion des tables
8. **Réservations** - Calendrier et gestion
9. **Caisse** - Encaissements et rapports
10. **Personnel** - Planning et performance
11. **Fidélité** - Cartes et points
12. **Rapports** - Ventes et analytics
13. **Paramètres** - Configuration

## Notes Techniques

- PHP 8.3 custom MVC (aucune dépendance externe)
- MySQL (schéma optimisé < 200 KB)
- CSS vanilla responsive (desktop + tablette + mobile)
- JavaScript vanilla (POS interactif)
- Paiement: CinetPay (Mobile Money) + Espèces
- Email: API Brevo (gratuit 300/jour)
