"""Couche de persistance : fichiers JSON dans data/ (100% local, offline)."""
import json
import os
import tempfile
from datetime import datetime


class Storage:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.tickets_dir = os.path.join(self.data_dir, "tickets")
        os.makedirs(self.tickets_dir, exist_ok=True)
        self.additions_dir = os.path.join(self.data_dir, "additions")
        os.makedirs(self.additions_dir, exist_ok=True)
        self.images_dir = os.path.join(self.data_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)

    def path(self, name: str) -> str:
        return os.path.join(self.data_dir, f"{name}.json")

    def load(self, name: str, default):
        p = self.path(name)
        if not os.path.exists(p):
            return default
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else default
        except (json.JSONDecodeError, OSError):
            # Fichier corrompu : on le sauvegarde avant de repartir propre
            try:
                os.replace(p, p + ".corrupt-" + datetime.now().strftime("%Y%m%d%H%M%S"))
            except OSError:
                pass
            return default

    def save(self, name: str, data) -> None:
        """Ecriture atomique : on ecrit dans un fichier temporaire puis on remplace."""
        p = self.path(name)
        fd, tmp = tempfile.mkstemp(dir=self.data_dir, prefix=f".{name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, p)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def exists(self, name: str) -> bool:
        return os.path.exists(self.path(name))

    @staticmethod
    def next_id(items: list) -> int:
        ids = [int(i.get("id", 0)) for i in items]
        return max(ids, default=0) + 1

    @staticmethod
    def now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def today() -> str:
        return datetime.now().strftime("%Y-%m-%d")
