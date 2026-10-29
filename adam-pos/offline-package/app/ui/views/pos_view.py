"""Onglet Point de vente : grille produits, panier, additions, encaissement."""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from .. import theme
from ...services import TABLE_STATUSES
from ..widgets import clear, confirm, show_error, info


class PosView(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, style="TFrame")
        self.state = state
        self._t = self.state.tr
        self.cart = []          # [{'product': {...}, 'qty': int}]
        self.current_category = None  # None = tous
        self.search_term = ""
        self._build()

    # ------------------------------------------------------------- layout --
    def _card_cell(self, parent) -> tk.Frame:
        """Carte blanche sans placement automatique : contrairement a
        widgets.card(), le cadre retourne n'est pas encore gere, on peut donc
        le packer/grider librement pour qu'il remplisse toute sa zone."""
        return tk.Frame(parent, bg=theme.CARD, highlightthickness=1,
                        highlightbackground="#e5ded0")

    def _build(self):
        # gauche : selection des articles ; droite : panier + commandes.
        # Tout s'adapte a la taille de l'ecran : proportions des colonnes
        # (_relayout), largeurs des tableaux (_fit_trees_now) et defilement
        # vertical de la colonne droite (ecrans courts).
        self.columnconfigure(0, weight=2, uniform="poscol")
        self.columnconfigure(1, weight=1, uniform="poscol")
        self.rowconfigure(0, weight=1)
        self.bind("<Configure>", self._relayout)

        left = tk.Frame(self, bg=theme.BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        right = tk.Frame(self, bg=theme.BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        # -- colonne droite : canevas a defilement vertical ---
        rc = tk.Canvas(right, bg=theme.BG, highlightthickness=0)
        rvbar = ttk.Scrollbar(right, orient="vertical", command=rc.yview)
        rc.configure(yscrollcommand=rvbar.set)
        rvbar.grid(row=0, column=1, sticky="ns")
        rc.grid(row=0, column=0, sticky="nsew")
        self.right_canvas = rc
        ri = tk.Frame(rc, bg=theme.BG)
        ri.columnconfigure(0, weight=1)
        ri.rowconfigure(0, weight=3)     # panier en haut
        ri.rowconfigure(1, weight=2)     # commandes en bas
        self.right_inner = ri
        self.right_win = rc.create_window((0, 0), window=ri, anchor="nw")
        ri.bind("<Configure>",
                lambda e: rc.configure(scrollregion=rc.bbox("all")))
        rc.bind("<Configure>", self._fit_right_panel)
        self._bind_right_wheel(ri)

        # ---- zone gauche : recherche + categories + grille ---------------
        search_row = tk.Frame(left, bg=theme.BG)
        search_row.pack(fill="x")
        ttk.Label(search_row, text=self._t("pos.search_label")).pack(side="left")
        self.e_search = ttk.Entry(search_row, width=24)
        self.e_search.pack(side="left", padx=8)
        self.e_search.bind("<KeyRelease>", lambda e: self._reload_grid())

        # categories : defilent horizontalement si trop nombreuses pour
        # l'ecran (sinon les boutons seraient coupes sur un petit ecran)
        chips_holder = tk.Frame(left, bg=theme.BG)
        chips_holder.pack(fill="x", pady=(8, 4))
        chips_holder.columnconfigure(0, weight=1)
        cc = tk.Canvas(chips_holder, bg=theme.BG, height=36,
                       highlightthickness=0)
        hsc = ttk.Scrollbar(chips_holder, orient="horizontal",
                            command=cc.xview)
        cc.configure(xscrollcommand=hsc.set)
        cc.grid(row=0, column=0, sticky="ew")
        hsc.grid(row=1, column=0, sticky="ew")
        self.chips_canvas = cc
        chips = tk.Frame(cc, bg=theme.BG)
        self.chips_frame = chips
        self.chips_win = cc.create_window((0, 0), window=chips, anchor="nw")

        def _sync_chips(_event=None):
            """Barre horizontale visible uniquement si besoin, pour ne pas
            couper les categories sur un petit ecran."""
            try:
                cc.configure(scrollregion=cc.bbox("all"))
                cc.itemconfig(self.chips_win, height=chips.winfo_height())
                if (cc.winfo_width() > 1
                        and chips.winfo_reqwidth() > cc.winfo_width()):
                    hsc.grid()
                else:
                    hsc.grid_remove()
            except tk.TclError:
                pass

        chips.bind("<Configure>", _sync_chips)
        cc.bind("<Configure>", _sync_chips)

        grid_holder = self._card_cell(left)
        grid_holder.pack(fill="both", expand=True, pady=(6, 0))

        self.canvas = tk.Canvas(grid_holder, bg=theme.CARD,
                                highlightthickness=0)
        vbar = ttk.Scrollbar(grid_holder, orient="vertical",
                             command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.grid_frame = tk.Frame(self.canvas, bg=theme.CARD)
        self.grid_win = self.canvas.create_window(
            (8, 8), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind(
            "<Configure>", self._on_canvas_resize)
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.bind_all(seq, self._on_wheel)

        # ---- zone droite haute : panier -------------------------------------
        cart_card = self._card_cell(ri)
        cart_card.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        cart_card.columnconfigure(0, weight=1)
        cart_card.rowconfigure(0, weight=1)

        head = tk.Frame(cart_card, bg=theme.CARD)
        head.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(head, text=self._t("pos.cart_title"), bg=theme.CARD,
                 font=("Segoe UI", 13, "bold"), fg=theme.TEXT).pack(side="left")
        ttk.Button(head, text=self._t("pos.cart_clear"), style="Danger.TButton", width=7,
                   command=self.clear_cart).pack(side="right")

        cols = ("qty", "pu", "total")
        tree_holder = tk.Frame(cart_card, bg=theme.CARD)
        tree_holder.pack(fill="both", expand=True, padx=12)
        self.tree = ttk.Treeview(tree_holder, columns=cols, show="tree headings",
                                 height=4, selectmode="browse")
        self.tree.heading("#0", text=self._t("pos.col_product"))
        self.tree.heading("qty", text=self._t("pos.col_qty"))
        self.tree.heading("pu", text=self._t("pos.col_unit_price"))
        self.tree.heading("total", text=self._t("pos.col_total"))
        self.tree.column("#0", width=170)
        for c in cols:
            self.tree.column(c, anchor="center", width=70, stretch=False)
        self.tree.column("#0", anchor="w", stretch=False)
        cbar = ttk.Scrollbar(tree_holder, orient="vertical",
                             command=self.tree.yview)
        self.tree.configure(yscrollcommand=cbar.set)
        cbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        qty_row = tk.Frame(cart_card, bg=theme.CARD)
        qty_row.pack(pady=4)
        ttk.Button(qty_row, text=self._t("pos.qty_decrease"), width=7,
                   command=lambda: self.change_qty(-1)).pack(side="left", padx=4)
        ttk.Button(qty_row, text=self._t("pos.qty_increase"), width=7,
                   command=lambda: self.change_qty(+1)).pack(side="left", padx=4)
        ttk.Button(qty_row, text=self._t("pos.remove_item"), width=14,
                   command=self.remove_line).pack(side="left", padx=4)

        # -- mode de service OBLIGATOIRE avant validation -------------------
        srv_row = tk.Frame(cart_card, bg=theme.CARD)
        srv_row.pack(fill="x", padx=12, pady=(4, 0))
        tk.Label(srv_row, text=self._t("pos.service_label"), bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="left")
        self.service_mode = None          # rien choisi par defaut
        self._srv_chips = {}
        for mode, label in (("dine_in", self._t("pos.service_dine_in")),
                            ("takeaway", self._t("pos.service_takeaway"))):
            b = tk.Button(srv_row, text=label, bd=1, bg="#ffffff",
                          fg=theme.MUTED, activebackground=theme.ACCENT,
                          font=theme.FONT_SMALL, relief="solid",
                          highlightthickness=0, cursor="hand2",
                          command=lambda m=mode: self._pick_service(m))
            b.pack(side="left", padx=(10 if mode == "dine_in" else 4, 0))
            self._srv_chips[mode] = b
        self.srv_err = tk.Label(cart_card, text="", bg=theme.CARD,
                                fg=theme.DANGER, font=theme.FONT_SMALL,
                                anchor="w")
        self.srv_err.pack(fill="x", padx=12, pady=(2, 0))

        trow = tk.Frame(cart_card, bg=theme.CARD)
        tk.Label(trow, text=self._t("pos.table_label"), bg=theme.CARD,
                 fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="left")
        self.table_cb = ttk.Combobox(trow, state="readonly")
        self.table_cb.pack(side="left", padx=(6, 0), fill="x", expand=True)
        self.table_cb.bind("<<ComboboxSelected>>",
                           lambda e: self.table_cb.selection_clear())
        self._floor_units = []

        disc_row = tk.Frame(cart_card, bg=theme.CARD)
        disc_row.pack(fill="x", padx=12, pady=(2, 4))
        tk.Label(disc_row, text=self._t("pos.discount_label"), bg=theme.CARD,
                 fg=theme.MUTED, font=theme.FONT_SMALL).pack(side="left")
        self.e_discount = ttk.Entry(disc_row, width=10, justify="right")
        self.e_discount.insert(0, "0")
        self.e_discount.pack(side="right")
        self.e_discount.bind("<KeyRelease>", lambda e: self.update_totals())

        totals = tk.Frame(cart_card, bg=theme.CARD)
        totals.pack(fill="x", padx=12)
        self.lbl_sub = tk.Label(totals, text="", bg=theme.CARD,
                                fg=theme.MUTED, font=theme.FONT, anchor="e")
        self.lbl_sub.pack(fill="x")
        self.lbl_disc = tk.Label(totals, text="", bg=theme.CARD,
                                 fg=theme.MUTED, font=theme.FONT, anchor="e")
        self.lbl_disc.pack(fill="x")
        self.lbl_total = tk.Label(totals, text=self._t("pos.total_zero"), bg=theme.CARD,
                                  fg=theme.TEXT, font=("Segoe UI", 17, "bold"),
                                  anchor="e")
        self.lbl_total.pack(fill="x", pady=(4, 6))

        gen_row = tk.Frame(cart_card, bg=theme.CARD)
        gen_row.pack(fill="x", padx=12, pady=(2, 10))
        ttk.Button(gen_row, text=self._t("pos.generate_order"), style="Accent.TButton",
                   command=lambda: self.generate_order(print_too=False)
                   ).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(gen_row, text=self._t("pos.instant_payment"),
                   style="Success.TButton",
                   command=self.checkout
                   ).pack(side="left", expand=True, fill="x")

        self._build_orders_section(ri)
        self._build_action_section(right)      # camouffee par defaut
        self._reload_grid()
        self._relayout()
        self.refresh()

    # ------------------------------------------------ adaptation ecran -----
    def _relayout(self, event=None):
        """Ajuste la proportion gauche/droite selon la largeur disponible :
        sur un petit ecran les deux colonnes deviennent quasi egales pour
        que panier et commandes restent lisibles sans etre coupes."""
        try:
            w = getattr(event, "width", None) or self.winfo_width()
        except tk.TclError:
            return
        if w <= 1:
            return
        if w >= 1150:
            lw, rw = 2, 1
        elif w >= 1000:
            lw, rw = 7, 5
        else:
            lw, rw = 1, 1
        if (lw, rw) != getattr(self, "_columns_ratio", None):
            self._columns_ratio = (lw, rw)
            self.columnconfigure(0, weight=lw, uniform="poscol")
            self.columnconfigure(1, weight=rw, uniform="poscol")

    def _bind_right_wheel(self, widget):
        """Molette = defilement vertical de la colonne droite (coupe la
        propagation vers la grille produits, qui gere ses propres evenements)."""
        def _scroll(event):
            if event.num == 4:
                self.right_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.right_canvas.yview_scroll(1, "units")
            else:
                delta = -1 if getattr(event, "delta", 120) > 0 else 1
                self.right_canvas.yview_scroll(delta, "units")
            return "break"
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            widget.bind(seq, _scroll)
        try:
            for child in widget.winfo_children():
                self._bind_right_wheel(child)
        except tk.TclError:
            pass

    def _fit_right_panel(self, event=None):
        """La colonne droite remplit l'espace visible ; si son contenu est
        plus haut (ecran court), une barre de defilement apparait et rien
        n'est perdu."""
        try:
            w = getattr(event, "width", None) \
                or self.right_canvas.winfo_width()
        except tk.TclError:
            return
        if w <= 1:
            return
        try:
            self.right_canvas.itemconfig(self.right_win, width=w)
            self.update_idletasks()
            req = self.right_inner.winfo_reqheight()
            ch = self.right_canvas.winfo_height()
            self.right_canvas.itemconfig(self.right_win,
                                         height=max(req, ch))
            self.right_canvas.configure(
                scrollregion=self.right_canvas.bbox("all"))
        except tk.TclError:
            return
        self._schedule_tree_fit()

    def _schedule_tree_fit(self):
        if getattr(self, "_tree_fit_after", None):
            try:
                self.after_cancel(self._tree_fit_after)
            except tk.TclError:
                pass
        self._tree_fit_after = self.after(15, self._fit_trees_now)

    def _tree_specs(self):
        """(Treeview, [(colonne, largeur_min, poids_flexible), ...])"""
        specs = []
        if hasattr(self, "tree"):
            specs.append((self.tree,
                          (("#0", 110, 3), ("qty", 44, 0),
                           ("pu", 44, 0), ("total", 56, 1))))
        if hasattr(self, "orders_tree"):
            specs.append((self.orders_tree,
                          (("num", 56, 1), ("time", 42, 0), ("table", 46, 0),
                           ("items", 52, 3), ("total", 62, 1),
                           ("by", 52, 1))))
        if hasattr(self, "hist_tree"):
            specs.append((self.hist_tree,
                          (("num", 52, 1), ("closed", 46, 1),
                           ("total", 58, 1), ("method", 48, 1),
                           ("by", 48, 1), ("status", 50, 1))))
        return specs

    def _fit_trees_now(self):
        """Redimensionne les colonnes des tableaux pour qu'elles tiennent
        toutes a l'ecran (aucune coupee horizontalement), quelle que soit
        la taille de la fenetre."""
        self._tree_fit_after = None
        for tree, specs in self._tree_specs():
            try:
                w = tree.winfo_width()
            except tk.TclError:
                continue
            if w <= 1:
                try:
                    w = max(self.right_canvas.winfo_width() - 30, 140)
                except tk.TclError:
                    continue
            self._resize_tree(tree, specs, w)

    @staticmethod
    def _resize_tree(tree, specs, avail):
        """Repartit la largeur disponible entre les colonnes, avec une
        taille minimale par colonne ; l'excedent va aux colonnes flexibles."""
        if avail <= 0:
            return
        total_min = sum(s[1] for s in specs)
        if avail <= total_min:
            factor = avail / total_min
            widths = {k: max(26, int(m * factor))
                      for k, m, _f in specs}
        else:
            weights = sum(s[2] for s in specs) or 1
            widths = {k: m for k, m, _f in specs}
            for k, m, f in specs:
                widths[k] += int((avail - total_min) * f / weights)
        widths[specs[0][0]] += avail - sum(widths.values())
        for k, wt in widths.items():
            try:
                tree.column(k, width=max(wt, 20),
                            minwidth=max(wt, 20), stretch=False)
            except tk.TclError:
                pass

    # ------------------------------------ commandes (droite, moitié basse) --
    def _build_orders_section(self, parent):
        orders_card = self._card_cell(parent)
        orders_card.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        ohead = tk.Frame(orders_card, bg=theme.CARD)
        ohead.pack(fill="x", padx=12, pady=(10, 2))
        tk.Label(ohead, text=self._t("pos.orders_title"),
                 bg=theme.CARD, font=("Segoe UI", 12, "bold"),
                 fg=theme.TEXT).pack(side="left")
        self.lbl_orders = tk.Label(ohead, text="", bg=theme.CARD,
                                   fg=theme.MUTED, font=theme.FONT_SMALL)
        self.lbl_orders.pack(side="right")

        # -- selection de la table/boucaro ou le client sera servi ---------
        # (deplacee dans la section panier, au-dessus de la remise)

        # -- derniere notification envoyee a une table ---------------------
        self.lbl_notif = tk.Label(orders_card, text="", bg="#eaf7ee",
                                  fg=theme.SUCCESS, font=theme.FONT_SMALL,
                                  anchor="w", padx=10, pady=4)
        self.lbl_notif.pack(fill="x", padx=12, pady=(2, 2))

        ocols = ("num", "time", "table", "items", "total", "by")
        self.orders_tree = ttk.Treeview(orders_card, columns=ocols,
                                        height=3, selectmode="browse")
        self.orders_tree.heading("#0", text="")
        self.orders_tree.column("#0", width=0, stretch=False)
        for key, label, width, anchor in (
                ("num", self._t("pos.col_order_number"), 120, "center"),
                ("time", self._t("pos.col_time"), 55, "center"),
                ("table", self._t("pos.col_table"), 60, "center"),
                ("items", self._t("pos.col_items"), 150, "w"),
                ("total", self._t("pos.col_order_total"), 100, "e"),
                ("by", self._t("pos.col_taken_by"), 95, "center")):
            self.orders_tree.heading(key, text=label)
            self.orders_tree.column(key, width=width, anchor=anchor,
                                    stretch=False)
        self.orders_tree.tag_configure("late", background="#fdf6e7")
        self.orders_tree.pack(fill="both", expand=True, padx=12)

        obtns = tk.Frame(orders_card, bg=theme.CARD)
        obtns.pack(fill="x", padx=12, pady=(4, 10))
        ttk.Button(obtns, text=self._t("pos.pay_order"), style="Success.TButton",
                   command=self.settle_selected).pack(side="left", padx=2)
        ttk.Button(obtns, text=self._t("pos.view_addition"),
                   command=self.view_addition).pack(side="left", padx=2)
        ttk.Button(obtns, text=self._t("pos.cancel_order"), style="Danger.TButton",
                   command=self.cancel_selected).pack(side="left", padx=2)

        # -- historique (admin uniquement) ------------------------------------
        if self.state.is_admin():
            hhead = tk.Frame(orders_card, bg=theme.CARD)
            hhead.pack(fill="x", padx=12)
            tk.Label(hhead, text=self._t("pos.history_title"),
                     bg=theme.CARD, font=("Segoe UI", 11, "bold"),
                     fg=theme.MUTED).pack(side="left")
            hcols = ("num", "closed", "total", "method", "by", "status")
            self.hist_tree = ttk.Treeview(orders_card, columns=hcols,
                                          height=3, selectmode="browse")
            self.hist_tree.heading("#0", text="")
            self.hist_tree.column("#0", width=0, stretch=False)
            for key, label, width, anchor in (
                    ("num", self._t("pos.col_number"), 105, "center"),
                    ("closed", self._t("pos.col_settled_at"), 60, "center"),
                    ("total", self._t("pos.col_total"), 90, "e"),
                    ("method", self._t("pos.col_mode"), 95, "center"),
                    ("by", self._t("pos.col_by"), 100, "center"),
                    ("status", self._t("pos.col_status"), 80, "center")):
                self.hist_tree.heading(key, text=label)
                self.hist_tree.column(key, width=width, anchor=anchor,
                                      stretch=False)
            self.hist_tree.tag_configure("cancel", foreground=theme.DANGER)
            self.hist_tree.tag_configure("ok", foreground=theme.SUCCESS)
            self.hist_tree.pack(fill="x", padx=12, pady=(4, 10))

    def _on_wheel(self, event):
        delta = -1 if getattr(event, "delta", 120) > 0 or event.num == 4 else 1
        self.canvas.yview_scroll(delta, "units")

    # ------------------------------------------------------- grille produit --
    def refresh(self):
        self._reload_tables()
        self._reload_chips()
        self._reload_grid()
        self._reload_orders()
        self.update_totals()

    def _reload_tables(self):
        """Menu deroulant : tables et boucaros avec leur statut."""
        cb = getattr(self, "table_cb", None)
        if not cb:
            return
        floor = self.state.floor
        self._floor_units = floor.units() if floor else []
        values = []
        for u in self._floor_units:
            kind = self._t("pos.table_type") if u["kind"] == "table" else self._t("pos.boucaro_type")
            seats = u.get("seats") or ""
            values.append(f"{u['name']} · {kind} "
                          f"{f'{seats} pl.' if seats else ''} — "
                          f"{TABLE_STATUSES[u['status']]}")
        cb.config(values=values)
        cur = cb.current()
        if 0 <= cur < len(values):
            cb.current(cur)      # on garde la selection existante
        # pas d'auto-selection : la caissiere doit choisir explicitement

    # ------------------------------------------------- selection de service --
    def _pick_service(self, mode):
        self.service_mode = mode
        self.srv_err.config(text="")
        for m, b in self._srv_chips.items():
            active = (m == mode)
            b.config(bg=theme.ACCENT if active else "#ffffff",
                     fg="#1a1a1a" if active else theme.MUTED)
        # le choix de table n'a de sens que pour "sur place"
        if mode == "dine_in":
            if not self.table_cb.winfo_ismapped():
                self.table_cb.master.pack(fill="x", padx=12, pady=(4, 0),
                                          before=self.srv_err)
                self.table_cb.master.lift()
            self._reload_tables()
        elif self.table_cb.winfo_ismapped():
            self.table_cb.master.pack_forget()

    def _resolve_service(self):
        """Retourne (unit_id, unit_name, mode, erreur)."""
        if self.service_mode is None:
            return None, None, None, self._t("pos.err_pick_service")
        if self.service_mode == "takeaway":
            return None, None, "takeaway", None
        idx = self.table_cb.current()
        if idx < 0 or idx >= len(getattr(self, "_floor_units", [])):
            return None, None, None, self._t("pos.err_pick_table")
        u = self._floor_units[idx]
        return u["id"], u["name"], "dine_in", None

    def _clear_srv_err(self):
        if self.srv_err.cget("text"):
            self.srv_err.config(text="")

    def _selected_table_id(self):
        cb = getattr(self, "table_cb", None)
        if not cb:
            return None
        idx = cb.current()
        return self._floor_units[idx]["id"] \
            if 0 <= idx < len(getattr(self, "_floor_units", [])) else None

    # ------------------------------------------------------------ commandes --
    def _selected_order(self):
        sel = self.orders_tree.selection()
        if not sel:
            return None
        return self.state.orders.get_order(int(sel[0]))

    def _reload_orders(self):
        self._reload_tables()          # statuts tables/boucaros a jour
        orders = self.state.orders.open_orders()
        if hasattr(self, "lbl_orders"):
            n = len(orders)
            self.lbl_orders.config(
                text=self._t("pos.orders_pending_count", n=n)
                if n else self._t("pos.orders_none"))
        if hasattr(self, "orders_tree"):
            tree = self.orders_tree
            # banniere : derniere notification de table
            if hasattr(self, "lbl_notif"):
                notifs = self.state.orders.notifications(limit=1) \
                    if hasattr(self.state.orders, "notifications") else []
                if notifs:
                    n = notifs[0]
                    self.lbl_notif.config(
                        text=self._t("pos.notif_format",
                                     unit=n['unit_name'], time=n['at'][11:16],
                                     order=n['order_number'], summary=n['summary']),
                        bg="#eaf7ee", fg=theme.SUCCESS)
                else:
                    self.lbl_notif.config(
                        text=self._t("pos.notif_none"),
                        bg=theme.CARD, fg=theme.MUTED)
            sel = tree.selection()
            tree.delete(*tree.get_children())
            now = datetime.now()
            for o in orders:
                hh = o["datetime"][11:16]
                items = ", ".join(f"{it['qty']}x {it['name'][:14]}"
                                  for it in o["items"][:3])
                if len(o["items"]) > 3:
                    items += "…"
                tags = ()
                try:
                    dt = datetime.strptime(o["datetime"], "%Y-%m-%d %H:%M:%S")
                    if (now - dt).total_seconds() > 3600:
                        tags = ("late",)
                except ValueError:
                    pass
                if o.get("unit_name"):
                    tbl = o["unit_name"] + (" ✓" if o.get("notified_at")
                                            else "")
                elif o.get("service_mode") == "takeaway":
                    tbl = self._t("pos.takeaway_short")
                else:
                    tbl = "—"
                tree.insert("", "end", iid=str(o["id"]), values=(
                    o["number"], hh, tbl, items,
                    theme.money(o["total"]), o["created_by"]), tags=tags)
            if sel:
                try:
                    tree.selection_set(sel[0])
                except tk.TclError:
                    pass
        if self.state.is_admin() and hasattr(self, "hist_tree"):
            htree = self.hist_tree
            hsel = htree.selection()
            htree.delete(*htree.get_children())
            for o in self.state.orders.closed_orders(limit=40):
                cancelled = o["status"] == "cancelled"
                method = {"cash": self._t("pos.method_cash"), "mobile_money": self._t("pos.method_mobile_money"),
                          "card": self._t("pos.method_card")}.get(o.get("method") or "", "—")
                status = (self._t("pos.status_cancelled") if cancelled
                          else self._t("pos.status_settled") + (f" ({o['sale_number']})"
                                                                 if o.get("sale_number") else ""))
                htree.insert("", "end", iid=str(o["id"]), values=(
                    o["number"],
                    (o.get("settled_at") or "")[11:16],
                    theme.money(o["total"]),
                    "—" if cancelled else method,
                    o.get("settled_by") or "—",
                    status),
                    tags=("cancel",) if cancelled else ("ok",))
            if hsel:
                try:
                    htree.selection_set(hsel[0])
                except tk.TclError:
                    pass

    def generate_order(self, print_too=False):
        """Enregistre la commande du client et genere son addition."""
        if not self.cart:
            info(self, self._t("pos.cart_empty"))
            return
        unit_id, unit_name, mode, err = self._resolve_service()
        if err:
            self.srv_err.config(text="⚠ " + err)
            return
        try:
            order = self.state.orders.create_order(
                self.cart, self._discount_value(), self.state.user,
                unit_id=unit_id, mode=mode)
        except Exception as exc:
            show_error(self, exc)
            return
        path = None
        if print_too:
            path = self.state.orders.save_addition_file(order,
                                                        self.state.settings)
        self._after_order_saved(unit_name)
        self._show_addition(order, printed_path=path)

    def view_addition(self):
        order = self._selected_order()
        if not order:
            info(self, self._t("pos.select_order_first"))
            return
        self._show_addition(order)

    def settle_selected(self):
        order = self._selected_order()
        if not order:
            info(self, self._t("pos.select_order_first"))
            return
        self._fill_settle(order)

    def cancel_selected(self):
        order = self._selected_order()
        if not order:
            info(self, self._t("pos.select_order_first"))
            return
        if not confirm(self, self._t("pos.cancel_confirm", number=order['number'])):
            return
        try:
            self.state.orders.cancel_order(order["id"], self.state.user)
        except Exception as exc:
            show_error(self, exc)
        self.refresh()

    def _reload_chips(self):
        clear(self.chips_frame)

        def chip(label, cat_id):
            active = self.current_category == cat_id
            bg = theme.ACCENT if active else "#ffffff"
            b = tk.Button(self.chips_frame, text=label, bd=1,
                          bg=bg, fg="#1a1a1a" if active else theme.MUTED,
                          activebackground=theme.ACCENT,
                          font=theme.FONT_SMALL, relief="solid",
                          highlightthickness=0, cursor="hand2",
                          command=lambda: self._pick_cat(cat_id))
            b.pack(side="left", padx=3)

        chip(self._t("pos.category_all"), None)
        for c in self.state.catalog.categories(active_only=True):
            chip(c["name"], c["id"])

    def _pick_cat(self, cat_id):
        self.current_category = cat_id
        self._reload_chips()
        self._reload_grid()

    def _reload_grid(self):
        self.search_term = self.e_search.get().lower().strip() \
            if hasattr(self, "e_search") else ""
        products = self.state.catalog.products(available_only=True)
        if self.current_category is not None:
            products = [p for p in products if p["category_id"] == self.current_category]
        if self.search_term:
            products = [p for p in products
                        if self.search_term in p["name"].lower()]
        self._grid_products = products
        self._grid_cats = {c["id"]: c["name"]
                           for c in self.state.catalog.categories()}
        self._render_grid(force=True)

    # ------------------------------------------- grille fluide (adaptative) --
    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.grid_win, width=max(event.width - 16, 1))
        self._render_grid()
        self._fit_grid_window()

    def _render_grid(self, force=False):
        if not hasattr(self, "_grid_products"):
            return
        avail_w = self.canvas.winfo_width() - 16
        if avail_w <= 1:
            return
        per_row = max(1, int(avail_w // 200))
        if not force and per_row == getattr(self, "_per_row", None):
            return
        self._per_row = per_row
        clear(self.grid_frame)
        products, cats = self._grid_products, self._grid_cats
        cell_w = max(120, (avail_w - 10 * per_row) // per_row)
        img_size = int(cell_w * 0.65)
        from ..product_images import load_thumb

        def _on_enter(c):
            c.config(highlightbackground=theme.ACCENT)

        def _on_leave(c):
            c.config(highlightbackground="#e5ded0")

        for i, p in enumerate(products):
            r, col = divmod(i, per_row)
            thumb = load_thumb(
                self.state.catalog.image_path(p.get("image")), img_size)
            card = tk.Frame(self.grid_frame, bg="#faf7f2",
                            highlightthickness=2, highlightbackground="#e5ded0",
                            cursor="hand2", width=cell_w, height=cell_w)
            card.grid_propagate(False)
            card.grid(row=r, column=col, padx=4, pady=4)
            card.bind("<Button-1>", lambda e, pp=p: self.add_to_cart(pp))
            card.bind("<Enter>", lambda e, c=card: _on_enter(c))
            card.bind("<Leave>", lambda e, c=card: _on_leave(c))
            if thumb:
                img_lbl = tk.Label(card, image=thumb, bg="#faf7f2")
                img_lbl.image = thumb
                img_lbl.place(relx=0.5, rely=0.35, anchor="center")
                img_lbl.bind("<Button-1>",
                             lambda e, pp=p: self.add_to_cart(pp))
            else:
                tk.Label(card, text="\U0001F37D\uFE0F",
                         bg="#f3ede1",
                         font=("Segoe UI", int(img_size / 3)),
                         width=4, height=2, anchor="center"
                         ).place(relx=0.5, rely=0.35, anchor="center")
            tk.Label(card, text=p["name"], bg="#faf7f2", fg=theme.TEXT,
                     font=("Segoe UI", 9, "bold"),
                     wraplength=cell_w - 16, justify="center"
                     ).place(relx=0.5, rely=0.72, anchor="center")
            tk.Label(card, text=f"{p['price']:,.0f} FCFA".replace(",", " "),
                     bg="#faf7f2", fg=theme.ACCENT_HOVER,
                     font=("Segoe UI", 9, "bold")
                     ).place(relx=0.5, rely=0.88, anchor="center")

        for c in range(per_row):
            self.grid_frame.columnconfigure(c, weight=0)
        if not products:
            tk.Label(self.grid_frame,
                     text=self._t("pos.no_products_in_category"),
                     bg=theme.CARD, fg=theme.MUTED, pady=30
                     ).grid(row=0, columnspan=max(per_row, 1))
        self.grid_frame.update_idletasks()
        self._fit_grid_window()

    def _fit_grid_window(self):
        """La grille remplit au moins toute la hauteur visible du canevas."""
        h = max(self.grid_frame.winfo_reqheight(),
                self.canvas.winfo_height() - 16)
        self.canvas.itemconfig(self.grid_win, height=h)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # --------------------------------------------------------------- panier --
    def add_to_cart(self, product):
        for line in self.cart:
            if line["product"]["id"] == product["id"]:
                line["qty"] += 1
                break
        else:
            self.cart.append({"product": product, "qty": 1})
        self.update_totals()

    def selected_line(self):
        sel = self.tree.selection()
        if not sel:
            return None
        iid = int(sel[0])
        idx = self.tree.index(sel[0])
        try:
            return self.cart[idx]
        except IndexError:
            return None

    def change_qty(self, delta):
        line = self.selected_line()
        if not line:
            info(self, self._t("pos.select_item_first"))
            return
        line["qty"] += delta
        if line["qty"] <= 0:
            self.cart.remove(line)
        self.update_totals()

    def remove_line(self):
        line = self.selected_line()
        if not line:
            info(self, self._t("pos.select_item_first"))
            return
        self.cart.remove(line)
        self.update_totals()

    def clear_cart(self):
        if self.cart and not confirm(self, self._t("pos.cart_clear_confirm")):
            return
        self.cart.clear()
        self.e_discount.delete(0, "end")
        self.e_discount.insert(0, "0")
        self.update_totals()

    def _discount_value(self) -> float:
        raw = self.e_discount.get().replace(",", ".").replace(" ", "") or "0"
        try:
            val = float(raw)
        except ValueError:
            return 0.0
        return max(0.0, val)

    def update_totals(self):
        subtotal = sum(l["product"]["price"] * l["qty"] for l in self.cart)
        disc = min(self._discount_value(), subtotal)
        total = subtotal - disc
        self.tree.delete(*self.tree.get_children())
        for i, line in enumerate(self.cart):
            p = line["product"]
            self.tree.insert("", "end", iid=str(i), open=False,
                             text=p["name"],
                             values=(line["qty"], f"{p['price']:,.0f}".replace(",", " "),
                                     f"{p['price'] * line['qty']:,.0f}".replace(",", " ")))
        self.lbl_sub.config(text=self._t("pos.subtotal_display", amount=f"{subtotal:,.0f}".replace(",", " ")))
        self.lbl_disc.config(text=self._t("pos.discount_display", amount=f"{disc:,.0f}".replace(",", " "))
                             if disc else "")
        self.lbl_total.config(text=self._t("pos.total_display", amount=f"{total:,.0f}".replace(",", " ")))

    # ------------------------------------------------------------ paiement --
    def _after_order_saved(self, unit_name):
        """Nettoyage commun apres enregistrement d'une commande."""
        self.cart.clear()
        self.e_discount.delete(0, "end")
        self.e_discount.insert(0, "0")
        self.update_totals()
        self._reload_orders()          # banniere notification incluse
        if unit_name is None and self.service_mode == "takeaway":
            self.srv_err.config(text="")
        self._pending_service = None

    def checkout(self):
        if not self.cart:
            info(self, self._t("pos.cart_empty"))
            return
        unit_id, unit_name, mode, err = self._resolve_service()
        if err:
            self.srv_err.config(text="⚠ " + err)
            return
        # le service choisi suit le panier jusqu'au paiement
        self._pending_service = {"mode": mode, "unit_id": unit_id,
                                 "unit_name": unit_name}
        self._fill_payment(self.cart, self._discount_value())

    # --------------------------------- section cachee multi-actions ---------
    def _build_action_section(self, parent):
        """Section flottante camouffee de la colonne droite : elle recoit
        le contenu de l'action en cours (encaissement, reglement,
        addition, recu) a la place des fenetres de dialogue."""
        card = tk.Frame(parent, bg=theme.CARD, highlightthickness=1,
                        highlightbackground="#b9ae95")
        inner = tk.Frame(card, bg=theme.CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.act_card = card

        self.act_banner = tk.Frame(inner, bg="#fdf6e7")
        self.act_banner.pack(fill="x")
        self.lbl_act_title = tk.Label(self.act_banner, text="",
                                      bg="#fdf6e7",
                                      font=("Segoe UI", 13, "bold"))
        self.lbl_act_title.pack(anchor="w", padx=14, pady=(10, 2))
        self.lbl_act_sub = tk.Label(self.act_banner, text="", bg="#fdf6e7",
                                    fg=theme.MUTED, font=theme.FONT_SMALL,
                                    wraplength=330, justify="left")
        self.lbl_act_sub.pack(anchor="w", padx=14, pady=(0, 10))

        self.act_body = tk.Frame(inner, bg=theme.CARD)
        self.act_body.pack(fill="both", expand=True, padx=14, pady=8)
        self.act_foot = tk.Frame(inner, bg=theme.CARD)
        self.act_foot.pack(fill="x", padx=14, pady=(0, 12))
        card.bind("<Escape>", lambda e: self._close_action())

    def _show_action(self, title, sub="", banner_bg="#fdf6e7",
                     banner_fg=None):
        self.lbl_act_title.config(text=title, bg=banner_bg,
                                  fg=banner_fg or theme.ACCENT_HOVER)
        self.lbl_act_sub.config(text=sub, bg=banner_bg)
        self.act_banner.config(bg=banner_bg)
        clear(self.act_body)
        clear(self.act_foot)
        self.act_card.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.act_card.lift()

    def _close_action(self):
        self.act_card.grid_remove()
        self.refresh()

    def _method_selector(self, body):
        var = tk.StringVar(value="cash")
        frame = tk.Frame(body, bg=theme.CARD)
        frame.pack(fill="x", pady=(4, 4))
        for value, label in (("cash", self._t("pos.method_cash")),
                             ("mobile_money", self._t("pos.method_mobile_money")),
                             ("mixed", self._t("pos.payment_mixed"))):
            tk.Radiobutton(frame, text=label, variable=var, value=value,
                           bg=theme.CARD, font=theme.FONT_BOLD,
                           selectcolor="#efe9de", anchor="w",
                           command=self._on_pay_method).pack(
                side="left", expand=True, fill="x")
        return var

    def _cash_area(self, body, due):
        area = tk.Frame(body, bg=theme.CARD)
        row = tk.Frame(area, bg=theme.CARD)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=self._t("pos.received_amount"), bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="left")
        e_received = ttk.Entry(row, width=12, justify="right",
                               font=("Segoe UI", 11, "bold"))
        e_received.insert(0, str(int(due)))
        e_received.pack(side="right")
        quicks = tk.Frame(area, bg=theme.CARD)
        quicks.pack(fill="x", pady=2)
        for amount in sorted({int(due), 1000, 2000, 5000, 10000} - {0}):
            ttk.Button(quicks, text=f"+{amount:,}".replace(",", " "),
                       command=lambda a=amount: self._add_cash(a)
                       ).pack(side="left", padx=2)
        lbl_change = tk.Label(area, text="", bg=theme.CARD,
                              fg=theme.SUCCESS, font=theme.FONT_BOLD,
                              anchor="e")
        lbl_change.pack(fill="x")
        return area, e_received, lbl_change

    def _mixed_area(self, body, due):
        area = tk.Frame(body, bg=theme.CARD)
        r1 = tk.Frame(area, bg=theme.CARD); r1.pack(fill="x", pady=2)
        tk.Label(r1, text=self._t("pos.part_cash"), bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="left")
        e_cash = ttk.Entry(r1, width=12, justify="right",
                           font=("Segoe UI", 11, "bold"))
        e_cash.insert(0, "0"); e_cash.pack(side="right")
        r2 = tk.Frame(area, bg=theme.CARD); r2.pack(fill="x", pady=2)
        tk.Label(r2, text=self._t("pos.part_mobile_money"), bg=theme.CARD, fg=theme.MUTED,
                 font=theme.FONT_SMALL).pack(side="left")
        e_mob = ttk.Entry(r2, width=12, justify="right",
                          font=("Segoe UI", 11, "bold"))
        e_mob.insert(0, str(int(due))); e_mob.pack(side="right")
        lbl = tk.Label(area, text="", bg=theme.CARD, fg=theme.TEXT,
                       font=theme.FONT_BOLD, anchor="e")
        lbl.pack(fill="x")
        e_cash.bind("<KeyRelease>", lambda e: self._update_mix())
        e_mob.bind("<KeyRelease>", lambda e: self._update_mix())
        return area, e_cash, e_mob, lbl

    def _on_pay_method(self):
        if getattr(self, "_pay_var", None) is None:
            return
        m = self._pay_var.get()
        self.pay_cash_area.pack_forget()
        self.pay_mixed_area.pack_forget()
        if m == "cash":
            self.pay_cash_area.pack(fill="x", before=self.pay_lbl_err)
        elif m == "mixed":
            self.pay_mixed_area.pack(fill="x", before=self.pay_lbl_err)
            self._update_mix()

    def _add_cash(self, amount):
        current = self._received_value()
        self.e_received.delete(0, "end")
        self.e_received.insert(0, str(int(current + amount)))
        self._calc_change()

    def _received_value(self) -> float:
        try:
            return float(self.e_received.get().replace(",", ".")
                         .replace(" ", "") or 0)
        except ValueError:
            return 0.0

    def _mix_values(self) -> tuple:
        try:
            mc = float(self.e_mix_cash.get().replace(",", ".")
                       .replace(" ", "") or 0)
        except ValueError:
            mc = 0.0
        try:
            mm = float(self.e_mix_mob.get().replace(",", ".")
                       .replace(" ", "") or 0)
        except ValueError:
            mm = 0.0
        return mc, mm

    # ---- encaissement immediat (panier courant) --------------------------
    def _fill_payment(self, cart, discount):
        total = round(sum(l["product"]["price"] * l["qty"]
                          for l in cart) - discount, 2)
        self._pay_total = total
        self._pay_discount = discount
        self._show_action(self._t("pos.encaissement_title"),
                          self._t("pos.n_articles", n=len(cart))
                          + (" — " + self._t("pos.remise_appliquee",
                                            amount=f"{discount:,.0f}".replace(",", " "))
                             if discount else ""))
        body = self.act_body
        tk.Label(body,
                 text=self._t("pos.amount_due", amount=f"{total:,.0f}".replace(",", " ")),
                 bg=theme.CARD, fg=theme.TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        self._pay_var = self._method_selector(body)
        self.pay_cash_area, self.e_received, self.lbl_change = \
            self._cash_area(body, total)
        self.pay_cash_area.pack(fill="x")
        self.pay_mixed_area, self.e_mix_cash, self.e_mix_mob, \
            self.pay_mix_lbl = self._mixed_area(body, total)
        self.pay_lbl_err = tk.Label(body, text="", bg=theme.CARD,
                                     fg=theme.DANGER, font=theme.FONT_SMALL,
                                     wraplength=340, justify="left")
        self.pay_lbl_err.pack(anchor="w", pady=(6, 0))
        ttk.Button(self.act_foot, text=self._t("pos.cancel"),
                   command=self._close_action).pack(side="right")
        ttk.Button(self.act_foot, text=self._t("pos.validate_payment"),
                   style="Success.TButton",
                   command=self._submit_payment).pack(side="right", padx=8)
        self.e_received.bind("<KeyRelease>",
                             lambda e: self._calc_change())
        self.e_received.bind("<Return>", lambda e: self._submit_payment())
        self.e_received.focus_set()

    def _calc_change(self):
        due = getattr(self, "_pay_total", None)
        if due is None:
            due = self._settle_order["total"]
        change = self._received_value() - due
        word = self._t("pos.change_to_give") if due == self._pay_total \
            else self._t("pos.refund")
        if change >= 0:
            self.lbl_change.config(
                text=self._t("pos.change_display", word=word, amount=f"{change:,.0f}".replace(",", " ")),
                fg=theme.SUCCESS)
        else:
            self.lbl_change.config(
                text=self._t("pos.shortage", amount=f"{abs(change):,.0f}".replace(",", " ")),
                fg=theme.DANGER)

    def _update_mix(self):
        due = getattr(self, "_pay_total", None)
        if due is None:
            due = self._settle_order["total"]
        mc = self._mix_values()[0]
        mm = self._mix_values()[1]
        total_parts = round(mc + mm, 2)
        gap = round(due - total_parts, 2)
        if gap == 0:
            self.pay_mix_lbl.config(
                text=self._t("pos.mix_ok",
                             mc=f"{mc:g}", mm=f"{mm:g}",
                             total=f"{total_parts:g}"),
                fg=theme.SUCCESS)
        elif gap > 0:
            self.pay_mix_lbl.config(
                text=self._t("pos.mix_short",
                             mc=f"{mc:g}", mm=f"{mm:g}",
                             total=f"{total_parts:g}", gap=f"{gap:g}"),
                fg=theme.TEXT)
        else:
            self.pay_mix_lbl.config(
                text=self._t("pos.mix_excess",
                             mc=f"{mc:g}", mm=f"{mm:g}",
                             total=f"{total_parts:g}", gap=f"{abs(gap):g}"),
                fg=theme.DANGER)

    def _submit_payment(self):
        method = self._pay_var.get()
        received = self._received_value() if method == "cash" else None
        mixed_cash = mixed_mobile = None
        if method == "mixed":
            mixed_cash, mixed_mobile = self._mix_values()
        svc = getattr(self, "_pending_service", None) or {}
        try:
            sale = self.state.sales.create_sale(
                self.cart, method, self._pay_discount, self.state.user,
                received=received,
                service_mode=svc.get("mode"),
                unit_name=svc.get("unit_name"),
                mixed_cash=mixed_cash,
                mixed_mobile=mixed_mobile)
        except Exception as exc:
            self.pay_lbl_err.config(text=str(exc))
            return
        # encaissement immediat sur place : on notifie aussi la table
        if svc.get("mode") == "dine_in" and svc.get("unit_name"):
            summary = ", ".join(f"{l['qty']}x {l['product']['name']}"
                                for l in self.cart)[:80]
            try:
                self.state.orders.notify(sale["number"], svc["unit_id"],
                                         svc["unit_name"], summary,
                                         sale["total"],
                                         self.state.user["name"])
            except Exception:
                pass
        path = self.state.sales.save_ticket_file(sale, self.state.settings)
        self.cart.clear()
        self.e_discount.delete(0, "end")
        self.e_discount.insert(0, "0")
        self.update_totals()
        self._reload_orders()
        self._show_receipt(sale, self.state.sales.ticket_text(
            sale, self.state.settings), path)

    def _show_receipt(self, sale, ticket_text, file_path=None):
        change = ""
        if sale.get("change") is not None:
            change = (f"   ·   {self._t('pos.change_to_give')} : "
                      f"{sale['change']:,.0f} F".replace(",", " "))
        self._show_action(self._t("pos.payment_recorded", number=sale['number']),
                          sub=self._t("pos.ticket", path=file_path) if file_path else "",
                          banner_bg=theme.SUCCESS, banner_fg="white")
        txt = tk.Text(self.act_body, width=42,
                      height=min(16, len(ticket_text.splitlines()) + 1),
                      font=("Consolas", 9), bg="#faf6ee", relief="flat")
        txt.insert("1.0", ticket_text)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)
        ttk.Button(self.act_foot, text=self._t("pos.close"), style="Accent.TButton",
                   command=self._close_action).pack(side="right")

    # ---- reglement d'une addition en attente ------------------------------
    def _fill_settle(self, order):
        self._settle_order = order
        self._pay_total = None          # bascule le calcul sur l'addition
        self._show_action(
            self._t("pos.settle_title", number=order['number']),
            self._t("pos.settle_subtitle",
                    amount=f"{order['total']:,.0f}".replace(",", " "),
                    n=len(order['items']),
                    time=order['datetime'][11:16],
                    user=order['created_by']))
        body = self.act_body
        tk.Label(body,
                 text=self._t("pos.amount_due",
                              amount=f"{order['total']:,.0f}".replace(",", " ")),
                 bg=theme.CARD, fg=theme.TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        self._pay_var = self._method_selector(body)
        self.pay_cash_area, self.e_received, self.lbl_change = \
            self._cash_area(body, order["total"])
        self.pay_cash_area.pack(fill="x")
        self.pay_mixed_area, self.e_mix_cash, self.e_mix_mob, \
            self.pay_mix_lbl = self._mixed_area(body, order["total"])
        self.pay_lbl_err = tk.Label(body, text="", bg=theme.CARD,
                                    fg=theme.DANGER, font=theme.FONT_SMALL,
                                    wraplength=340, justify="left")
        self.pay_lbl_err.pack(anchor="w", pady=(6, 0))
        ttk.Button(self.act_foot, text=self._t("pos.cancel"),
                   command=self._close_action).pack(side="right")
        ttk.Button(self.act_foot, text=self._t("pos.validate_settlement"),
                   style="Success.TButton",
                   command=self._submit_settle).pack(side="right", padx=8)
        self.e_received.bind("<KeyRelease>",
                             lambda e: self._calc_change())
        self.e_received.bind("<Return>", lambda e: self._submit_settle())
        self.e_received.focus_set()

    def _submit_settle(self):
        order = self._settle_order
        method = self._pay_var.get()
        received = self._received_value() if method == "cash" else None
        mixed_cash = mixed_mobile = None
        if method == "mixed":
            mixed_cash, mixed_mobile = self._mix_values()
        try:
            sale = self.state.orders.settle_order(
                order["id"], method, received, self.state.user,
                mixed_cash=mixed_cash,
                mixed_mobile=mixed_mobile)
            path = self.state.sales.save_ticket_file(sale,
                                                     self.state.settings)
        except Exception as exc:
            self.pay_lbl_err.config(text=str(exc))
            return
        self._reload_orders()
        self._show_receipt(sale, self.state.sales.ticket_text(
            sale, self.state.settings), path)

    # ---- addition d'une commande -------------------------------------------
    def _show_addition(self, order, printed_path=None):
        banner, fg, status = {
            "open": ("#fdf6e7", theme.ACCENT_HOVER,
                     self._t("pos.order_status_open")),
            "settled": ("#eafaf0", theme.SUCCESS, self._t("pos.order_status_settled")),
            "cancelled": ("#fdecea", theme.DANGER, self._t("pos.order_status_cancelled")),
        }[order["status"]]
        self._addition_order = order
        self._show_action(self._t("pos.addition_title", number=order['number']),
                          sub=self._t("pos.printed", path=printed_path)
                          if printed_path else "", banner_bg=banner,
                          banner_fg=fg)
        self.lbl_act_title.config(text=self._t("pos.addition_title", number=order['number']))
        text = self.state.orders.order_text(order, self.state.settings)
        txt = tk.Text(self.act_body, width=42,
                      height=min(18, len(text.splitlines()) + 1),
                      font=("Consolas", 9), bg="#faf6ee", relief="flat")
        txt.insert("1.0", text)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)
        self.lbl_print_info = tk.Label(self.act_body, text="",
                                       bg=theme.CARD, fg=theme.MUTED,
                                       font=theme.FONT_SMALL)
        self.lbl_print_info.pack(anchor="w", pady=(4, 0))
        ttk.Button(self.act_foot, text=self._t("pos.close"),
                   command=self._close_action).pack(side="right")
        ttk.Button(self.act_foot, text=self._t("pos.print_addition"), style="Accent.TButton",
                   command=self._print_addition).pack(side="right", padx=8)

    def _print_addition(self):
        path = self.state.orders.save_addition_file(
            self._addition_order, self.state.settings)
        self.lbl_print_info.config(
            text=self._t("pos.print_sent", path=path))
