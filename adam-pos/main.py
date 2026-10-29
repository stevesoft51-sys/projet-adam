#!/usr/bin/env python3
"""Restaurant ADAM — Point de Vente & Gestion (application locale, offline).

Lancement :
    python3 main.py

Architecture : UNE SEULE boucle d'evenements active a la fois.
login.mainloop()  ->  fenetre principale main.mainloop()  ->  retour login...
C'est ce qui evite le blocage "rien ne se passe apres connexion".
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.state import AppState                      # noqa: E402
from app.ui.login_window import LoginWindow         # noqa: E402
from app.ui.main_window import MainWindow           # noqa: E402
from app.ui.product_images import clear_cache       # noqa: E402
from app.activation import is_licensed              # noqa: E402
from app.ui.activation_window import ActivationWindow  # noqa: E402


def _data_dir():
    """Repertoire de donnees : cote a l'executable ou au script."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "data")


DATA_DIR = _data_dir()


def open_main_window(state) -> bool:
    """Ouvre la fenetre principale. Retourne True si l'utilisateur veut
    se reconnecter (deconnexion), False s'il quitte l'application."""
    try:
        clear_cache()
        main = MainWindow(state)
    except Exception:
        traceback.print_exc()
        return False
    main.mainloop()
    return getattr(main, "logout_requested", False)


def run_app(state):
    """Boucle de sessions : activation -> login -> app -> deconnexion -> login ..."""
    if not is_licensed(DATA_DIR):
        act = ActivationWindow(DATA_DIR)
        act.mainloop()
        if not act.activated:
            return

    while True:
        if state.user is None:
            login = LoginWindow(state)
            login.mainloop()
            if state.user is None:
                break
        try:
            again = open_main_window(state)
        except Exception:
            traceback.print_exc()
            break
        state.user = None
        if not again:
            break


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Données :", DATA_DIR)
    state = AppState(DATA_DIR)
    run_app(state)
