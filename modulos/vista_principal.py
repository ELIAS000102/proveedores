"""
Vista Principal: Menú de Proveedores
---------------------------------------------------------------------------
Mixin de la clase App con la pantalla de inicio: la barra superior (buscador,
botones de agregar/exportar) y la grilla de tarjetas resumen de cada
proveedor. Se combina con los demás mixins de vista en modulos/app.py.
"""
import tkinter as tk
from tkinter import ttk

from modulos.estilos import *  # noqa: F401,F403 - constantes de color/fuente
from modulos.modelo_datos import Proveedor


class VistaPrincipalMixin:
    """Pantalla de inicio: buscador, alta/baja rápida y grilla de proveedores."""

    def _mostrar_vista_principal(self):
        self.proveedor_seleccionado = None
        for w in self.main_container.winfo_children():
            w.destroy()

        self.main_container.grid_rowconfigure(0, weight=0)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        top_bar = tk.Frame(self.main_container, bg=COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        top_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))

        head_info = tk.Frame(top_bar, bg=COLOR_PANEL)
        head_info.pack(side="left", padx=13, pady=10)

        tk.Label(head_info, text="Panel de Gestión de Proveedores", font=FONT_TITLE, bg=COLOR_PANEL, fg=COLOR_PRIMARY).pack(anchor="w")
        tk.Label(head_info, text="Selecciona un proveedor para ver sus matrices de flujo de venta", font=FONT_CAPTION, bg=COLOR_PANEL, fg=COLOR_MUTED).pack(anchor="w", pady=(2, 0))

        right_box = tk.Frame(top_bar, bg=COLOR_PANEL)
        right_box.pack(side="right", padx=13, pady=10)

        btn_export = tk.Button(right_box, text="⬇ Exportar Todo", font=FONT_BOLD, bg="#059669", fg="white",
                               activebackground="#047857", relief="flat", cursor="hand2", padx=10, pady=5,
                               bd=0, command=self._exportar_matrices_csv)
        btn_export.pack(side="right", padx=(6, 0))

        btn_add = tk.Button(right_box, text="+ Agregar Proveedor", font=FONT_BOLD, bg=COLOR_ACCENT, fg="white",
                            activebackground=COLOR_ACCENT_HOVER, relief="flat", cursor="hand2", padx=10, pady=5,
                            bd=0, command=self._agregar_proveedor)
        btn_add.pack(side="right", padx=(6, 0))

        f_search = tk.Frame(right_box, bg="#f1f5f9", bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        f_search.pack(side="right", padx=(0, 6))

        tk.Label(f_search, text="Buscar", font=FONT_SMALL, bg="#f1f5f9", fg=COLOR_MUTED).pack(side="left", padx=(8, 2))
        ent = tk.Entry(f_search, textvariable=self.filtro_busqueda, font=FONT_BASE, bg="#f1f5f9", bd=0,
                       insertbackground=COLOR_TEXT)
        ent.pack(side="left", padx=(0, 6), pady=5)
        self.filtro_busqueda.trace_add("write", lambda *a: self._renderizar_grid_proveedores())

        f_scroll = tk.Frame(self.main_container, bg=COLOR_BG)
        f_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 9))

        canvas = tk.Canvas(f_scroll, bg=COLOR_BG, highlightthickness=0)
        sb = ttk.Scrollbar(f_scroll, orient="vertical", command=canvas.yview)

        self.cards_container = tk.Frame(canvas, bg=COLOR_BG)
        self.cards_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        c_win = canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(c_win, width=e.width))
        canvas.configure(yscrollcommand=sb.set)

        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._renderizar_grid_proveedores()

    def _renderizar_grid_proveedores(self):
        for w in self.cards_container.winfo_children():
            w.destroy()

        query = self.filtro_busqueda.get().strip().upper()
        filtro_provs = [p for name, p in self.proveedores.items() if not query or query in name.upper()]

        if not filtro_provs:
            tk.Label(self.cards_container, text="No se encontraron proveedores.", font=FONT_SUBTITLE, bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=29)
            return

        col_count = 3
        for i in range(col_count):
            self.cards_container.grid_columnconfigure(i, weight=1, uniform="card_col")

        for idx, prov in enumerate(filtro_provs):
            r, c = divmod(idx, col_count)
            self._crear_tarjeta_resumen_proveedor(self.cards_container, prov, r, c)

    def _crear_tarjeta_resumen_proveedor(self, parent, prov: Proveedor, row, col):
        card = tk.Frame(parent, bg=COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        chead = tk.Frame(card, bg=COLOR_HEADER_BG)
        chead.pack(fill="x")

        tk.Label(chead, text=prov.nombre, font=FONT_SUBTITLE, bg=COLOR_HEADER_BG, fg="white").pack(side="left", padx=9, pady=6)

        cbody = tk.Frame(card, bg=COLOR_PANEL)
        cbody.pack(fill="both", expand=True, padx=9, pady=7)

        f_codes = tk.Frame(cbody, bg=COLOR_PANEL)
        f_codes.pack(fill="x", pady=(0, 6))

        tk.Label(f_codes, text=f"TVI: {prov.tvi or '—'}", font=FONT_BOLD, bg="#f1f5f9", fg=COLOR_PRIMARY, padx=5, pady=2).pack(side="left", padx=(0, 3))
        tk.Label(f_codes, text=f"TFI: {prov.tfi or '—'}", font=FONT_BOLD, bg="#f1f5f9", fg=COLOR_PRIMARY, padx=5, pady=2).pack(side="left")

        f_badges = tk.Frame(cbody, bg=COLOR_PANEL)
        f_badges.pack(fill="x", pady=(0, 9))

        if prov.ddc_activo:
            tk.Label(f_badges, text="DDC ACTIVO", font=FONT_SMALL, bg="#dcfce7", fg="#15803d", padx=5, pady=2).pack(side="left", padx=(0, 3))
        else:
            tk.Label(f_badges, text="DDC INACTIVO", font=FONT_SMALL, bg="#f1f5f9", fg=COLOR_MUTED, padx=5, pady=2).pack(side="left", padx=(0, 3))

        if prov.dvr_activo:
            tk.Label(f_badges, text="DVR ACTIVO", font=FONT_SMALL, bg="#ffedd5", fg="#c2410c", padx=5, pady=2).pack(side="left")
        else:
            tk.Label(f_badges, text="DVR INACTIVO", font=FONT_SMALL, bg="#f1f5f9", fg=COLOR_MUTED, padx=5, pady=2).pack(side="left")

        f_actions = tk.Frame(card, bg="#f8fafc", bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        f_actions.pack(fill="x")

        btn_ver = tk.Button(f_actions, text="Ver Matrices →", font=FONT_BOLD, bg=COLOR_ACCENT, fg="white",
                            activebackground=COLOR_ACCENT_HOVER, activeforeground="white", relief="flat", bd=0,
                            cursor="hand2", pady=5,
                            command=lambda p=prov.nombre: self._mostrar_vista_detalle(p))
        btn_ver.pack(side="left", fill="x", expand=True, padx=(6, 3), pady=6)

        btn_del = tk.Button(f_actions, text="Eliminar", font=FONT_BOLD, bg="#fee2e2", fg="#dc2626",
                            activebackground="#fca5a5", activeforeground="#dc2626", relief="flat", bd=0,
                            cursor="hand2", pady=5, padx=9,
                            command=lambda p=prov.nombre: self._eliminar_proveedor(p))
        btn_del.pack(side="right", padx=(0, 6), pady=6)

