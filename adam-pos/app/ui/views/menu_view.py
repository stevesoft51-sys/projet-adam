"""Onglet Menu (admin) : categories et produits.

Le tableau des produits (DataGrid) montre : image, nom, categorie,
prix, disponibilite. Les formulaires (produit, categorie) s'affichent
en sections flottantes CAMOUFFLEES dans l'onglet : aucune fenetre
de dialogue. L'affichage est lie a l'onglet Point de vente qui lit
les memes donnees (image, nom, prix).
"""
import tkinter as tk
from tkinter import ttk

from .. import theme
from ..widgets import confirm, info, show_error, DataGrid


class MenuView(ttk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, style="TFrame")
        self.state = state
        self._prod_ids = []
        self._build()
        self.refresh()

    def _card_cell(self, parent) -> tk.Frame:
        """Carte blanche sans placement automatique (remplit sa zone)."""
        return tk.Frame(parent, bg=theme.CARD, highlightthickness=1,
                        highlightbackground="#e5ded0")

    # ================================================================ build
    def _build(self):
        # gauche : categories 1/4 | droite : produits 3/4
        self.columnconfigure(0, weight=1, uniform="menucol")
        self.columnconfigure(1, weight=3, uniform="menucol")
        self.rowconfigure(0, weight=1)

        # ---- colonne gauche : categories ---------------------------------
        left = self._card_cell(self)
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        self.left_card = left

        tk.Label(left, text=self.state.tr("menu.categories"), bg=theme.CARD,
                 fg=theme.ACCENT_HOVER,
                 font=("Segoe UI", 12, "bold")).grid(row=0, column=0,
                                                     sticky="w", padx=10,
                                                     pady=(10, 6))
        self.lb_cats = tk.Listbox(left, activestyle="none", relief="flat",
                                  bg="#faf7f2", highlightthickness=0,
                                  selectbackground=theme.ACCENT,
                                  selectforeground="#1a1a1a",
                                  font=theme.FONT, exportselection=False)
        self.lb_cats.grid(row=1, column=0, sticky="nsew", padx=10)
        self.lb_cats.bind("<<ListboxSelect>>",
                          lambda e: self._reload_products())

        btns = tk.Frame(left, bg=theme.CARD)
        btns.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        for label, cmd in ((self.state.tr("menu.add"), lambda: self._show_cat_form("add")),
                           (self.state.tr("menu.rename"),
                            lambda: self._show_cat_form("rename")),
                           (self.state.tr("menu.toggle"), self.toggle_category)):
            ttk.Button(btns, text=label, command=cmd
                       ).pack(side="left", expand=True, fill="x", padx=2)

        # ---- colonne droite : produits ------------------------------------
        # le tableau occupe ~90% de la section : une seule barre d'outils
        # compacte au-dessus, une barre d'actions fine en dessous
        right = self._card_cell(self)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.rowconfigure(1, weight=9)
        right.columnconfigure(0, weight=1)
        self.right_card = right

        top = tk.Frame(right, bg=theme.CARD)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        tk.Label(top, text=self.state.tr("menu.products"), bg=theme.CARD,
                 fg=theme.ACCENT_HOVER,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(top, text=self.state.tr("menu.new_product"), style="Accent.TButton",
                   command=self.new_product).pack(side="right")
        ttk.Label(top, text=self.state.tr("menu.filter")).pack(side="right", padx=(0, 10))
        self.e_search = ttk.Entry(top, width=22)
        self.e_search.pack(side="right")
        self.e_search.bind("<KeyRelease>", lambda e: self._reload_products())

        # image | nom | categorie | prix | disponibilite
        self.prod_holder = tk.Frame(right, bg=theme.CARD)
        self.prod_holder.grid(row=1, column=0, sticky="nsew",
                              padx=10, pady=(2, 0))
        self.prod_holder.rowconfigure(0, weight=1)
        self.prod_holder.columnconfigure(0, weight=1)

        actions = tk.Frame(right, bg=theme.CARD)
        actions.grid(row=2, column=0, sticky="ew", padx=10, pady=(6, 8))
        ttk.Button(actions, text=self.state.tr("menu.edit"),
                   command=self.edit_product).pack(side="left", padx=2)
        ttk.Button(actions, text=self.state.tr("menu.toggle_avail"),
                   command=self.toggle_product).pack(side="left", padx=2)
        ttk.Button(actions, text=self.state.tr("menu.delete"), style="Danger.TButton",
                   command=self.delete_product).pack(side="left", padx=2)

        # sections flottantes camouflees (creees une fois, cachees)
        self._build_product_form()
        self._build_category_form()

    # ------------------------------------------------- section produit ----
    THUMB_PREVIEW = 96

    def _build_product_form(self):
        f = tk.Frame(self.right_card, bg=theme.CARD, bd=0,
                     highlightthickness=1, highlightbackground="#b9ae95")
        inner = tk.Frame(f, bg=theme.CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.form_prod = f

        head = tk.Frame(inner, bg="#ece5d4")
        head.pack(fill="x")
        self.f_title = tk.Label(head, text="", bg="#ece5d4",
                                fg=theme.TEXT,
                                font=("Segoe UI", 11, "bold"))
        self.f_title.pack(anchor="w", padx=16, pady=8)

        body = tk.Frame(inner, bg=theme.CARD)
        body.pack(fill="x", padx=16, pady=(8, 4))
        body.columnconfigure(1, weight=1)

        def frow(r, label):
            tk.Label(body, text=label, bg=theme.CARD, fg=theme.MUTED,
                     font=theme.FONT_SMALL, width=15,
                     anchor="nw").grid(row=r, column=0, sticky="nw", pady=4)

        self.f_e_name = ttk.Entry(body)
        frow(0, self.state.tr("menu.field_name"))
        self.f_e_name.grid(row=0, column=1, sticky="ew", pady=4)

        self.f_cb_cat = ttk.Combobox(body, state="readonly")
        frow(1, self.state.tr("menu.field_category"))
        self.f_cb_cat.grid(row=1, column=1, sticky="ew", pady=4)

        self.f_e_price = ttk.Entry(body, justify="right")
        frow(2, self.state.tr("menu.field_price"))
        self.f_e_price.grid(row=2, column=1, sticky="ew", pady=4)

        frow(3, self.state.tr("menu.field_image"))
        img_zone = tk.Frame(body, bg=theme.CARD)
        img_zone.grid(row=3, column=1, sticky="ew", pady=4)
        self.lbl_thumb = tk.Label(img_zone, text=self.state.tr("menu.no_image"),
                                   bg="#f3ede1", fg=theme.MUTED,
                                  font=theme.FONT_SMALL,
                                  width=self.THUMB_PREVIEW // 7,
                                  height=self.THUMB_PREVIEW // 14,
                                  relief="solid", bd=1)
        self.lbl_thumb.pack(side="left", padx=(0, 10))
        img_btns = tk.Frame(img_zone, bg=theme.CARD)
        img_btns.pack(side="left")
        ttk.Button(img_btns, text=self.state.tr("menu.choose_image"),
                   command=self.pick_image).pack(anchor="w")
        ttk.Button(img_btns, text=self.state.tr("menu.remove_image"),
                   command=self.clear_image).pack(anchor="w", pady=(4, 0))

        self.f_avail = tk.BooleanVar(value=True)
        ttk.Checkbutton(body, text=self.state.tr("menu.available_for_sale"),
                        variable=self.f_avail).grid(row=4, column=1,
                                                    sticky="w", pady=4)

        self.f_txt_desc = tk.Text(body, height=3, font=theme.FONT,
                                  relief="solid", bd=1)
        frow(5, self.state.tr("menu.field_description"))
        self.f_txt_desc.grid(row=5, column=1, sticky="ew", pady=4)

        self.f_err = tk.Label(inner, bg=theme.CARD, fg=theme.DANGER,
                              font=theme.FONT_SMALL)
        self.f_err.pack(anchor="w", padx=16)

        foot = tk.Frame(inner, bg=theme.CARD)
        foot.pack(fill="x", padx=16, pady=(4, 14))
        ttk.Button(foot, text=self.state.tr("menu.cancel"),
                   command=self._hide_forms).pack(side="right")
        ttk.Button(foot, text=self.state.tr("menu.save"), style="Accent.TButton",
                   command=self._save_product).pack(side="right", padx=8)
        f.bind("<Escape>", lambda e: self._hide_forms())

    def _show_product_form(self, product=None):
        self._form_product = product
        self._pending_img = None
        self._image_name = product.get("image") if product else None
        cats = self.state.catalog.categories(active_only=True)
        names = [c["name"] for c in cats]
        self.f_cb_cat["values"] = names
        self.f_e_name.delete(0, "end")
        self.f_e_price.delete(0, "end")
        self.f_txt_desc.delete("1.0", "end")
        self.f_avail.set(bool(product.get("available", True))
                         if product else True)
        if product:
            for i, c in enumerate(cats):
                if c["id"] == product["category_id"]:
                    self.f_cb_cat.current(i)
                    break
            self.f_e_name.insert(0, product["name"])
            price = product["price"]
            self.f_e_price.insert(
                0, f"{price:g}" if isinstance(price, (int, float))
                else str(price))
            self.f_txt_desc.insert("1.0", product.get("description") or "")
        elif cats:
            self.f_cb_cat.current(0)
        if self._image_name:
            self._show_preview(
                self.state.catalog.image_path(self._image_name))
        else:
            self.clear_image()
        self.f_err.config(text="")
        self.f_title.config(text=self.state.tr("menu.edit_product_title") if product
                            else self.state.tr("menu.new_product_title"))
        self.form_prod.place(relx=0.5, rely=0.5, anchor="center",
                             width=430)
        self.form_prod.lift()
        self.f_e_name.focus_set()

    def _show_preview(self, path):
        from ..product_images import load_thumb
        thumb = load_thumb(path, self.THUMB_PREVIEW)
        if thumb is not None:
            self.lbl_thumb.config(image=thumb, text="", bg="#ffffff")
            self.lbl_thumb.image = thumb

    def pick_image(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            parent=self, title=self.state.tr("menu.image_dialog_title"),
            filetypes=[(self.state.tr("menu.filetype_images"), "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                       (self.state.tr("menu.filetype_all"), "*.*")])
        if not path:
            return
        from ..product_images import load_thumb
        thumb = load_thumb(path, self.THUMB_PREVIEW)
        if thumb is None:
            self.f_err.config(text=self.state.tr("menu.error_unreadable_image"))
            return
        self._pending_img = path
        self.lbl_thumb.config(image=thumb, text="", bg="#ffffff")
        self.lbl_thumb.image = thumb
        self.f_err.config(text="")

    def clear_image(self):
        self._pending_img = None
        self._image_name = None
        self.lbl_thumb.config(image="", text=self.state.tr("menu.no_image"), bg="#f3ede1")

    def _save_product(self):
        try:
            if self._pending_img:
                self._image_name = self.state.catalog.save_image(
                    self._pending_img)
            if not self._image_name:
                raise ValueError(self.state.tr("menu.error_image_required"))
            cats = self.state.catalog.categories(active_only=True)
            idx = self.f_cb_cat.current()
            data = {
                "name": self.f_e_name.get(),
                "category_id": cats[idx]["id"] if idx >= 0 and cats
                else None,
                "price": self.f_e_price.get().replace(",", "."),
                "description": self.f_txt_desc.get("1.0", "end").strip(),
                "available": self.f_avail.get(),
                "image": self._image_name,
            }
            prod_id = self._form_product["id"] if self._form_product \
                else None
            self.state.catalog.save_product(data, prod_id=prod_id)
        except Exception as exc:
            self.f_err.config(text=str(exc))
            return
        self._hide_forms()
        self.refresh()

    # ----------------------------------------------- section categorie ---
    def _build_category_form(self):
        f = tk.Frame(self.left_card, bg=theme.CARD,
                     highlightthickness=1, highlightbackground="#b9ae95")
        inner = tk.Frame(f, bg=theme.CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.form_cat = f

        head = tk.Frame(inner, bg="#ece5d4")
        head.pack(fill="x")
        self.cf_title = tk.Label(head, text="", bg="#ece5d4", fg=theme.TEXT,
                                 font=("Segoe UI", 11, "bold"))
        self.cf_title.pack(anchor="w", padx=14, pady=8)

        body = tk.Frame(inner, bg=theme.CARD)
        body.pack(fill="x", padx=14, pady=(6, 0))
        self.cf_entry = ttk.Entry(body)
        self.cf_entry.pack(fill="x")
        self.cf_err = tk.Label(inner, bg=theme.CARD, fg=theme.DANGER,
                               font=theme.FONT_SMALL)
        self.cf_err.pack(anchor="w", padx=14, pady=(4, 0))

        foot = tk.Frame(inner, bg=theme.CARD)
        foot.pack(fill="x", padx=14, pady=(4, 12))
        ttk.Button(foot, text=self.state.tr("menu.cancel"),
                   command=self._hide_forms).pack(side="right")
        ttk.Button(foot, text=self.state.tr("menu.save"), style="Accent.TButton",
                   command=self._save_category).pack(side="right", padx=8)
        f.bind("<Escape>", lambda e: self._hide_forms())

    def _show_cat_form(self, mode):
        cat = self._selected_category() if mode == "rename" else None
        if mode == "rename" and not cat:
            info(self, self.state.tr("menu.select_category_first"))
            return
        self._cat_mode, self._cat_target = mode, cat
        self.cf_entry.delete(0, "end")
        if cat:
            self.cf_entry.insert(0, cat["name"])
        self.cf_err.config(text="")
        self.cf_title.config(text=self.state.tr("menu.new_category") if mode == "add"
                             else self.state.tr("menu.rename_category_title", name=cat['name']))
        self.form_cat.place(relx=0.5, rely=0.5, anchor="center", width=300)
        self.form_cat.lift()
        self.cf_entry.focus_set()

    def _save_category(self):
        name = self.cf_entry.get()
        try:
            if self._cat_mode == "add":
                self.state.catalog.add_category(name)
            else:
                self.state.catalog.rename_category(
                    self._cat_target["id"], name)
        except Exception as exc:
            self.cf_err.config(text=str(exc))
            return
        self._hide_forms()
        self.refresh()

    def _hide_forms(self):
        self.form_prod.place_forget()
        self.form_cat.place_forget()

    # ============================================================== data --
    def refresh(self):
        self._reload_categories()
        self._reload_products()

    def _selected_category(self):
        sel = self.lb_cats.curselection()
        if not sel:
            return None
        cat_id = self.cat_map[sel[-1]]
        if cat_id is None:
            return None
        return next((c for c in self.state.catalog.categories()
                     if c["id"] == cat_id), None)

    def _selected_product(self):
        pgrid = getattr(self, "pgrid", None)
        if pgrid is None or pgrid.selected_row is None:
            return None
        pid = getattr(self, "_row_pid", {}).get(pgrid.selected_row)
        return self.state.catalog.product_by_id(pid) if pid else None

    # -------------------------------------------------------- categories --
    def _reload_categories(self):
        current = self.lb_cats.curselection()[-1] \
            if self.lb_cats.curselection() else 0
        self.lb_cats.delete(0, "end")
        # premiere entree : toutes les categories (pas de filtre)
        self.cat_map = [None]
        self.lb_cats.insert("end", self.state.tr("menu.all_categories"))
        for c in self.state.catalog.categories():
            name = c["name"] + ("" if c.get("active", True)
                                else self.state.tr("menu.disabled_suffix"))
            self.lb_cats.insert("end", name)
            self.cat_map.append(c["id"])
        if current is not None and current < self.lb_cats.size():
            # selection_set AJOUTE : on vide avant de poser la selection
            self.lb_cats.selection_clear(0, "end")
            self.lb_cats.selection_set(current)
            self.lb_cats.see(current)

    def toggle_category(self):
        cat = self._selected_category()
        if not cat:
            info(self, self.state.tr("menu.select_category_first"))
            return
        try:
            self.state.catalog.toggle_category(cat["id"])
        except Exception as exc:
            show_error(self, exc)
        self.refresh()

    # ----------------------------------------------------------- produits --
    def _reload_products(self):
        for w in self.prod_holder.winfo_children():
            w.destroy()
        from ..product_images import load_thumb

        prods = self.state.catalog.products()
        term = self.e_search.get().lower().strip()
        sel = self.lb_cats.curselection()
        cat_id = self.cat_map[sel[-1]] if sel else None
        if cat_id is not None:
            prods = [p for p in prods if p["category_id"] == cat_id]
        if term:
            prods = [p for p in prods if term in p["name"].lower()]

        cols = [("img", self.state.tr("menu.col_image"), 64, "center", False),
                ("name", self.state.tr("menu.col_name"), 180, "w", True),
                ("cat", self.state.tr("menu.col_category"), 130, "w", True),
                ("price", self.state.tr("menu.col_price"), 100, "e", False),
                ("avail", self.state.tr("menu.col_availability"), 110, "center", False)]
        self.pgrid = DataGrid(self.prod_holder, cols)
        self.pgrid.pack(fill="both", expand=True)
        self._prod_ids = []
        self._row_pid = {}

        cats = {c["id"]: c["name"] for c in self.state.catalog.categories()}
        for p in prods:
            thumb = load_thumb(
                self.state.catalog.image_path(p.get("image")), 40)
            ok = bool(p.get("available", True))
            row = self.pgrid.add_row(
                ["", p["name"], cats.get(p["category_id"], "?"),
                 f"{p['price']:,.0f}".replace(",", " ") + " F",
                 self.state.tr("menu.status_available") if ok else self.state.tr("menu.status_unavailable")],
                images=(thumb, None, None, None, None),
                fg=[theme.MUTED, theme.TEXT,
                    theme.TEXT if ok else theme.MUTED,
                    theme.TEXT if ok else theme.MUTED,
                    theme.SUCCESS if ok else theme.DANGER])
            self._row_pid[row] = p["id"]
            self._prod_ids.append(p["id"])

    def new_product(self):
        if not self.state.catalog.categories(active_only=True):
            info(self, self.state.tr("menu.create_category_first"))
            return
        self._show_product_form(None)

    def edit_product(self):
        prod = self._selected_product()
        if not prod:
            info(self, self.state.tr("menu.select_product_first"))
            return
        self._show_product_form(prod)

    def toggle_product(self):
        prod = self._selected_product()
        if not prod:
            info(self, self.state.tr("menu.select_product_first"))
            return
        try:
            prod["available"] = not prod.get("available", True)
            self.state.catalog.save_product(prod, prod_id=prod["id"])
        except Exception as exc:
            show_error(self, exc)
        self.refresh()

    def delete_product(self):
        prod = self._selected_product()
        if not prod:
            info(self, self.state.tr("menu.select_product_first"))
            return
        if not confirm(self, self.state.tr("menu.confirm_delete_product", name=prod['name'])):
            return
        self.state.catalog.delete_product(prod["id"])
        self.refresh()
