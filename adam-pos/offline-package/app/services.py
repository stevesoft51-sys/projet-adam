"""Logique metier : utilisateurs, catalogue, stock, caisse, ventes, rapports."""
import re
from datetime import datetime, timedelta

from .security import hash_password, verify_password
from .storage import Storage

PAYMENT_METHODS = {
    "cash": "Espèces",
    "mobile_money": "Mobile Money",
    "mixed": "Paiement mixte",
}
MOVEMENT_TYPES = {"in": "Entrée", "out": "Sortie", "adjust": "Ajustement"}
TABLE_STATUSES = {"free": "Libre", "occupied": "Occupée",
                  "reserved": "Réservée"}


class BizError(Exception):
    """Erreur metier a afficher a l'utilisateur."""


# ------------------------------------------------------------------ ROLES ------
# Modules (onglets) auxquels un role peut donner acces.
MODULES = {
    "dashboard": "Tableau de bord",
    "pos": "Point de vente",
    "cash": "Caisse",
    "floor": "Plan de salle",
    "menu": "Menu & produits",
    "stock": "Stocks",
    "suppliers": "Fournisseurs",
    "staff": "Personnel & salaires",
}

# Rôles de base (non supprimables) : l'admin a tout, la caissiere a le strict
# minimum du front d'accueil.
BUILTIN_ROLES = {
    "admin": {"name": "Administrateur", "modules": list(MODULES.keys())},
    "caissiere": {"name": "Caissière", "modules": ["pos", "cash", "floor"]},
}

# Rôles par defaut ajoutés lors de l'initialisation des données.
DEFAULT_ROLES = {
    "cuisine": {"name": "Cuisine", "modules": ["menu", "stock"]},
}


class RoleService:
    """Rôles dynamiques du personnel.

    Chaque role a une cle unique, un nom et une liste de modules accessibles.
    Les roles "admin" et "caissiere" sont fournis par defaut et ne peuvent
    pas etre supprimes. L'admin peut creer des roles supplementaires
    (ex: "cuisine") et choisir leurs permissions.
    """

    def __init__(self, storage: Storage):
        self.s = storage

    def roles(self) -> list:
        """Liste des roles : builtins + roles créés (ordonne : admin, puis nom)."""
        stored = self.s.load("roles", None)
        if stored is None:
            return self._seeded()
        return self._merge(stored)

    def _seeded(self) -> list:
        roles = [{"key": k, "name": v["name"], "modules": list(v["modules"])}
                 for k, v in BUILTIN_ROLES.items()]
        for k, v in DEFAULT_ROLES.items():
            roles.append({"key": k, "name": v["name"],
                          "modules": list(v["modules"])})
        return sorted(roles, key=lambda r: (r["key"] != "admin", r["name"].lower()))

    def _merge(self, stored: list) -> list:
        by_key = {r["key"]: r for r in stored}
        for k, v in BUILTIN_ROLES.items():
            if k not in by_key:
                by_key[k] = {"key": k, "name": v["name"],
                             "modules": list(v["modules"])}
            else:
                by_key[k]["modules"] = [
                    m for m in v["modules"] if m not in by_key[k].get("builtin_removed", [])] \
                    or list(v["modules"])
        return sorted(by_key.values(),
                      key=lambda r: (r["key"] != "admin", r["name"].lower()))

    def save(self, roles: list):
        self.s.save("roles", roles)

    def role_by_key(self, key: str) -> dict | None:
        return next((r for r in self.roles() if r["key"] == key), None)

    def label(self, key: str) -> str:
        r = self.role_by_key(key)
        return r["name"] if r else key

    def modules_for(self, key: str) -> list:
        r = self.role_by_key(key)
        return list(r["modules"]) if r else []

    def save_role(self, key: str, name: str, modules: list):
        key = (key or "").strip().lower().replace(" ", "_")
        if not re.match(r"^[a-z0-9_]+$", key):
            raise BizError("Clé de rôle invalide (lettres, chiffres, tirets bas).")
        name = (name or "").strip()
        if not name:
            raise BizError("Le nom du rôle est obligatoire.")
        if key in BUILTIN_ROLES:
            raise BizError("Ce rôle est fourni par défaut et ne peut être modifié.")
        unknown = [m for m in modules if m not in MODULES]
        valid = [m for m in MODULES if m in modules]
        roles = self.roles()
        existing = next((r for r in roles if r["key"] == key), None)
        if existing:
            existing["name"] = name
            existing["modules"] = valid
        else:
            roles.append({"key": key, "name": name, "modules": valid})
        self.save(roles)
        return key

    def delete_role(self, key: str):
        if key in BUILTIN_ROLES:
            raise BizError("Ce rôle par défaut ne peut pas être supprimé.")
        for u in self.s.load("users", []):
            if u["role"] == key:
                raise BizError("Ce rôle est utilisé par du personnel et "
                               "ne peut pas être supprimé.")
        roles = self.roles()
        self.save([r for r in roles if r["key"] != key])

    def valid_keys(self) -> list:
        return [r["key"] for r in self.roles()]


# ----------------------------------------------------------------- AUTH ------
class AuthService:
    def __init__(self, storage: Storage):
        self.s = storage

    def users(self):
        return self.s.load("users", [])

    def save_users(self, users):
        self.s.save("users", users)

    def login(self, username: str, password: str):
        username = (username or "").strip().lower()
        for u in self.users():
            if u["username"].lower() == username:
                if not u.get("active", True):
                    raise BizError("Ce compte est bloqué.\n"
                                   "Contactez l'administrateur du restaurant.")
                if verify_password(password, u["password_hash"]):
                    return {k: u.get(k, "fr" if k == "lang" else None) for k in
                            ("id", "name", "username", "role", "lang")}
        return None

    def change_password(self, user_id: int, old: str, new: str):
        if len(new) < 6:
            raise BizError("Le nouveau mot de passe doit contenir au moins 6 caractères.")
        users = self.users()
        for u in users:
            if u["id"] == user_id:
                if not verify_password(old, u["password_hash"]):
                    raise BizError("Mot de passe actuel incorrect.")
                u["password_hash"] = hash_password(new)
                self.save_users(users)
                return
        raise BizError("Utilisateur introuvable.")

    def set_lang(self, user_id: int, lang: str):
        """Enregistre la langue preferee de l'utilisateur."""
        lang = lang if lang in ("fr", "en", "ar") else "fr"
        users = self.users()
        for u in users:
            if u["id"] == user_id:
                u["lang"] = lang
                self.save_users(users)
                return
        raise BizError("Utilisateur introuvable.")

    # -- gestion du personnel (admin) ----------------------------------------
    @staticmethod
    def _check_username(username: str):
        username = (username or "").strip()
        if len(username) < 3:
            raise BizError("L'identifiant doit contenir au moins 3 caractères.")
        if not all(c.isalnum() or c in "._-" for c in username):
            raise BizError("L'identifiant ne peut contenir que des lettres, "
                           "chiffres, points, tirets et underscores.")
        return username.lower()

    @staticmethod
    def _check_password(password: str):
        password = password or ""
        if len(password) < 4:
            raise BizError("Le mot de passe doit contenir au moins 4 caractères.")
        return password

    def _unique_username(self, username: str, exclude_id=None):
        for u in self.users():
            if u["username"].lower() == username and u["id"] != exclude_id:
                raise BizError("Cet identifiant est déjà utilisé.")

    def staff(self):
        """Liste du personnel triee : admins d'abord, puis par nom."""
        return sorted(self.users(),
                      key=lambda u: (u["role"] != "admin", u["name"].lower()))

    def user_by_id(self, user_id: int):
        return next((u for u in self.users() if u["id"] == user_id), None)

    def user_by_username(self, username: str):
        username = (username or "").strip().lower()
        return next((u for u in self.users()
                     if u["username"].lower() == username), None)

    def add_staff(self, name: str, username: str, password: str, role: str,
                  roles: RoleService = None):
        name = (name or "").strip()
        if not name:
            raise BizError("Le nom complet est obligatoire.")
        if roles and role not in roles.valid_keys():
            raise BizError("Rôle invalide.")
        username = self._check_username(username)
        self._unique_username(username)
        password = self._check_password(password)
        users = self.users()
        u = {"id": Storage.next_id(users), "name": name,
             "username": username, "role": role,
             "active": True, "salary": 0.0, "lang": "fr",
             "password_hash": hash_password(password)}
        users.append(u)
        self.save_users(users)
        return {k: u[k] for k in ("id", "name", "username", "role")}

    def update_staff(self, user_id: int, name: str, username: str, role: str,
                     salary: float = None, roles: RoleService = None):
        name = (name or "").strip()
        if not name:
            raise BizError("Le nom complet est obligatoire.")
        if roles and role not in roles.valid_keys():
            raise BizError("Rôle invalide.")
        username = self._check_username(username)
        self._unique_username(username, exclude_id=user_id)
        users = self.users()
        target = next((u for u in users if u["id"] == user_id), None)
        if not target:
            raise BizError("Employé introuvable.")
        if target["role"] == "admin" and role != "admin" \
                and self._active_admin_count(exclude_id=user_id) == 0:
            raise BizError("Impossible de retirer le rôle du dernier administrateur.")
        target.update({"name": name, "username": username.lower(), "role": role})
        if salary is not None:
            target["salary"] = round(max(0.0, float(salary)), 2)
        self.save_users(users)

    def set_salary(self, user_id: int, salary: float):
        users = self.users()
        target = next((u for u in users if u["id"] == user_id), None)
        if not target:
            raise BizError("Employé introuvable.")
        target["salary"] = round(max(0.0, float(salary)), 2)
        self.save_users(users)

    def set_staff_active(self, user_id: int, active: bool, by_user: dict):
        if user_id == by_user["id"]:
            raise BizError("Vous ne pouvez pas bloquer votre propre compte.")
        users = self.users()
        target = next((u for u in users if u["id"] == user_id), None)
        if not target:
            raise BizError("Employé introuvable.")
        if not active and target["role"] == "admin" \
                and self._active_admin_count() <= 1:
            raise BizError("Impossible de bloquer le dernier administrateur actif.")
        target["active"] = bool(active)
        self.save_users(users)

    def reset_staff_password(self, user_id: int, new_password: str):
        new_password = self._check_password(new_password)
        users = self.users()
        target = next((u for u in users if u["id"] == user_id), None)
        if not target:
            raise BizError("Employé introuvable.")
        target["password_hash"] = hash_password(new_password)
        self.save_users(users)

    def delete_staff(self, user_id: int, by_user: dict):
        if user_id == by_user["id"]:
            raise BizError("Vous ne pouvez pas supprimer votre propre compte.")
        users = self.users()
        target = next((u for u in users if u["id"] == user_id), None)
        if not target:
            raise BizError("Employé introuvable.")
        if target["role"] == "admin" and self._active_admin_count() <= 1:
            raise BizError("Impossible de supprimer le dernier administrateur.")
        users.remove(target)
        self.save_users(users)

    def _active_admin_count(self, exclude_id=None) -> int:
        return sum(1 for u in self.users()
                   if u["role"] == "admin" and u.get("active", True)
                   and u["id"] != exclude_id)


