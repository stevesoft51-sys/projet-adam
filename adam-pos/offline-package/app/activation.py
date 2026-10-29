"""Verification de la cle d'activation universelle.

La cle est commune a toutes les installations.
Stockee dans data/license.json apres activation.
"""
import json
import os


_LICENSE_FILE = "license.json"
_ACTIVATION_KEY = "ADAM-2024-POS-UNIVERSAL"


def validate_key(key: str) -> bool:
    """Verifie la cle d'activation."""
    return key.strip().upper() == _ACTIVATION_KEY


def is_licensed(data_dir: str) -> bool:
    """Verifie si l'application est activee."""
    path = os.path.join(data_dir, _LICENSE_FILE)
    if not os.path.isfile(path):
        return False
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("activated") is True
    except Exception:
        return False


def save_license(data_dir: str):
    """Sauvegarde l'activation."""
    path = os.path.join(data_dir, _LICENSE_FILE)
    with open(path, "w") as f:
        json.dump({"key": _ACTIVATION_KEY, "activated": True}, f, indent=2)
