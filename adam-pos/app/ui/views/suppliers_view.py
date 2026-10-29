"""Onglet Fournisseurs (admin) : tableau recapitulatif + livraisons + paiements.

Formulaires FLOTTANTS camoufles dans l'onglet, aucune fenetre de dialogue ;
tableaux DataGrid avec vraies separations bien marquees.
"""
import tkinter as tk
from tkinter import ttk

from .. import theme
from ..widgets import DataGrid, clear, confirm, show_error


class SuppliersView(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, style="TFrame")
        self.state = state
        self._grid_rows = {}
        self._dl_rows = {}
        self._build()
        self.refresh()

    # ------------------------------------------------------------- layout --
    def _build(self):
        holder = tk.Frame(self, bg=theme.CARD, highlightthickness=1,
                          highlightbackground="#e5ded0")
        holder.pack(fill="both", expand=True, padx=10, pady=10)
        self.holder = holder

        top = tk.Frame(holder, bg=theme.CARD)
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(top, text=self.state.tr("sup.title"), bg=theme.CARD,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        btns = tk.Frame(top, bg=theme.CARD)
        btns.pack(side="right")
        ttk.Button(btns, text=self.state.tr("sup.btn_add"), style="Accent.TButton",
                   command=self.new_supplier).pack(side="left", padx=2)
        ttk.Button(btns, text=self.state.tr("sup.btn_delivery"),
                   command=self.new_delivery).pack(side="left", padx=2)
        ttk.Button(btns, text=self.state.tr("sup.form_pay"),
                   style="Success.TButton",
                   command=self.pay_supplier).pack(side="left", padx=2)

        self.kpis = tk.Frame(holder, bg=theme.CARD)
        self.kpis.pack(fill="x", padx=12, pady=(2, 6))

        self.grid_holder = tk.Frame(holder, bg=theme.CARD)
        self.grid_holder.pack(fill="both", expand=True, padx=12, pady=(2, 0))

        actions = tk.Frame(holder, bg=theme.CARD)
        actions.pack(fill="x", padx=10, pady=(6, 4))
        ttk.Button(actions, text=self.state.tr("sup.btn_edit"),
                   command=self.edit_selected).pack(side="left")
        ttk.Button(actions, text=self.state.tr("sup.btn_toggle"),
                   command=self.toggle_selected).pack(side="left", padx=6)
        ttk.Button(actions, text=self.state.tr("sup.btn_delete"), style="Danger.TButton",
                   command=self.delete_selected).pack(side="left")

        sep = tk.Frame(holder, bg=DataGrid.SEP, height=1)
        sep.pack(fill="x", padx=12, pady=(8, 4))

        dl_label = tk.Label(holder,
                            text=self.state.tr("sup.section_recent"),
                            bg=theme.CARD, font=("Segoe UI", 11, "bold"))
        dl_label.pack(anchor="w", padx=12, pady=(4, 2))

        self.dl_holder = tk.Frame(holder, bg=theme.CARD)
        self.dl_holder.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self._build_float_section()

    def _build_float_section(self):
        f = tk.Frame(self, bg=theme.CARD, highlightthickness=1,
                     highlightbackground="#b9ae95")
        inner = tk.Frame(f, bg=theme.CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.float_card = f

        banner = tk.Frame(inner, bg="#fdf6e7")
        banner.pack(fill="x")
        self.lbl_title = tk.Label(banner, text="", bg="#fdf6e7",
                                  fg=theme.ACCENT_HOVER,
                                  font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(anchor="w", padx=18, pady=(10, 2))
        self.lbl_sub = tk.Label(banner, text="", bg="#fdf6e7",
                                fg=theme.MUTED, font=theme.FONT_SMALL,
                                wraplength=520, justify="left")
        self.lbl_sub.pack(anchor="w", padx=18, pady=(0, 10))

        self.f_body = tk.Frame(inner, bg=theme.CARD)
        self.f_body.pack(fill="both", expand=True, padx=18, pady=(10, 4))
        self.f_foot = tk.Frame(inner, bg=theme.CARD)
        self.f_foot.pack(fill="x", padx=18, pady=(6, 14))
        f.bind("<Escape>", lambda e: self._hide_form())

    # ------------------------------------------------- formulaire flottant --
    def _open_form(self, title, sub, width=480):
        self.lbl_title.config(text=title)
        self.lbl_sub.config(text=sub)
        clear(self.f_body)
        clear(self.f_foot)
        self.float_card.place(relx=0.5, rely=0.5, anchor="center",
                              width=width)
        self.float_card.lift()

    def _hide_form(self):
        self.float_card.place_forget()

    @staticmethod
    def _frow(body, row, label, widget):
        tk.Label(body, text=label, bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL, width=16, anchor="w"
                 ).grid(row=row, column=0, sticky="w", pady=5)
        widget.grid(row=row, column=1, sticky="ew", pady=5)

    @staticmethod
    def _num(raw):
        try:
            return float((raw or "0").replace(",", ".").replace(" ", "")
                         or 0)
        except ValueError:
            return 0.0

    # -------------------------------------------------- form. fournisseur --
    def new_supplier(self):
        self._show_supplier_form(None)

    def _show_supplier_form(self, sup):
        self._form_sup = sup
        self._open_form(self.state.tr("sup.form_edit" if sup
                        else "sup.form_new"),
                        sub=self.state.tr("sup.form_supplier_sub"))
        body = self.f_body
        body.columnconfigure(1, weight=1)
        self.s_e_name = ttk.Entry(body)
        self._frow(body, 0, self.state.tr("sup.field_name"), self.s_e_name)
        self.s_e_contact = ttk.Entry(body)
        self._frow(body, 1, self.state.tr("sup.field_contact"), self.s_e_contact)
        self.s_e_phone = ttk.Entry(body)
        self._frow(body, 2, self.state.tr("sup.phone"), self.s_e_phone)
        self.s_e_products = ttk.Entry(body)
        self._frow(body, 3, self.state.tr("sup.field_products"), self.s_e_products)
        self.s_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.s_err.grid(row=4, column=0, columnspan=2, sticky="w")
        if sup:
            self.s_e_name.insert(0, sup["name"])
            self.s_e_contact.insert(0, sup.get("contact") or "")
            self.s_e_phone.insert(0, sup.get("phone") or "")
            self.s_e_products.insert(0, sup.get("products") or "")
        ttk.Button(self.f_foot, text=self.state.tr("common.cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("sup.save"), style="Accent.TButton",
                   command=self._save_supplier).pack(side="right", padx=8)
        self.s_e_name.focus_set()

    def _save_supplier(self):
        data = {
            "contact": self.s_e_contact.get().strip(),
            "phone": self.s_e_phone.get().strip(),
            "products": self.s_e_products.get().strip(),
            "name": self.s_e_name.get(),
        }
        try:
            self.state.suppliers.save_supplier(
                data, sup_id=self._form_sup["id"] if self._form_sup
                else None)
        except Exception as exc:
            self.s_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # ---------------------------------------------------- form. livraison --
    def new_delivery(self):
        sups = self.state.suppliers.suppliers(active_only=True)
        ings = self.state.stock.ingredients()
        if not sups:
            show_error(self, self.state.tr("sup.err_no_supplier"))
            return
        if not ings:
            show_error(self, self.state.tr("sup.err_no_ingredients"))
            return
        self._open_form(self.state.tr("sup.form_delivery"),
                        sub=self.state.tr("sup.form_delivery_sub"))
        body = self.f_body
        body.columnconfigure(1, weight=1)

        self._d_sups = sups
        self._d_all_ings = ings
        self.d_cb_sup = ttk.Combobox(
            body, values=[x["name"] for x in sups], state="readonly")
        self.d_cb_sup.current(0)
        self.d_cb_sup.bind("<<ComboboxSelected>>",
                           lambda e: self._d_refresh_ings())
        self._frow(body, 0, self.state.tr("sup.field_supplier"), self.d_cb_sup)

        self.d_cb_ing = ttk.Combobox(body, values=[], state="readonly")
        self.d_cb_ing.bind("<<ComboboxSelected>>",
                           lambda e: self._update_total())
        self._frow(body, 1, self.state.tr("sup.field_ingredient"), self.d_cb_ing)

        self.d_e_qty = ttk.Entry(body, justify="right")
        self._frow(body, 2, self.state.tr("sup.field_qty"), self.d_e_qty)
        self.d_e_punit = ttk.Entry(body)
        self.d_e_punit.insert(0, "kg")
        self.d_e_punit.bind("<KeyRelease>", lambda e: self._update_total())
        self._frow(body, 3, self.state.tr("sup.field_punit"),
                   self.d_e_punit)
        self.d_e_units = ttk.Entry(body, justify="right")
        self.d_e_units.insert(0, "")
        self.d_e_units.bind("<KeyRelease>", lambda e: self._update_total())
        self._frow(body, 4, self.state.tr("sup.field_pieces"),
                   self.d_e_units)
        self.d_e_cost = ttk.Entry(body, justify="right")
        self.d_e_cost.insert(0, "0")
        self.d_e_cost.bind("<KeyRelease>", lambda e: self._update_total())
        self._frow(body, 5, self.state.tr("sup.field_price"), self.d_e_cost)

        self.d_lbl_total = tk.Label(body, text="", bg=theme.CARD,
                                    fg=theme.ACCENT_HOVER,
                                    font=("Segoe UI", 11, "bold"))
        self.d_lbl_total.grid(row=6, column=0, columnspan=2, sticky="w")
        self.d_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.d_err.grid(row=7, column=0, columnspan=2, sticky="w")
        ttk.Button(self.f_foot, text=self.state.tr("common.cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("sup.btn_save_delivery"),
                   style="Accent.TButton",
                   command=self._save_delivery).pack(side="right", padx=8)
        self._d_refresh_ings()

    def _d_refresh_ings(self):
        sup_idx = self.d_cb_sup.current()
        if sup_idx < 0:
            return
        sup = self._d_sups[sup_idx]
        self._d_ings = [i for i in self._d_all_ings
                        if i.get("supplier_id") == sup["id"]]
        if not self._d_ings:
            self._d_ings = list(self._d_all_ings)
        labels = [self.state.tr("sup.ing_stock",
                                name=i['name'],
                                qty=f"{float(i['current_stock']):g}",
                                unit=i.get('unit', ''))
                  for i in self._d_ings]
        self.d_cb_ing["values"] = labels
        self.d_cb_ing.current(0) if labels else None

    def _d_find_sup(self):
        idx = self.d_cb_sup.current()
        return idx if 0 <= idx < len(self._d_sups) else 0

    def _d_find_ing(self):
        idx = self.d_cb_ing.current()
        return idx if 0 <= idx < len(self._d_ings) else 0

    def _update_total(self):
        idx = self._d_find_ing()
        if idx < 0 or idx >= len(self._d_ings):
            return
        ing = self._d_ings[idx]
        qty = self._num(self.d_e_qty.get())
        cost = self._num(self.d_e_cost.get())
        punit = (self.d_e_punit.get() or "").strip()
        pieces = self._num(self.d_e_units.get())
        stock_qty = pieces if pieces > 0 else qty
        unit_cost_val = self.state.tr("sup.total_unit_cost",
                                      cost=theme.money(cost / pieces if pieces else 0))
        self.d_lbl_total.config(
            text=self.state.tr("sup.total_summary",
                               qty=f"{qty:g}", unit=punit,
                               stock=f"{stock_qty:g}",
                               ing_unit=ing.get('unit', ''),
                               unit_cost_line=unit_cost_val,
                               total=theme.money(qty * cost))
            if qty > 0 else "")

    def _save_delivery(self):
        try:
            sup_idx = self._d_find_sup()
            ing_idx = self._d_find_ing()
            sup = self._d_sups[sup_idx]
            ing = self._d_ings[ing_idx]
            qty = self._num(self.d_e_qty.get())
            if qty <= 0:
                raise ValueError
            punit = (self.d_e_punit.get() or "").strip()
            pieces = self._num(self.d_e_units.get())
            self.state.suppliers.add_delivery(
                sup["id"], ing["id"], qty,
                self._num(self.d_e_cost.get()),
                self.state.user["name"], pieces, punit)
        except (IndexError, KeyError):
            self.d_err.config(text=self.state.tr("sup.err_invalid_selection"))
            return
        except ValueError:
            self.d_err.config(text=self.state.tr("sup.err_invalid_qty"))
            return
        except Exception as exc:
            self.d_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # -------------------------------------------------- form. paiement ----
    def pay_supplier(self):
        sups = self.state.suppliers.suppliers(active_only=True)
        if not sups:
            show_error(self, self.state.tr("sup.err_no_supplier"))
            return
        sup_sel = self._selected()
        idx_default = 0
        if sup_sel:
            for i, s in enumerate(sups):
                if s["id"] == sup_sel["id"]:
                    idx_default = i
                    break
        self._open_form(self.state.tr("sup.form_pay"),
                        sub=self.state.tr("sup.form_pay_sub"),
                        width=440)
        body = self.f_body
        body.columnconfigure(1, weight=1)

        self._p_sups = sups
        self.p_cb = ttk.Combobox(
            body, values=[x["name"] for x in sups], state="readonly")
        self.p_cb.current(idx_default)
        self._frow(body, 0, self.state.tr("sup.field_supplier"), self.p_cb)

        self.p_e_amount = ttk.Entry(body, justify="right",
                                    font=("Segoe UI", 11, "bold"))
        self._frow(body, 1, self.state.tr("sup.field_amount"), self.p_e_amount)

        self.p_e_note = ttk.Entry(body)
        self._frow(body, 2, self.state.tr("sup.field_note"), self.p_e_note)

        sup0 = sups[idx_default]
        t0 = self.state.suppliers.supplier_totals(sup0["id"])
        self.p_lbl_info = tk.Label(
            body, bg=theme.CARD, fg=theme.TEXT,
            font=theme.FONT_SMALL, wraplength=380, justify="left")
        self.p_lbl_info.grid(row=3, column=0, columnspan=2, sticky="w",
                             pady=(4, 0))
        self._refresh_pay_info()

        self.p_cb.bind("<<ComboboxSelected>>",
                       lambda e: self._refresh_pay_info())

        self.p_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.p_err.grid(row=4, column=0, columnspan=2, sticky="w")
        ttk.Button(self.f_foot, text=self.state.tr("common.cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("sup.btn_save_payment"),
                   style="Success.TButton",
                   command=self._save_payment).pack(side="right", padx=8)
        self.p_e_amount.focus_set()

    def _p_find_sup(self):
        idx = self.p_cb.current()
        return idx if 0 <= idx < len(self._p_sups) else 0

    def _refresh_pay_info(self):
        try:
            idx = self._p_find_sup()
            sup = self._p_sups[idx]
            t = self.state.suppliers.supplier_totals(sup["id"])
        except Exception:
            return
        debt = t["debt"]
        color = theme.SUCCESS if debt <= 0 else theme.DANGER
        self.p_lbl_info.config(
            text=self.state.tr("sup.pay_info",
                               expected=theme.money(t['expected']),
                               paid=theme.money(t['paid']),
                               debt=theme.money(debt)))
        self.p_lbl_info.config(fg=color)

    def _save_payment(self):
        try:
            idx = self._p_find_sup()
            sup = self._p_sups[idx]
            amount = self._num(self.p_e_amount.get())
            if amount <= 0:
                raise ValueError
            self.state.suppliers.add_payment(
                sup["id"], amount, self.state.user["name"],
                self.p_e_note.get().strip())
        except (IndexError, KeyError):
            self.p_err.config(text=self.state.tr("sup.err_invalid_selection"))
            return
        except ValueError:
            self.p_err.config(text=self.state.tr("sup.err_invalid_amount"))
            return
        except Exception as exc:
            self.p_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # ------------------------------------------------------------- actions --
    def edit_selected(self):
        sup = self._selected()
        if not sup:
            show_error(self, self.state.tr("sup.err_select"))
            return
        self._show_supplier_form(sup)

    def toggle_selected(self):
        sup = self._selected()
        if not sup:
            show_error(self, self.state.tr("sup.err_select"))
            return
        try:
            self.state.suppliers.set_active(sup["id"],
                                            not sup.get("active", True))
        except Exception as exc:
            show_error(self, exc)
            return
        self.refresh()

    def delete_selected(self):
        sup = self._selected()
        if not sup:
            show_error(self, self.state.tr("sup.err_select"))
            return
        if not confirm(self, self.state.tr("sup.confirm_delete", name=sup['name'])):
            return
        self.state.suppliers.delete_supplier(sup["id"])
        self.refresh()

    def _selected(self):
        r = getattr(self.grid, "selected_row", None)
        return self._grid_rows.get(r) if r is not None else None

    # ------------------------------------------------------------- refresh --
    def refresh(self):
        sups = self.state.suppliers.suppliers()
        active_n = sum(1 for x in sups if x.get("active", True))
        dls = self.state.suppliers.deliveries(limit=40)
        total_delivered = round(sum(d["total"] for d in dls), 2)

        totals = {}
        total_debt = 0.0
        total_paid = 0.0
        for sup in sups:
            t = self.state.suppliers.supplier_totals(sup["id"])
            totals[sup["id"]] = t
            total_debt += t["debt"]
            total_paid += t["paid"]

        clear(self.kpis)
        for title, val, color in (
                (self.state.tr("sup.title"), str(len(sups)), theme.TEXT),
                (self.state.tr("sup.kpi_active"), str(active_n),
                 theme.SUCCESS if active_n else theme.DANGER),
                (self.state.tr("sup.kpi_delivered"), theme.money(total_delivered),
                 theme.ACCENT_HOVER),
                (self.state.tr("sup.kpi_paid"), theme.money(total_paid),
                 theme.SUCCESS),
                (self.state.tr("sup.kpi_debt"), theme.money(round(total_debt, 2)),
                 theme.DANGER if total_debt > 0 else theme.SUCCESS)):
            f = tk.Frame(self.kpis, bg=theme.CARD)
            f.pack(side="left", padx=(0, 24))
            tk.Label(f, text=title.upper(), bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL).pack(anchor="w")
            tk.Label(f, text=val, bg=theme.CARD, fg=color,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")

        # -- tableau fournisseurs ------------------------------------------
        for w in self.grid_holder.winfo_children():
            w.destroy()
        self.grid = DataGrid(self.grid_holder, [
            ("name", self.state.tr("sup.col_supplier"), 140, "w", True),
            ("contact", self.state.tr("sup.col_contact"), 120, "w", True),
            ("phone", self.state.tr("sup.phone"), 100, "center", False),
            ("products", self.state.tr("sup.field_products"), 160, "w", True),
            ("expected", self.state.tr("sup.col_expected"), 120, "e", False),
            ("paid", self.state.tr("sup.col_paid"), 110, "e", False),
            ("debt", self.state.tr("sup.debt"), 110, "e", False),
        ])
        self.grid.pack(fill="both", expand=True)
        self._grid_rows = {}
        for x in sups:
            on = x.get("active", True)
            t = totals.get(x["id"], {"expected": 0, "paid": 0, "debt": 0})
            debt = t["debt"]
            if debt > 0:
                debt_fg = theme.DANGER
            elif debt < 0:
                debt_fg = "#2563eb"
            else:
                debt_fg = theme.SUCCESS
            r = self.grid.add_row(
                (x["name"], x.get("contact", ""), x.get("phone", ""),
                 x.get("products", ""),
                 theme.money(t["expected"]),
                 theme.money(t["paid"]),
                 theme.money(debt)),
                fg=[theme.TEXT, theme.MUTED, theme.TEXT, theme.MUTED,
                    theme.TEXT, theme.SUCCESS if t["paid"] else theme.MUTED,
                    debt_fg],
                fonts=[None, None, None, None, None, None,
                       ("Segoe UI", 10, "bold")])
            self._grid_rows[r] = x

        # -- tableau livraisons --------------------------------------------
        for w in self.dl_holder.winfo_children():
            w.destroy()
        self.dl_grid = DataGrid(self.dl_holder, [
            ("at", self.state.tr("sup.col_date"), 145, "w", False),
            ("supplier", self.state.tr("sup.col_supplier"), 130, "w", True),
            ("ing", self.state.tr("sup.col_ingredient"), 110, "w", True),
            ("qty", self.state.tr("sup.col_purchased"), 90, "e", False),
            ("in", self.state.tr("sup.col_in_stock"), 100, "e", False),
            ("cost", self.state.tr("sup.col_unit_cost"), 90, "e", False),
            ("total", self.state.tr("sup.col_total"), 95, "e", False),
            ("by", self.state.tr("sup.col_by"), 80, "center", False),
        ])
        self.dl_grid.pack(fill="both", expand=True)
        self._dl_rows = {}
        for d in dls:
            punit = d.get("purchase_unit", "")
            qty_s = f"{d['qty']:g}{(' ' + punit) if punit else ''}"
            self.dl_grid.add_row(
                (d["at"][:16], d["supplier_name"], d["ingredient_name"],
                 qty_s,
                 f"{float(d.get('stock_qty', d['qty'])):g} "
                 f"{d.get('ing_unit', '')}".strip(),
                 theme.money(d["unit_cost"]), theme.money(d["total"]),
                 d["by"]),
                fg=[theme.MUTED, theme.TEXT, theme.TEXT, theme.TEXT,
                    theme.SUCCESS,
                    theme.MUTED, theme.ACCENT_HOVER, theme.MUTED])