# ------------------------------------------------------------- CATALOGUE -----
class CatalogService:
    def __init__(self, storage: Storage):
        self.s = storage

    # categories ---------------------------------------------------------
    def categories(self, active_only=False):
        cats = sorted(self.s.load("categories", []), key=lambda c: c.get("sort_order", 0))
        return [c for c in cats if c.get("active", True)] if active_only else cats

    def add_category(self, name: str):
        name = name.strip()
        if not name:
            raise BizError("Le nom de la catégorie est obligatoire.")
        if any(c["name"].lower() == name.lower() for c in self.categories()):
            raise BizError("Cette catégorie existe déjà.")
        cats = self.s.load("categories", [])
        cat = {"id": Storage.next_id(cats), "name": name,
               "sort_order": len(cats) + 1, "active": True}
        cats.append(cat)
        self.s.save("categories", cats)
        return cat

    def rename_category(self, cat_id: int, new_name: str):
        new_name = new_name.strip()
        if not new_name:
            raise BizError("Le nom de la catégorie est obligatoire.")
        cats = self.s.load("categories", [])
        for c in cats:
            if c["id"] == cat_id:
                c["name"] = new_name
                self.s.save("categories", cats)
                return
        raise BizError("Catégorie introuvable.")

    def toggle_category(self, cat_id: int):
        cats = self.s.load("categories", [])
        for c in cats:
            if c["id"] == cat_id:
                c["active"] = not c.get("active", True)
                self.s.save("categories", cats)
                return c
        raise BizError("Catégorie introuvable.")

    # produits -------------------------------------------------------------
    def products(self, available_only=False, category_id=None):
        prods = self.s.load("products", [])
        if available_only:
            prods = [p for p in prods if p.get("available", True)]
        if category_id is not None:
            prods = [p for p in prods if p["category_id"] == category_id]
        return sorted(prods, key=lambda p: (p["name"].lower()))

    def product_by_id(self, pid: int):
        for p in self.products():
            if p["id"] == pid:
                return p
        return None

    # images produits ------------------------------------------------------
    ALLOWED_IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

    def save_image(self, src_path: str) -> str:
        """Enregistre le chemin complet de l'image source et le renvoie."""
        import os
        src = str(src_path)
        if not os.path.isfile(src):
            raise BizError("Fichier image introuvable.")
        ext = os.path.splitext(src)[1].lower()
        if ext not in self.ALLOWED_IMG_EXT:
            raise BizError("Format d'image non supporté "
                           "(png, jpg, gif, bmp, webp).")
        return os.path.abspath(src)

    def image_path(self, filename):
        """Chemin complet d'une image, ou None si absente.

        Accepte un chemin absolu (nouveau) ou un nom relatif (ancien format).
        """
        import os
        if not filename:
            return None
        p = str(filename)
        if os.path.isabs(p):
            return p if os.path.isfile(p) else None
        full = os.path.join(self.s.images_dir, p)
        return full if os.path.isfile(full) else None

    def save_product(self, data: dict, prod_id=None):
        name = (data.get("name") or "").strip()
        price = float(data.get("price") or 0)
        if not name:
            raise BizError("Le nom du produit est obligatoire.")
        if price <= 0:
            raise BizError("Le prix doit être supérieur à 0.")
        prods = self.s.load("products", [])
        dup = [p for p in prods if p["name"].lower() == name.lower() and p["id"] != prod_id]
        if dup:
            raise BizError("Un produit porte déjà ce nom.")
        if prod_id is None:
            p = {"id": Storage.next_id(prods), "description": "", **data,
                 "name": name, "price": price}
            prods.append(p)
        else:
            p = next((x for x in prods if x["id"] == prod_id), None)
            if not p:
                raise BizError("Produit introuvable.")
            p.update(data)
            p["name"], p["price"] = name, price
        self.s.save("products", prods)
        return p

    def delete_product(self, pid: int):
        prods = self.s.load("products", [])
        prods = [p for p in prods if p["id"] != pid]
        self.s.save("products", prods)


