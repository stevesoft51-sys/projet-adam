"""Etat global de l'application : services partages + session utilisateur."""
from .bootstrap import init_data
from .i18n import LANG_NAMES, LANGS, set_global_lang, tr
from .services import (AuthService, CatalogService, CashService, FloorPlanService,
                       OrderService, PayrollService, ReportService, RoleService,
                       SalesService, StockService, SupplierService)
from .storage import Storage


class AppState:
    def __init__(self, data_dir: str):
        self.storage = Storage(data_dir)
        init_data(self.storage)
        self.auth = AuthService(self.storage)
        self.roles = RoleService(self.storage)
        self.catalog = CatalogService(self.storage)
        self.stock = StockService(self.storage)
        self.cash = CashService(self.storage)
        self.sales = SalesService(self.storage, self.cash, self.stock)
        self.floor = FloorPlanService(self.storage)
        self.suppliers = SupplierService(self.storage, self.stock)
        self.orders = OrderService(self.storage, self.sales, self.floor)
        self.payroll = PayrollService(self.storage, self.auth)
        self.reports = ReportService(self.storage, self.stock, catalog=self.catalog,
                                     floor=self.floor, suppliers=self.suppliers,
                                     auth=self.auth)
        self.user = None
        self.lang = "fr"

    # -- langue ---------------------------------------------------------------
    @staticmethod
    def languages() -> list:
        """Langues disponibles : liste de (code, nom)."""
        return [(code, LANG_NAMES[code]) for code in LANGS]

    def tr(self, key: str, **fmt) -> str:
        return tr(self, key, **fmt)

    def set_lang(self, lang: str):
        """Definit la langue courante (state + registre global)."""
        self.lang = lang if lang in ("fr", "en", "ar") else "fr"
        set_global_lang(self.lang)
        return self.lang

    # -- parametres ---------------------------------------------------------
    @property
    def settings(self) -> dict:
        return self.storage.load("settings", {})

    def save_settings(self, data: dict):
        s = self.settings
        s.update(data)
        self.storage.save("settings", s)

    # -- session --------------------------------------------------------------
    def is_admin(self) -> bool:
        return bool(self.user) and self.user["role"] == "admin"

    def can_access(self, module: str) -> bool:
        """L'utilisateur courant peut-il voir ce module/onglet ?"""
        if not self.user:
            return False
        if self.user["role"] == "admin":
            return True
        return module in self.roles.modules_for(self.user["role"])

    def role_label(self) -> str:
        if not self.user:
            return ""
        return self.roles.label(self.user["role"])

    def logout(self):
        self.user = None
