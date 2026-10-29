"""Generation de rapports PDF (caisse, stock, fournisseurs, ventes).

Utilise fpdf2 + police Unicode DejaVu pour le support accents/emojis.
Format A4 — chaque rapport tient dans un format A4.
"""
import os
import sys
from datetime import datetime, timedelta

from fpdf import FPDF

from .services import PAYMENT_METHODS, period_range

_FONT = "DejaVu"


def _font_dir():
    """Chemin vers le dossier fonts/ — fonctionne depuis la source et depuis l'exe."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "fonts")

_W = 190  # largeur utile A4 (210 - 2*10 marges)


class _ReportPDF(FPDF):
    """Base commune pour tous les rapports."""

    def __init__(self, title, restaurant_name="", address="", phone=""):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        fd = _font_dir()
        self.add_font(_FONT, "", os.path.join(fd, "DejaVuSans.ttf"),
                      uni=True)
        self.add_font(_FONT, "B",
                      os.path.join(fd, "DejaVuSans-Bold.ttf"),
                      uni=True)
        self.add_font(_FONT, "I",
                      os.path.join(fd, "DejaVuSans-Oblique.ttf"),
                      uni=True)
        self._title = title
        self._resto = restaurant_name
        self._addr = address
        self._phone = phone

    def header(self):
        self.set_font(_FONT, "B", 14)
        self.cell(0, 7, self._resto.upper(), new_x="LMARGIN", new_y="NEXT",
                  align="C")
        if self._addr:
            self.set_font(_FONT, "", 7)
            self.cell(0, 3.5, self._addr, new_x="LMARGIN", new_y="NEXT",
                      align="C")
        if self._phone:
            self.set_font(_FONT, "", 7)
            self.cell(0, 3.5, "Tel : " + self._phone,
                      new_x="LMARGIN", new_y="NEXT", align="C")
        self.line(10, self.get_y() + 1.5, 200, self.get_y() + 1.5)
        self.ln(4)
        self.set_font(_FONT, "B", 11)
        self.cell(0, 6, self._title, new_x="LMARGIN", new_y="NEXT",
                  align="C")
        self.set_font(_FONT, "", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, datetime.now().strftime("Généré le %d/%m/%Y à %H:%M"),
                  new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font(_FONT, "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section(self, title):
        self.set_font(_FONT, "B", 10)
        self.set_fill_color(236, 229, 212)
        self.cell(0, 6, "  " + title, new_x="LMARGIN", new_y="NEXT",
                  fill=True)
        self.ln(1.5)

    def table_header(self, cols):
        self.set_font(_FONT, "B", 8)
        self.set_fill_color(236, 229, 212)
        for label, w, align in cols:
            self.cell(w, 5.5, label, border=1, align=align, fill=True)
        self.ln()

    def table_row(self, values, cols, bold=False):
        style = "B" if bold else ""
        self.set_font(_FONT, style, 8)
        for (val, (_, w, align)) in zip(values, cols):
            self.cell(w, 5, str(val), border=1, align=align)
        self.ln()

    def kv_line(self, key, value, bold_value=False):
        self.set_font(_FONT, "", 9)
        self.cell(70, 5, key)
        style = "B" if bold_value else ""
        self.set_font(_FONT, style, 9)
        self.cell(0, 5, str(value), new_x="LMARGIN", new_y="NEXT")

    def money(self, amount):
        return f"{amount:,.0f} F".replace(",", " ")


# -------------------------------------------------------------------- helpers --

def _settings_path(state):
    s = state.settings
    return (s.get("restaurant_name") or "Restaurant ADAM",
            s.get("address") or "", s.get("phone") or "")


def _ensure_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(base, "reports")
    os.makedirs(d, exist_ok=True)
    return d


def _pdf_path(label):
    d = _ensure_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(d, f"{label}_{ts}.pdf")


# ============================================================ RAPPORT VENTES --
def rapport_ventes(state, period="Jour") -> str:
    """Rapport de ventes groupé par catégorie — format A4."""
    resto, addr, phone = _settings_path(state)
    start, end = period_range(period)
    start_s = start.strftime("%Y-%m-%d %H:%M:%S")
    end_s = end.strftime("%Y-%m-%d %H:%M:%S")

    pdf = _ReportPDF(f"Rapport de ventes — {period}", resto, addr, phone)
    pdf.alias_nb_pages()
    pdf.add_page()

    sales = [s for s in state.sales.sales()
             if start_s <= s["datetime"] < end_s]

    pdf.set_font(_FONT, "", 9)
    pdf.cell(0, 5, f"Période : {start.strftime('%d/%m/%Y')} — "
                    f"{end.strftime('%d/%m/%Y')}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # résumé global
    total = sum(s["total"] for s in sales)
    discounts = sum(s.get("discount", 0) for s in sales)
    pdf.section("Résumé")
    pdf.kv_line("Nombre de ventes", len(sales))
    pdf.kv_line("Chiffre d'affaires", pdf.money(total), True)
    pdf.kv_line("Remises appliquées", pdf.money(discounts))
    pdf.kv_line("Panier moyen",
                pdf.money(total / len(sales)) if sales else "0 F")

    # par mode de paiement
    by_method = {}
    for s in sales:
        m = s["method"]
        by_method[m] = by_method.get(m, 0) + s["total"]
    if by_method:
        pdf.ln(1)
        pdf.section("Répartition par mode de paiement")
        mcols = [("Mode", 60, "L"), ("Montant", 45, "R"),
                 ("Part", 30, "R")]
        pdf.table_header(mcols)
        for m, amt in sorted(by_method.items(),
                             key=lambda x: x[1], reverse=True):
            pct = amt / total * 100 if total else 0
            pdf.table_row([
                PAYMENT_METHODS.get(m, m),
                pdf.money(amt),
                f"{pct:.1f} %"], mcols)

    # regrouper les items par catégorie
    cats_map = {c["id"]: c["name"] for c in state.catalog.categories()}
    prod_map = {}
    for p in state.catalog.products():
        prod_map[p["id"]] = p

    cat_data = {}  # cat_name -> {items: {name: {qty, price, total}}, qty, rev}
    for s in sales:
        for it in s["items"]:
            pid = it.get("product_id")
            prod = prod_map.get(pid)
            cat_id = prod["category_id"] if prod else None
            cat_name = cats_map.get(cat_id, "Autre") if cat_id else "Autre"
            if cat_name not in cat_data:
                cat_data[cat_name] = {"items": {}, "qty": 0, "rev": 0}
            name = it["name"]
            if name not in cat_data[cat_name]["items"]:
                cat_data[cat_name]["items"][name] = {
                    "qty": 0, "price": it.get("price", 0), "total": 0}
            cat_data[cat_name]["items"][name]["qty"] += it["qty"]
            cat_data[cat_name]["items"][name]["total"] += it["total"]
            cat_data[cat_name]["qty"] += it["qty"]
            cat_data[cat_name]["rev"] += it["total"]

    # un tableau par catégorie
    for cat_name in sorted(cat_data.keys()):
        cd = cat_data[cat_name]
        pdf.add_page()
        pdf.section(f"{cat_name}  ({cd['qty']} plats vendus)")

        tcols = [("Plat", 60, "L"), ("Qté", 18, "C"),
                 ("Prix unit.", 32, "R"), ("Total", 32, "R")]
        pdf.table_header(tcols)

        for pname, pd in sorted(cd["items"].items(),
                                key=lambda x: x[1]["total"], reverse=True):
            pdf.table_row([
                pname[:35],
                f"{pd['qty']:g}",
                pdf.money(pd["price"]),
                pdf.money(pd["total"])], tcols)

        # sous-total catégorie
        pdf.table_row(["", "", "SOUS-TOTAL", pdf.money(cd["rev"])],
                      tcols, bold=True)

    # total général
    if cat_data:
        pdf.ln(3)
        pdf.set_font(_FONT, "B", 10)
        pdf.set_fill_color(236, 229, 212)
        pdf.cell(0, 7, f"  TOTAL GÉNÉRAL : {pdf.money(total)}",
                 new_x="LMARGIN", new_y="NEXT", fill=True)

    path = _pdf_path("rapport_ventes")
    pdf.output(path)
    return path


# ============================================================ RAPPORT CAISSE --
def rapport_casse(state, period="Jour") -> str:
    """Rapport de caisse — un tableau par manipulateur de caisse. Format A4."""
    resto, addr, phone = _settings_path(state)
    start, end = period_range(period)
    start_s = start.strftime("%Y-%m-%d %H:%M:%S")
    end_s = end.strftime("%Y-%m-%d %H:%M:%S")

    pdf = _ReportPDF(f"Rapport de caisse — {period}", resto, addr, phone)
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font(_FONT, "", 9)
    pdf.cell(0, 5, f"Période : {start.strftime('%d/%m/%Y')} — "
                    f"{end.strftime('%d/%m/%Y')}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    sessions = [c for c in state.cash.sessions()
                if c["opened_at"] < end_s
                and (not c.get("closed_at")
                     or c["closed_at"] >= start_s)]

    # regrouper les mouvements par personne
    person_data = {}  # person -> {in, out, sales, sessions}
    for sess in sessions:
        opened_by = sess.get("opened_by", "—")
        closed_by = sess.get("closed_by")
        if opened_by not in person_data:
            person_data[opened_by] = {"in": 0, "out": 0, "sales": 0,
                                      "sessions": [], "closed_by": {}}
        person_data[opened_by]["sessions"].append(sess)

        for m in sess.get("movements", []):
            if not (start_s <= m["at"] < end_s):
                continue
            actor = m.get("by", opened_by)
            if actor not in person_data:
                person_data[actor] = {"in": 0, "out": 0, "sales": 0,
                                      "sessions": [], "closed_by": {}}
            if m["type"] == "in":
                person_data[actor]["in"] += m["amount"]
            elif m["type"] == "out":
                person_data[actor]["out"] += m["amount"]
            elif m["type"] == "sale":
                person_data[actor]["sales"] += m["amount"]

    # résumé global
    total_in = sum(p["in"] for p in person_data.values())
    total_out = sum(p["out"] for p in person_data.values())
    total_sales = sum(p["sales"] for p in person_data.values())

    pdf.section("Résumé global")
    pdf.kv_line("Nombre de sessions", len(sessions))
    pdf.kv_line("Entrées manuelles", pdf.money(total_in))
    pdf.kv_line("Sorties manuelles", pdf.money(total_out))
    pdf.kv_line("Ventes en espèces", pdf.money(total_sales), True)
    pdf.kv_line("Total mouvements",
                pdf.money(total_in + total_sales - total_out))

    # un tableau par personne
    for person in sorted(person_data.keys()):
        pd = person_data[person]
        pdf.add_page()
        pdf.section(f"Manipulateur : {person}")

        # sessions de cette personne
        my_sessions = pd["sessions"]
        if my_sessions:
            scols = [("Ouverture", 25, "C"), ("Fermeture", 25, "C"),
                     ("Fond", 30, "R"), ("Attendu", 30, "R"),
                     ("Obtenu", 30, "R"), ("Manquant", 30, "R")]
            pdf.table_header(scols)
            for sess in my_sessions:
                expected = state.cash.expected_amount(sess) \
                    if sess["status"] == "closed" else None
                obtained = sess.get("closing_counted")
                missing = None
                if expected is not None and obtained is not None:
                    missing = round(obtained - expected, 2)
                pdf.table_row([
                    sess["opened_at"][11:16],
                    (sess.get("closed_at") or "—")[11:16]
                    if sess.get("closed_at") else "—",
                    pdf.money(sess["opening_amount"]),
                    pdf.money(expected) if expected is not None else "—",
                    pdf.money(obtained) if obtained is not None else "—",
                    pdf.money(missing) if missing is not None else "—"],
                    scols)

        # détail des mouvements de cette personne
        pdf.ln(2)
        pdf.section("Détail des mouvements")
        mcols = [("Type", 30, "L"), ("Montant", 35, "R"),
                 ("Motif", 60, "L"), ("Heure", 25, "C")]
        pdf.table_header(mcols)

        # collecter tous les mouvements de cette personne
        all_moves = []
        for sess in my_sessions:
            for m in sess.get("movements", []):
                if m.get("by", sess.get("opened_by")) == person \
                        and start_s <= m["at"] < end_s:
                    all_moves.append(m)

        if not all_moves:
            pdf.set_font(_FONT, "I", 8)
            pdf.cell(0, 5, "Aucun mouvement enregistré.",
                     new_x="LMARGIN", new_y="NEXT")
        else:
            for m in sorted(all_moves, key=lambda x: x["at"]):
                type_label = {"in": "Entrée", "out": "Sortie",
                              "sale": "Vente"}[m["type"]]
                pdf.table_row([
                    type_label,
                    pdf.money(m["amount"]),
                    m.get("reason", "—")[:35],
                    m["at"][11:16]], mcols)

            # sous-totaux
            pdf.table_row(["Entrées", pdf.money(pd["in"]), "", ""],
                          mcols, bold=True)
            pdf.table_row(["Sorties", pdf.money(pd["out"]), "", ""],
                          mcols, bold=True)
            pdf.table_row(["Ventes", pdf.money(pd["sales"]), "", ""],
                          mcols, bold=True)
            net = pd["in"] + pd["sales"] - pd["out"]
            pdf.table_row(["NET", pdf.money(net), "", ""],
                          mcols, bold=True)

    path = _pdf_path("rapport_caisse")
    pdf.output(path)
    return path


# ================================================================ RAPPORT STOCK --
def rapport_stock(state, period="Jour") -> str:
    """Rapport de stock — ruptures et en voie de rupture. Format A4."""
    resto, addr, phone = _settings_path(state)
    start, end = period_range(period)
    start_s = start.strftime("%Y-%m-%d %H:%M:%S")
    end_s = end.strftime("%Y-%m-%d %H:%M:%S")

    pdf = _ReportPDF(f"Rapport de stock — {period}", resto, addr, phone)
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font(_FONT, "", 9)
    pdf.cell(0, 5, f"Période : {start.strftime('%d/%m/%Y')} — "
                    f"{end.strftime('%d/%m/%Y')}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    ings = state.stock.ingredients()
    low = state.stock.low_stock()

    # classer : rupture (stock == 0) vs en voie de rupture (0 < stock <= min)
    rupture = [i for i in low if float(i.get("current_stock", 0)) == 0]
    en_voie = [i for i in low if 0 < float(i.get("current_stock", 0))
               <= float(i.get("min_stock", 0))]
    ok = [i for i in ings if i not in low]

    # résumé
    pdf.section("Résumé")
    pdf.kv_line("Total ingrédients", len(ings))
    pdf.kv_line("En rupture de stock", len(rupture),
                bold_value=bool(rupture))
    pdf.kv_line("En voie de rupture", len(en_voie),
                bold_value=bool(en_voie))
    pdf.kv_line("Stocks OK", len(ok))

    # table rupture
    if rupture:
        pdf.ln(2)
        pdf.set_font(_FONT, "B", 10)
        pdf.set_text_color(220, 38, 38)
        pdf.cell(0, 6, f"⚠ RUPTURE DE STOCK ({len(rupture)})",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

        rcols = [("Ingrédient", 50, "L"), ("Stock", 22, "R"),
                 ("Seuil", 22, "R"), ("Prix unit.", 30, "R"),
                 ("Unité", 25, "L"), ("Fournisseur", 41, "L")]
        pdf.table_header(rcols)
        for i in sorted(rupture, key=lambda x: x["name"]):
            pdf.table_row([
                i["name"][:30],
                f"{float(i.get('current_stock', 0)):g}",
                f"{float(i.get('min_stock', 0)):g}",
                pdf.money(i.get("cost_price", 0)),
                i.get("unit", "—"),
                (i.get("supplier") or "—")[:25]], rcols)

    # table en voie de rupture
    if en_voie:
        pdf.ln(2)
        pdf.set_font(_FONT, "B", 10)
        pdf.set_text_color(217, 119, 6)
        pdf.cell(0, 6, f"⚠ EN VOIE DE RUPTURE ({len(en_voie)})",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

        pdf.table_header(rcols)
        for i in sorted(en_voie, key=lambda x: x["name"]):
            pdf.table_row([
                i["name"][:30],
                f"{float(i.get('current_stock', 0)):g}",
                f"{float(i.get('min_stock', 0)):g}",
                pdf.money(i.get("cost_price", 0)),
                i.get("unit", "—"),
                (i.get("supplier") or "—")[:25]], rcols)

    # stocks OK (résumé compact)
    if ok:
        pdf.ln(2)
        pdf.section(f"Stocks OK ({len(ok)})")
        ocols = [("Ingrédient", 50, "L"), ("Stock", 22, "R"),
                 ("Seuil", 22, "R"), ("Statut", 22, "C")]
        pdf.table_header(ocols)
        for i in sorted(ok, key=lambda x: x["name"]):
            stk = float(i.get("current_stock", 0))
            min_s = float(i.get("min_stock", 0))
            pdf.table_row([
                i["name"][:30],
                f"{stk:g}",
                f"{min_s:g}",
                "OK"], ocols)

    # mouvements sur la période
    mv_all = state.stock.movements()
    mv = [m for m in mv_all if start_s <= m["at"] < end_s]
    if mv:
        pdf.add_page()
        pdf.section(f"Mouvements de stock ({len(mv)})")
        mcols = [("Date", 25, "L"), ("Ingrédient", 38, "L"),
                 ("Type", 18, "C"), ("Qté", 18, "R"),
                 ("Motif", 50, "L"), ("Par", 25, "L")]
        pdf.table_header(mcols)
        for m in mv[:50]:
            sign = {"in": "+", "out": "−"}.get(m["type"], "")
            pdf.table_row([
                m["at"][5:16],
                m["ingredient_name"][:22],
                {"in": "Entrée", "out": "Sortie",
                 "adjust": "Ajust."}[m["type"]],
                f"{sign}{m['qty']:g}",
                m.get("reason", "")[:30],
                str(m.get("by", "—"))[:15]], mcols)

    path = _pdf_path("rapport_stock")
    pdf.output(path)
    return path


# ========================================================= RAPPORT FOURNISSEURS --
def rapport_fournisseurs(state, period="Jour") -> str:
    """Rapport fournisseurs — livraisons + dettes. Format A4."""
    resto, addr, phone = _settings_path(state)
    start, end = period_range(period)
    start_s = start.strftime("%Y-%m-%d %H:%M:%S")
    end_s = end.strftime("%Y-%m-%d %H:%M:%S")

    pdf = _ReportPDF(f"Rapport fournisseurs — {period}", resto, addr, phone)
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font(_FONT, "", 9)
    pdf.cell(0, 5, f"Période : {start.strftime('%d/%m/%Y')} — "
                    f"{end.strftime('%d/%m/%Y')}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    sups = state.suppliers.suppliers()

    # résumé
    total_debt = 0.0
    total_expected = 0.0
    for s in sups:
        t = state.suppliers.supplier_totals(s["id"])
        total_debt += t["debt"]
        total_expected += t["expected"]

    pdf.section("Résumé")
    pdf.kv_line("Nombre de fournisseurs", len(sups))
    pdf.kv_line("Montant total livré", pdf.money(total_expected))
    pdf.kv_line("Montant total payé",
                pdf.money(total_expected - total_debt))
    pdf.kv_line("Dettes totales", pdf.money(total_debt),
                bold_value=bool(total_debt))

    # livraisons regroupées par fournisseur
    dls_all = [d for d in state.suppliers.deliveries()
               if start_s <= d["at"] < end_s]
    dls_by_sup = {}
    for d in dls_all:
        sname = d.get("supplier_name", "—")
        if sname not in dls_by_sup:
            dls_by_sup[sname] = []
        dls_by_sup[sname].append(d)

    for sname in sorted(dls_by_sup.keys()):
        dls = dls_by_sup[sname]
        pdf.add_page()
        pdf.section(f"Livraisons — {sname} ({len(dls)})")
        lcols = [("Date", 25, "L"), ("Ingrédient", 34, "L"),
                 ("Acheté", 24, "R"), ("En stock", 26, "R"),
                 ("Coût unit.", 25, "R"), ("Total", 26, "R"), ("Par", 18, "L")]
        pdf.table_header(lcols)
        sous_total = 0.0
        for d in dls:
            punit = d.get("purchase_unit", "")
            qty_s = f"{d['qty']:g}{(' ' + punit) if punit else ''}"
            pdf.table_row([
                d["at"][:10],
                d["ingredient_name"][:19],
                qty_s,
                f"{float(d.get('stock_qty', d['qty'])):g} "
                f"{d.get('ing_unit', '')}".strip(),
                pdf.money(d["unit_cost"]),
                pdf.money(d["total"]),
                str(d.get("by", "—"))[:12]], lcols)
            sous_total += d["total"]
        pdf.table_row(["", "", "", "", "", pdf.money(sous_total), ""],
                      lcols, bold=True)

    # dettes par fournisseur
    sups_with_debt = [(s, state.suppliers.supplier_totals(s["id"]))
                      for s in sups
                      if state.suppliers.supplier_totals(s["id"])["debt"] > 0]
    if sups_with_debt:
        pdf.add_page()
        pdf.section(f"Dettes fournisseurs ({len(sups_with_debt)})")
        dcols = [("Fournisseur", 45, "L"), ("Livré", 30, "R"),
                 ("Payé", 30, "R"), ("Dette", 30, "R"),
                 ("Produits", 55, "L")]
        pdf.table_header(dcols)
        for s, t in sorted(sups_with_debt,
                           key=lambda x: x[1]["debt"], reverse=True):
            pdf.table_row([
                s["name"][:25],
                pdf.money(t["expected"]),
                pdf.money(t["paid"]),
                pdf.money(t["debt"]),
                (s.get("products") or "—")[:30]], dcols)

        pdf.ln(2)
        pdf.set_font(_FONT, "B", 10)
        pdf.set_fill_color(236, 229, 212)
        pdf.cell(0, 7,
                 f"  TOTAL DETTES : {pdf.money(total_debt)}",
                 new_x="LMARGIN", new_y="NEXT", fill=True)

    # paiements sur la période
    pays = [p for p in state.suppliers.payments()
            if start_s <= p["at"] < end_s]
    if pays:
        pdf.add_page()
        pdf.section(f"Paiements effectués ({len(pays)})")
        pcols = [("Date", 25, "L"), ("Fournisseur", 35, "L"),
                 ("Montant", 30, "R"), ("Par", 25, "L"),
                 ("Note", 45, "L")]
        pdf.table_header(pcols)
        for p in pays[:50]:
            pdf.table_row([
                p["at"][:16],
                p["supplier_name"][:20],
                pdf.money(p["amount"]),
                str(p.get("by", "—"))[:15],
                (p.get("note") or "—")[:30]], pcols)

    path = _pdf_path("rapport_fournisseurs")
    pdf.output(path)
    return path


# ============================================================ FICHE DE PAIE --
def _fmt_dt(s, with_time=True):
    """Format 'YYYY-MM-DD HH:MM:SS' vers 'DD/MM/YYYY HH:MM' (ou date seule)."""
    if not s:
        return "—"
    try:
        dt = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M" if with_time else "%d/%m/%Y")
    except ValueError:
        return str(s)


def fiche_paie(state, user, month: str) -> str:
    """Bulletin de paie individuel (A4) pour un employe sur un mois donne.

    Affiche le salaire de base, le detail des avances et des paiements,
    le total verse et le net a payer. Renvoie le chemin du PDF genere.
    """
    payroll = state.payroll
    name, addr, phone = _settings_path(state)
    pdf = _ReportPDF("FICHE DE PAIE", name, addr, phone)
    pdf.add_page()

    # -- entete du bulletin --------------------------------------------------
    label = payroll.month_label(month)
    role_label = state.roles.label(user["role"])
    pdf.set_font(_FONT, "", 9)
    pdf.kv_line("Employé", user["name"], bold_value=True)
    pdf.kv_line("Rôle", role_label)
    pdf.kv_line("Mois", label)

    salary = payroll.monthly_salary(user)
    adv_recs = payroll.advances(user["id"], month)
    pay_recs = payroll.payments(user["id"], month)
    adv_total = round(sum(a["amount"] for a in adv_recs), 2)
    pay_total = round(sum(p["amount"] for p in pay_recs), 2)
    net = payroll.net_to_pay(user["id"], month)
    total_verse = round(adv_total + pay_total, 2)
    solde_restant = round(salary - total_verse, 2)

    # -- detail des avances --------------------------------------------------
    pdf.ln(2)
    if adv_recs:
        pdf.section(f"Avances du mois ({len(adv_recs)})")
        acols = [("Date", 34, "L"), ("Montant", 26, "R"),
                 ("Par", 30, "L"), ("Note", 50, "L")]
        pdf.table_header(acols)
        for a in adv_recs:
            pdf.table_row([
                _fmt_dt(a["at"]),
                pdf.money(a["amount"]),
                str(a.get("by", "—"))[:18],
                (a.get("note") or "—")[:40]], acols)
    else:
        pdf.section("Avances du mois")
        pdf.set_font(_FONT, "", 9)
        pdf.cell(0, 6, "Aucune avance enregistrée.",
                 new_x="LMARGIN", new_y="NEXT")

    # -- detail des paiements -------------------------------------------------
    pdf.ln(2)
    if pay_recs:
        pdf.section(f"Paiements du mois ({len(pay_recs)})")
        pcols = [("Date", 34, "L"), ("Montant", 26, "R"),
                 ("Par", 30, "L"), ("Note", 50, "L")]
        pdf.table_header(pcols)
        for p in pay_recs:
            pdf.table_row([
                _fmt_dt(p["at"]),
                pdf.money(p["amount"]),
                str(p.get("by", "—"))[:18],
                (p.get("note") or "—")[:40]], pcols)
    else:
        pdf.section("Paiements du mois")
        pdf.set_font(_FONT, "", 9)
        pdf.cell(0, 6, "Aucun paiement enregistré.",
                 new_x="LMARGIN", new_y="NEXT")

    # -- recapitulatif ---------------------------------------------------------
    pdf.ln(3)
    pdf.section("Récapitulatif")
    pdf.kv_line("Salaire de base", pdf.money(salary))
    pdf.kv_line("Avances du mois", pdf.money(adv_total))
    pdf.kv_line("Paiements du mois", pdf.money(pay_total))
    pdf.kv_line("Total versé", pdf.money(total_verse))
    pdf.kv_line("Net à payer", pdf.money(net), bold_value=True)
    pdf.kv_line("Solde restant", pdf.money(solde_restant))

    # -- signature --------------------------------------------------------------
    pdf.ln(5)
    pdf.set_font(_FONT, "", 8)
    pdf.cell(_W / 2, 5, "Signature du responsable :")
    pdf.cell(0, 5, "Signature de l'employé :")

    path = _pdf_path("fiche_paie")
    pdf.output(path)
    return path
