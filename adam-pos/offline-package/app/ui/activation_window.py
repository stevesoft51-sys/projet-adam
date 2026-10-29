"""Fenetre d'activation — affichee au premier lancement."""
import tkinter as tk
from tkinter import ttk

from . import theme
from ..activation import validate_key, save_license
from ..i18n import T


class ActivationWindow(tk.Tk):
    def __init__(self, data_dir: str):
        super().__init__()
        self.data_dir = data_dir
        self.activated = False
        self._lang = "fr"
        self.title("Restaurant ADAM — Activation")
        self.resizable(False, False)
        self.configure(bg=theme.DARK)
        self._build()
        self._center()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center(self):
        self.update_idletasks()
        w, h = 480, 430
        x = (self.winfo_screenwidth() - w) // 2
        y = max(0, (self.winfo_screenheight() - h) // 3)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _txt(self, key, **fmt):
        return T(self._lang, key, **fmt)

    def _refresh(self):
        self.lbl_subtitle.config(text=self._txt("app.subtitle"))
        self.lbl_title.config(text=self._txt("act.title"))
        self.lbl_prompt.config(text=self._txt("act.prompt"))
        self.lbl_key.config(text=self._txt("act.key_label"))
        self.btn_activate.config(text=self._txt("act.activate"))
        if self._lang == "ar":
            for w in (self.lbl_subtitle, self.lbl_title, self.lbl_prompt,
                      self.lbl_key, self.lbl_err):
                w.configure(anchor="e", justify="right")

    def _build(self):
        header = tk.Frame(self, bg=theme.DARK)
        header.pack(pady=(24, 4))
        tk.Label(header, text="ADAM", font=("Playfair Display", 34, "bold"),
                 bg=theme.DARK, fg=theme.ACCENT).pack()
        self.lbl_subtitle = tk.Label(header, text="", bg=theme.DARK,
                                     fg="#9ca3af", font=theme.FONT_SMALL)
        self.lbl_subtitle.pack()

        form = tk.Frame(self, bg=theme.CARD, padx=30, pady=22,
                        highlightthickness=1, highlightbackground=theme.ACCENT)
        form.pack(pady=14, padx=30, fill="x")

        self.lbl_title = tk.Label(form, text="", bg=theme.CARD,
                                  font=("Segoe UI", 13, "bold"), fg=theme.TEXT)
        self.lbl_title.pack(anchor="w")
        self.lbl_prompt = tk.Label(form, text="", bg=theme.CARD,
                                   fg=theme.MUTED, font=theme.FONT_SMALL,
                                   wraplength=360, justify="left")
        self.lbl_prompt.pack(anchor="w", pady=(4, 10))

        lang_row = tk.Frame(form, bg=theme.CARD)
        lang_row.pack(fill="x", pady=(0, 12))
        self.cb_lang = ttk.Combobox(lang_row, state="readonly",
                                    values=[n for _c, n in _lang_names()],
                                    width=28)
        self.cb_lang.current(0)
        self.cb_lang.pack(fill="x", ipady=1)
        self.cb_lang.bind("<<ComboboxSelected>>",
                          lambda e: self._on_lang(self.cb_lang.current(0)))

        self.lbl_key = tk.Label(form, text="", bg=theme.CARD,
                                fg=theme.MUTED, font=theme.FONT_SMALL)
        self.lbl_key.pack(anchor="w")
        self.e_key = ttk.Entry(form, font=("Segoe UI", 12), width=30,
                               justify="center")
        self.e_key.pack(fill="x", pady=(6, 10))

        self.lbl_err = tk.Label(form, text="", bg=theme.CARD,
                                fg=theme.DANGER, font=theme.FONT_SMALL,
                                wraplength=360, justify="left")
        self.lbl_err.pack(anchor="w")

        btns = tk.Frame(form, bg=theme.CARD)
        btns.pack(fill="x", pady=(14, 0))
        self.btn_activate = ttk.Button(form, text="", style="Accent.TButton",
                                       command=self._try_activate)
        self.btn_activate.pack(fill="x", ipady=2)

        self.e_key.focus_set()
        self.e_key.bind("<Return>", lambda e: self._try_activate())

        self._refresh()

    def _on_lang(self, idx):
        codes = _lang_codes()
        if 0 <= idx < len(codes):
            self._lang = codes[idx]
        self._refresh()

    def _try_activate(self):
        key = self.e_key.get().strip()
        if not key:
            self.lbl_err.config(text=self._txt("act.key_label"))
            return
        if validate_key(key):
            save_license(self.data_dir)
            self.activated = True
            self.destroy()
        else:
            self.lbl_err.config(text=self._txt("act.invalid"))

    def _on_close(self):
        self.activated = False
        self.destroy()


def _lang_names():
    from ..state import AppState
    return [(c, n) for c, n in AppState.languages()]


def _lang_codes():
    from ..state import AppState
    return [c for c, _n in AppState.languages()]

