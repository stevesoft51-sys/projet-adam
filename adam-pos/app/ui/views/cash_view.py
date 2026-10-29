"""Onglet Caisse : session (ouverture / mouvements / cloture) + historique.

Les trois etats (caisse fermee, formulaire d'ouverture, caisse ouverte)
s'affichent en camouflage dans les memes cartes : aucune fenetre flottante.
"""
import tkinter as tk
from tkinter import ttk

from .. import theme
from ..widgets import clear, confirm, DataGrid


def _card(parent) -> tk.Frame:
    """Carte blanche sans placement automatique (voir PosView._card_cell)."""
    return tk.Frame(parent, bg=theme.CARD, highlightthickness=1,
                    highlightbackground="#e5ded0")


def _stable_combobox(cb: ttk.Combobox):
    """Ferme la liste deroulante quand l'application perd le focus,
    mais la laisse ouverte si le focus passe a sa propre liste."""

    def close(_event=None):
        try:
            focused = str(cb.tk.call("focus"))
        except tk.TclError:
            focused = ""
        if focused.startswith(str(cb)) or ".popdown" in focused:
            return          # l'utilisateur interagit encore avec la liste
        try:
            cb.tk.eval(f"catch {{ttk::combobox::Unpost {cb}}}")
        except tk.TclError:
            pass

    cb.bind("<FocusOut>", close)
    cb.winfo_toplevel().bind("<Deactivate>", close, add="+")


