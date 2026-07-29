"""
Ventana Principal de la Aplicación
---------------------------------------------------------------------------
Define la clase App (ventana raíz tk.Tk): construye el layout general
(sidebar + contenedor principal) y combina, mediante mixins, cada pantalla
de la app:

    - VistaPrincipalMixin        -> modulos/vista_principal.py
    - VistaAjustesSistemaMixin   -> modulos/vista_ajustes_sistema.py
    - VistaDetalleProveedorMixin -> modulos/vista_detalle_proveedor.py
    - TarjetasFlujoMixin         -> modulos/tarjetas_flujo.py

Cada mixin aporta un conjunto de métodos que operan sobre el mismo `self`
(la instancia de App), por eso comparten atributos como self.proveedores,
self.bloqueos, self.main_container, etc. definidos en __init__.

Para modificar el comportamiento de una pantalla concreta, edita el
archivo del mixin correspondiente en vez de buscar en este archivo.
"""
import sys
import tkinter as tk
from datetime import date

from modulos.estilos import *  # noqa: F401,F403 - constantes de color/fuente
from modulos.utilidades import _geometria_adaptativa
from modulos.modelo_datos import cargar_proveedores_json, cargar_bloqueos_json

from modulos.vista_principal import VistaPrincipalMixin
from modulos.vista_ajustes_sistema import VistaAjustesSistemaMixin
from modulos.vista_detalle_proveedor import VistaDetalleProveedorMixin
from modulos.tarjetas_flujo import TarjetasFlujoMixin


class App(VistaPrincipalMixin, VistaAjustesSistemaMixin,
          VistaDetalleProveedorMixin, TarjetasFlujoMixin, tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Supply Chain Flow Monitor - Dashboard Principal")
        self.configure(bg=COLOR_BG)
        _geometria_adaptativa(self, ancho_ideal=1400, alto_ideal=850, ancho_min=1000, alto_min=620)

        self.proveedores = cargar_proveedores_json()
        self.bloqueos = cargar_bloqueos_json()
        self.proveedor_seleccionado = None
        self.sidebar_expandido = True
        self.filtro_busqueda = tk.StringVar()
        self.menu_labels = []

        hoy_cal = date.today()
        self.calendario_anio = hoy_cal.year
        self.calendario_mes = hoy_cal.month
        self.dia_calendario_seleccionado = None

        self._construir_layout()
        self._configurar_scroll_global()
        self._mostrar_vista_principal()

    def _configurar_scroll_global(self):
        def _al_usar_rueda(event):
            widget = self.winfo_containing(event.x_root, event.y_root)
            if not widget:
                return

            curr = widget
            canvas = None
            while curr:
                if isinstance(curr, tk.Canvas):
                    canvas = curr
                    break
                curr = getattr(curr, "master", None)

            if canvas:
                if event.num == 4:
                    delta = -1
                elif event.num == 5:
                    delta = 1
                else:
                    delta = int(-1 * (event.delta / 120))
                    if sys.platform == "darwin":
                        delta = -1 if event.delta > 0 else 1

                canvas.yview_scroll(delta * 2, "units")

        self.bind_all("<MouseWheel>", _al_usar_rueda)
        self.bind_all("<Button-4>", _al_usar_rueda)
        self.bind_all("<Button-5>", _al_usar_rueda)

    def _construir_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(self, bg=COLOR_SIDEBAR_BG, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)

        self.sb_top = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_BG)
        self.sb_top.pack(fill="x", padx=10, pady=12)

        self.btn_toggle = tk.Button(self.sb_top, text="☰", font=("Segoe UI", 12, "bold"), bg=COLOR_SIDEBAR_BG, fg="white",
                                    activebackground=COLOR_SIDEBAR_HOVER, activeforeground="white", relief="flat",
                                    bd=0, cursor="hand2", command=self._toggle_sidebar)
        self.btn_toggle.pack(side="left")

        self.lbl_brand = tk.Label(self.sb_top, text="FLOW MONITOR", font=FONT_BRAND, bg=COLOR_SIDEBAR_BG, fg="white")
        self.lbl_brand.pack(side="left", padx=7)

        tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_HOVER, height=1).pack(fill="x", padx=10)

        self.sb_items_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_BG)
        self.sb_items_frame.pack(fill="x", padx=6, pady=9)

        self._crear_item_menu("Menú Principal", self._mostrar_vista_principal)

        self.lbl_seccion = tk.Label(self.sb_items_frame, text="OTROS APARTADOS", font=FONT_CAPTION, bg=COLOR_SIDEBAR_BG, fg="#64748b")
        self.lbl_seccion.pack(anchor="w", padx=9, pady=(12, 5))

        self._crear_item_menu("Ajustes Sistema", self._mostrar_vista_ajustes_sistema)

        self.main_container = tk.Frame(self, bg=COLOR_BG)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

    def _crear_item_menu(self, texto, comando):
        cursor_style = "hand2" if comando else ""
        btn_f = tk.Frame(self.sb_items_frame, bg=COLOR_SIDEBAR_BG, cursor=cursor_style)
        btn_f.pack(fill="x", pady=2)

        lbl_txt = tk.Label(btn_f, text=texto, font=FONT_BOLD, bg=COLOR_SIDEBAR_BG,
                           fg="white" if comando else "#64748b", cursor=cursor_style)
        lbl_txt.pack(side="left", padx=7, pady=6)

        self.menu_labels.append(lbl_txt)

        if comando:
            for w in (btn_f, lbl_txt):
                w.bind("<Button-1>", lambda e: comando())
                w.bind("<Enter>", lambda e, f=btn_f: f.configure(bg=COLOR_SIDEBAR_HOVER))
                w.bind("<Leave>", lambda e, f=btn_f: f.configure(bg=COLOR_SIDEBAR_BG))

    def _toggle_sidebar(self):
        if self.sidebar_expandido:
            self.lbl_brand.pack_forget()
            self.lbl_seccion.pack_forget()
            for lbl in self.menu_labels:
                lbl.pack_forget()
            self.sidebar.configure(width=52)
            self.sidebar_expandido = False
        else:
            self.lbl_brand.pack(side="left", padx=7)
            self.lbl_seccion.pack(anchor="w", padx=9, pady=(12, 5))
            for lbl in self.menu_labels:
                lbl.pack(side="left", padx=7, pady=6)
            self.sidebar.configure(width=220)
            self.sidebar_expandido = True
