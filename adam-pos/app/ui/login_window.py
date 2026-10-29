"""Fenetre de connexion avec gestion des roles et choix de langue."""
import tkinter as tk
from tkinter import ttk

from . import theme
from ..i18n import T


class LoginWindow(tk.Tk):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self._lang = "fr"
        self.title("Restaurant ADAM — Connexion")
        self.resizable(False, False)
        self.configure(bg=theme.DARK)
        theme.setup_style(self)
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        w = 460
        h = max(600, self.winfo_reqheight())
        sh = self.winfo_screenheight()
        h = min(h, sh)                    # ne jamais depasser l'ecran
        x = (self.winfo_screenwidth() - w) // 2
        y = max(0, (sh - h) // 3)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _lang_text(self, key, **fmt):
        return T(self._lang, key, **fmt)

    def _refresh_texts(self):
        self.lbl_subtitle.config(
            text=self._lang_text("app.subtitle"))
        self.lbl_title.config(text=self._lang_text("login.title"))
        self.lbl_user.config(text=self._lang_text("login.username"))
        self.lbl_pass.config(text=self._lang_text("login.password"))
        self.lbl_lang.config(text=self._lang_text("login.language"))
        self.btn_login.config(text=self._lang_text("login.submit"))
        if self._lang == "ar":
            for lbl in (self.lbl_subtitle, self.lbl_title, self.lbl_user,
                        self.lbl_pass, self.lbl_lang, self.lbl_err):
                lbl.configure(anchor="e", justify="right")
            self.lbl_err.configure(justify="right")
        else:
            for lbl in (self.lbl_subtitle, self.lbl_title, self.lbl_user,
                        self.lbl_pass, self.lbl_lang, self.lbl_err):
                lbl.configure(anchor="w", justify="left")

    def _build(self):
        header = tk.Frame(self, bg=theme.DARK)
        header.pack(pady=(40, 6))
        tk.Label(header, text="ADAM", font=("Playfair Display", 34, "bold"),
                 bg=theme.DARK, fg=theme.ACCENT).pack()
        self.lbl_subtitle = tk.Label(header, text="", bg=theme.DARK,
                                     fg="#9ca3af", font=theme.FONT_SMALL)
        self.lbl_subtitle.pack()

        form_holder = tk.Frame(self, bg=theme.CARD, padx=34, pady=26,
                               highlightthickness=1,
                               highlightbackground=theme.ACCENT)
        form_holder.pack(pady=20)

        self.lbl_title = tk.Label(form_holder, text="", bg=theme.CARD,
                                  fg=theme.TEXT, font=("Segoe UI", 13, "bold"))
        self.lbl_title.pack(anchor="w")

        self.lbl_lang = tk.Label(form_holder, text="", bg=theme.CARD,
                                 fg=theme.MUTED, font=theme.FONT_SMALL)
        self.lbl_lang.pack(anchor="w", pady=(14, 0))
        lang_row = tk.Frame(form_holder, bg=theme.CARD)
        lang_row.pack(fill="x")
        self.cb_lang = ttk.Combobox(lang_row, state="readonly",
                                    values=list(state_lang_names()), width=28)
        self.cb_lang.current(0)
        self.cb_lang.pack(fill="x", ipady=1)
        self.cb_lang.bind(
            "<<ComboboxSelected>>",
            lambda e: self._on_lang_change(self.cb_lang.current()))

        self.lbl_user = tk.Label(form_holder, text="", bg=theme.CARD,
                                 fg=theme.MUTED, font=theme.FONT_SMALL)
        self.lbl_user.pack(anchor="w", pady=(12, 0))
        self.e_user = ttk.Entry(form_holder, font=theme.FONT, width=28)
        self.e_user.pack(fill="x", ipady=3)
        self.e_user.bind("<FocusOut>", lambda e: self._prefill_lang())
        self.e_user.bind("<Return>", lambda e: self._prefill_lang())

        self.lbl_pass = tk.Label(form_holder, text="", bg=theme.CARD,
                                 fg=theme.MUTED, font=theme.FONT_SMALL)
        self.lbl_pass.pack(anchor="w", pady=(12, 0))
        self.e_pass = ttk.Entry(form_holder, show="•", font=theme.FONT, width=28)
        self.e_pass.pack(fill="x", ipady=3)

        self.lbl_err = tk.Label(form_holder, text="", bg=theme.CARD,
                                fg=theme.DANGER, font=theme.FONT_SMALL,
                                wraplength=280, justify="left")
        self.lbl_err.pack(anchor="w", pady=(8, 0))

        self.btn_login = ttk.Button(form_holder, text="", style="Accent.TButton",
                                    command=self.try_login)
        self.btn_login.pack(fill="x", pady=(16, 0), ipady=2)

        for w in (self.e_user, self.e_pass):
            w.bind("<Return>", lambda e: self.try_login())
        self.e_user.focus_set()

        self._refresh_texts()

    def _on_lang_change(self, idx):
        languages = state_lang_codes()
        if 0 <= idx < len(languages):
            self._lang = languages[idx]
        self._refresh_texts()

    def _prefill_lang(self):
        """Preregle la langue depuis la preference enregistree de l'utilisateur
        des que son identifiant est saisi."""
        username = (self.e_user.get() or "").strip().lower()
        if not username:
            return
        try:
            user = self.state.auth.user_by_username(username)
        except Exception:
            user = None
        if not user:
            return
        stored = user.get("lang", "fr")
        codes = state_lang_codes()
        if stored in codes:
            self._lang = stored
            self.cb_lang.current(codes.index(stored))
            self._refresh_texts()

    def try_login(self):
        self.state.set_lang(self._lang)
        try:
            user = self.state.auth.login(self.e_user.get(), self.e_pass.get())
        except Exception as exc:
            self.lbl_err.config(text=str(exc))
            self.e_pass.delete(0, "end")
            return
        if not user:
            self.lbl_err.config(text=self._lang_text("login.bad_credentials"))
            self.e_pass.delete(0, "end")
            return
        user.setdefault("lang", self._lang)
        self.state.user = user
        # Memorisautomatiquement la langue choisie sur le compte
        try:
            self.state.auth.set_lang(user["id"], self._lang)
        except Exception:
            pass
        role_label = "Administrateur" if user["role"] == "admin" else "Caissière"
        print(f"[OK] Connexion : {user['username']} ({role_label})")
        # Fermer la fenetre termine proprement le mainloop() du login ;
        # c'est main.py qui ouvre alors la fenêtre principale.
        self.destroy()


def state_lang_names():
    from ..state import AppState
    return [n for _c, n in AppState.languages()]


def state_lang_codes():
    from ..state import AppState
    return [c for c, _n in AppState.languages()]

