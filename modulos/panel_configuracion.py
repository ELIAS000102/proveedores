"""
Modal de Configuración de Proveedor
---------------------------------------------------------------------------
Ventana emergente (Toplevel) para crear/editar un proveedor: días de
reporte/preparación/despacho de los flujos DDC y DVR, plazos adicionales,
plazos mínimos y desfase. Incluye una vista previa en vivo que usa los
mismos cálculos que el resto de la app (modulos.calculos_ddc /
modulos.calculos_dvr) para no duplicar lógica de negocio aquí.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

from modulos.estilos import *  # noqa: F401,F403 - constantes de color/fuente
from modulos.utilidades import _geometria_adaptativa
from modulos.modelo_datos import Proveedor
from modulos.calculos_ddc import calcular_ciclo_ddc_plazo
from modulos.calculos_dvr import calcular_ciclo_dvr_plazo


class PanelConfiguracion(tk.Toplevel):
    def __init__(self, master, proveedor, al_guardar, nombres_existentes):
        super().__init__(master)
        self.al_guardar = al_guardar
        self.proveedor_original = proveedor
        self.nombres_existentes = nombres_existentes

        self.title("Configuración de Proveedor" if proveedor else "Agregar Nuevo Proveedor")
        self.configure(bg=COLOR_BG)
        self.resizable(True, True)
        _geometria_adaptativa(self, ancho_ideal=820, alto_ideal=940, ancho_min=620, alto_min=520)
        self.transient(master)
        self.grab_set()

        self.var_nombre = tk.StringVar(value=proveedor.nombre if proveedor else "")
        self.var_tvi = tk.StringVar(value=proveedor.tvi if proveedor else "")
        self.var_tfi = tk.StringVar(value=proveedor.tfi if proveedor else "")

        self.var_ddc_activo = tk.BooleanVar(value=proveedor.ddc_activo if proveedor else False)
        self.chk_ddc_reporte = [tk.BooleanVar(value=(i in proveedor.ddc_reporte_dias) if proveedor else False) for i in range(7)]
        self.chk_ddc_preparacion = [tk.BooleanVar(value=(i in proveedor.ddc_preparacion_dias) if proveedor else False) for i in range(7)]
        self.chk_ddc_despacho = [tk.BooleanVar(value=(i in proveedor.ddc_despacho_dias) if proveedor else False) for i in range(7)]
        
        plazos_ddc_orig = proveedor.ddc_plazos_adicionales if proveedor else {}
        self.vars_ddc_plazos = {dia: tk.IntVar(value=plazos_ddc_orig.get(dia, 7)) for dia in ORDEN_VENTA}

        self.var_dvr_activo = tk.BooleanVar(value=proveedor.dvr_activo if proveedor else False)
        self.chk_dvr_reporte = [tk.BooleanVar(value=(i in proveedor.dvr_reporte_dias) if proveedor else False) for i in range(7)]
        self.chk_dvr_preparacion = [tk.BooleanVar(value=(i in proveedor.dvr_preparacion_dias) if proveedor else False) for i in range(7)]
        self.chk_dvr_ingreso = [tk.BooleanVar(value=(i in proveedor.dvr_ingreso_dias) if proveedor else False) for i in range(7)]
        self.chk_dvr_despacho = [tk.BooleanVar(value=(i in proveedor.dvr_despacho_dias) if proveedor else False) for i in range(7)]

        plazos_dvr_orig = proveedor.dvr_plazos_adicionales if proveedor else {}
        self.vars_dvr_plazos = {dia: tk.IntVar(value=plazos_dvr_orig.get(dia, 7)) for dia in ORDEN_VENTA}

        plazos_dvr_min_orig = proveedor.dvr_plazos_minimos if proveedor else {}
        self.vars_dvr_plazos_min = {dia: tk.IntVar(value=plazos_dvr_min_orig.get(dia, 1)) for dia in ORDEN_VENTA}

        # Desfase DVR
        self.var_dvr_usar_desface = tk.BooleanVar(value=proveedor.dvr_usar_desface if proveedor else False)
        desfaces_orig = proveedor.dvr_desfaces if proveedor else {}
        self.vars_dvr_desfaces = {dia: tk.IntVar(value=desfaces_orig.get(dia, 0)) for dia in ORDEN_VENTA}

        self._bloqueo_traza = False
        self._construir_ui()
        self._vincular_sincronizacion()
        self._actualizar_estados()

    def _construir_ui(self):
        main_box = tk.Frame(self, bg=COLOR_BG)
        main_box.pack(fill="both", expand=True, padx=6, pady=6)

        canvas = tk.Canvas(main_box, bg=COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_box, orient="vertical", command=canvas.yview)
        self.scroll_content = tk.Frame(canvas, bg=COLOR_BG)

        self.scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        card_gen = self._crear_tarjeta(self.scroll_content, "INFORMACIÓN GENERAL DEL PROVEEDOR")
        f_inputs = tk.Frame(card_gen, bg=COLOR_PANEL)
        f_inputs.pack(fill="x", padx=9, pady=6)
        f_inputs.grid_columnconfigure(1, weight=1)
        f_inputs.grid_columnconfigure(3, weight=1)

        ent_kwargs = dict(font=FONT_BASE, bd=0, relief="flat", highlightthickness=1,
                          highlightbackground=COLOR_CARD_BORDER, highlightcolor=COLOR_ACCENT)

        tk.Label(f_inputs, text="Nombre Proveedor:", font=FONT_BOLD, bg=COLOR_PANEL, fg=COLOR_TEXT).grid(row=0, column=0, sticky="w", pady=3)
        tk.Entry(f_inputs, textvariable=self.var_nombre, **ent_kwargs).grid(row=0, column=1, columnspan=3, sticky="ew", padx=(6, 0), pady=3, ipady=2)

        tk.Label(f_inputs, text="Código TVI:", font=FONT_BOLD, bg=COLOR_PANEL, fg=COLOR_TEXT).grid(row=1, column=0, sticky="w", pady=3)
        tk.Entry(f_inputs, textvariable=self.var_tvi, **ent_kwargs).grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=3, ipady=2)

        tk.Label(f_inputs, text="Código TFI:", font=FONT_BOLD, bg=COLOR_PANEL, fg=COLOR_TEXT).grid(row=1, column=2, sticky="w", padx=(9, 0), pady=3)
        tk.Entry(f_inputs, textvariable=self.var_tfi, **ent_kwargs).grid(row=1, column=3, sticky="ew", padx=(6, 0), pady=3, ipady=2)

        card_ddc = self._crear_tarjeta(self.scroll_content, "CONFIGURACIÓN FLUJO DDC (DESPACHO DIRECTO A CLIENTE)")
        top_ddc = tk.Frame(card_ddc, bg=COLOR_PANEL)
        top_ddc.pack(fill="x", padx=6, pady=(3, 2))

        tk.Checkbutton(top_ddc, text="Activar Flujo DDC", variable=self.var_ddc_activo,
                       command=self._actualizar_estados, font=FONT_SUBTITLE, bg=COLOR_PANEL, fg=COLOR_ACCENT).pack(side="left")

        self.f_ddc_rep = self._crear_grupo_dias(card_ddc, "Días de REPORTE DDC", self.chk_ddc_reporte)
        self.f_ddc_prep = self._crear_grupo_dias(card_ddc, "Días de PREPARACIÓN DDC", self.chk_ddc_preparacion)
        self.f_ddc_desp = self._crear_grupo_dias(card_ddc, "Días de DESPACHO DDC", self.chk_ddc_despacho)
        self.f_ddc_plazos, self.spins_ddc_plazos = self._crear_grid_plazos(card_ddc, "Plazo Adicional (Días Intermedios DDC):", self.vars_ddc_plazos)

        self.tabla_ddc_frame, self.lbls_ddc_resumen = self._crear_tabla_resumen_efectivos(
            card_ddc, "Resumen Informativo DDC (Solo Lectura)", incluir_plazo_min=False
        )

        card_dvr = self._crear_tarjeta(self.scroll_content, "CONFIGURACIÓN FLUJO DVR (DESPACHO VÍA RIPLEY)")
        top_dvr = tk.Frame(card_dvr, bg=COLOR_PANEL)
        top_dvr.pack(fill="x", padx=6, pady=(3, 2))

        tk.Checkbutton(top_dvr, text="Activar Flujo DVR", variable=self.var_dvr_activo,
                       command=self._actualizar_estados, font=FONT_SUBTITLE, bg=COLOR_PANEL, fg=COLOR_ACCENT).pack(side="left")

        self.f_dvr_rep = self._crear_grupo_dias(card_dvr, "Días de REPORTE DVR", self.chk_dvr_reporte)
        self.f_dvr_prep = self._crear_grupo_dias(card_dvr, "Días de PREPARACIÓN DVR", self.chk_dvr_preparacion)
        self.f_dvr_ing = self._crear_grupo_dias(card_dvr, "Días INGRESO AL CD DVR", self.chk_dvr_ingreso)
        self.f_dvr_desp = self._crear_grupo_dias(card_dvr, "Días de DESPACHO DVR", self.chk_dvr_despacho)

        self.f_dvr_plazos, self.spins_dvr_plazos = self._crear_grid_plazos(card_dvr, "Plazo Adicional (Días Venta -> Ingreso CD):", self.vars_dvr_plazos)
        self.f_dvr_plazos_min, self.spins_dvr_plazos_min = self._crear_grid_plazos(card_dvr, "Plazo Mínimo Base (Ingreso CD -> Despacho):", self.vars_dvr_plazos_min)

        # Apartado de Desfase DVR
        f_desface_container = tk.Frame(card_dvr, bg=COLOR_PANEL)
        f_desface_container.pack(fill="x", padx=6, pady=3)
        
        self.chk_dvr_usar_desface = tk.Checkbutton(
            f_desface_container, text="Proveedor cuenta con Desfase DVR (Afecta Plazo Mínimo)",
            variable=self.var_dvr_usar_desface, command=self._actualizar_estados,
            font=FONT_BOLD, bg=COLOR_PANEL, fg=COLOR_PRIMARY
        )
        self.chk_dvr_usar_desface.pack(anchor="w", pady=2)

        self.f_dvr_desfaces_grid, self.spins_dvr_desfaces = self._crear_grid_plazos(
            card_dvr, "Desfase por Día de Venta (Se suma al Plazo Mínimo del DVR):", self.vars_dvr_desfaces
        )

        self.tabla_dvr_frame, self.lbls_dvr_resumen = self._crear_tabla_resumen_efectivos(
            card_dvr, "Resumen Informativo DVR y Plazo Mínimo Dinámico (Solo Lectura)", incluir_plazo_min=True
        )

        btn_box = tk.Frame(self.scroll_content, bg=COLOR_BG)
        btn_box.pack(fill="x", pady=(3, 2))

        tk.Button(btn_box, text="Guardar Configuración", font=FONT_BOLD, bg=COLOR_ACCENT, fg="white",
                  activebackground=COLOR_ACCENT_HOVER, activeforeground="white", relief="flat", bd=0,
                  padx=12, pady=5, cursor="hand2",
                  command=self._guardar).pack(side="right")

        tk.Button(btn_box, text="Cancelar", font=FONT_BOLD, bg=COLOR_PANEL, fg="#dc2626",
                  activebackground="#fee2e2", activeforeground="#dc2626", relief="flat", bd=0,
                  highlightthickness=1, highlightbackground="#fecaca",
                  padx=12, pady=5, cursor="hand2",
                  command=self.destroy).pack(side="right", padx=(0, 6))

    def _crear_tarjeta(self, parent, titulo):
        card = tk.Frame(parent, bg=COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        card.pack(fill="x", pady=(0, 7))
        head = tk.Frame(card, bg=COLOR_HEADER_BG)
        head.pack(fill="x")
        tk.Label(head, text=titulo, font=FONT_HEADER, bg=COLOR_HEADER_BG, fg=COLOR_HEADER_TXT).pack(anchor="w", padx=7, pady=4)
        return card

    def _crear_tabla_resumen_efectivos(self, parent, titulo, incluir_plazo_min=False):
        container = tk.LabelFrame(parent, text=f" {titulo} ", font=FONT_HEADER, bg="#f0fdf4", fg="#15803d",
                                  bd=1, relief="solid", highlightthickness=0)
        container.pack(fill="x", padx=7, pady=6, ipadx=3, ipady=3)

        tbl = tk.Frame(container, bg="#bbf7d0")
        tbl.pack(fill="x", padx=3, pady=2)

        num_cols = 4 if incluir_plazo_min else 3
        for col_i in range(num_cols):
            tbl.grid_columnconfigure(col_i, weight=1)

        bg_hdr = "#dcfce7"
        fg_hdr = "#166534"

        tk.Label(tbl, text="Día Venta", font=FONT_HEADER, bg=bg_hdr, fg=fg_hdr).grid(row=0, column=0, sticky="nsew", padx=1, pady=1, ipady=2)
        tk.Label(tbl, text="Días Reporte", font=FONT_HEADER, bg=bg_hdr, fg=fg_hdr).grid(row=0, column=1, sticky="nsew", padx=1, pady=1, ipady=2)
        tk.Label(tbl, text="Días Preparación", font=FONT_HEADER, bg=bg_hdr, fg=fg_hdr).grid(row=0, column=2, sticky="nsew", padx=1, pady=1, ipady=2)
        
        if incluir_plazo_min:
            tk.Label(tbl, text="Plazo Mín. Dinámico", font=FONT_HEADER, bg=bg_hdr, fg=fg_hdr).grid(row=0, column=3, sticky="nsew", padx=1, pady=1, ipady=2)

        dict_labels = {}
        for idx, dia_nom in enumerate(ORDEN_VENTA):
            row_idx = idx + 1
            bg_row = "#f0fdf4" if row_idx % 2 != 0 else "#ffffff"

            tk.Label(tbl, text=dia_nom, font=FONT_SMALL, bg=bg_row, fg="#14532d").grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)

            lbl_rep = tk.Label(tbl, text="0", font=FONT_SMALL, bg=bg_row, fg="#14532d")
            lbl_rep.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)

            lbl_prep = tk.Label(tbl, text="0", font=FONT_SMALL, bg=bg_row, fg="#14532d")
            lbl_prep.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)

            if incluir_plazo_min:
                lbl_plazo_min = tk.Label(tbl, text="0", font=FONT_BOLD, bg=bg_row, fg="#c2410c")
                lbl_plazo_min.grid(row=row_idx, column=3, sticky="nsew", padx=1, pady=1)
                dict_labels[dia_nom] = (lbl_rep, lbl_prep, lbl_plazo_min)
            else:
                dict_labels[dia_nom] = (lbl_rep, lbl_prep)

        return container, dict_labels

    def _crear_grupo_dias(self, parent, titulo, variables):
        frame = tk.Frame(parent, bg=COLOR_PANEL)
        frame.pack(fill="x", padx=7, pady=2)
        tk.Label(frame, text=titulo, font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_MUTED).pack(anchor="w")

        sub = tk.Frame(frame, bg=COLOR_PANEL)
        sub.pack(fill="x", pady=1)
        for i in range(7):
            sub.grid_columnconfigure(i, weight=1)
            c = tk.Frame(sub, bg=COLOR_PANEL)
            c.grid(row=0, column=i, sticky="nsew")
            tk.Label(c, text=DIAS[i][:3], font=FONT_SMALL, bg=COLOR_PANEL).pack()
            cb = tk.Checkbutton(c, variable=variables[i], bg=COLOR_PANEL, command=self._refrescar_todo)
            cb.pack()
        return frame

    def _crear_grid_plazos(self, parent, titulo, dicc_vars):
        f_plaz = tk.Frame(parent, bg="#f8fafc", bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        f_plaz.pack(fill="x", padx=7, pady=4, ipadx=2, ipady=3)

        tk.Label(f_plaz, text=titulo, font=FONT_HEADER, bg="#f8fafc", fg=COLOR_PRIMARY).pack(anchor="w", padx=3, pady=(2, 3))
        grid = tk.Frame(f_plaz, bg="#f8fafc")
        grid.pack(fill="x", padx=2)

        spins = {}
        for idx, dia_nom in enumerate(ORDEN_VENTA):
            sub = tk.Frame(grid, bg="#f8fafc")
            sub.grid(row=0, column=idx, padx=1, sticky="ew")
            grid.grid_columnconfigure(idx, weight=1)

            tk.Label(sub, text=dia_nom[:3], font=FONT_SMALL, bg="#f8fafc", fg=COLOR_MUTED).pack()
            sp = tk.Spinbox(sub, from_=-10, to=30, width=2, textvariable=dicc_vars[dia_nom],
                            font=FONT_BASE, justify="center", bd=1, relief="solid", command=self._refrescar_todo)
            sp.pack(pady=1)
            spins[dia_nom] = sp
        return f_plaz, spins

    def _vincular_sincronizacion(self):
        def _sync_plazos(*args):
            if self._bloqueo_traza:
                return
            if self.var_ddc_activo.get():
                for dia in ORDEN_VENTA:
                    self.vars_dvr_plazos[dia].set(self.vars_ddc_plazos[dia].get())
            self._refrescar_todo()

        for dia in ORDEN_VENTA:
            self.vars_ddc_plazos[dia].trace_add("write", _sync_plazos)
            self.vars_dvr_plazos[dia].trace_add("write", lambda *a: self._refrescar_todo())
            self.vars_dvr_plazos_min[dia].trace_add("write", lambda *a: self._refrescar_todo())
            self.vars_dvr_desfaces[dia].trace_add("write", lambda *a: self._refrescar_todo())

    def _set_estado_controles(self, frame, activo):
        estado = "normal" if activo else "disabled"
        for w in frame.winfo_children():
            if isinstance(w, (tk.Checkbutton, tk.Spinbox, tk.Entry)):
                w.configure(state=estado)
            elif isinstance(w, (tk.Frame, tk.LabelFrame)):
                self._set_estado_controles(w, activo)

    def _actualizar_estados(self):
        ddc_on = self.var_ddc_activo.get()
        self._set_estado_controles(self.f_ddc_rep, ddc_on)
        self._set_estado_controles(self.f_ddc_prep, ddc_on)
        self._set_estado_controles(self.f_ddc_desp, ddc_on)
        self._set_estado_controles(self.f_ddc_plazos, ddc_on)

        dvr_on = self.var_dvr_activo.get()
        self._set_estado_controles(self.f_dvr_rep, dvr_on)
        self._set_estado_controles(self.f_dvr_prep, dvr_on)
        self._set_estado_controles(self.f_dvr_ing, dvr_on)
        self._set_estado_controles(self.f_dvr_desp, dvr_on)
        self._set_estado_controles(self.f_dvr_plazos_min, dvr_on)

        # Estado del check y grid de desfasamiento
        if dvr_on:
            self.chk_dvr_usar_desface.configure(state="normal")
            usar_desface = self.var_dvr_usar_desface.get()
            self._set_estado_controles(self.f_dvr_desfaces_grid, usar_desface)
        else:
            self.chk_dvr_usar_desface.configure(state="disabled")
            self._set_estado_controles(self.f_dvr_desfaces_grid, False)

        if ddc_on:
            for dia in ORDEN_VENTA:
                self.vars_dvr_plazos[dia].set(self.vars_ddc_plazos[dia].get())
                self.spins_dvr_plazos[dia].configure(state="disabled")
        else:
            estado_dvr_plazo = "normal" if dvr_on else "disabled"
            for dia in ORDEN_VENTA:
                self.spins_dvr_plazos[dia].configure(state=estado_dvr_plazo)

        self._refrescar_todo()

    def _refrescar_todo(self):
        if self._bloqueo_traza:
            return
        self._bloqueo_traza = True

        prov_temp = Proveedor(
            nombre="TEMP",
            ddc_activo=self.var_ddc_activo.get(),
            ddc_reporte_dias={i for i, v in enumerate(self.chk_ddc_reporte) if v.get()},
            ddc_preparacion_dias={i for i, v in enumerate(self.chk_ddc_preparacion) if v.get()},
            ddc_despacho_dias={i for i, v in enumerate(self.chk_ddc_despacho) if v.get()},
            ddc_plazos_adicionales={d: v.get() for d, v in self.vars_ddc_plazos.items()},
            
            dvr_activo=self.var_dvr_activo.get(),
            dvr_reporte_dias={i for i, v in enumerate(self.chk_dvr_reporte) if v.get()},
            dvr_preparacion_dias={i for i, v in enumerate(self.chk_dvr_preparacion) if v.get()},
            dvr_ingreso_dias={i for i, v in enumerate(self.chk_dvr_ingreso) if v.get()},
            dvr_despacho_dias={i for i, v in enumerate(self.chk_dvr_despacho) if v.get()},
            dvr_plazos_adicionales={d: v.get() for d, v in self.vars_dvr_plazos.items()},
            dvr_plazos_minimos={d: v.get() for d, v in self.vars_dvr_plazos_min.items()},
            dvr_usar_desface=self.var_dvr_usar_desface.get(),
            dvr_desfaces={d: v.get() for d, v in self.vars_dvr_desfaces.items()}
        )

        ref = date.today() - timedelta(days=date.today().weekday())
        ventas = [ref + timedelta(days=i) for i in range(7)]

        for i, nom_dia in enumerate(ORDEN_VENTA):
            lbl_rep, lbl_prep = self.lbls_ddc_resumen[nom_dia]
            if prov_temp.ddc_activo:
                c_ddc = calcular_ciclo_ddc_plazo(ventas[i], nom_dia, prov_temp)
                if c_ddc:
                    cant_rep = 1 if c_ddc[0] else 0
                    cant_prep = len(c_ddc[1])
                    lbl_rep.config(text=str(cant_rep))
                    lbl_prep.config(text=str(cant_prep))
                else:
                    lbl_rep.config(text="0")
                    lbl_prep.config(text="0")
            else:
                lbl_rep.config(text="0")
                lbl_prep.config(text="0")

        for i, nom_dia in enumerate(ORDEN_VENTA):
            lbl_rep, lbl_prep, lbl_plazo_min = self.lbls_dvr_resumen[nom_dia]
            if prov_temp.dvr_activo:
                c_dvr = calcular_ciclo_dvr_plazo(ventas[i], nom_dia, prov_temp)
                if c_dvr:
                    cant_rep = 1 if c_dvr[0] else 0
                    cant_prep = len(c_dvr[1])
                    plazo_min_efectivo = c_dvr[4]
                    lbl_rep.config(text=str(cant_rep))
                    lbl_prep.config(text=str(cant_prep))
                    lbl_plazo_min.config(text=str(plazo_min_efectivo))
                else:
                    lbl_rep.config(text="0")
                    lbl_prep.config(text="0")
                    lbl_plazo_min.config(text="0")
            else:
                lbl_rep.config(text="0")
                lbl_prep.config(text="0")
                lbl_plazo_min.config(text="0")

        self._bloqueo_traza = False

    def _guardar(self):
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "El nombre del proveedor es obligatorio.", parent=self)
            return

        nombre_previo = self.proveedor_original.nombre if self.proveedor_original else None
        if nombre != nombre_previo and nombre in self.nombres_existentes:
            messagebox.showwarning("Atención", "Ya existe un proveedor con este nombre.", parent=self)
            return

        p = Proveedor(
            nombre=nombre,
            tvi=self.var_tvi.get().strip(),
            tfi=self.var_tfi.get().strip(),
            
            ddc_activo=self.var_ddc_activo.get(),
            ddc_reporte_dias={i for i, v in enumerate(self.chk_ddc_reporte) if v.get()},
            ddc_preparacion_dias={i for i, v in enumerate(self.chk_ddc_preparacion) if v.get()},
            ddc_despacho_dias={i for i, v in enumerate(self.chk_ddc_despacho) if v.get()},
            ddc_plazos_adicionales={dia: v.get() for dia, v in self.vars_ddc_plazos.items()},
            
            dvr_activo=self.var_dvr_activo.get(),
            dvr_reporte_dias={i for i, v in enumerate(self.chk_dvr_reporte) if v.get()},
            dvr_preparacion_dias={i for i, v in enumerate(self.chk_dvr_preparacion) if v.get()},
            dvr_ingreso_dias={i for i, v in enumerate(self.chk_dvr_ingreso) if v.get()},
            dvr_despacho_dias={i for i, v in enumerate(self.chk_dvr_despacho) if v.get()},
            dvr_plazos_adicionales={dia: v.get() for dia, v in self.vars_dvr_plazos.items()},
            dvr_plazos_minimos={dia: v.get() for dia, v in self.vars_dvr_plazos_min.items()},
            dvr_usar_desface=self.var_dvr_usar_desface.get(),
            dvr_desfaces={dia: v.get() for dia, v in self.vars_dvr_desfaces.items()}
        )

        self.al_guardar(p, nombre_previo, self.proveedor_original is None)
        self.destroy()


# ---------------------------------------------------------------------------
# Aplicación Principal
# ---------------------------------------------------------------------------

