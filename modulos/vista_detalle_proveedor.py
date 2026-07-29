"""
Vista de Detalle de Proveedor (CRUD)
---------------------------------------------------------------------------
Mixin de la clase App con la pantalla de detalle de un proveedor (cabecera,
botón de configuración) y las acciones de alta/edición/baja, que abren el
PanelConfiguracion y persisten los cambios. El dibujo de las matrices DDC/DVR
vive en modulos/tarjetas_flujo.py para no mezclar ambas responsabilidades.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from modulos.estilos import *  # noqa: F401,F403 - constantes de color/fuente
from modulos.modelo_datos import guardar_proveedores_json
from modulos.panel_configuracion import PanelConfiguracion


class VistaDetalleProveedorMixin:
    """Pantalla de detalle de un proveedor y sus acciones de alta/edición/baja."""

    def _mostrar_vista_detalle(self, nombre_proveedor):
        self.proveedor_seleccionado = nombre_proveedor
        for w in self.main_container.winfo_children():
            w.destroy()

        self.main_container.grid_rowconfigure(0, weight=0)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        prov = self.proveedores[nombre_proveedor]

        top_bar = tk.Frame(self.main_container, bg=COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        top_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))

        btn_back = tk.Button(top_bar, text="← Volver al Menú", font=FONT_BOLD, bg="#e2e8f0", fg=COLOR_PRIMARY,
                             activebackground="#cbd5e1", activeforeground=COLOR_PRIMARY, relief="flat", bd=0,
                             cursor="hand2", padx=9, pady=5,
                             command=self._mostrar_vista_principal)
        btn_back.pack(side="left", padx=10, pady=9)

        head_tit = tk.Frame(top_bar, bg=COLOR_PANEL)
        head_tit.pack(side="left", padx=12)

        tk.Label(head_tit, text=f"MATRICES DE FLUJO DE VENTA: {prov.nombre}", font=FONT_TITLE, bg=COLOR_PANEL, fg=COLOR_PRIMARY).pack(anchor="w")
        
        f_sub_codes = tk.Frame(head_tit, bg=COLOR_PANEL)
        f_sub_codes.pack(anchor="w", pady=(2, 0))
        tk.Label(f_sub_codes, text=f"Código TVI: {prov.tvi or 'N/A'}", font=FONT_BOLD, bg="#e0f2fe", fg="#0369a1", padx=5, pady=1).pack(side="left", padx=(0, 5))
        tk.Label(f_sub_codes, text=f"Código TFI: {prov.tfi or 'N/A'}", font=FONT_BOLD, bg="#fef3c7", fg="#b45309", padx=5, pady=1).pack(side="left")

        btn_cfg = tk.Button(top_bar, text="⚙ Configurar", font=FONT_BOLD, bg="#0f172a", fg="white",
                            activebackground="#1e293b", activeforeground="white", relief="flat", bd=0,
                            cursor="hand2", padx=10, pady=5,
                            command=lambda: self._editar_proveedor(prov))
        btn_cfg.pack(side="right", padx=9, pady=7)

        f_scroll = tk.Frame(self.main_container, bg=COLOR_BG)
        f_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 9))

        canvas = tk.Canvas(f_scroll, bg=COLOR_BG, highlightthickness=0)
        sb = ttk.Scrollbar(f_scroll, orient="vertical", command=canvas.yview)

        contenido = tk.Frame(canvas, bg=COLOR_BG)
        contenido.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        c_win = canvas.create_window((0, 0), window=contenido, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(c_win, width=e.width))
        canvas.configure(yscrollcommand=sb.set)

        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        if not prov.ddc_activo and not prov.dvr_activo:
            tk.Label(contenido, text="Este proveedor no tiene activado ningún flujo de venta (DDC o DVR).",
                     font=FONT_SUBTITLE, bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=14, anchor="nw")
            return

        if prov.ddc_activo:
            card_ddc = self._crear_tarjeta_ddc(contenido, prov)
            card_ddc.pack(fill="x", expand=False, pady=(0, 9), anchor="nw")

        if prov.dvr_activo:
            card_dvr = self._crear_tarjeta_dvr(contenido, prov)
            card_dvr.pack(fill="x", expand=False, pady=(0, 9), anchor="nw")

    def _agregar_proveedor(self):
        PanelConfiguracion(self, None, self._al_guardar_proveedor, set(self.proveedores.keys()))

    def _editar_proveedor(self, proveedor):
        nombres = set(self.proveedores.keys()) - {proveedor.nombre}
        PanelConfiguracion(self, proveedor, self._al_guardar_proveedor, nombres)

    def _eliminar_proveedor(self, nombre):
        if messagebox.askyesno("Confirmar Eliminación", f"¿Deseas eliminar al proveedor '{nombre}'?", parent=self):
            del self.proveedores[nombre]
            guardar_proveedores_json(self.proveedores)
            
            if self.proveedor_seleccionado == nombre:
                self._mostrar_vista_principal()
            else:
                self._renderizar_grid_proveedores()

    def _al_guardar_proveedor(self, proveedor, nombre_previo, es_nuevo):
        if not es_nuevo and nombre_previo and nombre_previo in self.proveedores:
            del self.proveedores[nombre_previo]
            
        self.proveedores[proveedor.nombre] = proveedor
        guardar_proveedores_json(self.proveedores)

        if self.proveedor_seleccionado:
            self._mostrar_vista_detalle(proveedor.nombre)
        else:
            self._mostrar_vista_principal()

