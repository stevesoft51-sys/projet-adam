"""Miniatures d'images produits, mises en cache.

Le cache conserve la reference des PhotoImage : sans cela, Tk les
detruit des que Python garbage-collecte l'objet.
"""
import os

try:
    from PIL import Image, ImageTk
    HAVE_PIL = True
except ImportError:          # l'app reste utilisable sans Pillow
    HAVE_PIL = False

_cache = {}


def clear_cache():
    """Vide le cache PhotoImage — a appeler a chaque nouvelle session Tk."""
    _cache.clear()


def load_thumb(path, size):
    """Retourne une PhotoImage carree reduite a `size` px max, ou None.

    `path` est le chemin complet du fichier image.
    """
    if not path or not HAVE_PIL:
        return None
    try:
        path = str(path)
        mtime = os.path.getmtime(path)
    except OSError:
        return None
    key = (path, int(size), mtime)
    if key not in _cache:
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((int(size), int(size)))
            _cache[key] = ImageTk.PhotoImage(img)
        except Exception:
            _cache[key] = None
    return _cache[key]