# ------------------------------------------------------------------ STOCK ----
class StockService:
    def __init__(self, storage: Storage):
        self.s = storage

    def ingredients(self):
        return sorted(self.s.load("ingredients", []), key=lambda i: i["name"].lower())

    def ingredient_by_id(self, iid: int):
        return next((i for i in self.ingredients() if i["id"] == iid), None)

    def save_ingredient(self, data: dict, ing_id=None):
        name = (data.get("name") or "").strip()
        if not name:
            raise BizError("Le nom de l'ingrédient est obligatoire.")
        ing_list = self.s.load("ingredients", [])
        dup = [i for i in ing_list if i["name"].lower() == name.lower() and i["id"] != ing_id]
        if dup:
            raise BizError("Un ingrédient porte déjà ce nom.")
        if ing_id is None:
            ing = {"id": Storage.next_id(ing_list), "current_stock": 0.0, **data, "name": name}
            ing_list.append(ing)
            self.s.save("ingredients", ing_list)
            if float(ing.get("current_stock", 0)) > 0:
                self.add_movement(ing["id"], "in", float(ing["current_stock"]),
                                  "Stock initial", "système")
            return ing
        ing = next((x for x in ing_list if x["id"] == ing_id), None)
        if not ing:
            raise BizError("Ingrédient introuvable.")
        ing.update(data)
        ing["name"] = name
        self.s.save("ingredients", ing_list)
        return ing

    def delete_ingredient(self, iid: int):
        lst = self.s.load("ingredients", [])
        self.s.save("ingredients", [i for i in lst if i["id"] != iid])
        rec = self.s.load("recipes", [])
        self.s.save("recipes", [r for r in rec if r["ingredient_id"] != iid])

    def movements(self, limit=None):
        mv = sorted(self.s.load("stock_movements", []),
                    key=lambda m: (m["at"], m.get("id", 0)), reverse=True)
        return mv[:limit] if limit else mv

    def add_movement(self, ingredient_id: int, mtype: str, qty: float,
                     reason: str, by: str):
        """mtype: in / out / adjust. qty toujours positif sauf adjust signe."""
        if mtype not in MOVEMENT_TYPES:
            raise BizError("Type de mouvement invalide.")
        qty = float(qty)
        if qty == 0:
            raise BizError("La quantité ne peut pas être nulle.")
        if mtype in ("in", "out") and qty < 0:
            raise BizError("La quantité doit être positive.")
        reason = (reason or "").strip()
        if not reason:
            raise BizError("Le motif est obligatoire.")

        ing_list = self.s.load("ingredients", [])
        ing = next((i for i in ing_list if i["id"] == ingredient_id), None)
        if not ing:
            raise BizError("Ingrédient introuvable.")

        before = float(ing.get("current_stock", 0))
        after = before + qty if mtype == "in" else \
            before - qty if mtype == "out" else before + qty
        if mtype == "adjust":
            after = before + qty  # ajustement signe
        if after < 0:
            raise BizError(
                f"Stock insuffisant : disponible {before:g} {ing.get('unit','')}.")
        ing["current_stock"] = round(after, 3)
        self.s.save("ingredients", ing_list)

        mv = self.s.load("stock_movements", [])
        mv.append({
            "id": Storage.next_id(mv),
            "at": Storage.now(),
            "ingredient_id": ing["id"],
            "ingredient_name": ing["name"],
            "unit": ing.get("unit", ""),
            "type": mtype,
            "qty": round(qty, 3),
            "before": round(before, 3),
            "after": round(after, 3),
            "reason": reason,
            "by": by,
        })
        self.s.save("stock_movements", mv)

    # recettes (lien produit -> ingredients) --------------------------------
    def recipes(self):
        return self.s.load("recipes", [])

    def set_recipe(self, product_id: int, lines: list):
        """lines: [{ingredient_id, qty}]"""
        rec = [r for r in self.recipes() if r["product_id"] != product_id]
        for l in lines:
            q = float(l.get("qty") or 0)
            if q > 0 and self.ingredient_by_id(int(l["ingredient_id"])):
                rec.append({"product_id": product_id,
                            "ingredient_id": int(l["ingredient_id"]), "qty": q})
        self.s.save("recipes", rec)

    def recipe_for(self, product_id: int):
        return [r for r in self.recipes() if r["product_id"] == product_id]

    def requirements_for(self, cart: list) -> list:
        """Besoins totaux du panier : [{ing, qty}] aggreges par ingredient.
        cart : [{'product': {...}, 'qty': n}]"""
        needs = {}
        for line in cart:
            for r in self.recipe_for(line["product"]["id"]):
                ing = self.ingredient_by_id(r["ingredient_id"])
                if not ing:
                    continue
                slot = needs.setdefault(ing["id"], {"ing": ing, "qty": 0.0})
                slot["qty"] += float(r["qty"]) * float(line["qty"])
        return list(needs.values())

    def check_availability(self, cart: list):
        """Refuse la vente/commande si le stock ne couvre pas la recette."""
        short = []
        for item in self.requirements_for(cart):
            ing = item["ing"]
            avail = float(ing.get("current_stock", 0))
            if item["qty"] > avail:
                short.append(
                    f"• {ing['name']} : il faut {item['qty']:g} "
                    f"{ing.get('unit', '')}, disponible {avail:g} "
                    f"{ing.get('unit', '')}")
        if short:
            raise BizError("Stock insuffisant — vente impossible :\n"
                           + "\n".join(short))

    def deduct_for_sale(self, product_id: int, quantity: float,
                        sale_number: str):
        """Consomme automatiquement les ingredients selon la recette.
        L'appelant a deja valide la disponibilite via check_availability."""
        for line in self.recipe_for(product_id):
            need = float(line["qty"]) * quantity
            ing = self.ingredient_by_id(line["ingredient_id"])
            if not ing:
                continue
            avail = float(ing.get("current_stock", 0))
            if need > avail:
                # securite : on ne descend jamais sous zero, l'ecart reste visible
                need = avail
            if need <= 0:
                continue
            self.add_movement(line["ingredient_id"], "out", need,
                              f"Vente {sale_number}", "vente auto")

    def low_stock(self):
        return [i for i in self.ingredients()
                if float(i.get("current_stock", 0)) <= float(i.get("min_stock", 0))]


# ------------------------------------------------------------------ CAISSE ---
class CashService:
    def __init__(self, storage: Storage):
        self.s = storage

    def sessions(self):
        return sorted(self.s.load("cash_sessions", []),
                      key=lambda x: x["opened_at"], reverse=True)

    def get_open(self):
        return next((c for c in self.sessions() if c["status"] == "open"), None)

    def open_session(self, opening_amount: float, user: dict, notes=""):
        if self.get_open():
            raise BizError("Une caisse est déjà ouverte. Fermez-la d'abord.")
        amount = float(opening_amount)
        if amount < 0:
            raise BizError("Le fond de caisse ne peut pas être négatif.")
        sessions = self.s.load("cash_sessions", [])
        sess = {
            "id": Storage.next_id(sessions),
            "opened_at": Storage.now(),
            "closed_at": None,
            "opening_amount": amount,
            "total_cash_in": 0.0,
            "total_cash_out": 0.0,
            "closing_counted": None,
            "expected": None,
            "difference": None,
            "status": "open",
            "opened_by": user["name"],
            "closed_by": None,
            "notes": notes,
            "movements": [],
        }
        sessions.append(sess)
        self.s.save("cash_sessions", sessions)
        return sess

    def _update_open(self, mutator):
        sessions = self.s.load("cash_sessions", [])
        for c in sessions:
            if c["status"] == "open":
                mutator(c)
                self.s.save("cash_sessions", sessions)
                return c
        raise BizError("Aucune caisse ouverte.")

    def add_movement(self, mtype: str, amount: float, reason: str, user: dict):
        if mtype not in ("in", "out"):
            raise BizError("Type de mouvement invalide.")
        amount = float(amount)
        if amount <= 0:
            raise BizError("Le montant doit être positif.")
        reason = (reason or "").strip()
        if not reason:
            raise BizError("Le motif est obligatoire.")

        def mut(c):
            mid = Storage.next_id(c["movements"])
            c["movements"].append({"id": mid, "at": Storage.now(), "type": mtype,
                                   "amount": amount, "reason": reason, "by": user["name"]})
            key = "total_cash_in" if mtype == "in" else "total_cash_out"
            c[key] = round(float(c[key]) + amount, 2)

        return self._update_open(mut)

    def register_cash_sale(self, amount: float, sale_number: str):
        def mut(c):
            c["movements"].append({"id": Storage.next_id(c["movements"]),
                                   "at": Storage.now(), "type": "sale",
                                   "amount": float(amount), "reason": f"Vente {sale_number}",
                                   "by": "caisse"})
            c["total_cash_in"] = round(float(c["total_cash_in"]) + float(amount), 2)

        return self._update_open(mut)

    def expected_amount(self, session: dict) -> float:
        return round(float(session["opening_amount"])
                     + float(session["total_cash_in"])
                     - float(session["total_cash_out"]), 2)

    def auto_close_on_logout(self, user: dict):
        """Fermeture automatique de la caisse ouverte a la deconnexion.

        Le montant compte est fixe au montant attendu (ecart = 0) et une
        note signale la fermeture automatique.  Retourne la session fermee
        ou None si aucune caisse ouverte."""
        sess = self.get_open()
        if not sess:
            return None
        expected = self.expected_amount(sess)
        return self.close_session(
            expected, user,
            notes="Fermeture automatique lors de la déconnexion.")

    def close_session(self, counted: float, user: dict, notes=""):
        sessions = self.s.load("cash_sessions", [])
        for c in sessions:
            if c["status"] == "open":
                counted = float(counted)
                if counted < 0:
                    raise BizError("Le montant compté ne peut pas être négatif.")
                c["expected"] = self.expected_amount(c)
                c["difference"] = round(counted - c["expected"], 2)
                c["closing_counted"] = counted
                c["status"] = "closed"
                c["closed_at"] = Storage.now()
                c["closed_by"] = user["name"]
                if notes:
                    c["notes"] = ((c.get("notes") or "") + "\n" + notes).strip()
                self.s.save("cash_sessions", sessions)
                return c
        raise BizError("Aucune caisse ouverte.")


