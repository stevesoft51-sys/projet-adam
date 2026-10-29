"""Onglet Tableau de bord : monitoring global de TOUS les modules + rapports PDF."""
import os
import tkinter as tk
from tkinter import ttk, filedialog

from .. import theme
from ...services import PAYMENT_METHODS, PERIODS
from ..widgets import card, clear, show_error, info, CalendarPopup, DataGrid

_PERIOD_KEYS = {
    "Jour": "dash.period.day",
    "Hier": "dash.period.yesterday_short",
    "Semaine": "dash.period.week",
    "Mois": "dash.period.month_short",
    "Année": "dash.period.year_short",
}


class ReportsView(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, style="TFrame")
        self.state = state
        self._build()
        self.refresh()

    def _build(self):
        # -- barre de controle -------------------------------------------------
        controls = tk.Frame(self, bg=theme.BG)
        controls.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(controls, text=self.state.tr("dash.period_label"),
                 bg=theme.BG).pack(side="left")
        period_labels = [self.state.tr(k) for k in _PERIOD_KEYS.values()]
        self.cb_period = ttk.Combobox(controls, values=period_labels,
                                      state="readonly", width=10)
        self.cb_period.current(0)
        self.cb_period.pack(side="left", padx=6)
        self.cb_period.bind("<<ComboboxSelected>>", lambda e: self._use_period())
        ttk.Button(controls, text=self.state.tr("dash.refresh"),
                   command=self.refresh).pack(side="left")
        self.lbl_range = tk.Label(controls, text="", bg=theme.BG,
                                   fg=theme.MUTED, font=theme.FONT_SMALL)
        self.lbl_range.pack(side="right")

        # -- filtre par plage de dates + employe -------------------------------
        filters = tk.Frame(self, bg=theme.BG)
        filters.pack(fill="x", padx=12, pady=(4, 0))
        tk.Label(filters, text=self.state.tr("dash.filter.date"),
                 bg=theme.BG, font=("Segoe UI", 9, "bold")).pack(side="left")
        self.e_date_from = self._date_entry(filters)
        self.e_date_from.pack(side="left", padx=(4, 0))
        ttk.Button(filters, text="📅", width=3,
                   command=lambda: self._open_cal("from")).pack(side="left",
                                                                padx=2)
        tk.Label(filters, text="—", bg=theme.BG).pack(side="left", padx=2)
        self.e_date_to = self._date_entry(filters)
        self.e_date_to.pack(side="left", padx=(0, 2))
        ttk.Button(filters, text="📅", width=3,
                   command=lambda: self._open_cal("to")).pack(side="left",
                                                              padx=2)
        ttk.Button(filters, text=self.state.tr("dash.filter.apply"),
                   style="Accent.TButton",
                   command=self._apply_range).pack(side="left", padx=6)

        sep = tk.Frame(filters, bg=theme.MUTED, width=1)
        sep.pack(side="left", fill="y", padx=8)

        tk.Label(filters, text=self.state.tr("dash.filter.employee"),
                 bg=theme.BG, font=("Segoe UI", 9, "bold")).pack(side="left")
        staff = [u for u in self.state.auth.staff() if u["role"] != "admin"]
        all_lbl = self.state.tr("dash.filter.all_employees")
        self._emp_names = [all_lbl] + [u["name"] for u in staff]
        self._emp_objs = [None] + staff
        self.cb_employee = ttk.Combobox(filters,
                                        values=self._emp_names,
                                        state="readonly", width=16)
        self.cb_employee.current(0)
        self.cb_employee.pack(side="left", padx=6)
        self.cb_employee.bind("<<ComboboxSelected>>",
                              lambda e: self.refresh())

        # -- bandes de monitoring (7 modules) ----------------------------------
        self.mon_frame = tk.Frame(self, bg=theme.BG)
        self.mon_frame.pack(fill="x", padx=10, pady=(8, 0))

        # -- KPIs --------------------------------------------------------------
        self.kpi_row = tk.Frame(self, bg=theme.BG)
        self.kpi_row.pack(fill="x", padx=10, pady=(6, 0))

        # -- suivi total par module --------------------------------------------
        self.suivi_card = card(self, padx=10)
        self.suivi_card.pack(fill="x", padx=10, pady=(6, 0))
        self.suivi_head = tk.Label(
            self.suivi_card, text="", bg=theme.CARD,
            font=("Segoe UI", 12, "bold"))
        self.suivi_head.pack(anchor="w", padx=12, pady=(10, 0))
        self.suivi_body = tk.Frame(self.suivi_card, bg=theme.CARD)
        self.suivi_body.pack(fill="x", padx=12, pady=(6, 12))

        # -- boutons PDF -------------------------------------------------------
        pdf_row = tk.Frame(self, bg=theme.BG)
        pdf_row.pack(fill="x", padx=10, pady=(8, 0))
        tk.Label(pdf_row, text=self.state.tr("dash.generate_pdf"),
                 bg=theme.BG,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        for label, cmd in (
            (self.state.tr("dash.pdf.cash"), lambda: self._gen_pdf("caisse")),
            (self.state.tr("dash.pdf.sales"), lambda: self._gen_pdf("ventes")),
            (self.state.tr("dash.pdf.stock"), lambda: self._gen_pdf("stock")),
            (self.state.tr("dash.pdf.suppliers"),
             lambda: self._gen_pdf("fournisseurs")),
        ):
            ttk.Button(pdf_row, text=label,
                       command=cmd).pack(side="left", padx=4)
        ttk.Button(pdf_row, text=self.state.tr("dash.reports_yesterday"),
                   style="Accent.TButton",
                   command=self._gen_yesterday).pack(side="left", padx=10)

        # -- graphique ---------------------------------------------------------
        chart_holder = card(self, padx=10)
        chart_holder.pack(fill="x", padx=10, pady=(6, 0))
        self.chart = tk.Canvas(chart_holder, height=190, bg=theme.CARD,
                               highlightthickness=0)
        self.chart.pack(fill="both", expand=True, padx=10, pady=8)

        # -- 3 sections pleine largeur -----------------------------------------
        self.mid_row = card(self, padx=10)
        self.mid_row.pack(fill="x", padx=10, pady=(6, 0))

        # -- colonnes du bas ---------------------------------------------------
        bottom = tk.Frame(self, bg=theme.BG)
        bottom.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)
        bottom.rowconfigure(0, weight=1)
        self.left_col = card(bottom)
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(1, 4),
                           ipadx=4, ipady=4)
        self.right_col = card(bottom)
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(4, 1),
                            ipadx=4, ipady=4)

    def _date_entry(self, parent):
        """Champ date au format AAAA-MM-JJ (editable)."""
        from datetime import date
        var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self._dt_vars = getattr(self, "_dt_vars", [])
        self._dt_vars.append(var)
        return ttk.Entry(parent, textvariable=var, width=12)

    # ========================================================== monitoring ===
    def _refresh_monitoring(self):
        for w in self.mon_frame.winfo_children():
            w.destroy()

        # --- 1. CAISSE ---
        open_sess = self.state.cash.get_open()
        if open_sess:
            expected = self.state.cash.expected_amount(open_sess)
            nb_mv = len(open_sess.get("movements", []))
            cash_info = (f"{self.state.tr('dash.cash.opened_by', user=open_sess['opened_by'], time=open_sess['opened_at'][11:16])}  ·  "
                         f"{self.state.tr('dash.cash.fund')} : {theme.money(open_sess['opening_amount'])}  ·  "
                         f"{self.state.tr('dash.cash.expected')} : {theme.money(expected)}  ·  "
                         f"{self.state.tr('dash.cash.movements')} : {nb_mv}")
            bg = "#eafaf0"
            fg = theme.SUCCESS
        else:
            sessions = self.state.cash.sessions()
            if sessions:
                last = sessions[0]
                cash_info = (f"{self.state.tr('dash.cash.closed_by', user=last.get('closed_by', '?'), time=(last.get('closed_at') or '?')[11:16])}  ·  "
                             f"{self.state.tr('dash.cash.gap')} : {theme.money(last.get('difference', 0))}")
                bg = "#f3f4f6"
                fg = theme.MUTED
            else:
                cash_info = self.state.tr("dash.cash.no_session")
                bg = "#f3f4f6"
                fg = theme.MUTED
        self._monitor_badge(self.state.tr("dash.mod.cash"), cash_info, bg, fg)

        # --- 2. COMMANDES ---
        pending = self.state.orders.open_orders()
        if pending:
            tables = [str(o.get("unit_name") or "?") for o in pending[:3]]
            extra = f" +{len(pending)-3}" if len(pending) > 3 else ""
            order_info = (f"{self.state.tr('dash.orders.pending_count', count=len(pending))}  ·  "
                          f"{', '.join(tables)}{extra}")
            bg = "#fdecea"
            fg = theme.DANGER
        else:
            order_info = self.state.tr("dash.orders.all_served")
            bg = "#eafaf0"
            fg = theme.SUCCESS
        self._monitor_badge(self.state.tr("dash.mod.orders"), order_info, bg, fg)

        # --- 3. STOCK ---
        low = self.state.stock.low_stock()
        ings = self.state.stock.ingredients()
        if low:
            names = ", ".join(i["name"] for i in low[:3])
            extra = f" +{len(low)-3}" if len(low) > 3 else ""
            stock_info = self.state.tr("dash.stock.low_count", low=len(low), total=len(ings)) + f" : {names}{extra}"
            bg = "#fdecea"
            fg = theme.DANGER
        else:
            stock_info = self.state.tr("dash.stock.all_ok", count=len(ings))
            bg = "#eafaf0"
            fg = theme.SUCCESS
        self._monitor_badge(self.state.tr("dash.mod.stock"), stock_info, bg, fg)

        # --- 4. FOURNISSEURS ---
        sups = self.state.suppliers.suppliers()
        total_debt = sum(
            self.state.suppliers.supplier_totals(s["id"])["debt"]
            for s in sups)
        total_debt = round(total_debt, 2)
        total_delivered = sum(
            self.state.suppliers.supplier_totals(s["id"])["expected"]
            for s in sups)
        if total_debt > 0:
            debt_info = (f"{self.state.tr('dash.suppliers.count', count=len(sups))}  ·  "
                         f"{self.state.tr('dash.suppliers.debt')} : {theme.money(total_debt)}")
            bg = "#fef3cd"
            fg = theme.WARNING
        else:
            debt_info = self.state.tr("dash.suppliers.none_due", count=len(sups))
            bg = "#eafaf0"
            fg = theme.SUCCESS
        self._monitor_badge(self.state.tr("dash.mod.suppliers"), debt_info, bg, fg)

        # --- 5. PERSONNEL ---
        staff = self.state.auth.staff()
        active = [u for u in staff if u.get("active", True)]
        blocked = [u for u in staff if not u.get("active", True)]
        admins = [u for u in staff if u["role"] == "admin"]
        if blocked:
            staff_info = (f"{self.state.tr('dash.staff.active_of', active=len(active), total=len(staff))}  ·  "
                          f"{self.state.tr('dash.staff.blocked', count=len(blocked))}  ·  "
                          f"{self.state.tr('dash.staff.admins', count=len(admins))}")
            bg = "#fef3cd"
            fg = theme.WARNING
        else:
            staff_info = (f"{self.state.tr('dash.staff.active_of', active=len(active), total=len(staff))}  ·  "
                          f"{self.state.tr('dash.staff.admins', count=len(admins))}")
            bg = "#eafaf0"
            fg = theme.SUCCESS
        self._monitor_badge(self.state.tr("dash.mod.staff"), staff_info, bg, fg)

        # --- 6. MENU ---
        cats = self.state.catalog.categories()
        prods = self.state.catalog.products()
        prods_active = self.state.catalog.products(available_only=True)
        cats_active = self.state.catalog.categories(active_only=True)
        if len(prods_active) < len(prods):
            menu_info = (f"{self.state.tr('dash.menu.active_products', active=len(prods_active), total=len(prods))}  ·  "
                         f"{self.state.tr('dash.menu.categories', active=len(cats_active), total=len(cats))}")
            bg = "#fef3cd"
            fg = theme.WARNING
        else:
            menu_info = (f"{self.state.tr('dash.menu.all_active_products', count=len(prods))}  ·  "
                         f"{self.state.tr('dash.menu.all_active_categories', count=len(cats))}")
            bg = "#eafaf0"
            fg = theme.SUCCESS
        self._monitor_badge(self.state.tr("dash.mod.menu"), menu_info, bg, fg)

        # --- 7. PLAN DE SALLE ---
        units = self.state.floor.units()
        occupied = [u for u in units if u.get("status") == "occupied"]
        reserved = [u for u in units if u.get("status") == "reserved"]
        tables = [u for u in units if u.get("kind") == "table"]
        boucaros = [u for u in units if u.get("kind") == "boucaro"]
        if occupied or reserved:
            occ_names = [u["name"] for u in occupied[:3]]
            res_names = [u["name"] for u in reserved[:2]]
            parts = []
            if occ_names:
                label = self.state.tr("dash.salle.occupied") + " : " + ", ".join(occ_names)
                if len(occupied) > 3:
                    label += f" +{len(occupied)-3}"
                parts.append(label)
            if res_names:
                label = self.state.tr("dash.salle.reserved") + " : " + ", ".join(res_names)
                if len(reserved) > 2:
                    label += f" +{len(reserved)-2}"
                parts.append(label)
            salle_info = (f"{self.state.tr('dash.salle.counts', tables=len(tables), boucaros=len(boucaros))}  ·  "
                          f"  ·  ".join(parts))
            bg = "#fdecea"
            fg = theme.DANGER
        else:
            salle_info = (f"{self.state.tr('dash.salle.counts', tables=len(tables), boucaros=len(boucaros))}  ·  "
                          f"{self.state.tr('dash.salle.all_free')}")
            bg = "#eafaf0"
            fg = theme.SUCCESS
        self._monitor_badge(self.state.tr("dash.mod.salle"), salle_info, bg, fg)

    def _monitor_badge(self, title, detail, bg, fg):
        b = tk.Frame(self.mon_frame, bg=bg, padx=10, pady=6,
                     highlightthickness=1, highlightbackground="#e5ded0")
        b.pack(side="left", expand=True, fill="x", padx=2, pady=2)
        tk.Label(b, text=title, bg=bg, fg=fg,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x")
        tk.Label(b, text=detail, bg=bg, fg=fg,
                 font=theme.FONT_SMALL, anchor="w").pack(fill="x")

    # ========================================================== refresh ======
    def _selected_period_key(self):
        label = self.cb_period.get()
        idx = self.cb_period.current()
        keys = list(_PERIOD_KEYS.keys())
        if 0 <= idx < len(keys):
            return keys[idx]
        return "Jour"

    def _use_period(self):
        """Choix d'une periode rapide ecrase toute plage personnalisee."""
        self._custom = False
        self.refresh()

    def _open_cal(self, which):
        from datetime import date
        def _ok(dstr):
            if which == "from":
                self.e_date_from.delete(0, "end")
                self.e_date_from.insert(0, dstr)
            else:
                self.e_date_to.delete(0, "end")
                self.e_date_to.insert(0, dstr)
        anchor = self.e_date_from if which == "from" else self.e_date_to
        CalendarPopup(self, anchor, _ok, title=self.state.tr("cal.title"))

    def _apply_range(self):
        from datetime import datetime
        try:
            d0 = datetime.strptime(self.e_date_from.get().strip(), "%Y-%m-%d")
            d1 = datetime.strptime(self.e_date_to.get().strip(), "%Y-%m-%d")
        except ValueError:
            show_error(self, self.state.tr("dash.filter.invalid_date"))
            return
        if d1 < d0:
            d0, d1 = d1, d0
        self._custom = True
        self._custom_start = d0.strftime("%Y-%m-%d") + " 00:00:00"
        self._custom_end = d1.strftime("%Y-%m-%d") + " 23:59:59"
        self.refresh()

    def _selected_employee(self):
        idx = self.cb_employee.current()
        if 0 <= idx < len(self._emp_objs):
            return self._emp_objs[idx]
        return None

    def _compute_range(self):
        """Renvoie (period, start_s, end_s). Si une plage personnalisee est
        active, period vaut 'Jour' fantome mais start/end sont utilises."""
        custom = getattr(self, "_custom", False)
        if custom:
            return ("Jour", self._custom_start, self._custom_end)
        period = self._selected_period_key()
        from ...services import period_range
        start, end = period_range(period)
        return (period,
                start.strftime("%Y-%m-%d %H:%M:%S"),
                end.strftime("%Y-%m-%d %H:%M:%S"))

    def refresh(self):
        period, start_s, end_s = self._compute_range()
        fin = self.state.reports.financial(period, start_s=start_s, end_s=end_s)
        stock_sum = self.state.reports.stock_summary(period, start_s=start_s,
                                                     end_s=end_s)
        emp = self._selected_employee()
        emp_id = emp["id"] if emp else None
        emp_name = emp["name"] if emp else None
        act = self.state.reports.activity_summary(start_s, end_s,
                                                  user_id=emp_id,
                                                  user_name=emp_name)
        from .reports_helpers import period_label
        base = period_label(period, self.state)
        if getattr(self, "_custom", False):
            from datetime import datetime
            start_d = datetime.strptime(start_s[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
            end_d = datetime.strptime(end_s[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
            base = f"{self.state.tr('dash.range_label')} {start_d} → {end_d}"
        if emp:
            base += "  ·  " + self.state.tr("dash.filter.employee") + " : " + emp["name"]
        self.lbl_range.config(text=base)

        self._refresh_monitoring()
        self._refresh_activity(act)

        clear(self.kpi_row)
        cards_data = [
            (self.state.tr("dash.kpi.revenue"),
             theme.money(fin["revenue"]),
             theme.ACCENT_HOVER),
            (self.state.tr("dash.kpi.tickets"),
             str(fin["count"]), theme.TEXT),
            (self.state.tr("dash.kpi.avg_basket"),
             theme.money(fin["avg_basket"]), theme.TEXT),
            (self.state.tr("dash.kpi.cash_in"),
             theme.money(fin["cash_in_manual"]),
             theme.SUCCESS),
            (self.state.tr("dash.kpi.cash_out"),
             theme.money(fin["cash_out_manual"]),
             theme.DANGER),
        ]
        for title, val, color in cards_data:
            f = tk.Frame(self.kpi_row, bg=theme.CARD, padx=14, pady=10,
                         highlightthickness=1,
                         highlightbackground="#e5ded0")
            f.pack(side="left", expand=True, fill="x", padx=3, pady=3)
            tk.Label(f, text=title.upper(), bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL).pack(anchor="w")
            tk.Label(f, text=val, bg=theme.CARD, fg=color,
                     font=("Segoe UI", 15, "bold")).pack(anchor="w")

        labels, values = self.state.reports.series(period, start_s=start_s,
                                                   end_s=end_s)
        self._draw_chart(labels, values)
        self._render_mid(fin)
        self._render_left(fin)
        self._render_right(stock_sum)

    # =================================================== suivi par module ====
    def _refresh_activity(self, act):
        for w in self.suivi_body.winfo_children():
            w.destroy()
        emp = self._selected_employee()
        if emp:
            head = self.state.tr("dash.suivi.title_employee",
                                 name=emp["name"])
        else:
            head = self.state.tr("dash.suivi.title")
        self.suivi_head.config(text=head)

        def stat_block(parent, module_title, items):
            col = tk.Frame(parent, bg=theme.CARD,
                           highlightthickness=1, highlightbackground="#e5ded0")
            col.pack(side="left", fill="x", expand=True, padx=2, pady=2)
            tk.Label(col, text="  " + module_title, bg=theme.CARD,
                     fg=theme.ACCENT_HOVER,
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(
                fill="x", pady=(6, 2))
            for label, val, color in items:
                row = tk.Frame(col, bg=theme.CARD)
                row.pack(fill="x", padx=8, pady=1)
                tk.Label(row, text=label, bg=theme.CARD, fg=theme.MUTED,
                         font=theme.FONT_SMALL, anchor="w"
                         ).pack(side="left")
                tk.Label(row, text=val, bg=theme.CARD, fg=color,
                         font=("Segoe UI", 9, "bold"), anchor="e"
                         ).pack(side="right")

        # 2 lignes x 4 + 3 = 7 modules
        row1 = tk.Frame(self.suivi_body, bg=theme.CARD)
        row1.pack(fill="x")
        row2 = tk.Frame(self.suivi_body, bg=theme.CARD)
        row2.pack(fill="x")

        c = act["caisse"]
        stat_block(row1, self.state.tr("dash.mod.cash"), [
            (self.state.tr("dash.suivi.cash_opens"),
             str(c["open"]) + "/" + str(c["closed"]), theme.TEXT),
            (self.state.tr("dash.suivi.cash_in"), theme.money(c["in"]),
             theme.SUCCESS),
            (self.state.tr("dash.suivi.cash_out"), theme.money(c["out"]),
             theme.DANGER),
            (self.state.tr("dash.suivi.cash_net"), theme.money(c["net"]),
             theme.ACCENT_HOVER),
        ])

        v = act["ventes"]
        stat_block(row1, self.state.tr("dash.mod.orders"), [
            (self.state.tr("dash.suivi.sales_count"), str(v["count"]),
             theme.TEXT),
            (self.state.tr("dash.suivi.revenue"), theme.money(v["revenue"]),
             theme.ACCENT_HOVER),
            (self.state.tr("dash.suivi.avg_basket"),
             theme.money(v["avg_basket"]), theme.TEXT),
            (self.state.tr("dash.suivi.orders"),
             str(v["orders"]) + "/" + str(v["settled"]), theme.TEXT),
        ])

        st = act["stock"]
        stat_block(row1, self.state.tr("dash.mod.stock"), [
            (self.state.tr("dash.suivi.stock_entries"),
             f"{st['entries']:g}", theme.SUCCESS),
            (self.state.tr("dash.suivi.stock_exits"), f"{st['exits']:g}",
             theme.DANGER),
            (self.state.tr("dash.suivi.stock_adjusts"),
             f"{st['adjusts']:g}", theme.WARNING),
            (self.state.tr("dash.suivi.stock_movements"), str(st["count"]),
             theme.TEXT),
        ])

        sup = act["fournisseurs"]
        stat_block(row1, self.state.tr("dash.mod.suppliers"), [
            (self.state.tr("dash.suivi.deliveries"),
             str(sup["count_deliveries"]), theme.TEXT),
            (self.state.tr("dash.suivi.delivery_total"),
             theme.money(sup["delivery_total"]), theme.SUCCESS),
            (self.state.tr("dash.suivi.payments"),
             str(sup["count_payments"]) + " / " + theme.money(sup["paid"]),
             theme.TEXT),
            (self.state.tr("dash.suivi.debt"), theme.money(sup["debt"]),
             theme.WARNING),
        ])

        p = act["personnel"]
        stat_block(row2, self.state.tr("dash.mod.staff"), [
            (self.state.tr("dash.suivi.advances"),
             str(p["count_advances"]) + " / " + theme.money(p["advances_total"]),
             theme.ACCENT),
            (self.state.tr("dash.suivi.salaries"),
             str(p["count_payments"]) + " / " + theme.money(p["salaries_total"]),
             theme.SUCCESS),
            (self.state.tr("dash.suivi.active"), str(p["active"]), theme.TEXT),
            ("", "", theme.TEXT),
        ])

        m = act["menu"]
        stat_block(row2, self.state.tr("dash.mod.menu"), [
            (self.state.tr("dash.suivi.categories"), str(m["categories"]),
             theme.TEXT),
            (self.state.tr("dash.suivi.products"), str(m["products"]),
             theme.TEXT),
            (self.state.tr("dash.suivi.available"), str(m["available"]),
             theme.SUCCESS),
            ("", "", theme.TEXT),
        ])

        sa = act["salle"]
        names = ", ".join(sa["occupied_names"][:3])
        extra = " +…" if len(sa["occupied_names"]) > 3 else ""
        stat_block(row2, self.state.tr("dash.mod.salle"), [
            (self.state.tr("dash.suivi.occupied"), str(sa["occupied"]),
             theme.DANGER),
            (self.state.tr("dash.suivi.reserved"), str(sa["reserved"]),
             theme.WARNING),
            (self.state.tr("dash.suivi.tables"),
             names + extra or "—", theme.TEXT),
            ("", "", theme.TEXT),
        ])

    # ========================================================== PDF ==========
    def _gen_yesterday(self):
        try:
            from ...pdf_generator import (rapport_casse, rapport_ventes,
                                          rapport_stock,
                                          rapport_fournisseurs)
            from .reports_helpers import period_label
            paths = []
            for gen in (rapport_casse, rapport_ventes, rapport_stock,
                        rapport_fournisseurs):
                paths.append(gen(self.state, "Hier"))
            info(self, self.state.tr("dash.yesterday.success",
                                     range_text=period_label("Hier", self.state)))
        except Exception as exc:
            show_error(self, self.state.tr("dash.gen_error", error=exc))

    def _gen_pdf(self, kind):
        period = self._selected_period_key()
        try:
            from ...pdf_generator import (rapport_casse, rapport_ventes,
                                          rapport_stock,
                                          rapport_fournisseurs)
            generators = {
                "caisse": rapport_casse,
                "ventes": rapport_ventes,
                "stock": rapport_stock,
                "fournisseurs": rapport_fournisseurs,
            }
            path = generators[kind](self.state, period)
            info(self, self.state.tr("dash.gen_success", path=path))
        except Exception as exc:
            show_error(self, self.state.tr("dash.gen_error", error=exc))

    # ========================================================== graphique =====
    def _draw_chart(self, labels, values):
        c = self.chart
        c.delete("all")
        width = max(c.winfo_width() or 800, 400)
        height = max(c.winfo_height() or 190, 120)
        pad_l, pad_b, pad_t = 46, 26, 14
        plot_w = width - pad_l - 10
        plot_h = height - pad_b - pad_t
        max_val = max(values, default=0) or 1

        nice_max = max_val * 1.15
        for i in range(5):
            y = pad_t + plot_h - plot_h * i / 4
            val = nice_max * i / 4
            c.create_line(pad_l, y, width - 8, y, fill="#efe9de")
            c.create_text(pad_l - 6, y,
                          text=f"{val:,.0f}".replace(",", " "),
                          anchor="e", font=("Segoe UI", 8), fill=theme.MUTED)

        n = len(values)
        if n == 0:
            c.create_text(width // 2, height // 2,
                          text=self.state.tr("dash.chart.no_sales"),
                          fill=theme.MUTED, font=theme.FONT)
            return
        slot = plot_w / n
        bar_w = min(slot * 0.62, 42)
        for i, v in enumerate(values):
            x0 = pad_l + i * slot + (slot - bar_w) / 2
            h = plot_h * (v / nice_max) if v > 0 else 0
            y0 = pad_t + plot_h - h
            color = theme.ACCENT if v > 0 else "#e5ded0"
            if v > 0:
                c.create_rectangle(x0, y0, x0 + bar_w, pad_t + plot_h,
                                   fill=color, outline="")
            step = max(1, n // 12)
            if i % step == 0:
                c.create_text(x0 + bar_w / 2, pad_t + plot_h + 8,
                              text=labels[i], font=("Segoe UI", 8),
                              fill=theme.MUTED)
            if v > 0 and n <= 16:
                c.create_text(x0 + bar_w / 2, y0 - 8,
                              text=f"{v:,.0f}".replace(",", " "),
                              font=("Segoe UI", 7, "bold"), fill=theme.TEXT)

    # ========================================================== tables ========
    SEP = "#c9c1b0"
    HEAD_BG = "#ece5d4"
    ZEBRA = "#faf6ec"

    def _mini_table(self, parent, title, columns, rows, stretch=False,
                    scrollable=False):
        wrap = tk.Frame(parent, bg=theme.CARD,
                        highlightthickness=1, highlightbackground=self.SEP)
        wrap.pack(fill="both", expand=True, pady=(0, 8))
        if title:
            tk.Label(wrap, text=title, bg=theme.CARD,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w",
                                                         pady=(0, 3))

        tree = ttk.Treeview(wrap, columns=[c[0] for c in columns],
                            height=rows, show="tree headings")
        tree.heading("#0", text="")
        tree.column("#0", width=0, stretch=False)
        for key, label, width, anchor in columns:
            tree.heading(key, text=label)
            if stretch and width == 0:
                tree.column(key, width=width, minwidth=40, anchor=anchor,
                            stretch=True)
            else:
                tree.column(key, width=width, anchor=anchor)
        tree.configure(height=max(rows, 3))

        s = ttk.Style()
        s.configure("sep.Treeview", rowheight=32, borderwidth=0,
                    background=theme.CARD, fieldbackground=theme.CARD)
        s.configure("sep.Treeview.Heading", background=self.HEAD_BG,
                    foreground=theme.TEXT, font=("Segoe UI", 9, "bold"),
                    padding=(8, 5), relief="flat")
        s.map("sep.Treeview.Heading",
              background=[("active", "#e5ddcd")])
        tree.configure(style="sep.Treeview")

        tree.tag_configure("odd", background=theme.CARD)
        tree.tag_configure("even", background=self.ZEBRA)

        if scrollable:
            vsb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
        else:
            pack_kw = {"fill": "both", "expand": True} if stretch else {"fill": "x"}
            tree.pack(**pack_kw)
        return tree

    def _render_mid(self, fin):
        for w in self.mid_row.winfo_children():
            w.destroy()
        mid = self.mid_row

        row = tk.Frame(mid, bg=theme.CARD)
        row.pack(fill="x", padx=10, pady=(10, 8))
        row.columnconfigure(0, weight=1, uniform="cols")
        row.columnconfigure(1, weight=1, uniform="cols")
        row.columnconfigure(2, weight=1, uniform="cols")

        col_top = tk.Frame(row, bg=theme.CARD)
        col_top.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        col_pay = tk.Frame(row, bg=theme.CARD)
        col_pay.grid(row=0, column=1, sticky="nsew", padx=4)
        col_sales = tk.Frame(row, bg=theme.CARD)
        col_sales.grid(row=0, column=2, sticky="nsew", padx=(4, 0))

        tk.Label(col_top, text=self.state.tr("dash.table.top_products"),
                 bg=theme.CARD,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 3))
        top_tree = self._mini_table(
            col_top, "", [("name", self.state.tr("dash.th.product"), 0, "w"),
                          ("qty", self.state.tr("dash.th.qty"), 0, "center"),
                          ("rev", self.state.tr("dash.th.revenue_short"),
                           0, "e")],
            len(fin["top_products"]), stretch=True, scrollable=True)
        for i, item in enumerate(fin["top_products"]):
            top_tree.insert("", "end", values=(
                item["name"], f"x{item['qty']:g}",
                theme.money(item["revenue"])),
                tags=("even" if i % 2 == 0 else "odd",))
        if not fin["top_products"]:
            top_tree.insert("", "end", values=(
                self.state.tr("dash.table.no_sales"), "", ""))
        top_tree.configure(height=max(len(fin["top_products"]) or 1, 3))

        tk.Label(col_pay, text=self.state.tr("dash.table.payment_split"),
                 bg=theme.CARD,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 3))
        pay_tree = self._mini_table(
            col_pay, "", [("m", self.state.tr("dash.th.mode"), 0, "w"),
                          ("v", self.state.tr("dash.th.amount"), 0, "e"),
                          ("p", "%", 0, "e")], 3, stretch=True)
        total = sum(fin["by_method"].values()) or 1
        for i, (key, amount) in enumerate(sorted(fin["by_method"].items(),
                                  key=lambda kv: kv[1], reverse=True)):
            pct = amount / total * 100
            pay_tree.insert("", "end", values=(
                PAYMENT_METHODS.get(key, key), theme.money(amount),
                f"{pct:.0f} %"),
                tags=("even" if i % 2 == 0 else "odd",))
        pay_tree.configure(height=max(len(fin["by_method"]) or 1, 3))

        tk.Label(col_sales, text=self.state.tr("dash.table.recent_sales"),
                 bg=theme.CARD,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 3))
        sales_tree = self._mini_table(
            col_sales, "", [("n", self.state.tr("dash.th.ticket"), 0, "center"),
                            ("t", self.state.tr("dash.th.time"), 0, "center"),
                            ("c", self.state.tr("dash.th.cashier"), 0, "w"),
                            ("tot", self.state.tr("dash.th.total"), 0, "e")],
            6, stretch=True, scrollable=True)
        for i, sale in enumerate(fin["sales_recent"][:8]):
            sales_tree.insert("", "end", values=(
                sale["number"], sale["datetime"][11:16], sale["cashier"],
                theme.money(sale["total"])),
                tags=("even" if i % 2 == 0 else "odd",))
        sales_tree.configure(height=min(max(len(fin["sales_recent"]) or 1,
                                            3), 8))

    def _render_left(self, fin):
        for w in self.left_col.winfo_children():
            w.destroy()

    def _render_right(self, stock_sum):
        for w in self.right_col.winfo_children():
            w.destroy()
        right = self.right_col

        row = tk.Frame(right, bg=theme.CARD)
        row.pack(fill="x", padx=10, pady=(10, 2))

        def stat(title, val, color):
            f = tk.Frame(row, bg=theme.CARD)
            f.pack(side="left", expand=True, fill="x")
            tk.Label(f, text=title.upper(), bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL).pack()
            tk.Label(f, text=val, bg=theme.CARD, fg=color,
                     font=("Segoe UI", 12, "bold")).pack()

        stat(self.state.tr("dash.stock.entries"),
             f"{stock_sum['entries']:g}", theme.SUCCESS)
        stat(self.state.tr("dash.stock.exits"),
             f"{stock_sum['exits']:g}", theme.DANGER)
        stat(self.state.tr("dash.stock.adjusts"),
             f"{stock_sum['adjusts']:+g}", theme.WARNING)

        low = stock_sum["low"]
        color = theme.DANGER if low else theme.SUCCESS
        banner = tk.Frame(right, bg="#fdecea" if low else "#eafaf0",
                          padx=10, pady=7)
        banner.pack(fill="x", padx=10, pady=6)
        if low:
            names = ", ".join(i["name"] for i in low[:4])
            extra = "…" if len(low) > 4 else ""
            msg = self.state.tr("dash.stock.low_warning") + " " + names + extra
        else:
            msg = self.state.tr("dash.stock.all_above_thresholds")
        tk.Label(banner, text=msg, bg=banner["bg"], fg=color,
                 font=theme.FONT_BOLD, anchor="w").pack(fill="x")

        tk.Label(right, text=self.state.tr("dash.stock.total_value",
                                            value=theme.money(stock_sum['inventory_value'])),
                 bg=theme.CARD, fg=theme.ACCENT_HOVER,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10,
                                                     pady=(8, 10))
