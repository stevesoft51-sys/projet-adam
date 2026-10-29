"""Catalogues de traduction (francais / anglais / arabe) — 100% offline.

Etat global : la langue active est portee par AppState.lang.
`T(lang, key, **fmt)` renvoie la chaine traduite (et remplace {..}).
Les cles non trouvees renvoient la cle elle-meme afin de ne jamais casser l'UI.
L'arabe est rendu de droite a gauche par l'interface.
"""

LANGS = ["fr", "en", "ar"]
LANG_NAMES = {"fr": "Français", "en": "English", "ar": "العربية"}

# ---------------------------------------------------------------------------
# Traduction des cles d'unites / methodes / statuts stockes en base (donnees
# utilisateur, donc gardees dans la langue saisie) — ces valeurs sont du DATA,
# pas de l'UI : on ne les traduit pas. Seul le libelle d'interface l'est.
# ---------------------------------------------------------------------------

L = {
    # ------------------------------------------------------------- connexion --
    "app.subtitle": {
        "fr": "Point de Vente & Gestion",
        "en": "Point of Sale & Management",
        "ar": "نقطة البيع والإدارة",
    },
    "login.title": {
        "fr": "Connexion",
        "en": "Sign in",
        "ar": "تسجيل الدخول",
    },
    "login.username": {
        "fr": "Identifiant",
        "en": "Username",
        "ar": "اسم المستخدم",
    },
    "login.password": {
        "fr": "Mot de passe",
        "en": "Password",
        "ar": "كلمة المرور",
    },
    "login.language": {
        "fr": "Langue",
        "en": "Language",
        "ar": "اللغة",
    },
    "login.submit": {
        "fr": "Se connecter",
        "en": "Sign in",
        "ar": "تسجيل الدخول",
    },
    "login.bad_credentials": {
        "fr": "Identifiant ou mot de passe incorrect.",
        "en": "Incorrect username or password.",
        "ar": "اسم المستخدم أو كلمة المرور غير صحيحة.",
    },
    "login.blocked": {
        "fr": "Ce compte est bloqué.\nContactez l'administrateur du restaurant.",
        "en": "This account is blocked.\nContact the restaurant administrator.",
        "ar": "هذا الحساب محظور.\nاتصل بمدير المطعم.",
    },
    "role.admin": {"fr": "Administrateur", "en": "Administrator", "ar": "مدير"},
    "role.caissiere": {"fr": "Caissière", "en": "Cashier", "ar": "أمين الصندوق"},

    # ------------------------------------------------------------ activation --
    "act.title": {
        "fr": "Activation",
        "en": "Activation",
        "ar": "التفعيل",
    },
    "act.prompt": {
        "fr": "Saisissez votre clé d'activation pour débloquer l'application.",
        "en": "Enter your activation key to unlock the application.",
        "ar": "أدخل مفتاح التفعيل لفتح التطبيق.",
    },
    "act.key_label": {"fr": "Clé d'activation", "en": "Activation key", "ar": "مفتاح التفعيل"},
    "act.activate": {"fr": "Activer", "en": "Activate", "ar": "تفعيل"},
    "act.invalid": {
        "fr": "Clé d'activation invalide.",
        "en": "Invalid activation key.",
        "ar": "مفتاح التفعيل غير صالح.",
    },
    "act.success": {
        "fr": "Application activée avec succès.",
        "en": "Application activated successfully.",
        "ar": "تم تفعيل التطبيق بنجاح.",
    },

    # ------------------------------------------------------------- fenetre --
    "main.title": {"fr": "Restaurant ADAM — Gestion", "en": "Restaurant ADAM — Management", "ar": "مطعم آدم — الإدارة"},
    "main.logout": {"fr": "Déconnexion", "en": "Log out", "ar": "تسجيل الخروج"},
    "main.confirm_logout": {
        "fr": "Voulez-vous vous déconnecter ?",
        "en": "Do you want to log out?",
        "ar": "هل تريد تسجيل الخروج؟",
    },
    "main.error_display": {"fr": "Erreur d'affichage : {err}", "en": "Display error: {err}", "ar": "خطأ في العرض: {err}"},

    # -------------------------------------------------------------- onglets --
    "tab.dashboard": {"fr": "Tableau de bord", "en": "Dashboard", "ar": "لوحة التحكم"},
    "tab.pos": {"fr": "Point de vente", "en": "Point of Sale", "ar": "نقطة البيع"},
    "tab.cash": {"fr": "Caisse", "en": "Cash Register", "ar": "الصندوق"},
    "tab.floor": {"fr": "Plan de salle", "en": "Floor Plan", "ar": "خريطة القاعة"},
    "tab.menu": {"fr": "Menu", "en": "Menu", "ar": "القائمة"},
    "tab.stock": {"fr": "Stocks", "en": "Stock", "ar": "المخزون"},
    "tab.suppliers": {"fr": "Fournisseurs", "en": "Suppliers", "ar": "الموردون"},
    "tab.staff": {"fr": "Personnel", "en": "Staff", "ar": "الموظفون"},

    # ----------------------------------------------------------------- POS --
    "pos.service": {"fr": "Mode de service", "en": "Service mode", "ar": "نوع الخدمة"},
    "pos.dine_in": {"fr": "Sur place", "en": "Dine-in", "ar": "في الداخل"},
    "pos.takeaway": {"fr": "À emporter", "en": "Takeaway", "ar": "للتوصيل"},
    "pos.table": {"fr": "Table", "en": "Table", "ar": "طاولة"},
    "pos.cart": {"fr": "Panier", "en": "Cart", "ar": "السلة"},
    "pos.search": {"fr": "Rechercher un produit…", "en": "Search a product…", "ar": "ابحث عن منتج…"},
    "pos.add": {"fr": "Ajouter", "en": "Add", "ar": "إضافة"},
    "pos.qty": {"fr": "Qté", "en": "Qty", "ar": "الكمية"},
    "pos.remove": {"fr": "Retirer", "en": "Remove", "ar": "إزالة"},
    "pos.clear": {"fr": "Vider", "en": "Clear", "ar": "مسح"},
    "pos.total": {"fr": "Total", "en": "Total", "ar": "المجموع"},
    "pos.pay": {"fr": "Payer", "en": "Pay", "ar": "الدفع"},
    "pos.empty_cart": {"fr": "Le panier est vide.", "en": "The cart is empty.", "ar": "السلة فارغة."},
    "pos.choose_service": {
        "fr": "Choisissez le mode de service (Sur place / À emporter).",
        "en": "Choose the service mode (Dine-in / Takeaway).",
        "ar": "اختر نوع الخدمة (في الداخل / للتوصيل).",
    },
    "pos.choose_table": {
        "fr": "Sélectionnez la table pour le service sur place.",
        "en": "Select a table for dine-in service.",
        "ar": "اختر الطاولة للخدمة في الداخل.",
    },
    "pos.no_table_free": {
        "fr": "Aucune table libre n'est sélectionnée.",
        "en": "No free table is selected.",
        "ar": "لا توجد طاولة حرة محددة.",
    },
    "pos.out_of_stock": {
        "fr": "Stock insuffisant pour « {name} » (disponible : {qty}).",
        "en": "Insufficient stock for « {name} » (available: {qty}).",
        "ar": "المخزون غير كافٍ لـ « {name} » (المتاح: {qty}).",
    },
    "pos.payment": {"fr": "Paiement", "en": "Payment", "ar": "الدفع"},
    "pos.pay_confirm": {
        "fr": "Confirmer la vente de {total} ?",
        "en": "Confirm the sale of {total}?",
        "ar": "تأكيد بيع {total}؟",
    },
    "pos.success": {"fr": "Vente enregistrée.", "en": "Sale recorded.", "ar": "تم تسجيل البيع."},
    "pos.cash": {"fr": "Espèces", "en": "Cash", "ar": "نقدًا"},
    "pos.mobile": {"fr": "Mobile Money", "en": "Mobile Money", "ar": "المال عبر الهاتف"},
    "pos.mixed": {"fr": "Paiement mixte", "en": "Mixed payment", "ar": "دفع مختلط"},
    "pos.cash_part": {"fr": "Part espèces", "en": "Cash part", "ar": "الجزء النقدي"},
    "pos.mobile_part": {"fr": "Part Mobile Money", "en": "Mobile Money part", "ar": "جزء الموبايل"},
    "pos.mixed_not_equal": {
        "fr": "Espèces + Mobile Money doivent égaler le total.",
        "en": "Cash + Mobile Money must equal the total.",
        "ar": "يجب أن يساوي النقدي + الموبايل المجموع.",
    },
    "pos.unit": {"fr": "Table", "en": "Unit", "ar": "الوحدة"},

    # ------------------------------------------------------------- caisse --
    "cash.title": {"fr": "Caisse", "en": "Cash Register", "ar": "الصندوق"},
    "cash.open": {"fr": "Ouvrir la caisse", "en": "Open the register", "ar": "فتح الصندوق"},
    "cash.close": {"fr": "Fermer la caisse", "en": "Close the register", "ar": "إغلاق الصندوق"},
    "cash.session_open": {"fr": "Caisse ouverte", "en": "Register open", "ar": "الصندوق مفتوح"},
    "cash.session_closed": {"fr": "Caisse fermée", "en": "Register closed", "ar": "الصندوق مغلق"},
    "cash.opening_balance": {"fr": "Fond de caisse", "en": "Opening balance", "ar": "الرصيد الافتتاحي"},
    "cash.total_in": {"fr": "Total entrées", "en": "Total in", "ar": "إجمالي الداخل"},
    "cash.total_out": {"fr": "Total sorties", "en": "Total out", "ar": "إجمالي الخارج"},
    "cash.expected": {"fr": "Attendu en caisse", "en": "Expected in register", "ar": "المتوقع في الصندوق"},
    "cash.movements": {"fr": "Mouvements", "en": "Movements", "ar": "الحركات"},
    "cash.add_in": {"fr": "Entrée", "en": "Cash in", "ar": "دخول"},
    "cash.add_out": {"fr": "Sortie", "en": "Cash out", "ar": "خروج"},
    "cash.amount": {"fr": "Montant", "en": "Amount", "ar": "المبلغ"},
    "cash.reason": {"fr": "Motif", "en": "Reason", "ar": "السبب"},
    "cash.type": {"fr": "Type", "en": "Type", "ar": "النوع"},
    "cash.date": {"fr": "Date", "en": "Date", "ar": "التاريخ"},
    "cash.user": {"fr": "Par", "en": "By", "ar": "بواسطة"},
    "cash.already_open": {"fr": "Une caisse est déjà ouverte.", "en": "A register is already open.", "ar": "الصندوق مفتوح بالفعل."},
    "cash.no_open": {"fr": "Aucune caisse n'est ouverte.", "en": "No register is open.", "ar": "لا يوجد صندوق مفتوح."},
    "cash.sales_count": {"fr": "{n} ventes", "en": "{n} sales", "ar": "{n} عملية بيع"},
    "cash.error_close_low": {
        "fr": "Le total attendu ne peut pas être négatif : les sorties dépassent le fond + les entrées.",
        "en": "The expected total cannot be negative: withdrawals exceed the float plus deposits.",
        "ar": "لا يمكن أن يكون الإجمالي المتوقع سالبًا: السحوبات تتجاوز الافتتاحي + الإيداعات.",
    },

    # --------------------------------------------------------- plan salle --
    "floor.title": {"fr": "Plan de salle", "en": "Floor Plan", "ar": "خريطة القاعة"},
    "floor.add_table": {"fr": "Ajouter une table", "en": "Add a table", "ar": "إضافة طاولة"},
    "floor.add_boucaro": {"fr": "Ajouter un boucaro", "en": "Add a boucaro", "ar": "إضافة بوكارو"},
    "floor.name": {"fr": "Nom / Numéro", "en": "Name / Number", "ar": "الاسم / الرقم"},
    "floor.kind": {"fr": "Type", "en": "Type", "ar": "النوع"},
    "floor.table": {"fr": "Table", "en": "Table", "ar": "طاولة"},
    "floor.boucaro": {"fr": "Boucaro", "en": "Boucaro", "ar": "بوكارو"},
    "floor.seats": {"fr": "Places", "en": "Seats", "ar": "المقاعد"},
    "floor.free": {"fr": "Libre", "en": "Free", "ar": "حرة"},
    "floor.occupied": {"fr": "Occupée", "en": "Occupied", "ar": "مشغولة"},
    "floor.reserved": {"fr": "Réservée", "en": "Reserved", "ar": "محجوزة"},
    "floor.status": {"fr": "Statut", "en": "Status", "ar": "الحالة"},
    "floor.set_free": {"fr": "Libérer", "en": "Free up", "ar": "تحرير"},
    "floor.set_reserved": {"fr": "Réserver", "en": "Reserve", "ar": "حجز"},
    "floor.delete": {"fr": "Supprimer", "en": "Delete", "ar": "حذف"},
    "floor.delete_confirm": {
        "fr": "Supprimer définitivement « {name} » ?",
        "en": "Permanently delete « {name} »?",
        "ar": "حذف « {name} » نهائيًا؟",
    },
    "floor.no_name": {"fr": "Le nom/numéro est obligatoire.", "en": "The name/number is required.", "ar": "الاسم/الرقم مطلوب."},
    "floor.invalid_seats": {"fr": "Nombre de places invalide.", "en": "Invalid number of seats.", "ar": "عدد المقاعد غير صالح."},
    "floor.zone": {"fr": "Zone", "en": "Zone", "ar": "المنطقة"},

    # ------------------------------------------------------------- menu --
    "menu.title": {"fr": "Menu & produits", "en": "Menu & Products", "ar": "القائمة والمنتجات"},
    "menu.add": {"fr": "Ajouter un produit", "en": "Add a product", "ar": "إضافة منتج"},
    "menu.edit": {"fr": "Modifier", "en": "Edit", "ar": "تعديل"},
    "menu.delete": {"fr": "Supprimer", "en": "Delete", "ar": "حذف"},
    "menu.name": {"fr": "Nom", "en": "Name", "ar": "الاسم"},
    "menu.price": {"fr": "Prix", "en": "Price", "ar": "السعر"},
    "menu.category": {"fr": "Catégorie", "en": "Category", "ar": "الفئة"},
    "menu.available": {"fr": "Disponible", "en": "Available", "ar": "متاح"},
    "menu.hidden": {"fr": "Caché", "en": "Hidden", "ar": "مخفي"},
    "menu.image": {"fr": "Image", "en": "Image", "ar": "الصورة"},
    "menu.delete_confirm": {
        "fr": "Supprimer « {name} » ? Les recettes liées seront aussi supprimées.",
        "en": "Delete « {name} »? Linked recipes will also be deleted.",
        "ar": "حذف « {name} »؟ سيتم حذف الوصفات المرتبطة أيضًا.",
    },
    "menu.no_name": {"fr": "Le nom du produit est obligatoire.", "en": "The product name is required.", "ar": "اسم المنتج مطلوب."},
    "menu.no_price": {"fr": "Le prix doit être positif.", "en": "The price must be positive.", "ar": "يجب أن يكون السعر موجبًا."},
    "menu.recipe": {"fr": "Recette", "en": "Recipe", "ar": "الوصفة"},
    "menu.recipe_empty": {"fr": "(aucun ingrédient)", "en": "(no ingredient)", "ar": "(لا مكونات)"},

    # ---------------------------------------------------------- stock --
    "stock.title": {"fr": "Stocks", "en": "Stock", "ar": "المخزون"},
    "stock.add_ing": {"fr": "Ajouter un ingrédient", "en": "Add an ingredient", "ar": "إضافة مكون"},
    "stock.ing_name": {"fr": "Ingrédient", "en": "Ingredient", "ar": "المكون"},
    "stock.unit": {"fr": "Unité", "en": "Unit", "ar": "الوحدة"},
    "stock.qty": {"fr": "Stock", "en": "Stock", "ar": "المخزون"},
    "stock.min_stock": {"fr": "Seuil min.", "en": "Min. level", "ar": "الحد الأدنى"},
    "stock.cost": {"fr": "Coût", "en": "Cost", "ar": "التكلفة"},
    "stock.status": {"fr": "Statut", "en": "Status", "ar": "الحالة"},
    "stock.low": {"fr": "Bas", "en": "Low", "ar": "منخفض"},
    "stock.ok": {"fr": "OK", "en": "OK", "ar": "جيد"},
    "stock.out": {"fr": "Rupture", "en": "Out of stock", "ar": "نفد"},
    "stock.move": {"fr": "Mouvement", "en": "Movement", "ar": "حركة"},
    "stock.movements": {"fr": "Mouvements", "en": "Movements", "ar": "الحركات"},
    "stock.in": {"fr": "Entrée", "en": "In", "ar": "إدخال"},
    "stock.out_move": {"fr": "Sortie", "en": "Out", "ar": "إخراج"},
    "stock.adjust": {"fr": "Ajustement", "en": "Adjustment", "ar": "تسوية"},
    "stock.type": {"fr": "Type", "en": "Type", "ar": "النوع"},

    # ------------------------------------------------------- fournisseurs --
    "sup.title": {"fr": "Fournisseurs", "en": "Suppliers", "ar": "الموردون"},
    "sup.add": {"fr": "Ajouter un fournisseur", "en": "Add a supplier", "ar": "إضافة مورد"},
    "sup.name": {"fr": "Nom", "en": "Name", "ar": "الاسم"},
    "sup.phone": {"fr": "Téléphone", "en": "Phone", "ar": "الهاتف"},
    "sup.address": {"fr": "Adresse", "en": "Address", "ar": "العنوان"},
    "sup.products": {"fr": "Produits", "en": "Products", "ar": "المنتجات"},
    "sup.debt": {"fr": "Dette", "en": "Debt", "ar": "الديون"},
    "sup.delivery": {"fr": "Livraison", "en": "Delivery", "ar": "تسليم"},
    "sup.receive": {"fr": "Réceptionner", "en": "Receive", "ar": "استلام"},
    "sup.qty_bought": {"fr": "Qté achetée", "en": "Quantity bought", "ar": "الكمية المشتراة"},
    "sup.purchase_unit": {"fr": "Unité d'achat", "en": "Purchase unit", "ar": "وحدة الشراء"},
    "sup.pieces": {"fr": "Pièces en stock", "en": "Pieces in stock", "ar": "القطع في المخزون"},
    "sup.purchase_price": {"fr": "Prix d'achat", "en": "Purchase price", "ar": "سعر الشراء"},
    "sup.save": {"fr": "Enregistrer", "en": "Save", "ar": "حفظ"},
    "sup.store": {"fr": "Comptoir", "en": "Store", "ar": "المتجر"},

    # ------------------------------------------------------- personnel --
    "staff.title": {"fr": "Personnel & salaires", "en": "Staff & Payroll", "ar": "الموظفون والرواتب"},
    "staff.add": {"fr": "Ajouter un employé", "en": "Add an employee", "ar": "إضافة موظف"},
    "staff.edit": {"fr": "Modifier", "en": "Edit", "ar": "تعديل"},
    "staff.name": {"fr": "Nom complet", "en": "Full name", "ar": "الاسم الكامل"},
    "staff.username": {"fr": "Identifiant", "en": "Username", "ar": "اسم المستخدم"},
    "staff.role": {"fr": "Rôle", "en": "Role", "ar": "الدور"},
    "staff.salary": {"fr": "Salaire", "en": "Salary", "ar": "الراتب"},
    "staff.status": {"fr": "Statut", "en": "Status", "ar": "الحالة"},
    "staff.active": {"fr": "Actif", "en": "Active", "ar": "نشط"},
    "staff.blocked": {"fr": "Bloqué", "en": "Blocked", "ar": "محظور"},
    "staff.password": {"fr": "Mot de passe", "en": "Password", "ar": "كلمة المرور"},
    "staff.advance": {"fr": "Avance", "en": "Advance", "ar": "سلفة"},
    "staff.pay_salary": {"fr": "Verser le salaire", "en": "Pay salary", "ar": "صرف الراتب"},
    "staff.movements": {"fr": "Mouvements de salaires", "en": "Salary movements", "ar": "حركات الرواتب"},
    "staff.paid": {"fr": "Payé", "en": "Paid", "ar": "مدفوع"},
    "staff.net": {"fr": "Solde à verser", "en": "Balance to pay", "ar": "الرصيد المستحق"},
    "staff.manage_roles": {"fr": "Gérer les rôles", "en": "Manage roles", "ar": "إدارة الأدوار"},
    "staff.month": {"fr": "Mois", "en": "Month", "ar": "الشهر"},
    "staff.employees": {"fr": "Employés", "en": "Employees", "ar": "الموظفون"},
    "staff.accounts_active": {"fr": "Comptes actifs", "en": "Active accounts", "ar": "حسابات نشطة"},
    "staff.accounts_blocked": {"fr": "Comptes bloqués", "en": "Blocked accounts", "ar": "حسابات محظورة"},
    "staff.advances_month": {"fr": "Avances du mois", "en": "Advances this month", "ar": "سلف هذا الشهر"},
    "staff.paid_month": {"fr": "Payé ce mois", "en": "Paid this month", "ar": "المدفوع هذا الشهر"},
    "staff.net_month": {"fr": "Net à verser", "en": "Net to pay", "ar": "صافي المطلوب"},

    # ----------------------------------------------------- dashboard --
    "dash.today": {"fr": "Tableau de bord", "en": "Dashboard", "ar": "لوحة التحكم"},
    "dash.reports_yesterday": {
        "fr": "📅 Rapports d'hier",
        "en": "📅 Yesterday's reports",
        "ar": "📅 تقارير الأمس",
    },

    # ------------------------------------------------------- divers --
    "common.cancel": {"fr": "Annuler", "en": "Cancel", "ar": "إلغاء"},
    "cal.title": {"fr": "Choisir une date", "en": "Pick a date", "ar": "اختر تاريخًا"},
    "cal.weekdays": {"fr": "Lu|Ma|Me|Je|Ve|Sa|Di",
                     "en": "Mo|Tu|We|Th|Fr|Sa|Su",
                     "ar": "الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت|الأحد"},
    "cal.months": {"fr": "Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Octobre|Novembre|Décembre",
                   "en": "January|February|March|April|May|June|July|August|September|October|November|December",
                   "ar": "يناير|فبراير|مارس|أبريل|مايو|يونيو|يوليو|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر"},
    "common.save": {"fr": "Enregistrer", "en": "Save", "ar": "حفظ"},
    "common.validate": {"fr": "Valider", "en": "Validate", "ar": "تأكيد"},
    "common.required": {"fr": "Champ obligatoire.", "en": "This field is required.", "ar": "هذا الحقل مطلوب."},
    "common.invalid_number": {
        "fr": "Montant invalide. Veuillez saisir un nombre valide.",
        "en": "Invalid amount. Please enter a valid number.",
        "ar": "مبلغ غير صالح. الرجاء إدخال رقم صحيح.",
    },
    "common.confirm_title": {"fr": "Confirmation", "en": "Confirmation", "ar": "تأكيد"},
    "common.info_title": {"fr": "Information", "en": "Information", "ar": "معلومات"},
    "common.error_title": {"fr": "Erreur", "en": "Error", "ar": "خطأ"},
    "common.not_selected": {"fr": "Sélectionnez un élément dans la liste.", "en": "Select an item in the list.", "ar": "حدد عنصرًا من القائمة."},
}


