"""Initialisation des fichiers de donnees au premier lancement."""
from .security import hash_password
from .storage import Storage

DEFAULT_SETTINGS = {
    "restaurant_name": "Restaurant ADAM",
    "address": "Ngaoundéré, au bois de Mardock",
    "phone": "+237 694 469 678",
    "currency": "FCFA",
    "ticket_footer": "Merci de votre visite ! A bientot.",
}

DEFAULT_USERS = [
    {"id": 1, "name": "Administrateur", "username": "adam",
     "role": "admin", "password_hash": hash_password("adam")},
]


def init_data(storage: Storage) -> bool:
    """Cree les fichiers manquants. Retourne True si premiere installation."""
    first_run = not storage.exists("users")
    defaults = [
        ("settings", DEFAULT_SETTINGS),
        ("users", DEFAULT_USERS),
        ("categories", []),
        ("products", []),
        ("ingredients", []),
        ("recipes", []),
        ("sales", []),
        ("orders", []),
        ("cash_sessions", []),
        ("stock_movements", []),
        ("suppliers", []),
        ("deliveries", []),
        ("supplier_payments", []),
        ("salary_advances", []),
        ("salary_payments", []),
        ("floor_units", []),
        ("table_notifications", []),
    ]
    for name, data in defaults:
        if not storage.exists(name):
            storage.save(name, data)
    return first_run
