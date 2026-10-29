"""Onglet Personnel (admin) : comptes du personnel et acces a l'application.

Tableau DataGrid avec vraies separations, formulaires FLOTTANTS camoufles
dans l'onglet — aucune fenetre de dialogue.
"""
import tkinter as tk
from tkinter import ttk

from .. import theme
from ...services import MODULES, BizError
from ..widgets import DataGrid, clear, confirm, info, show_error


class StaffView(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, style="TFrame")
        self.state = state
        self._grid_rows = {}
        self._build()
        self.refresh()

    # ------------------------------------------------------------- layout --
    def _build(self):
        holder = tk.Frame(self, bg=theme.CARD, highlightthickness=1,
                          highlightbackground="#e5ded0")
        holder.pack(fill="both", expand=True, padx=10, pady=10)

        top = tk.Frame(holder, bg=theme.CARD)
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(top, text=self.state.tr("staff.title"), bg=theme.CARD,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        btns = tk.Frame(top, bg=theme.CARD)
        btns.pack(side="right")
        ttk.Button(btns, text=self.state.tr("staff.btn_new_employee"),
                   style="Accent.TButton",
                   command=self.new_staff).pack(side="left", padx=2)
        ttk.Button(btns, text=self.state.tr("staff.btn_manage_roles"),
                   command=self.roles_manager).pack(side="left", padx=2)
        ttk.Button(btns, text=self.state.tr("staff.btn_new_advance"),
                   command=self.new_advance).pack(side="left", padx=2)
        ttk.Button(btns, text=self.state.tr("staff.btn_pay_salary"),
                   style="Success.TButton",
                   command=self.new_payment).pack(side="left", padx=2)

        self.kpis = tk.Frame(holder, bg=theme.CARD)
        self.kpis.pack(fill="x", padx=12, pady=(2, 6))

        self.grid_holder = tk.Frame(holder, bg=theme.CARD)
        self.grid_holder.pack(fill="both", expand=True, padx=12, pady=(2, 0))

        actions = tk.Frame(holder, bg=theme.CARD)
        actions.pack(fill="x", padx=10, pady=(6, 4))
        ttk.Button(actions, text=self.state.tr("staff.btn_edit"),
                   command=self.edit_staff).pack(side="left", padx=2)
        ttk.Button(actions, text=self.state.tr("staff.btn_toggle_active"),
                   command=self.toggle_active).pack(side="left", padx=2)
        ttk.Button(actions, text=self.state.tr("staff.btn_delete"),
                   style="Danger.TButton",
                   command=self.delete_staff).pack(side="left", padx=2)

        sep = tk.Frame(holder, bg=DataGrid.SEP, height=1)
        sep.pack(fill="x", padx=12, pady=(4, 2))

        pay_head = tk.Frame(holder, bg=theme.CARD)
        pay_head.pack(fill="x", padx=12, pady=(2, 2))
        self.pay_head_label = tk.Label(
            pay_head, text=self.state.tr("staff.section_movements"),
            bg=theme.CARD, font=("Segoe UI", 11, "bold"))
        self.pay_head_label.pack(side="left")
        cb = ttk.Combobox(pay_head, state="readonly", width=14)
        months = self.state.payroll.salary_months()
        self._month_keys = months
        cb["values"] = [self.state.payroll.month_label(m) for m in months]
        cb.current(len(months) - 1)
        cb.pack(side="right")
        self.cb_month = cb
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_movements())
        ttk.Button(pay_head, text=self.state.tr("staff.btn_payslip"),
                   command=self.gen_fiche_paie).pack(side="right", padx=(0, 8))

        self.pay_holder = tk.Frame(holder, bg=theme.CARD)
        self.pay_holder.pack(fill="both", expand=True, padx=12, pady=(0, 2))

        note = tk.Label(
            holder,
            text=self.state.tr("staff.note_roles"),
            bg=theme.CARD, fg=theme.MUTED, font=theme.FONT_SMALL,
            justify="left")
        note.pack(anchor="w", padx=14, pady=(2, 8))

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
    def _open_form(self, title, sub, width=460):
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
                 font=theme.FONT_SMALL, width=18, anchor="w"
                 ).grid(row=row, column=0, sticky="w", pady=5)
        widget.grid(row=row, column=1, sticky="ew", pady=5)

    # ------------------------------------------------ gestion des roles ------
    def roles_manager(self):
        """Affiche la liste des roles et leurs permissions."""
        roles = self.state.roles.roles()
        self._open_form(self.state.tr("staff.form_roles_title"),
                        sub=self.state.tr("staff.form_roles_sub"), width=520)
        body = self.f_body
        body.columnconfigure(1, weight=1)

        # liste des rôles
        for i, r in enumerate(roles):
            tk.Label(body, text=r["name"], bg=theme.CARD, fg=theme.TEXT,
                     font=theme.FONT_BOLD).grid(
                row=i, column=0, sticky="w", pady=3)
            mods = ", ".join(MODULES[m] for m in r["modules"]
                             if m in MODULES) or "—"
            tk.Label(body, text=mods, bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL, justify="left",
                     wraplength=330).grid(
                row=i, column=1, sticky="w", pady=3)
            if r["key"] not in ("admin", "caissiere"):
                btns = tk.Frame(body, bg=theme.CARD)
                btns.grid(row=i, column=2, sticky="e", padx=4)
                ttk.Button(btns, text="✎",
                           width=3,
                           command=lambda k=r["key"]: self.edit_role(k)
                           ).pack(side="left", padx=1)
                ttk.Button(btns, text="🗑", width=3, style="Danger.TButton",
                           command=lambda k=r["key"]: self.delete_role(k)
                           ).pack(side="left", padx=1)

        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_close"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_new_role"),
                   style="Accent.TButton",
                   command=self.new_role).pack(side="right", padx=8)

    def new_role(self):
        self._edit_role_form(None)

    def edit_role(self, key):
        role = self.state.roles.role_by_key(key)
        if role:
            self._edit_role_form(role)

    def delete_role(self, key):
        if not confirm(self, self.state.tr("staff.confirm_delete_role")):
            return
        try:
            self.state.roles.delete_role(key)
        except Exception as exc:
            show_error(self, str(exc))
            return
        self.roles_manager()

    def _edit_role_form(self, role):
        self._open_form(
            self.state.tr("staff.form_new_role") if not role else
            self.state.tr("staff.form_edit_role", name=role['name']),
            sub=self.state.tr("staff.form_role_sub"),
            width=480)
        body = self.f_body
        body.columnconfigure(1, weight=1)

        self._role_form_role = role
        self.e_role_name = ttk.Entry(body)
        self._frow(body, 0, self.state.tr("staff.label_role_name"),
                   self.e_role_name)
        if role:
            self.e_role_name.insert(0, role["name"])

        tk.Label(body, text=self.state.tr("staff.label_tab_access"),
                 bg=theme.CARD,
                 fg=theme.MUTED, font=theme.FONT_SMALL, width=18,
                 anchor="w").grid(row=1, column=0, sticky="w", pady=5)
        mod_holder = tk.Frame(body, bg=theme.CARD)
        mod_holder.grid(row=1, column=1, sticky="w", pady=5)
        self._mod_vars = {}
        cur = set(role["modules"]) if role else set()
        for j, (mkey, mlabel) in enumerate(MODULES.items()):
            var = tk.BooleanVar(value=mkey in cur)
            self._mod_vars[mkey] = var
            tk.Checkbutton(mod_holder, text=mlabel, variable=var,
                           bg=theme.CARD, fg=theme.TEXT, activebackground=theme.CARD,
                           font=theme.FONT_SMALL).grid(
                row=j // 2, column=j % 2, sticky="w", padx=(0, 12), pady=2)

        self.role_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                                 font=theme.FONT_SMALL)
        self.role_err.grid(row=2, column=0, columnspan=2, sticky="w")
        self.e_role_name.focus_set()

        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_cancel"),
                   command=lambda: self.roles_manager()).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_save"),
                   style="Accent.TButton",
                   command=self._save_role).pack(side="right", padx=8)

    def _save_role(self):
        name = self.e_role_name.get().strip().lower()
        key = name.replace(" ", "_")
        modules = [m for m, v in self._mod_vars.items() if v.get()]
        try:
            self.state.roles.save_role(key, name, modules)
        except Exception as exc:
            self.role_err.config(text=str(exc))
            return
        self.roles_manager()

    # -------------------------------------------------- form. employe ------
    def new_staff(self):
        self._show_staff_form(None)

    def edit_staff(self):
        user = self._selected_user()
        if not user:
            show_error(self, self.state.tr("staff.err_select_employee"))
            return
        self._show_staff_form(user)

    def _show_staff_form(self, user):
        self._form_user = user
        self._open_form(
            self.state.tr("staff.form_edit_employee") if user
            else self.state.tr("staff.form_new_employee"),
            sub=self.state.tr("staff.form_employee_sub"))
        body = self.f_body
        body.columnconfigure(1, weight=1)
        self.e_name = ttk.Entry(body)
        self._frow(body, 0, self.state.tr("staff.label_full_name"),
                   self.e_name)
        self.e_username = ttk.Entry(body)
        self._frow(body, 1, self.state.tr("staff.label_username"),
                   self.e_username)

        self._roles = self.state.roles.roles()
        self.cb_role = ttk.Combobox(
            body, state="readonly", width=25,
            values=[r["name"] for r in self._roles])
        self._frow(body, 2, self.state.tr("staff.label_role"), self.cb_role)
        idx = next((i for i, r in enumerate(self._roles)
                    if r["key"] == (user["role"] if user else "caissiere")), 0)
        self.cb_role.current(idx)

        self.e_salary = ttk.Entry(body, justify="right")
        self.e_salary.insert(0, "0")
        self._frow(body, 3, self.state.tr("staff.label_salary"),
                   self.e_salary)

        self.e_password = None
        if not user:
            self.e_password = ttk.Entry(body, show="•")
            self._frow(body, 4, self.state.tr("staff.label_password"),
                       self.e_password)

        self.s_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        err_row = 5 if not user else 4
        self.s_err.grid(row=err_row, column=0, columnspan=2, sticky="w")

        if user:
            self.e_name.insert(0, user["name"])
            self.e_username.insert(0, user["username"])
            self.e_salary.delete(0, "end")
            self.e_salary.insert(
                0, f"{max(0, int(user.get('salary', 0) or 0)):g}")
            tk.Label(body,
                     text=self.state.tr("staff.note_password_hint"),
                     bg=theme.CARD, fg=theme.MUTED, font=theme.FONT_SMALL,
                     justify="left").grid(row=err_row + 1, column=0,
                                          columnspan=2, sticky="w",
                                          pady=(4, 0))

        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_save"),
                   style="Accent.TButton",
                   command=self._save_staff).pack(side="right", padx=8)
        self.e_name.focus_set()

    def _save_staff(self):
        name = self.e_name.get().strip()
        username = self.e_username.get().strip()
        role = self._roles[self.cb_role.current()]["key"]
        user = self._form_user
        if not name or not username or (not user and
                                        not self.e_password.get()):
            self.s_err.config(
                text=self.state.tr("staff.err_fill_required"))
            return
        try:
            salary = float(
                (self.e_salary.get() or "0").replace(",", ".").replace(" ", "")
                or 0)
            if user:
                self.state.auth.update_staff(user["id"], name, username, role,
                                             salary, roles=self.state.roles)
            else:
                self.state.auth.add_staff(name, username,
                                          self.e_password.get(), role,
                                          roles=self.state.roles)
                created = self.state.auth.user_by_username(username)
                if created:
                    self.state.auth.set_salary(created["id"], salary)
        except Exception as exc:
            self.s_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # -------------------------------------------------- form. reset pwd ----
    def reset_password(self):
        user = self._selected_user()
        if not user:
            show_error(self, self.state.tr("staff.err_select_employee"))
            return
        self._form_user = user
        self._open_form(
            self.state.tr("staff.form_reset_title", name=user['name']),
            sub=self.state.tr("staff.form_reset_sub"),
            width=420)
        body = self.f_body
        body.columnconfigure(1, weight=1)
        self.e_pwd = ttk.Entry(body, show="•")
        self._frow(body, 0, self.state.tr("staff.label_new_password"),
                   self.e_pwd)
        self.e_pwd2 = ttk.Entry(body, show="•")
        self._frow(body, 1, self.state.tr("staff.label_confirm"),
                   self.e_pwd2)
        self.s_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.s_err.grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_reset"),
                   style="Accent.TButton",
                   command=self._save_password).pack(side="right", padx=8)
        self.e_pwd.focus_set()

    def _save_password(self):
        pwd = self.e_pwd.get()
        pwd2 = self.e_pwd2.get()
        if pwd != pwd2:
            self.s_err.config(
                text=self.state.tr("staff.err_password_mismatch"))
            return
        try:
            self.state.auth.reset_staff_password(
                self._form_user["id"], pwd)
        except Exception as exc:
            self.s_err.config(text=str(exc))
            return
        self._hide_form()
        self.refresh()

    # ------------------------------------------------------------- actions --
    def toggle_active(self):
        user = self._selected_user()
        if not user:
            show_error(self, self.state.tr("staff.err_select_employee"))
            return
        is_active = user.get("active", True)
        action_key = ("staff.action_block" if is_active
                      else "staff.action_reactivate")
        action = self.state.tr(action_key)
        if not confirm(self, self.state.tr("staff.confirm_toggle",
                                           action=action.capitalize(),
                                           name=user['name'])):
            return
        try:
            self.state.auth.set_staff_active(user["id"], not is_active,
                                             self.state.user)
        except Exception as exc:
            show_error(self, exc)
        self.refresh()

    def delete_staff(self):
        user = self._selected_user()
        if not user:
            show_error(self, self.state.tr("staff.err_select_employee"))
            return
        if not confirm(self, self.state.tr("staff.confirm_delete_employee",
                                           name=user['name'])):
            return
        try:
            self.state.auth.delete_staff(user["id"], self.state.user)
        except Exception as exc:
            show_error(self, exc)
        self.refresh()

    # ------------------------------------------------------------- helpers --
    def _selected_user(self):
        r = getattr(self.grid, "selected_row", None)
        return self._grid_rows.get(r) if r is not None else None

    # ------------------------------------------------------------- refresh --
    def refresh(self):
        staff = self.state.auth.staff()
        active = [u for u in staff if u.get("active", True)]
        admins = [u for u in staff if u["role"] == "admin"]
        blocked = len(staff) - len(active)
        month = self.state.payroll.current_month()
        adv_total = sum(
            self.state.payroll.advance_total(u["id"], month) for u in staff if
            u["role"] != "admin")
        pay_total = sum(
            self.state.payroll.paid_total(u["id"], month) for u in staff)
        net_total = sum(
            self.state.payroll.net_to_pay(u["id"], month)
            for u in staff if u["role"] != "admin")

        clear(self.kpis)
        for title, val, color in (
                (self.state.tr("staff.kpi_employees"),
                 str(len(staff)), theme.TEXT),
                (self.state.tr("staff.kpi_active"),
                 str(len(active)), theme.SUCCESS),
                (self.state.tr("staff.kpi_blocked"),
                 str(blocked),
                 theme.DANGER if blocked else theme.MUTED),
                (self.state.tr("staff.kpi_advances"),
                 theme.money(adv_total), theme.ACCENT),
                (self.state.tr("staff.kpi_paid"),
                 theme.money(pay_total), theme.SUCCESS),
                (self.state.tr("staff.kpi_net"),
                 theme.money(net_total), theme.ACCENT_HOVER)):
            f = tk.Frame(self.kpis, bg=theme.CARD)
            f.pack(side="left", padx=(0, 30))
            tk.Label(f, text=title.upper(), bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL).pack(anchor="w")
            tk.Label(f, text=val, bg=theme.CARD, fg=color,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")

        for w in self.grid_holder.winfo_children():
            w.destroy()
        self.grid = DataGrid(self.grid_holder, [
            ("name", self.state.tr("staff.col_name"), 200, "w", True),
            ("username", self.state.tr("staff.col_username"), 130, "w", True),
            ("role", self.state.tr("staff.col_role"), 130, "center", False),
            ("salary", self.state.tr("staff.col_salary"), 110, "e", False),
            ("status", self.state.tr("staff.col_status"), 100, "center", False),
        ])
        self.grid.pack(fill="both", expand=True)
        self._grid_rows = {}
        for u in staff:
            is_active = u.get("active", True)
            if u["role"] == "admin":
                role_fg = theme.ACCENT_HOVER
            else:
                role_fg = theme.TEXT
            status_fg = theme.SUCCESS if is_active else theme.DANGER
            r = self.grid.add_row(
                (u["name"], u["username"],
                 self.state.roles.label(u["role"]),
                 theme.money(int(u.get("salary", 0) or 0)),
                 self.state.tr("staff.status_active") if is_active
                 else self.state.tr("staff.status_blocked")),
                fg=[theme.TEXT, theme.MUTED, role_fg, theme.TEXT, status_fg])
            self._grid_rows[r] = u

        # Refresh month list and combobox
        prev_month = self._selected_month()
        months = self.state.payroll.salary_months()
        self._month_keys = months
        self.cb_month["values"] = [
            self.state.payroll.month_label(m) for m in months]
        if prev_month in months:
            self.cb_month.current(months.index(prev_month))
        elif months:
            self.cb_month.current(len(months) - 1)
        self.refresh_movements()

    def gen_fiche_paie(self):
        user = self._selected_user()
        if not user or user["role"] == "admin":
            show_error(self, self.state.tr("staff.err_select_employee_payslip"))
            return
        from ...pdf_generator import fiche_paie
        month = self._selected_month()
        try:
            path = fiche_paie(self.state, user, month)
        except Exception as exc:
            show_error(self, self.state.tr("staff.err_payslip", error=exc))
            return
        info(self, self.state.tr("staff.payslip_success", path=path))
        self.refresh()

    # --------------------------------------------------- mouvements salaires --
    def _selected_month(self):
        months = getattr(self, "_month_keys",
                         [self.state.payroll.current_month()]) or \
            [self.state.payroll.current_month()]
        idx = self.cb_month.current()
        if 0 <= idx < len(months):
            return months[idx]
        return months[-1]

    def refresh_movements(self):
        month = self._selected_month()
        self.pay_head_label.config(
            text=self.state.tr("staff.movements_title",
                               month=self.state.payroll.month_label(month)))
        staff = self.state.auth.staff()
        for w in self.pay_holder.winfo_children():
            w.destroy()
        g = DataGrid(self.pay_holder, [
            ("name", self.state.tr("staff.paycol_employee"), 200, "w", False),
            ("salary", self.state.tr("staff.paycol_salary"), 110, "e", False),
            ("adv", self.state.tr("staff.paycol_advances"), 110, "e", False),
            ("paid", self.state.tr("staff.paycol_paid"), 110, "e", False),
            ("net", self.state.tr("staff.paycol_net"), 130, "e", False),
        ])
        g.pack(fill="both", expand=True)
        for u in staff:
            if u["role"] == "admin":
                continue
            salary = self.state.payroll.monthly_salary(u)
            adv = self.state.payroll.advance_total(u["id"], month)
            paid = self.state.payroll.paid_total(u["id"], month)
            net = self.state.payroll.net_to_pay(u["id"], month)
            fg = theme.MUTED
            if adv == 0 and paid == 0:
                fg = theme.MUTED
            elif net == 0:
                fg = theme.SUCCESS
            g.add_row(
                (u["name"], theme.money(salary), theme.money(adv),
                 theme.money(paid), theme.money(net)),
                fg=[theme.TEXT, theme.TEXT, theme.ACCENT, theme.SUCCESS,
                    fg])

    # ------------------------------------------------ form. avance / salaire --
    def _pick_staff(self, title, sub, on_save, btn_label, only_salary=True):
        staff = [u for u in self.state.auth.staff() if u["role"] != "admin"]
        if not staff:
            show_error(self, self.state.tr("staff.err_create_first"))
            return
        sel = self._selected_user()
        idx = 0
        if sel:
            for i, u in enumerate(staff):
                if u["id"] == sel["id"]:
                    idx = i
                    break
        self._open_form(title, sub, width=440)
        body = self.f_body
        body.columnconfigure(1, weight=1)
        self._pay_staff = staff
        self.p_cb = ttk.Combobox(
            body, values=[u["name"] for u in staff], state="readonly")
        self.p_cb.current(idx)
        self._frow(body, 0, self.state.tr("staff.paylabel_employee"),
                   self.p_cb)
        self.p_amo = ttk.Entry(body, justify="right",
                               font=("Segoe UI", 11, "bold"))
        self._frow(body, 1, self.state.tr("staff.paylabel_amount"),
                   self.p_amo)
        self.p_note = ttk.Entry(body)
        self._frow(body, 2, self.state.tr("staff.paylabel_note"),
                   self.p_note)
        self.p_info = tk.Label(body, bg=theme.CARD, fg=theme.TEXT,
                               font=theme.FONT_SMALL, wraplength=360,
                               justify="left")
        self.p_info.grid(row=3, column=0, columnspan=2, sticky="w",
                         pady=(2, 0))
        self._refresh_pick_info()
        self.p_cb.bind("<<ComboboxSelected>>",
                       lambda e: self._refresh_pick_info())
        self.p_err = tk.Label(body, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.p_err.grid(row=4, column=0, columnspan=2, sticky="w")
        self._pay_on_save = on_save
        ttk.Button(self.f_foot, text=self.state.tr("staff.btn_cancel"),
                   command=self._hide_form).pack(side="right")
        ttk.Button(self.f_foot, text=btn_label, style="Accent.TButton",
                   command=self._save_pick).pack(side="right", padx=8)
        self.p_amo.focus_set()

    def _selected_pay_user(self):
        idx = self.p_cb.current()
        if 0 <= idx < len(self._pay_staff):
            return self._pay_staff[idx]
        return None

    def _refresh_pick_info(self):
        u = self._selected_pay_user()
        if not u:
            return
        month = self.state.payroll.current_month()
        salary = self.state.payroll.monthly_salary(u)
        adv = self.state.payroll.advance_total(u["id"], month)
        paid = self.state.payroll.paid_total(u["id"], month)
        net = self.state.payroll.net_to_pay(u["id"], month)
        self.p_info.config(
            text=self.state.tr("staff.payinfo",
                               salary=theme.money(salary),
                               adv=theme.money(adv),
                               paid=theme.money(paid),
                               net=theme.money(net)))

    def new_advance(self):
        self._pick_staff(self.state.tr("staff.form_advance_title"),
                         self.state.tr("staff.form_advance_sub"),
                         "advance",
                         self.state.tr("staff.btn_save_advance"))

    def new_payment(self):
        self._pick_staff(self.state.tr("staff.form_payment_title"),
                         self.state.tr("staff.form_payment_sub"),
                         "payment",
                         self.state.tr("staff.btn_save_payment"))

    def _save_pick(self):
        u = self._selected_pay_user()
        if not u:
            self.p_err.config(text=self.state.tr("staff.err_select_employee_short"))
            return
        try:
            amount = float((self.p_amo.get() or "0").replace(",", ".").
                           replace(" ", "") or 0)
        except ValueError:
            amount = 0
        mode = self._pay_on_save
        try:
            if mode == "advance":
                self.state.payroll.add_advance(
                    u["id"], amount, self.state.user["name"],
                    self.p_note.get().strip())
            else:
                self.state.payroll.pay_salary(
                    u["id"], amount, self.state.user["name"],
                    self.p_note.get().strip())
        except BizError as exc:
            self.p_err.config(text=str(exc))
            return
        except ValueError:
            self.p_err.config(text=self.state.tr("staff.err_invalid_amount"))
            return
        except Exception as exc:
            self.p_err.config(text=str(exc))
            return
        self._hide_form()
        if not hasattr(self, "_month_keys"):
            self._month_keys = self.state.payroll.salary_months()
        m = self.state.payroll.current_month()
        if m in self._month_keys:
            self.cb_month.current(self._month_keys.index(m))
        else:
            self._month_keys = self.state.payroll.salary_months()
            self.cb_month["values"] = [
                self.state.payroll.month_label(x) for x in self._month_keys]
            self.cb_month.current(len(self._month_keys) - 1)
        self.refresh()