# ---------------------------------------------------------------------------
# Fusion des catalogues des vues (i18n_extra_*) dans le catalogue principal.
# ---------------------------------------------------------------------------
def _build_cache():
    cache = dict(L)
    from . import i18n_extra_pos, i18n_extra_views, i18n_extra_staff
    for mod in (i18n_extra_pos, i18n_extra_views, i18n_extra_staff):
        for k, v in mod.collect().items():
            cache[k] = v
    return cache


_CACHE = _build_cache()


def T(lang: str, key: str, **fmt) -> str:
    """Renvoie la traduction de `key` pour `lang`, remplace {..} si fourni."""
    entry = _CACHE.get(key)
    if not entry:
        return key
    val = entry.get(lang) or entry.get("fr") or key
    if fmt:
        try:
            return val.format(**fmt)
        except (KeyError, IndexError, ValueError):
            return val
    return val


def is_rtl(lang: str) -> bool:
    """L'arabe s'affiche de droite a gauche."""
    return lang == "ar"


def tr(state, key: str, **fmt) -> str:
    """Couche pratique : traduit selon la langue portee par state."""
    lang = getattr(state, "lang", None) or "fr"
    return T(lang, key, **fmt)


# ---------------------------------------------------------------------------
# Langue globale courante (pour les helpers sans acces direct a `state`,
# ex : boites de dialogue de widgets.py). Mise a jour par login/main.
# ---------------------------------------------------------------------------
_global_lang = ["fr"]


def set_global_lang(lang: str):
    if lang in ("fr", "en", "ar"):
        _global_lang[0] = lang
    return _global_lang[0]


def global_lang() -> str:
    return _global_lang[0]


def TGlobal(key: str, **fmt) -> str:
    """Traduit via la langue globale courante (helpers widgets)."""
    return T(_global_lang[0], key, **fmt)
