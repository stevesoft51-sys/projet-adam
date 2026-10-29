# Restaurant ADAM — Point de Vente & Gestion (desktop, offline)

Application de caisse et de gestion pour le Restaurant Adam.
100 % locale et offline : Python + Tkinter, données stockées dans des
fichiers JSON (dossier `data/`). Aucun serveur, aucune connexion requise.

## Lancement

```bash
./lancer.sh
```

ou directement :

```bash
python3 main.py
```

Prérequis : Python 3.10+ avec tkinter (inclus avec Python sous Windows ;
`sudo apt install python3-tk` si absent sous Linux).

## Comptes

| Identifiant | Mot de passe | Rôle |
|---|---|---|
| `admin` | `admin123` | Administrateur (accès complet) |
| `caisse` | `caisse123` | Caissière (Point de vente + Caisse) |

Les comptes se gèrent dans l'onglet **Personnel** (admin) : création,
modification, blocage/réactivation, réinitialisation de mot de passe.

## Modules

- **Tableau de bord** *(admin)* — chiffre d'affaires, tickets, panier moyen,
  entrées/sorties de caisse, graphique du CA par jour/semaine/mois/année,
  top produits, répartition par mode de paiement, mouvements de stock récents,
  alertes stock bas.
- **Point de vente** — grille produits filtrable par catégorie et recherche,
  commande en cours (quantités, remise), **génération de l'addition**
  (seule ou avec impression dans `data/additions/`), section des commandes
  non réglées avec bouton **Régler** : fenêtre de règlement (montant perçu,
  calcul automatique du *remboursement = perçu − addition*), historique des
  commandes *(admin)*. Encaissement direct possible (espèces / mobile
  money / carte), monnaie calculée, ticket imprimable en fichier
  (`data/tickets/`).
- **Caisse** — ouverture avec fond de caisse, journal des mouvements
  (ventes espèces, entrées/sorties manuelles), fermeture avec écart calculé,
  historique des sessions.
- **Menu** *(admin)* — catégories (ajouter/renommer/on-off) et produits
  (créer/modifier/disponibilité/supprimer).
- **Stocks** *(admin)* — ingrédients avec seuils d'alerte et valorisation,
  mouvements (entrée / sortie / ajustement), recettes : associer des
  quantités d'ingrédients à un plat pour déduction automatique du stock
  à chaque vente.
- **Personnel** *(admin)* — comptes du personnel : ajouter/modifier/supprimer
  un employé, rôles (administrateur / caissière), bloquer ou réactiver un
  accès, réinitialiser les mots de passe. Un compte bloqué ne peut plus se
  connecter ; protections : impossible de bloquer/supprimer son propre
  compte ou le dernier administrateur.

## Données

Tout est conservé dans `data/*.json` :

`users`, `categories`, `products`, `ingredients`, `recipes`, `orders`,
`stock_movements`, `cash_sessions`, `sales`, `settings`.

Sauvegarde = copier le dossier `data/`. Tickets clients : `data/tickets/`.

Pour repartir de zéro : fermer l'app puis supprimer le dossier `data/`.

## Tests

```bash
python3 test_logic.py     # logique métier (54 vérifications)
python3 main.py --smoke   # ouvre l'interface, parcourt les onglets, referme
```