# ------------------------------------------------------------------ VENTES ---
class SalesService:
    def __init__(self, storage: Storage, cash: CashService, stock: StockService):
        self.s = storage
        self.cash = cash
        self.stock = stock

    def sales(self):
        return sorted(self.s.load("sales", []), key=lambda x: x["datetime"], reverse=True)

    def _next_number(self, sales):
        today = datetime.now().strftime("%Y%m%d")
        todays = [x for x in sales if x["number"].startswith(f"T{today}")]
        seq = len(todays) + 1
        return f"T{today}-{seq:04d}"

    def create_sale(self, cart: list, method: str, discount: float,
                    user: dict, received: float | None = None,
                    service_mode: str | None = None,
                    unit_name: str | None = None,
                    mixed_cash=None, mixed_mobile=None):
        """cart: [{'product': {...}, 'qty': int}]
        service_mode : 'dine_in' (sur place) ou 'takeaway' (a emporter).
        method 'mixed' : mixed_cash + mixed_mobile doivent couvrir le total."""
        if method not in PAYMENT_METHODS:
            raise BizError("Mode de paiement invalide.")
        if method == "cash" and not self.cash.get_open():
            raise BizError("Aucune caisse ouverte : impossible d'encaisser en espèces.\n"
                           "Ouvrez la caisse dans l'onglet Caisse.")
        if not cart:
            raise BizError("Le panier est vide.")
        discount = max(0.0, float(discount or 0))

        subtotal = sum(p["product"]["price"] * q for p, q in
                       [(l, l["qty"]) for l in cart])
        total = round(subtotal - discount, 2)
        if total < 0:
            raise BizError("La remise dépasse le total.")
        if received is not None and float(received) < total:
            raise BizError(f"Montant reçu insuffisant ({received:g} < {total:g} FCFA).")
        # paiement mixte : une partie especes + une partie mobile money
        if method == "mixed":
            if not self.cash.get_open():
                raise BizError("Aucune caisse ouverte : la part espèces du "
                               "paiement mixte ne peut pas être enregistrée.\n"
                               "Ouvrez la caisse dans l'onglet Caisse.")
            try:
                mc = round(float(mixed_cash or 0), 2)
                mm = round(float(mixed_mobile or 0), 2)
            except (TypeError, ValueError):
                raise BizError("Répartition mixte invalide : saisissez les "
                               "deux montants.")
            if mc < 0 or mm < 0:
                raise BizError("Les parts espèces et mobile money doivent "
                               "être positives.")
            if round(mc + mm, 2) != total:
                raise BizError(f"La répartition mixte ({mc:g} + {mm:g} = "
                               f"{round(mc + mm, 2):g}) doit couvrir "
                               f"exactement le total ({total:g} FCFA).")
            mixed_cash, mixed_mobile = mc, mm

        # le stock doit couvrir les recettes du panier
        self.stock.check_availability(cart)

        sales = self.s.load("sales", [])
        number = self._next_number(sales)
        sale = {
            "id": Storage.next_id(sales),
            "number": number,
            "datetime": Storage.now(),
            "items": [{"product_id": l["product"]["id"],
                       "name": l["product"]["name"],
                       "qty": l["qty"],
                       "price": l["product"]["price"],
                       "total": round(l["product"]["price"] * l["qty"], 2)}
                      for l in cart],
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "total": total,
            "method": method,
            "status": "paid",
            "cashier_id": user["id"],
            "cashier": user["name"],
            "service_mode": service_mode,
            "unit_name": unit_name,
        }
        if method == "cash" and received is not None:
            sale["received"] = round(float(received), 2)
            sale["change"] = round(float(received) - total, 2)
        if method == "mixed":
            sale["cash_part"] = mixed_cash
            sale["mobile_part"] = mixed_mobile
        sales.append(sale)
        self.s.save("sales", sales)

        # consommation automatique des ingrédients (recettes)
        for line in cart:
            self.stock.deduct_for_sale(line["product"]["id"], line["qty"], number)
        # entrée d'argent en caisse : total en espèces, part espèces si mixte
        if method == "cash":
            self.cash.register_cash_sale(total, number)
        elif method == "mixed":
            self.cash.register_cash_sale(mixed_cash, number)
        return sale

    def ticket_text(self, sale: dict, settings: dict):
        w = 40
        lines = []
        center = lambda t: t.center(w).rstrip()  # noqa: E731
        lines.append("=" * w)
        lines.append(center((settings.get("restaurant_name") or "Restaurant ADAM").upper()))
        addr = settings.get("address") or ""
        if addr:
            lines.append(center(addr))
        tel = settings.get("phone") or ""
        if tel:
            lines.append(center("Tél : " + tel))
        lines.append("=" * w)
        lines.append(center(f"TICKET {sale['number']}"))
        lines.append(sale["datetime"])
        lines.append("-" * w)
        for it in sale["items"]:
            left = f"{it['qty']:>2} x {it['name'][:20]:<20}"
            right = f"{it['total']:>12,.0f}".replace(",", " ")
            lines.append(left + right)
        lines.append("-" * w)
        lines.append(f"{'Sous-total':<26}{sale['subtotal']:>14,.0f}".replace(",", " "))
        if sale.get("discount"):
            lines.append(f"{'Remise':<26}- {sale['discount']:>12,.0f}".replace(",", " "))
        lines.append(f"{'TOTAL':<26}{sale['total']:>14,.0f}".replace(",", " "))
        lines.append(f"{'Paiement':<26}{PAYMENT_METHODS[sale['method']]:>14}")
        if sale.get("cash_part") is not None:
            lines.append(f"{'  Part especes':<26}{sale['cash_part']:>14,.0f}".replace(",", " "))
            lines.append(f"{'  Part Mobile':<26}{sale['mobile_part']:>14,.0f}".replace(",", " "))
        if sale.get("received") is not None:
            lines.append(f"{'Reçu':<26}{sale['received']:>14,.0f}".replace(",", " "))
            lines.append(f"{'Monnaie rendue':<26}{sale['change']:>14,.0f}".replace(",", " "))
        lines.append("=" * w)
        lines.append(center(settings.get("ticket_footer") or "Merci de votre visite !"))
        return "\n".join(lines)

    def save_ticket_file(self, sale: dict, settings: dict) -> str:
        text = self.ticket_text(sale, settings)
        path = os_path_join(self.s.tickets_dir, f"{sale['number']}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path


# ------------------------------------------------------------- COMMANDES -----
class OrderService:
    """Commandes generees avant paiement : addition non reglee -> reglement."""

    def __init__(self, storage: Storage, sales: SalesService,
                 floor=None):
        self.s = storage
        self.sales = sales
        self.floor = floor

    def orders(self):
        return sorted(self.s.load("orders", []),
                      key=lambda o: o["datetime"], reverse=True)

    def open_orders(self):
        return [o for o in self.orders() if o["status"] == "open"]

    def closed_orders(self, limit=None):
        lst = [o for o in self.orders() if o["status"] != "open"]
        return lst[:limit] if limit else lst

    def _next_number(self, orders):
        today = datetime.now().strftime("%Y%m%d")
        todays = [o for o in orders if o["number"].startswith(f"C{today}")]
        return f"C{today}-{len(todays) + 1:04d}"

    def create_order(self, cart: list, discount: float, user: dict,
                     unit_id=None, mode: str | None = None):
        """Enregistre la commande d'un client et genere son addition.
        mode : 'dine_in' -> unit_id requis (table/boucaro occupee) ;
               'takeaway' -> a emporter, pas de table ;
               None -> compatibilite ancien appel."""
        if not cart:
            raise BizError("Le panier est vide.")
        if mode == "dine_in" and not unit_id:
            raise BizError("Sélectionnez la table ou le boucaro où le "
                           "client est installé.")
        if mode not in ("dine_in", "takeaway", None):
            raise BizError("Mode de service invalide.")
        discount = max(0.0, float(discount or 0))
        subtotal = sum(l["product"]["price"] * l["qty"] for l in cart)
        total = round(subtotal - discount, 2)
        if total < 0:
            raise BizError("La remise dépasse le total.")
        # le stock doit deja couvrir la commande au moment de la prise
        self.sales.stock.check_availability(cart)
        unit_name = None
        if unit_id is not None and self.floor:
            unit = self.floor.unit_by_id(int(unit_id))
            if not unit:
                raise BizError("Table/boucaro introuvable dans le plan "
                               "de salle.")
            unit_name = f"{unit['name']}"
            self.floor.set_status(unit["id"], "occupied")
        orders = self.s.load("orders", [])
        order = {
            "id": Storage.next_id(orders),
            "number": self._next_number(orders),
            "datetime": Storage.now(),
            "items": [{"product_id": l["product"]["id"],
                       "name": l["product"]["name"],
                       "qty": l["qty"],
                       "price": l["product"]["price"],
                       "total": round(l["product"]["price"] * l["qty"], 2)}
                      for l in cart],
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "total": total,
            "status": "open",
            "created_by": user["name"],
            "service_mode": mode or ("dine_in" if unit_name else None),
            "unit_id": unit["id"] if unit_name else None,
            "unit_name": unit_name,
            "notified_at": None,
            "settled_at": None, "settled_by": None,
            "method": None, "received": None, "change": None,
            "sale_number": None,
        }
        orders.append(order)
        self.s.save("orders", orders)
        # notification de la table : le client est informe de sa commande
        # des l'enregistrement, AVANT tout reglement
        if unit_name:
            summary = ", ".join(f"{l['qty']}x {l['product']['name']}"
                                for l in cart)
            order["notified_at"] = self._notify_table(order, summary,
                                                      user["name"])
            for o in orders:
                if o["id"] == order["id"]:
                    o["notified_at"] = order["notified_at"]
                    break
            self.s.save("orders", orders)
        return order

    def notify(self, number: str, unit_id, unit_name: str, summary: str,
               total: float, by: str) -> str:
        """Notifie une table (encaissement immediat sur place)."""
        return self._notify_table(
            {"number": number, "unit_id": unit_id, "unit_name": unit_name,
             "total": total}, summary, by)

    def _notify_table(self, order: dict, summary: str, by: str) -> str:
        notifs = self.s.load("table_notifications", [])
        rec = {
            "id": Storage.next_id(notifs),
            "at": Storage.now(),
            "order_id": order.get("id"),
            "order_number": order["number"],
            "unit_id": order.get("unit_id"),
            "unit_name": order.get("unit_name"),
            "summary": summary[:80],
            "total": order["total"],
            "by": by,
        }
        notifs.append(rec)
        self.s.save("table_notifications", notifs)
        return rec["at"]

    def notifications(self, limit=None):
        """Dernieres notifications de table (les plus recentes d'abord)."""
        lst = sorted(self.s.load("table_notifications", []),
                     key=lambda n: (n["at"], n.get("id", 0)), reverse=True)
        return lst[:limit] if limit else lst

    def get_order(self, order_id: int):
        return next((o for o in self.s.load("orders", [])
                     if o["id"] == order_id), None)

    def settle_order(self, order_id: int, method: str, received, user: dict,
                     mixed_cash=None, mixed_mobile=None):
        """Reglement valide par le caissier : cree la vente et archive."""
        order = self.get_order(order_id)
        if not order:
            raise BizError("Commande introuvable.")
        if order["status"] != "open":
            raise BizError("Cette commande est déjà réglée.")
        cart = [{"product": {"id": it["product_id"], "name": it["name"],
                             "price": it["price"]},
                 "qty": it["qty"]}
                for it in order["items"]]
        if method == "cash":
            if received is None or float(received) <= 0:
                raise BizError("Le montant reçu en espèces est requis.")
            received = float(received)
        else:
            received = None
        sale = self.sales.create_sale(cart, method, order["discount"], user,
                                      received=received,
                                      mixed_cash=mixed_cash,
                                      mixed_mobile=mixed_mobile)
        orders = self.s.load("orders", [])
        for o in orders:
            if o["id"] == order_id:
                o.update({"status": "settled", "settled_at": Storage.now(),
                          "settled_by": user["name"], "method": method,
                          "received": sale.get("received"),
                          "change": sale.get("change"),
                          "sale_number": sale["number"]})
                break
        self.s.save("orders", orders)
        self._release_unit(order)
        return sale

    def _release_unit(self, order: dict):
        """Remet la table/boucaro de la commande en 'libre'."""
        if self.floor and order.get("unit_id"):
            try:
                self.floor.set_status(order["unit_id"], "free")
            except BizError:
                pass

    def cancel_order(self, order_id: int, user: dict):
        order = self.get_order(order_id)
        if not order:
            raise BizError("Commande introuvable.")
        if order["status"] != "open":
            raise BizError("Seule une commande non réglée peut être annulée.")
        orders = self.s.load("orders", [])
        for o in orders:
            if o["id"] == order_id:
                o.update({"status": "cancelled",
                          "settled_at": Storage.now(), "settled_by": user["name"]})
                break
        self.s.save("orders", orders)
        self._release_unit(order)

    # -- impression de l'addition ---------------------------------------------
    def order_text(self, order: dict, settings: dict):
        w = 40
        lines = []
        center = lambda t: t.center(w).rstrip()  # noqa: E731
        lines.append("=" * w)
        lines.append(center((settings.get("restaurant_name")
                             or "Restaurant ADAM").upper()))
        addr = settings.get("address") or ""
        if addr:
            lines.append(center(addr))
        tel = settings.get("phone") or ""
        if tel:
            lines.append(center("Tél : " + tel))
        lines.append("=" * w)
        lines.append(center("A D D I T I O N"))
        lines.append(f"{order['number']:<20}{order['datetime']}")
        if order.get("service_mode") == "takeaway":
            lines.append(f"{'À EMPORTER':<20}")
        elif order.get("unit_name"):
            lines.append(f"{'Table : ' + order['unit_name']:<20}")
        lines.append("-" * w)
        for it in order["items"]:
            left = f"{it['qty']:>2} x {it['name'][:20]:<20}"
            right = f"{it['total']:>12,.0f}".replace(",", " ")
            lines.append(left + right)
        lines.append("-" * w)
        lines.append(f"{'Sous-total':<26}{order['subtotal']:>14,.0f}".replace(",", " "))
        if order.get("discount"):
            lines.append(f"{'Remise':<26}- {order['discount']:>12,.0f}".replace(",", " "))
        lines.append(f"{'TOTAL A REGLER':<26}{order['total']:>14,.0f}".replace(",", " "))
        lines.append("=" * w)
        lines.append(center("Merci ! Presentez-vous en caisse pour regler."))
        return "\n".join(lines)

    def save_addition_file(self, order: dict, settings: dict) -> str:
        path = os_path_join(self.s.additions_dir, f"{order['number']}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.order_text(order, settings))
        return path


def os_path_join(*parts):
    import os
    return os.path.join(*parts)


# ---------------------------------------------------------------- RAPPORTS ---
PERIODS = ["Jour", "Hier", "Semaine", "Mois", "Année"]


def period_range(period: str, ref: datetime | None = None):
    ref = ref or datetime.now()
    start = end = ref
    if period == "Jour":
        start = ref.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "Hier":
        start = (ref - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0)
        end = ref.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, end
    elif period == "Semaine":
        start = (ref - timedelta(days=ref.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0)
    elif period == "Mois":
        start = ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "Année":
        start = ref.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return start, end


class ReportService:
    def __init__(self, storage: Storage, stock: StockService, catalog=None,
                 floor=None, suppliers=None, auth=None):
        self.s = storage
        self.stock = stock
        self.catalog = catalog
        self.floor = floor
        self.suppliers = suppliers
        self.auth = auth

    def financial(self, period: str, start_s: str = None, end_s: str = None):
        if start_s is None or end_s is None:
            start, end = period_range(period)
            start_str = start.strftime("%Y-%m-%d %H:%M:%S")
            end_str = end.strftime("%Y-%m-%d %H:%M:%S")
        else:
            start_str, end_str = start_s, end_s
        sales = [x for x in self.s.load("sales", [])
                 if start_str <= x["datetime"] < end_str]
        revenue = sum(x["total"] for x in sales)
        discounts = sum(x.get("discount", 0) for x in sales)
        by_method = {}
        for x in sales:
            by_method[x["method"]] = round(by_method.get(x["method"], 0) + x["total"], 2)

        # mouvements de caisse sur la periode
        cash_in = cash_out = 0.0
        for c in self.s.load("cash_sessions", []):
            for m in c.get("movements", []):
                if not (start_str <= m["at"] < end_str):
                    continue
                if m["type"] in ("in", "sale"):
                    cash_in += m["amount"]
                elif m["type"] == "out":
                    cash_out += m["amount"]

        top_products = {}
        per_product_revenue = {}
        for x in sales:
            for it in x["items"]:
                k = it["name"]
                top_products[k] = top_products.get(k, 0) + it["qty"]
                per_product_revenue[k] = per_product_revenue.get(k, 0) + it["total"]
        top = sorted(top_products.items(), key=lambda kv: kv[1], reverse=True)[:8]

        return {
            "count": len(sales),
            "revenue": round(revenue, 2),
            "discounts": round(discounts, 2),
            "avg_basket": round(revenue / len(sales), 2) if sales else 0.0,
            "by_method": by_method,
            "cash_in_manual": round(cash_in, 2),
            "cash_out_manual": round(cash_out, 2),
            "top_products": [{"name": n, "qty": q,
                              "revenue": round(per_product_revenue[n], 2)}
                             for n, q in top],
            "sales_recent": sales[:15],
        }

    def series(self, period: str, start_s: str = None, end_s: str = None):
        """Serie temporelle du CA pour le graphique."""
        now = datetime.now()
        custom = start_s is not None and end_s is not None
        buckets = []
        if custom:
            sdt = datetime.strptime(start_s[:10], "%Y-%m-%d")
            edt = datetime.strptime(end_s[:10], "%Y-%m-%d")
            total_days = (edt - sdt).days + 1
            if total_days <= 1:
                buckets = [(sdt.replace(hour=h, minute=0, second=0,
                                        microsecond=0), f"{h:02d}h")
                           for h in range(24)]
            else:
                step = max(1, (total_days + 13) // 14) if total_days > 32 else 1
                buckets = [(sdt + timedelta(days=i),
                            (sdt + timedelta(days=i)).strftime("%d/%m")
                            if step > 1 else str((sdt + timedelta(days=i)).day))
                           for i in range(0, total_days, step)]
        elif period == "Jour":
            buckets = [(now.replace(hour=h, minute=0, second=0, microsecond=0), f"{h:02d}h")
                       for h in range(now.hour + 1)]
        elif period == "Hier":
            y = (now - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0)
            buckets = [(y + timedelta(hours=h), f"{h:02d}h") for h in range(24)]
        elif period == "Semaine":
            monday = (now - timedelta(days=now.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0)
            names = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
            buckets = [(monday + timedelta(days=i), names[i]) for i in range(7)]
        elif period == "Mois":
            first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            nb_days = (now - first).days + 1
            buckets = [(first + timedelta(days=i), str(i + 1)) for i in range(nb_days)]
        else:  # Année
            labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                      "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
            buckets = [(now.year, m, labels[m - 1]) for m in range(1, now.month + 1)]

        values = [0.0] * len(buckets)
        fmt = "%Y-%m-%d %H:%M:%S"
        for x in self.s.load("sales", []):
            dt = datetime.strptime(x["datetime"], fmt)
            for idx, b in enumerate(buckets):
                if custom:
                    if len(b) == 2 and isinstance(b[1], str) and b[1].endswith("h"):
                        bdt = b[0]
                        if bdt <= dt < bdt + timedelta(hours=1):
                            values[idx] += x["total"]
                    else:
                        bdt = b[0]
                        if bdt <= dt < bdt + timedelta(days=1):
                            values[idx] += x["total"]
                elif period == "Année":
                    byear, bmonth, _lbl = b
                    if dt.year == byear and dt.month == bmonth:
                        values[idx] += x["total"]
                elif period in ("Semaine", "Mois"):
                    bdt = b[0]
                    if bdt <= dt < bdt + timedelta(days=1):
                        values[idx] += x["total"]
                else:  # Jour (heures)
                    bdt = b[0]
                    if bdt <= dt < bdt + timedelta(hours=1):
                        values[idx] += x["total"]
        labels = [b[-1] for b in buckets]
        return labels, [round(v, 2) for v in values]

    def stock_summary(self, period: str, start_s: str = None, end_s: str = None):
        if start_s is None or end_s is None:
            start, end = period_range(period)
            start_str = start.strftime("%Y-%m-%d %H:%M:%S")
            end_str = end.strftime("%Y-%m-%d %H:%M:%S")
        else:
            start_str, end_str = start_s, end_s
        mv = [m for m in self.stock.movements()
              if start_str <= m["at"] < end_str]
        entries = round(sum(m["qty"] for m in mv if m["type"] == "in"), 3)
        exits = round(sum(m["qty"] for m in mv if m["type"] == "out"), 3)
        adjusts = round(sum(m["qty"] for m in mv if m["type"] == "adjust"), 3)
        value_low = round(sum(i["current_stock"] * i.get("cost_price", 0)
                              for i in self.stock.ingredients()), 2)
        return {"entries": entries, "exits": exits, "adjusts": adjusts,
                "count": len(mv), "inventory_value": value_low,
                "low": self.stock.low_stock(), "recent": mv[:15]}

    # ------------------------------------------------------- SUIVI TOTAL ------
    def activity_summary(self, start_s: str, end_s: str,
                         user_id: int = None, user_name: str = None) -> dict:
        """Recapitulatif de TOUTE l'activite des 7 modules sur une plage de dates
        [start_s, end_s) (format 'YYYY-MM-DD HH:MM:SS'). Si `user_id` est fourni,
        seules l'activite realisee par cet employe est comptee.

        Les modules 'menu' et 'salle' n'ont pas d'horodatage persistant : on
        affiche un etat (instantan) plutot qu'un depliage sur la periode.
        """
        def _in_range(at):
            return start_s <= at < end_s

        # --- 1. CAISSE -----------------------------------------------------
        sessions = self.s.load("cash_sessions", [])
        cash_in = cash_out = 0.0
        cash_movs = []
        for c in sessions:
            for m in c.get("movements", []):
                if not _in_range(m["at"]):
                    continue
                if user_name and m.get("by") != user_name:
                    continue
                cash_movs.append({**m, "session": c.get("opened_by", "?")})
                if m["type"] in ("in", "sale"):
                    cash_in += m["amount"]
                elif m["type"] == "out":
                    cash_out += m["amount"]
        cash_opens = [c for c in sessions
                      if _in_range(c.get("opened_at", ""))
                      and (not user_name or c.get("opened_by") == user_name)]
        cash_closes = [c for c in sessions
                       if c.get("closed_at") and _in_range(c["closed_at"])
                       and (not user_name or c.get("closed_by") == user_name)]

        # --- 2. VENTES / COMMANDES -----------------------------------------
        sales = [x for x in self.s.load("sales", []) if _in_range(x["datetime"])]
        if user_id is not None:
            sales = [x for x in sales
                     if x.get("cashier_id") == user_id
                     or (user_name and x.get("cashier") == user_name)]
        revenue = round(sum(x["total"] for x in sales), 2)
        discounts = round(sum(x.get("discount", 0) for x in sales), 2)
        by_method = {}
        for x in sales:
            by_method[x["method"]] = round(by_method.get(x["method"], 0)
                                           + x["total"], 2)
        top_prod = {}
        for x in sales:
            for it in x["items"]:
                k = it["name"]
                top_prod[k] = top_prod.get(k, 0) + it["qty"]
        top_products = sorted(top_prod.items(), key=lambda kv: kv[1],
                              reverse=True)[:8]

        orders = [o for o in self.s.load("orders", [])
                  if _in_range(o.get("datetime", ""))
                  and (not user_name or o.get("created_by") == user_name)]
        settled = [o for o in orders if o.get("settled_at")
                   and _in_range(o["settled_at"])
                   and (not user_name or o.get("settled_by") == user_name)]

        # --- 3. STOCK ------------------------------------------------------
        mv = [m for m in self.stock.movements() if _in_range(m["at"])
              and (not user_name or m.get("by") == user_name)]
        entries = round(sum(m["qty"] for m in mv if m["type"] == "in"), 3)
        exits = round(sum(m["qty"] for m in mv if m["type"] == "out"), 3)
        adjusts = round(sum(m["qty"] for m in mv if m["type"] == "adjust"), 3)

        # --- 4. FOURNISSEURS -----------------------------------------------
        deliveries = [d for d in self.s.load("deliveries", [])
                      if _in_range(d["at"])
                      and (not user_name or d.get("by") == user_name)]
        sup_pays = [p for p in self.s.load("supplier_payments", [])
                    if _in_range(p["at"])
                    and (not user_name or p.get("by") == user_name)]
        deliv_total = round(sum(d["total"] for d in deliveries), 2)
        sup_paid = round(sum(p["amount"] for p in sup_pays), 2)
        sups = self.suppliers.suppliers()
        total_debt = round(sum(
            self.suppliers.supplier_totals(s["id"])["debt"] for s in sups), 2)

        # --- 5. PERSONNEL (avances + paiements salaires) --------------------
        advs = [a for a in self.s.load("salary_advances", [])
                if _in_range(a["at"])
                and (not user_name or a.get("by") == user_name)]
        payr = [a for a in self.s.load("salary_payments", [])
                if _in_range(a["at"])
                and (not user_name or a.get("by") == user_name)]
        adv_total = round(sum(a["amount"] for a in advs), 2)
        payr_total = round(sum(a["amount"] for a in payr), 2)
        staff = self.auth.staff()
        active_count = len([u for u in staff if u.get("active", True)])

        # --- 6. MENU / 7. SALLE (etat instantane) ---------------------------
        prods = self.catalog.products()
        cats = self.catalog.categories()
        units = self.floor.units()
        occupied = [u for u in units if u.get("status") == "occupied"]
        reserved = [u for u in units if u.get("status") == "reserved"]

        return {
            "caisse": {
                "open": len(cash_opens), "closed": len(cash_closes),
                "in": round(cash_in, 2), "out": round(cash_out, 2),
                "net": round(cash_in - cash_out, 2),
                "movements": cash_movs[:30],
            },
            "ventes": {
                "count": len(sales), "revenue": revenue,
                "avg_basket": round(revenue / len(sales), 2) if sales else 0.0,
                "discounts": discounts, "by_method": by_method,
                "orders": len(orders), "settled": len(settled),
                "top_products": top_products,
                "recent": sales[:12],
            },
            "stock": {
                "entries": entries, "exits": exits, "adjusts": adjusts,
                "count": len(mv),
                "low": self.stock.low_stock(),
            },
            "fournisseurs": {
                "count_deliveries": len(deliveries),
                "delivery_total": deliv_total,
                "count_payments": len(sup_pays),
                "paid": sup_paid,
                "debt": total_debt,
                "deliveries": deliveries[:12],
                "payments": sup_pays[:12],
            },
            "personnel": {
                "count_advances": len(advs),
                "advances_total": adv_total,
                "count_payments": len(payr),
                "salaries_total": payr_total,
                "active": active_count,
            },
            "menu": {
                "categories": len(cats),
                "products": len(prods),
                "available": len(self.catalog.products(available_only=True)),
            },
            "salle": {
                "occupied": len(occupied), "reserved": len(reserved),
                "occupied_names": [u["name"] for u in occupied],
                "reserved_names": [u["name"] for u in reserved],
            },
        }


# ------------------------------------------------------- PLAN DE SALLE ------
class FloorPlanService:
    """Unites du plan de salle : tables et boucaros (espaces traditionnels).

    Une unite : {id, name, kind, seats, zone, status, note}
    kind : "table" | "boucaro" ; status : free / occupied / reserved."""

    KINDS = {"table": "Table", "boucaro": "Boucaro"}

    def __init__(self, storage: Storage):
        self.s = storage

    def units(self, kind=None):
        lst = sorted(self.s.load("floor_units", []),
                     key=lambda u: (u.get("kind", ""), u["name"].lower()))
        return [u for u in lst if kind is None or u["kind"] == kind]

    def unit_by_id(self, uid: int):
        return next((u for u in self.units() if u["id"] == uid), None)

    def save_unit(self, data: dict, unit_id=None):
        name = (data.get("name") or "").strip()
        if not name:
            raise BizError("Le nom/numero est obligatoire.")
        kind = data.get("kind")
        if kind not in self.KINDS:
            raise BizError("Type d'unite invalide (table ou boucaro).")
        seats = int(data.get("seats") or 0)
        if seats < 0:
            raise BizError("Le nombre de places ne peut pas etre negatif.")
        lst = self.s.load("floor_units", [])
        dup = [u for u in lst if u["kind"] == kind
               and u["name"].lower() == name.lower() and u["id"] != unit_id]
        if dup:
            raise BizError("Ce nom est déjà utilisé par une unité du "
                           "même type (table ou boucaro).")
        defaults = {"status": "free", "zone": "", "note": "", "seats": 4}
        if unit_id is None:
            unit = {"id": Storage.next_id(lst), **defaults,
                    **data, "name": name, "seats": seats}
            lst.append(unit)
        else:
            unit = next((u for u in lst if u["id"] == unit_id), None)
            if not unit:
                raise BizError("Unite introuvable.")
            unit.update(data)
            unit["name"] = name
            unit["seats"] = seats
            unit.setdefault("status", "free")
        self.s.save("floor_units", lst)
        return unit

    def delete_unit(self, uid: int):
        lst = self.s.load("floor_units", [])
        self.s.save("floor_units", [u for u in lst if u["id"] != uid])

    def set_status(self, uid: int, status: str):
        if status not in TABLE_STATUSES:
            raise BizError("Statut invalide.")
        unit = self.unit_by_id(uid)
        if not unit:
            raise BizError("Unite introuvable.")
        lst = self.s.load("floor_units", [])
        for u in lst:
            if u["id"] == uid:
                u["status"] = status
                break
        self.s.save("floor_units", lst)


# ---------------------------------------------------------- FOURNISSEURS ----
class SupplierService:
    """Fournisseurs + livraisons (reception qui alimente le stock)."""

    def __init__(self, storage: Storage, stock: StockService):
        self.s = storage
        self.stock = stock

    # -- fournisseurs --------------------------------------------------------
    def suppliers(self, active_only=False):
        lst = sorted(self.s.load("suppliers", []),
                     key=lambda x: x["name"].lower())
        return [x for x in lst if x.get("active", True)] if active_only \
            else lst

    def supplier_by_id(self, sid: int):
        return next((x for x in self.suppliers() if x["id"] == sid), None)

    def save_supplier(self, data: dict, sup_id=None):
        name = (data.get("name") or "").strip()
        if not name:
            raise BizError("Le nom du fournisseur est obligatoire.")
        lst = self.s.load("suppliers", [])
        dup = [x for x in lst
               if x["name"].lower() == name.lower() and x["id"] != sup_id]
        if dup:
            raise BizError("Un fournisseur porte déjà ce nom.")
        if sup_id is None:
            sup = {"id": Storage.next_id(lst), "active": True,
                   **data, "name": name}
            lst.append(sup)
        else:
            sup = next((x for x in lst if x["id"] == sup_id), None)
            if not sup:
                raise BizError("Fournisseur introuvable.")
            sup.update(data)
            sup["name"] = name
            sup.setdefault("active", True)
        self.s.save("suppliers", lst)
        return sup

    def set_active(self, sup_id: int, active: bool):
        lst = self.s.load("suppliers", [])
        for x in lst:
            if x["id"] == sup_id:
                x["active"] = bool(active)
                break
        else:
            raise BizError("Fournisseur introuvable.")
        self.s.save("suppliers", lst)

    def delete_supplier(self, sup_id: int):
        lst = self.s.load("suppliers", [])
        self.s.save("suppliers", [x for x in lst if x["id"] != sup_id])

    # -- paiements au fournisseur --------------------------------------------
    def payments(self, supplier_id=None):
        lst = sorted(self.s.load("supplier_payments", []),
                     key=lambda p: (p["at"], p.get("id", 0)), reverse=True)
        if supplier_id is not None:
            lst = [p for p in lst if p["supplier_id"] == supplier_id]
        return lst

    def add_payment(self, supplier_id: int, amount: float, user: str,
                    note: str = ""):
        sup = self.supplier_by_id(supplier_id)
        if not sup:
            raise BizError("Fournisseur introuvable.")
        amount = round(float(amount), 2)
        if amount <= 0:
            raise BizError("Le montant payé doit être positif.")
        ps = self.s.load("supplier_payments", [])
        rec = {
            "id": Storage.next_id(ps),
            "at": Storage.now(),
            "supplier_id": sup["id"],
            "supplier_name": sup["name"],
            "amount": amount,
            "by": user,
            "note": (note or "").strip(),
        }
        ps.append(rec)
        self.s.save("supplier_payments", ps)
        return rec

    def supplier_totals(self, supplier_id: int) -> dict:
        """Retourne {expected, paid, debt} pour un fournisseur."""
        dl = self.deliveries()
        expected = round(sum(d["total"] for d in dl
                             if d["supplier_id"] == supplier_id), 2)
        paid = round(sum(p["amount"] for p in self.payments(supplier_id)), 2)
        debt = round(expected - paid, 2)
        return {"expected": expected, "paid": paid, "debt": debt}

    # -- livraisons (entree de stock chez le fournisseur) --------------------
    def deliveries(self, limit=None):
        dl = sorted(self.s.load("deliveries", []),
                    key=lambda d: (d["at"], d.get("id", 0)), reverse=True)
        return dl[:limit] if limit else dl

    def add_delivery(self, supplier_id: int, ingredient_id: int,
                     qty: float, unit_cost: float, by: str,
                     pieces: float = None,
                     purchase_unit: str = ""):
        """Reception d'une livraison fournisseur.

        Le fournisseur livre en quantite brute (qty, dans `purchase_unit`,
        ex: 5 kg). Cette quantite est transformee en `pieces` unites qui
        entrent reellement en stock (ex: 5 kg -> 20 pieces de boeuf).
        Le cout unitaire stock = prix total / pieces.
        Si `pieces` est None, la quantite achetee entre telle quelle (=1).
        """
        sup = self.supplier_by_id(supplier_id)
        if not sup:
            raise BizError("Selectionnez un fournisseur.")
        ing = self.stock.ingredient_by_id(ingredient_id)
        if not ing:
            raise BizError("Selectionnez un ingredient.")
        qty = float(qty)
        if qty <= 0:
            raise BizError("La quantite doit etre positive.")
        unit_cost = max(0.0, float(unit_cost or 0))

        pieces = qty if pieces in (None, 0, "") else float(pieces)
        if pieces < 0:
            raise BizError("Le nombre de pieces doit etre positif.")
        pieces = max(0.0, round(pieces, 3))

        stock_qty = pieces          # quantite reelle entrant en stock
        unit_price = round(unit_cost / pieces, 2) if pieces > 0 else 0.0

        self.stock.add_movement(ingredient_id, "in", stock_qty,
                                f"Réception fournisseur — {sup['name']}", by)
        dl = self.s.load("deliveries", [])
        rec = {
            "id": Storage.next_id(dl),
            "at": Storage.now(),
            "supplier_id": sup["id"],
            "supplier_name": sup["name"],
            "ingredient_id": ing["id"],
            "ingredient_name": ing["name"],
            "qty": round(qty, 3),
            "purchase_unit": (purchase_unit or "").strip(),
            "ing_unit": ing.get("unit", ""),
            "units_per_purchase": pieces if pieces else 1,
            "stock_qty": stock_qty,
            "unit_cost": unit_price,
            "total": round(qty * unit_cost, 2),
            "by": by,
        }
        dl.append(rec)
        self.s.save("deliveries", dl)
        return rec


# ------------------------------------------------------------------ PAYROLL ----
class PayrollService:
    """Gestion des salaires des employés : avances et paiement final.

    Chaque mois, on enregistre des avances pour un employé puis un paiement
    final du solde. net = salaire - somme(avances du mois).
    Reference mois = "YYYY-MM".
    """

    def __init__(self, storage: Storage, auth: AuthService):
        self.s = storage
        self.auth = auth

    # -- référence au mois courant -------------------------------------------
    @staticmethod
    def current_month(dt: datetime = None) -> str:
        dt = dt or datetime.now()
        return dt.strftime("%Y-%m")

    @staticmethod
    def month_label(month: str) -> str:
        try:
            d = datetime.strptime(month + "-01", "%Y-%m-%d")
            return d.strftime("%B %Y")
        except ValueError:
            return month

    def salary_months(self) -> list:
        """Mois (YYYY-MM) ayant des mouvements, tries, plus le mois courant."""
        months = set()
        for a in self.s.load("salary_advances", []):
            months.add(a.get("month", self.current_month()))
        for p in self.s.load("salary_payments", []):
            months.add(p.get("month", self.current_month()))
        # Le mois courant est toujours proposé, meme sans mouvement.
        months.add(self.current_month())
        return sorted(months)

    # -- avances -------------------------------------------------------------
    def advances(self, user_id: int = None, month: str = None):
        lst = sorted(self.s.load("salary_advances", []),
                     key=lambda a: (a["at"], a.get("id", 0)))
        if user_id is not None:
            lst = [a for a in lst if a["user_id"] == user_id]
        if month is not None:
            lst = [a for a in lst if a["month"] == month]
        return lst

    def advance_total(self, user_id: int, month: str) -> float:
        return round(sum(a["amount"] for a in self.advances(user_id, month)),
                     2)

    def add_advance(self, user_id: int, amount: float, by: str, note=""):
        user = self.auth.user_by_id(user_id)
        if not user:
            raise BizError("Employé introuvable.")
        amount = round(float(amount), 2)
        if amount <= 0:
            raise BizError("Le montant de l'avance doit être positif.")
        lst = self.s.load("salary_advances", [])
        rec = {
            "id": Storage.next_id(lst),
            "at": Storage.now(),
            "month": self.current_month(),
            "user_id": user["id"],
            "user_name": user["name"],
            "amount": amount,
            "by": by,
            "note": (note or "").strip(),
        }
        lst.append(rec)
        self.s.save("salary_advances", lst)
        return rec

    # -- paiements (soldes) --------------------------------------------------
    def payments(self, user_id: int = None, month: str = None):
        lst = sorted(self.s.load("salary_payments", []),
                     key=lambda p: (p["at"], p.get("id", 0)))
        if user_id is not None:
            lst = [p for p in lst if p["user_id"] == user_id]
        if month is not None:
            lst = [p for p in lst if p["month"] == month]
        return lst

    def pay_salary(self, user_id: int, amount: float, by: str, note=""):
        """Paiement final du solde d'un salaire mensuel."""
        user = self.auth.user_by_id(user_id)
        if not user:
            raise BizError("Employé introuvable.")
        month = self.current_month()
        net = self.net_to_pay(user_id, month)
        amount = round(float(amount), 2)
        if amount <= 0:
            raise BizError("Le montant versé doit être positif.")
        if amount > net + 0.01:
            raise BizError(
                f"Le montant dépasse le solde à verser "
                f"({theme_money(net)}).")
        lst = self.s.load("salary_payments", [])
        rec = {
            "id": Storage.next_id(lst),
            "at": Storage.now(),
            "month": month,
            "user_id": user["id"],
            "user_name": user["name"],
            "amount": amount,
            "by": by,
            "note": (note or "").strip(),
        }
        lst.append(rec)
        self.s.save("salary_payments", lst)
        return rec

    # -- calculs -------------------------------------------------------------
    def monthly_salary(self, user) -> float:
        return round(max(0.0, float(user.get("salary", 0) or 0)), 2)

    def paid_total(self, user_id: int, month: str) -> float:
        return round(sum(p["amount"] for p in self.payments(user_id, month)),
                     2)

    def user_total(self, user_id: int, month: str) -> float:
        """Total versé à l'employé sur le mois (avances + paiements)."""
        return round(self.advance_total(user_id, month)
                     + self.paid_total(user_id, month), 2)

    def net_to_pay(self, user_id: int, month: str) -> float:
        """Solde restant à verser = salaire - avances - déjà payé."""
        user = self.auth.user_by_id(user_id)
        if not user:
            return 0.0
        salary = self.monthly_salary(user)
        return round(max(0.0,
                         salary - self.advance_total(user_id, month)
                         - self.paid_total(user_id, month)), 2)


def theme_money(amount: float) -> str:
    return f"{amount:,.0f} F".replace(",", " ")
