"""Test headless de la logique metier (sans interface graphique)."""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.state import AppState

tmp = tempfile.mkdtemp(prefix="adam_test_")
state = AppState(tmp)
errors = []


def check(name, cond):
    print(("  OK  " if cond else " FAIL ") + name)
    if not cond:
        errors.append(name)


# --- auth -----------------------------------------------------------------
admin = state.auth.login("admin", "admin123")
caisse = state.auth.login("caisse", "caisse123")
check("login admin", admin and admin["role"] == "admin")
check("login caissiere", caisse and caisse["role"] == "caissiere")
check("mauvais mdp refuse", state.auth.login("admin", "wrong") is None)

# --- catalogue -------------------------------------------------------------
prods = state.catalog.products(available_only=True)
check("26 produits initialises", len(prods) == 26)
poulet = state.catalog.product_by_id(1)
check("produit Poulet DG", poulet and poulet["name"] == "Poulet DG")

# --- caisse : vente cash impossible sans session ---------------------------
try:
    state.sales.create_sale([{"product": poulet, "qty": 2}], "cash", 0, admin)
    check("vente cash bloquee sans caisse", False)
except Exception:
    check("vente cash bloquee sans caisse", True)

# --- ouverture caisse --------------------------------------------------------
sess = state.cash.open_session(5000, admin, "test")
check("session ouverte", state.cash.get_open() is not None)
try:
    state.cash.open_session(100, admin)
    check("2e session refusee", False)
except Exception:
    check("2e session refusee", True)

# --- stock avant vente -------------------------------------------------------
poulet_stock_before = state.stock.ingredient_by_id(1)["current_stock"]
riz_before = state.stock.ingredient_by_id(5)["current_stock"]

# --- vente avec recette (Poulet DG x3 -> poulet -1.05 kg) -------------------
sale = state.sales.create_sale([{"product": poulet, "qty": 3}], "cash", 500,
                               caisse, received=20000)
check("numero ticket", sale["number"].startswith("T"))
check("total = 11500", sale["total"] == 11500)
check("monnaie = 8500", sale.get("change") == 8500)
poulet_after = state.stock.ingredient_by_id(1)["current_stock"]
check(f"stock poulet deduit ({poulet_stock_before} -> {poulet_after})",
      abs(poulet_stock_before - poulet_after - 1.05) < 0.001)

# riz n'est PAS dans la recette du Poulet DG
riz_after = state.stock.ingredient_by_id(5)["current_stock"]
check("stock riz intact", riz_before == riz_after)

# --- vente mobile money : ne touche pas la caisse especes --------------------
eau = state.catalog.product_by_id(23)
sale2 = state.sales.create_sale([{"product": eau, "qty": 4}], "mobile_money",
                                0, caisse)
sess_now = state.cash.get_open()
expected_cash = 5000 + 11500
check("mobile money pas en especes",
      abs(sess_now["total_cash_in"] - 11500) < 0.01)

# --- mouvements de caisse ------------------------------------------------------
state.cash.add_movement("out", 2000, "Dépense course", admin)
sess_now = state.cash.get_open()
check("sortie caisse enregistree", sess_now["total_cash_out"] == 2000)
check("attendu = fond + in - out",
      state.cash.expected_amount(sess_now) == expected_cash - 2000)

# --- fermeture ---------------------------------------------------------------
closed = state.cash.close_session(expected_cash - 2000 + 300, admin)
check("ecart calcule = +300", closed["difference"] == 300)
try:
    state.cash.add_movement("in", 100, "x", admin)
    check("mouvement apres cloture bloque", False)
except Exception:
    check("mouvement apres cloture bloque", True)

# --- stock : mouvement manuel --------------------------------------------------
state.stock.add_movement(5, "in", 10, "Achat marché", "admin")
check("entree stock riz", abs(state.stock.ingredient_by_id(5)["current_stock"]
                              - (riz_after + 10)) < 0.001)
try:
    state.stock.add_movement(5, "out", 99999, "test", "admin")
    check("sortie excessive bloquee", False)
except Exception:
    check("sortie excessive bloquee", True)

# --- rapports -------------------------------------------------------------------
fin = state.reports.financial("Jour")
check("CA jour = 14300", fin["revenue"] == 14300)
check("nb tickets = 2", fin["count"] == 2)
labels, values = state.reports.series("Jour")
check("serie jour non vide", sum(values) > 0)
labels_w, values_w = state.reports.series("Semaine")
check("serie semaine 7 points", len(labels_w) == 7 and sum(values_w) == 14300)
labels_y, values_y = state.reports.series("Année")
check("serie annee mois courant", len(values_y) >= 8)
ssum = state.reports.stock_summary("Jour")
check("resume stock entrees > sorties", ssum["entries"] > 0 and ssum["exits"] > 0)

# --- ticket fichier -------------------------------------------------------------
path = state.sales.save_ticket_file(sale, state.settings)
check("fichier ticket cree", os.path.exists(path))
txt = open(path, encoding="utf-8").read()
check("ticket contient total et monnaie", "11 500" in txt and "8 500" in txt)