class CashView(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, style="TFrame")
        self.state = state
        self._show_open_form = False      # camouflage du formulaire d'ouverture
        self._expected = 0.0              # attendu de la session affichee
        self._build()
        self.refresh()

    def _build(self):
        self.top_card = _card(self)
        self.top_card.pack(fill="x", padx=10, pady=(10, 5))
        self.body_card = _card(self)
        self.body_card.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ------------------------------------------------------------- refresh --
    def refresh(self):
        session = self.state.cash.get_open()
        clear(self.top_card)
        clear(self.body_card)
        if session:
            self._render_status(session)
            self._render_session_body(session)
        elif self._show_open_form:
            self._render_open_form()
            self._render_sessions_table()
        else:
            self._render_closed_banner()
            self._render_sessions_table()

    # -------------------------------------------------- caisse fermee -------
    def _render_closed_banner(self):
        body = self.top_card
        row = tk.Frame(body, bg=theme.CARD)
        row.pack(fill="x", padx=14, pady=12)
        box = tk.Frame(row, bg=theme.CARD)
        box.pack(side="left")
        tk.Label(box, text=self.state.tr("cash.session_closed").upper(),
                 bg=theme.CARD, fg=theme.DANGER,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(box, text=self.state.tr("cash.open_hint"),
                 bg=theme.CARD, fg=theme.MUTED).pack(anchor="w")
        ttk.Button(row, text=self.state.tr("cash.open"), style="Success.TButton",
                   command=self._start_open).pack(side="right")

    def _render_open_form(self):
        """Formulaire integre : montant reellement trouve dans la caisse."""
        body = self.top_card
        head = tk.Frame(body, bg=theme.CARD)
        head.pack(fill="x", padx=14, pady=(12, 2))
        tk.Label(head, text=self.state.tr("cash.open").upper(), bg=theme.CARD,
                 fg=theme.SUCCESS,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(head, text=self.state.tr("cash.opened_by_name",
                                            name=self.state.user['name']),
                 bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="left", padx=12)

        row = tk.Frame(body, bg=theme.CARD)
        row.pack(fill="x", padx=14, pady=(8, 0))
        tk.Label(row, text=self.state.tr("cash.amount_found_fcfa"),
                 bg=theme.CARD,
                 fg=theme.TEXT, font=theme.FONT_BOLD).pack(side="left")
        self.e_open = ttk.Entry(row, justify="right",
                                font=("Segoe UI", 12, "bold"), width=14)
        self.e_open.insert(0, "5000")
        self.e_open.pack(side="right")
        self.e_open.bind("<Return>", lambda e: self._submit_open())
        self.e_open.focus_set()

        self.lbl_open_err = tk.Label(body, text="", bg=theme.CARD,
                                     fg=theme.DANGER, font=theme.FONT_SMALL)
        self.lbl_open_err.pack(anchor="w", padx=14)

        btns = tk.Frame(body, bg=theme.CARD)
        btns.pack(fill="x", padx=14, pady=(4, 12))
        ttk.Button(btns, text=self.state.tr("common.cancel"), command=self._cancel_open,
                   width=10).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text=self.state.tr("cash.open"), style="Success.TButton",
                   command=self._submit_open).pack(side="right")

    def _start_open(self):
        self._show_open_form = True
        self.refresh()

    def _cancel_open(self):
        self._show_open_form = False
        self.refresh()

    def _submit_open(self):
        raw = self.e_open.get().replace(",", ".").replace(" ", "") or "0"
        try:
            amount = float(raw)
            if amount < 0:
                raise ValueError
        except ValueError:
            self.lbl_open_err.config(text=self.state.tr("cash.invalid_amount"))
            return
        try:
            self.state.cash.open_session(amount, self.state.user)
        except Exception as exc:
            self.lbl_open_err.config(text=str(exc))
            return
        self._show_open_form = False
        self.refresh()

    # --------------------------------------------------- caisse ouverte -----
    def _render_status(self, session):
        body = self.top_card
        head = tk.Frame(body, bg=theme.CARD)
        head.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(head, text="●  " + self.state.tr("cash.session_open").upper(),
                 bg=theme.CARD,
                 fg=theme.SUCCESS,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(head, bg=theme.CARD, fg=theme.MUTED, font=theme.FONT_SMALL,
                 text=self.state.tr("cash.opened_info",
                                     date=session['opened_at'],
                                     user=session['opened_by'])).pack(side="left", padx=14)

        self._expected = self.state.cash.expected_amount(session)
        grid = tk.Frame(body, bg=theme.CARD)
        grid.pack(fill="x", padx=14, pady=(6, 12))

        def stat(col, title, value, color=theme.TEXT):
            f = tk.Frame(grid, bg=theme.CARD)
            f.grid(row=0, column=col, sticky="w", padx=(0, 30))
            tk.Label(f, text=title.upper(), bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL).pack(anchor="w")
            tk.Label(f, text=value, bg=theme.CARD, fg=color,
                     font=("Segoe UI", 14, "bold")).pack(anchor="w")

        stat(0, self.state.tr("cash.opening_balance"), theme.money(session["opening_amount"]))
        stat(1, self.state.tr("cash.add_in"), theme.money(session["total_cash_in"]), theme.SUCCESS)
        stat(2, self.state.tr("cash.add_out"), theme.money(session["total_cash_out"]), theme.DANGER)
        stat(3, self.state.tr("cash.expected"), theme.money(self._expected),
             theme.ACCENT_HOVER)

    def _render_session_body(self, session):
        body = self.body_card
        body.columnconfigure(0, weight=1, uniform="cashcol")
        body.columnconfigure(1, weight=2, uniform="cashcol")
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=theme.BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        right = tk.Frame(body, bg=theme.BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self._build_movement_form(left)
        self._build_close_box(left)
        self._build_day_journal(right, session)

    # -- sous-section : mouvement de caisse ---------------------------------
    def _build_movement_form(self, left):
        card = _card(left)
        card.grid(row=0, column=0, sticky="nsew")
        tk.Label(card, text=self.state.tr("cash.movement_header").upper(),
                 bg=theme.CARD,
                 fg=theme.ACCENT_HOVER,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12,
                                                     pady=(12, 6))

        row_t = tk.Frame(card, bg=theme.CARD)
        row_t.pack(fill="x", padx=12, pady=4)
        tk.Label(row_t, text=self.state.tr("cash.type"), bg=theme.CARD,
                 fg=theme.MUTED,
                 font=theme.FONT_SMALL, width=10,
                 anchor="w").pack(side="left")
        self.cb_type = ttk.Combobox(row_t, values=("Entrée", "Sortie"),
                                    state="readonly", width=17)
        self.cb_type.current(0)
        self.cb_type.pack(side="right")
        _stable_combobox(self.cb_type)

        row_a = tk.Frame(card, bg=theme.CARD)
        row_a.pack(fill="x", padx=12, pady=4)
        tk.Label(row_a, text=self.state.tr("cash.amount"), bg=theme.CARD,
                 fg=theme.MUTED,
                 font=theme.FONT_SMALL, width=10,
                 anchor="w").pack(side="left")
        self.e_mv_amount = ttk.Entry(row_a, justify="right", width=19)
        self.e_mv_amount.pack(side="right")

        row_r = tk.Frame(card, bg=theme.CARD)
        row_r.pack(fill="x", padx=12, pady=4)
        tk.Label(row_r, text=self.state.tr("cash.reason"), bg=theme.CARD,
                 fg=theme.MUTED,
                 font=theme.FONT_SMALL, width=10,
                 anchor="n").pack(side="left", pady=4)
        self.e_reason = tk.Text(row_r, height=3, font=theme.FONT, padx=5,
                                pady=4, relief="solid", bd=1, bg="#ffffff",
                                highlightthickness=0)
        self.e_reason.pack(side="right", fill="both", expand=True)

        self.lbl_move_err = tk.Label(card, text="", bg=theme.CARD,
                                     fg=theme.DANGER, font=theme.FONT_SMALL,
                                     wraplength=260, justify="left")
        self.lbl_move_err.pack(anchor="w", padx=12)

        ttk.Button(card, text=self.state.tr("cash.save_movement"),
                   style="Accent.TButton",
                   command=self._submit_movement).pack(fill="x", padx=12,
                                                       pady=(6, 12))
        self.e_mv_amount.focus_set()

    def _submit_movement(self):
        mtype = "in" if self.cb_type.get() == "Entrée" else "out"
        raw = self.e_mv_amount.get().replace(",", ".").replace(" ", "")
        reason = self.e_reason.get("1.0", "end").strip()
        try:
            amount = float(raw)
            if not reason:
                raise ValueError("raison")
        except ValueError:
            self.lbl_move_err.config(
                text=self.state.tr("cash.required_fields"))
            return
        try:
            self.state.cash.add_movement(mtype, amount, reason,
                                         self.state.user)
        except Exception as exc:
            self.lbl_move_err.config(text=str(exc))
            return
        self.refresh()

    # -- sous-section : fermeture -------------------------------------------
    def _build_close_box(self, left):
        card = _card(left)
        card.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        tk.Label(card, text=self.state.tr("cash.close").upper(), bg=theme.CARD,
                 fg=theme.DANGER,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12,
                                                     pady=(12, 4))
        row = tk.Frame(card, bg=theme.CARD)
        row.pack(fill="x", padx=12)
        tk.Label(row, text=self.state.tr("cash.counted_amount_fcfa"),
                 bg=theme.CARD,
                 fg=theme.MUTED, font=theme.FONT_SMALL).pack(side="left")
        self.e_close = ttk.Entry(row, justify="right", width=14,
                                 font=("Segoe UI", 12, "bold"))
        self.e_close.insert(0, str(int(self._expected)))
        self.e_close.pack(side="right")
        self.e_close.bind("<KeyRelease>", lambda e: self._calc_close_diff())

        self.lbl_close_diff = tk.Label(card, text="", bg=theme.CARD,
                                       font=theme.FONT_BOLD, anchor="e")
        self.lbl_close_diff.pack(fill="x", padx=12, pady=(2, 0))
        self.lbl_close_err = tk.Label(card, text="", bg=theme.CARD,
                                      fg=theme.DANGER, font=theme.FONT_SMALL)
        self.lbl_close_err.pack(anchor="w", padx=12)
        ttk.Button(card, text=self.state.tr("cash.close").upper(),
                   style="Danger.TButton",
                   command=self._submit_close).pack(fill="x", padx=12,
                                                    pady=(6, 12), ipady=2)
        self._calc_close_diff()

    def _close_value(self):
        raw = self.e_close.get().replace(",", ".").replace(" ", "") or "0"
        return float(raw)

    def _calc_close_diff(self):
        try:
            diff = round(self._close_value() - self._expected, 2)
        except ValueError:
            self.lbl_close_diff.config(text="")
            return
        if abs(diff) < 1:
            self.lbl_close_diff.config(text=self.state.tr("cash.exact"),
                                       fg=theme.SUCCESS)
        else:
            sign_str = '+' if diff > 0 else ''
            amount_str = f"{sign_str}{diff:,.0f}".replace(",", " ")
            txt = self.state.tr("cash.gap_display", amount=amount_str)
            self.lbl_close_diff.config(
                text=txt, fg=theme.SUCCESS if diff > 0 else theme.DANGER)

    def _submit_close(self):
        try:
            counted = self._close_value()
            if counted < 0:
                raise ValueError
        except ValueError:
            self.lbl_close_err.config(text=self.state.tr("cash.invalid_close_amount"))
            return
        diff = round(counted - self._expected, 2)
        if abs(diff) < 1:
            msg = self.state.tr("cash.perfect_close")
        else:
            sign_str = '+' if diff > 0 else ''
            amount_str = f"{sign_str}{diff:,.0f}".replace(",", " ")
            msg = self.state.tr("cash.gap_display", amount=amount_str)
        if not confirm(self, f"{msg}\n{self.state.tr('cash.confirm_close')}"):
            return
        try:
            self.state.cash.close_session(counted, self.state.user)
        except Exception as exc:
            self.lbl_close_err.config(text=str(exc))
            return
        self.refresh()

    # -- sous-section : historique des mouvements du jour --------------------
    def _build_day_journal(self, right, session):
        card = _card(right)
        card.grid(row=0, column=0, sticky="nsew")

        mv = session.get("movements", [])
        tot_in = sum(m["amount"] for m in mv if m["type"] != "out")
        tot_out = sum(m["amount"] for m in mv if m["type"] == "out")
        final = round(session["opening_amount"] + tot_in - tot_out, 2)

        head = tk.Frame(card, bg=theme.CARD)
        head.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(head, text=self.state.tr("cash.daily_journal").upper(),
                 bg=theme.CARD, fg=theme.ACCENT_HOVER,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        fmt = lambda v: f"{v:,.0f}".replace(",", " ")
        daily_txt = self.state.tr("cash.daily_summary",
                                  in_amount=f"+{fmt(tot_in)}",
                                  out_amount=f"\u2212{fmt(tot_out)}",
                                  balance=f"{fmt(final)} FCFA")
        tk.Label(head,
                 text=daily_txt,
                 bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="right")

        cols_spec = (
            ("time", self.state.tr("cash.col_time"), 60, "center", False),
            ("kind", self.state.tr("cash.type"), 105, "w", False),
            ("amount", self.state.tr("cash.amount"), 95, "e", False),
            ("balance", self.state.tr("cash.col_balance_after"), 100, "e", False),
            ("by", self.state.tr("cash.user"), 70, "center", False),
            ("reason", self.state.tr("cash.reason"), 180, "w", True))
        grid = DataGrid(card, cols_spec)
        grid.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # soldes cumules (ordre chronologique) puis affichage antichronologique
        bal = float(session["opening_amount"])
        balances = []
        for m in mv:
            bal = round(bal + (m["amount"] if m["type"] != "out"
                               else -m["amount"]), 2)
            balances.append(bal)

        flat = lambda s: " ".join(str(s).split()) or "\u2014"
        _kind_labels = {
            "sale": self.state.tr("cash.type_sale"),
            "in": self.state.tr("cash.add_in"),
            "out": self.state.tr("cash.add_out"),
        }
        for m, b in zip(reversed(mv), reversed(balances)):
            is_out = m["type"] == "out"
            kind = _kind_labels.get(m["type"], m["type"])
            color = theme.DANGER if is_out else (
                theme.ACCENT_HOVER if m["type"] == "sale" else theme.SUCCESS)
            sign = "\u2212 " if is_out else "+ "
            grid.add_row(
                (m["at"][11:16], kind, sign + fmt(m["amount"]), fmt(b),
                 m["by"], flat(m["reason"])),
                fg=(theme.MUTED, color, color, theme.TEXT,
                    theme.MUTED, theme.TEXT),
                fonts=(theme.FONT, theme.FONT, theme.FONT_BOLD,
                       theme.FONT_BOLD, theme.FONT, theme.FONT))
        if not mv:
            grid.add_row((self.state.tr("cash.no_movements"),
                          "", "", "", "", ""), fg=theme.MUTED)

    # ------------------------------- historique des sessions (caisse fermee)
    def _render_sessions_table(self):
        holder = self.body_card
        tk.Label(holder, text=self.state.tr("cash.sessions_history").upper(),
                 bg=theme.CARD, fg=theme.ACCENT_HOVER,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12,
                                                     pady=(12, 6))

        cols_spec = (
            ("id", self.state.tr("cash.col_num"), 45, "center", False),
            ("by", self.state.tr("cash.col_cashier"), 105, "w", False),
            ("open", self.state.tr("cash.col_open_amount"), 115, "e", True),
            ("close", self.state.tr("cash.col_close_amount"), 120, "e", False),
            ("tin", self.state.tr("cash.total_in"), 95, "e", False),
            ("tout", self.state.tr("cash.total_out"), 95, "e", False),
            ("expected", self.state.tr("cash.col_expected"), 115, "e", False),
            ("real", self.state.tr("cash.col_real"), 105, "e", False),
            ("ecart", self.state.tr("cash.col_gap"), 90, "e", False),
            ("status", self.state.tr("cash.col_status"), 80, "center", False))
        grid = DataGrid(holder, cols_spec)
        grid.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        MUTED, TEXT = theme.MUTED, theme.TEXT
        for c in self.state.cash.sessions()[:25]:
            if c["status"] == "open":
                grid.add_row(
                    (c["id"], c["opened_by"],
                     theme.money(c["opening_amount"]),
                     "\u2014",
                     theme.money(c["total_cash_in"]),
                     theme.money(c["total_cash_out"]),
                     theme.money(self.state.cash.expected_amount(c)),
                     "\u2014", "\u2014", self.state.tr("cash.status_open")),
                    fg=(MUTED, TEXT, TEXT, MUTED,
                        theme.SUCCESS, theme.DANGER,
                        theme.ACCENT_HOVER, MUTED, MUTED, theme.ACCENT_HOVER),
                    bg="#fdf6e7")
            else:
                ecart = c.get("difference") or 0
                if abs(ecart) < 1:
                    ecart_txt, ecolor = self.state.tr("cash.gap_exact"), theme.SUCCESS
                else:
                    ecart_txt = f"{ecart:+,.0f}".replace(",", " ") + " F"
                    ecolor = theme.DANGER if ecart < 0 else theme.SUCCESS
                grid.add_row(
                    (c["id"], c.get("closed_by") or c["opened_by"],
                     theme.money(c["opening_amount"]),
                     theme.money(c.get("expected") or 0),
                     theme.money(c["total_cash_in"]),
                     theme.money(c["total_cash_out"]),
                     theme.money(c.get("expected") or 0),
                     theme.money(c.get("closing_counted") or 0),
                     ecart_txt, self.state.tr("cash.status_closed")),
                    fg=(MUTED, TEXT, TEXT, TEXT,
                        theme.SUCCESS, theme.DANGER,
                        TEXT, TEXT, ecolor, MUTED))