# --- persistance ------------------------------------------------------------------
state2 = AppState(tmp)
check("donnees persistees (sessions)",
      len(state2.storage.load("cash_sessions", [])) == 1)
check("donnees persistees (ventes)", len(state2.sales.sales()) == 2)

# --- changement mot de passe -----------------------------------------------------
state.auth.change_password(caisse["id"], "caisse123", "nouveau456")
check("changement mdp", state.auth.login("caisse", "nouveau456") is not None)

# --- personnel : creation, doublons, blocage, suppression ------------------------
new_emp = state.auth.add_staff("Marie Ngo", "marie", "pass1234", "caissiere")
check("employe cree", new_emp and new_emp["role"] == "caissiere")
check("login nouvel employe",
      state.auth.login("marie", "pass1234") is not None)
try:
    state.auth.add_staff("X", "marie", "pass1234", "caissiere")
    check("identifiant duplique refuse", False)
except Exception:
    check("identifiant duplique refuse", True)
try:
    state.auth.add_staff("X", "ok_id", "abc", "caissiere")
    check("mdp trop court refuse", False)
except Exception:
    check("mdp trop court refuse", True)
state.auth.update_staff(new_emp["id"], "Marie Ngo Biba", "marie.b", "admin")
updated = next(u for u in state.auth.users() if u["id"] == new_emp["id"])
check("employe modifie (nom, id, role)",
      updated["name"] == "Marie Ngo Biba" and updated["username"] == "marie.b"
      and updated["role"] == "admin")
try:
    state.auth.set_staff_active(admin["id"], False, admin)
    check("auto-blocage refuse", False)
except Exception:
    check("auto-blocage refuse", True)
state.auth.set_staff_active(new_emp["id"], False, admin)
try:
    bloque = state.auth.login("marie.b", "pass1234")
except Exception:
    bloque = None
check("compte bloque refuse", bloque is None)
state.auth.set_staff_active(new_emp["id"], True, admin)
check("compte reactive",
      state.auth.login("marie.b", "pass1234") is not None)
state.auth.reset_staff_password(new_emp["id"], "fresh999")
check("mdp reinitialise", state.auth.login("marie.b", "fresh999") is not None)
try:
    state.auth.delete_staff(admin["id"], admin)
    check("auto-suppression refusee", False)
except Exception:
    check("auto-suppression refusee", True)
try:
    state.auth.delete_staff(1, admin)  # dernier admin actif
    check("dernier admin protege", False)
except Exception:
    check("dernier admin protege", True)
state.auth.delete_staff(new_emp["id"], admin)
check("employe supprime",
      not any(u["username"] == "marie.b" for u in state.auth.users()))

# --- commandes : addition -> reglement -> historique -----------------------------
state.cash.open_session(2000, admin, "test commandes")
order = state.orders.create_order([{"product": poulet, "qty": 2}], 0, caisse)
check("commande creee non reglee",
      order["status"] == "open" and order["total"] == 8000)
check("numero commande", order["number"].startswith("C"))
check("commande dans les non reglees",
      any(o["id"] == order["id"] for o in state.orders.open_orders()))
try:
    state.orders.settle_order(order["id"], "cash", 5000, caisse)
    check("reglement insuffisant refuse", False)
except Exception:
    check("reglement insuffisant refuse", True)
poulet_before_settle = state.stock.ingredient_by_id(1)["current_stock"]
sale_o = state.orders.settle_order(order["id"], "cash", 10000, admin)
check("reglement cree vente + remboursement",
      sale_o["number"].startswith("T") and sale_o.get("change") == 2000)
settled = state.orders.get_order(order["id"])
check("commande passee a l'historique",
      settled["status"] == "settled"
      and settled["sale_number"] == sale_o["number"]
      and any(o["id"] == order["id"] for o in state.orders.closed_orders()))
try:
    state.orders.settle_order(order["id"], "cash", 8000, admin)
    check("double reglement bloque", False)
except Exception:
    check("double reglement bloque", True)
check("stock deduit au reglement",
      abs(state.stock.ingredient_by_id(1)["current_stock"]
          - (poulet_before_settle - 0.70)) < 0.001)
order2 = state.orders.create_order([{"product": poulet, "qty": 1}], 0, admin)
state.orders.cancel_order(order2["id"], admin)
check("commande annulee",
      state.orders.get_order(order2["id"])["status"] == "cancelled")
txt_add = state.orders.order_text(order, state.settings)
check("texte addition contient total", "8 000" in txt_add)
path_add = state.orders.save_addition_file(order, state.settings)
check("fichier addition cree", os.path.exists(path_add))
state.cash.close_session(
    state.cash.expected_amount(state.cash.get_open()), admin)

print()
shutil.rmtree(tmp)
if errors:
    print(f"{len(errors)} TEST(S) EN ECHEC :", errors)
    sys.exit(1)
print("TOUS LES TESTS PASSENT ✓")
