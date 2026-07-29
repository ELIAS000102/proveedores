"""
Vista de Ajustes del Sistema: Días Inoperativos (Bloqueo Masivo)
---------------------------------------------------------------------------
Mixin de la clase App con la pantalla de "Ajustes Sistema": el calendario
mensual y la lista de días inoperativos configurados. Al seleccionar un día
en el calendario se abre una ventana emergente (Toplevel) para elegir si el
bloqueo afecta a todos los proveedores o solo a algunos.
"""
import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from modulos.estilos import *  # noqa: F401,F403 - constantes de color/fuente
from modulos.utilidades import _geometria_adaptativa
from modulos.modelo_datos import TODOS_LOS_PROVEEDORES, guardar_bloqueos_json


class VistaAjustesSistemaMixin:
    """Pantalla de calendario de días inoperativos y su ventana de bloqueo."""

    def _mostrar_vista_ajustes_sistema(self):
        self.proveedor_seleccionado = None
        for w in self.main_container.winfo_children():
            w.destroy()

        self.main_container.grid_rowconfigure(0, weight=0)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        top_bar = tk.Frame(self.main_container, bg=COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        top_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))

        head_info = tk.Frame(top_bar, bg=COLOR_PANEL)
        head_info.pack(side="left", padx=12, pady=9)

        tk.Label(head_info, text="Ajustes del Sistema", font=FONT_TITLE, bg=COLOR_PANEL, fg=COLOR_PRIMARY).pack(anchor="w")
        tk.Label(head_info, text="Declara días inoperativos (feriados o casos únicos) para uno o varios proveedores",
                 font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_MUTED).pack(anchor="w")

        body = tk.Frame(self.main_container, bg=COLOR_BG)
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 9))
        body.grid_columnconfigure(0, weight=3, minsize=480)
        body.grid_columnconfigure(1, weight=2, minsize=280)
        body.grid_rowconfigure(0, weight=1)

        # --- Panel de Calendario (ampliado) ---
        cal_panel = tk.Frame(body, bg=COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        cal_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        nav = tk.Frame(cal_panel, bg=COLOR_PANEL)
        nav.pack(fill="x", padx=14, pady=(14, 8))

        tk.Button(nav, text="‹", font=("Segoe UI", 13, "bold"), bg=COLOR_ACCENT, fg="white",
                  activebackground=COLOR_ACCENT_HOVER, activeforeground="white", relief="flat", bd=0,
                  cursor="hand2", width=3, pady=4, command=self._calendario_mes_anterior).pack(side="left")

        self.lbl_mes_actual = tk.Label(nav, text="", font=("Segoe UI", 12, "bold"), bg=COLOR_PANEL, fg=COLOR_PRIMARY)
        self.lbl_mes_actual.pack(side="left", expand=True)

        tk.Button(nav, text="›", font=("Segoe UI", 13, "bold"), bg=COLOR_ACCENT, fg="white",
                  activebackground=COLOR_ACCENT_HOVER, activeforeground="white", relief="flat", bd=0,
                  cursor="hand2", width=3, pady=4, command=self._calendario_mes_siguiente).pack(side="right")

        leyenda_cal = tk.Frame(cal_panel, bg=COLOR_PANEL)
        leyenda_cal.pack(fill="x", padx=14)
        tk.Label(leyenda_cal, text="Día inoperativo", font=FONT_SMALL, bg=COLOR_DIA_INOPERATIVO,
                 fg=COLOR_DIA_INOPERATIVO_TXT, padx=6, pady=2).pack(side="left")
        tk.Label(leyenda_cal, text="Seleccionado", font=FONT_SMALL, bg=COLOR_HOY_BORDER,
                 fg="white", padx=6, pady=2).pack(side="left", padx=6)

        self.cal_grid_frame = tk.Frame(cal_panel, bg=COLOR_BORDER)
        self.cal_grid_frame.pack(fill="both", expand=True, padx=14, pady=14)

        # --- Panel Lateral: solo lista de días inoperativos configurados ---
        side_panel = tk.Frame(body, bg=COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        side_panel.grid(row=0, column=1, sticky="nsew")

        side_head = tk.Frame(side_panel, bg=COLOR_PANEL)
        side_head.pack(fill="x", padx=14, pady=(14, 8))

        tk.Label(side_head, text="Días inoperativos configurados", font=FONT_SUBTITLE,
                 bg=COLOR_PANEL, fg=COLOR_PRIMARY).pack(anchor="w")
        tk.Label(side_head, text="Selecciona un día en el calendario para bloquearlo o editarlo",
                 font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_MUTED, wraplength=260, justify="left").pack(anchor="w", pady=(2, 0))

        lista_wrap = tk.Frame(side_panel, bg=COLOR_PANEL)
        lista_wrap.pack(fill="both", expand=True, padx=14, pady=(4, 14))

        canvas_lista = tk.Canvas(lista_wrap, bg=COLOR_PANEL, highlightthickness=0)
        sb_lista = ttk.Scrollbar(lista_wrap, orient="vertical", command=canvas_lista.yview)

        self.frame_lista_bloqueos = tk.Frame(canvas_lista, bg=COLOR_PANEL)
        self.frame_lista_bloqueos.bind("<Configure>", lambda e: canvas_lista.configure(scrollregion=canvas_lista.bbox("all")))
        c_win_lb = canvas_lista.create_window((0, 0), window=self.frame_lista_bloqueos, anchor="nw")
        canvas_lista.bind("<Configure>", lambda e: canvas_lista.itemconfig(c_win_lb, width=e.width))
        canvas_lista.configure(yscrollcommand=sb_lista.set)

        sb_lista.pack(side="right", fill="y")
        canvas_lista.pack(side="left", fill="both", expand=True)

        self._renderizar_calendario_bloqueos()
        self._renderizar_lista_bloqueos()

    def _calendario_mes_anterior(self):
        self.calendario_mes -= 1
        if self.calendario_mes < 1:
            self.calendario_mes = 12
            self.calendario_anio -= 1
        self.dia_calendario_seleccionado = None
        self._renderizar_calendario_bloqueos()

    def _calendario_mes_siguiente(self):
        self.calendario_mes += 1
        if self.calendario_mes > 12:
            self.calendario_mes = 1
            self.calendario_anio += 1
        self.dia_calendario_seleccionado = None
        self._renderizar_calendario_bloqueos()

    def _seleccionar_dia_calendario(self, fecha_sel):
        self.dia_calendario_seleccionado = fecha_sel
        self._renderizar_calendario_bloqueos()
        self._abrir_dialogo_bloqueo_dia(fecha_sel)

    def _renderizar_calendario_bloqueos(self):
        for w in self.cal_grid_frame.winfo_children():
            w.destroy()

        meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
                    "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_mes_actual.config(text=f"{meses_es[self.calendario_mes - 1]} {self.calendario_anio}")

        for c in range(7):
            self.cal_grid_frame.grid_columnconfigure(c, weight=1, uniform="cal_c")

        for c, nombre_dia in enumerate(["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]):
            tk.Label(self.cal_grid_frame, text=nombre_dia, font=FONT_SMALL, bg=COLOR_HEADER_BG, fg=COLOR_HEADER_TXT
                     ).grid(row=0, column=c, sticky="nsew", padx=1, pady=1, ipady=4)

        cal = calendar.Calendar(firstweekday=0)
        semanas = cal.monthdatescalendar(self.calendario_anio, self.calendario_mes)
        hoy = date.today()

        for r, semana in enumerate(semanas):
            self.cal_grid_frame.grid_rowconfigure(r + 1, weight=1, uniform="cal_r")
            for c, dia_fecha in enumerate(semana):
                del_mes_actual = dia_fecha.month == self.calendario_mes
                info_bloqueo = self.bloqueos.get(dia_fecha.isoformat())
                seleccionado = self.dia_calendario_seleccionado == dia_fecha

                if info_bloqueo:
                    bg, fg = COLOR_DIA_INOPERATIVO, COLOR_DIA_INOPERATIVO_TXT
                elif seleccionado:
                    bg, fg = COLOR_HOY_BORDER, "white"
                else:
                    bg = COLOR_PANEL if del_mes_actual else "#f1f5f9"
                    fg = COLOR_ACCENT if (dia_fecha == hoy and del_mes_actual) else (COLOR_TEXT if del_mes_actual else COLOR_MUTED)

                lbl = tk.Label(self.cal_grid_frame, text=str(dia_fecha.day), font=("Segoe UI", 11, "bold"), bg=bg, fg=fg,
                               cursor="hand2", padx=4, pady=16)
                lbl.grid(row=r + 1, column=c, sticky="nsew", padx=1, pady=1)
                lbl.bind("<Button-1>", lambda e, f=dia_fecha: self._seleccionar_dia_calendario(f))

    def _abrir_dialogo_bloqueo_dia(self, fecha_sel):
        """Ventana emergente que se abre al elegir un día del calendario: permite
        declararlo inoperativo para todos los proveedores o solo para algunos."""
        info_actual = self.bloqueos.get(fecha_sel.isoformat())
        provs_actuales = info_actual.get("proveedores", []) if info_actual else []

        dlg = tk.Toplevel(self)
        dlg.title("Día inoperativo")
        dlg.configure(bg=COLOR_PANEL)
        dlg.transient(self)
        _geometria_adaptativa(dlg, 440, 560, 380, 420)
        dlg.grab_set()

        def _cerrar_dialogo():
            self.dia_calendario_seleccionado = None
            self._renderizar_calendario_bloqueos()
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", _cerrar_dialogo)

        header = tk.Frame(dlg, bg=COLOR_PANEL)
        header.pack(fill="x", padx=18, pady=(18, 8))
        tk.Label(header, text=fecha_sel.strftime("%d/%m/%Y"), font=FONT_TITLE,
                 bg=COLOR_PANEL, fg=COLOR_PRIMARY).pack(anchor="w")
        tk.Label(header, text="¿El día inoperativo afecta a todos los proveedores o solo a algunos?",
                 font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_MUTED, wraplength=390, justify="left"
                 ).pack(anchor="w", pady=(3, 0))

        tk.Frame(dlg, bg=COLOR_BORDER, height=1).pack(fill="x", padx=18, pady=(10, 12))

        body = tk.Frame(dlg, bg=COLOR_PANEL)
        body.pack(fill="both", expand=True, padx=18)

        var_todos = tk.BooleanVar(value=(TODOS_LOS_PROVEEDORES in provs_actuales))
        vars_prov = {}
        chk_prov = {}

        def _toggle_todos():
            estado = "disabled" if var_todos.get() else "normal"
            for chk in chk_prov.values():
                chk.config(state=estado)

        tk.Checkbutton(body, text="Todos los proveedores", variable=var_todos, font=FONT_BOLD,
                        bg=COLOR_PANEL, activebackground=COLOR_PANEL, cursor="hand2",
                        command=_toggle_todos).pack(anchor="w", pady=(0, 10))

        tk.Label(body, text="Proveedores específicos", font=FONT_BOLD, bg=COLOR_PANEL, fg=COLOR_TEXT
                 ).pack(anchor="w", pady=(0, 4))

        lista_wrap = tk.Frame(body, bg=COLOR_PANEL, bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        lista_wrap.pack(fill="both", expand=True)

        canvas_p = tk.Canvas(lista_wrap, bg=COLOR_PANEL, highlightthickness=0)
        sb_p = ttk.Scrollbar(lista_wrap, orient="vertical", command=canvas_p.yview)
        frame_p = tk.Frame(canvas_p, bg=COLOR_PANEL)
        frame_p.bind("<Configure>", lambda e: canvas_p.configure(scrollregion=canvas_p.bbox("all")))
        win_p = canvas_p.create_window((0, 0), window=frame_p, anchor="nw")
        canvas_p.bind("<Configure>", lambda e: canvas_p.itemconfig(win_p, width=e.width))
        canvas_p.configure(yscrollcommand=sb_p.set)
        sb_p.pack(side="right", fill="y")
        canvas_p.pack(side="left", fill="both", expand=True)

        estado_inicial = "disabled" if var_todos.get() else "normal"
        for nombre in sorted(self.proveedores.keys()):
            var = tk.BooleanVar(value=(nombre in provs_actuales))
            chk = tk.Checkbutton(frame_p, text=nombre, variable=var, font=FONT_BASE, bg=COLOR_PANEL,
                                  state=estado_inicial)
            chk.pack(anchor="w", padx=8, pady=2)
            vars_prov[nombre] = var
            chk_prov[nombre] = chk

        footer = tk.Frame(dlg, bg=COLOR_PANEL)
        footer.pack(fill="x", padx=18, pady=18)

        def _guardar():
            if var_todos.get():
                provs = [TODOS_LOS_PROVEEDORES]
            else:
                provs = [nombre for nombre, var in vars_prov.items() if var.get()]

            if not provs:
                messagebox.showwarning(
                    "Selecciona proveedores",
                    "Marca 'Todos los proveedores' o al menos un proveedor específico para declarar este día como inoperativo.",
                    parent=dlg)
                return

            self.bloqueos[fecha_sel.isoformat()] = {"proveedores": provs}
            guardar_bloqueos_json(self.bloqueos)
            self.dia_calendario_seleccionado = None
            self._renderizar_calendario_bloqueos()
            self._renderizar_lista_bloqueos()
            dlg.destroy()

        def _quitar():
            self._quitar_bloqueo_fecha(fecha_sel.isoformat())
            self.dia_calendario_seleccionado = None
            self._renderizar_calendario_bloqueos()
            dlg.destroy()

        tk.Button(footer, text="Guardar", font=FONT_BOLD, bg="#059669", fg="white",
                  activebackground="#047857", activeforeground="white", relief="flat", bd=0,
                  cursor="hand2", padx=14, pady=7, command=_guardar).pack(side="left")

        if info_actual:
            tk.Button(footer, text="Quitar bloqueo", font=FONT_BOLD, bg="#fee2e2", fg="#dc2626",
                      activebackground="#fca5a5", activeforeground="#dc2626", relief="flat", bd=0,
                      cursor="hand2", padx=14, pady=7, command=_quitar).pack(side="left", padx=(8, 0))

        tk.Button(footer, text="Cancelar", font=FONT_BOLD, bg="#e2e8f0", fg=COLOR_PRIMARY,
                  activebackground="#cbd5e1", activeforeground=COLOR_PRIMARY, relief="flat", bd=0,
                  cursor="hand2", padx=14, pady=7, command=_cerrar_dialogo).pack(side="right")

    def _quitar_bloqueo_fecha(self, fecha_str):
        if fecha_str in self.bloqueos:
            del self.bloqueos[fecha_str]
            guardar_bloqueos_json(self.bloqueos)
        self._renderizar_calendario_bloqueos()
        self._renderizar_lista_bloqueos()

    def _renderizar_lista_bloqueos(self):
        for w in self.frame_lista_bloqueos.winfo_children():
            w.destroy()

        if not self.bloqueos:
            tk.Label(self.frame_lista_bloqueos, text="No hay días inoperativos configurados.",
                     font=FONT_SMALL, bg=COLOR_PANEL, fg=COLOR_MUTED).pack(anchor="w", pady=7)
            return

        for fecha_str in sorted(self.bloqueos.keys()):
            info = self.bloqueos[fecha_str]
            provs = info.get("proveedores", [])
            try:
                fecha_fmt = date.fromisoformat(fecha_str).strftime("%d/%m/%Y")
            except ValueError:
                fecha_fmt = fecha_str

            texto_provs = "Todos los proveedores" if TODOS_LOS_PROVEEDORES in provs else (", ".join(provs) if provs else "—")

            row = tk.Frame(self.frame_lista_bloqueos, bg="#fef2f2", bd=0, highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
            row.pack(fill="x", pady=2)

            info_box = tk.Frame(row, bg="#fef2f2")
            info_box.pack(side="left", fill="x", expand=True, padx=6, pady=5)

            tk.Label(info_box, text=fecha_fmt, font=FONT_BOLD, bg="#fef2f2", fg="#991b1b").pack(anchor="w")
            tk.Label(info_box, text=texto_provs, font=FONT_SMALL, bg="#fef2f2", fg=COLOR_MUTED,
                     wraplength=220, justify="left").pack(anchor="w")

            tk.Button(row, text="×", font=("Segoe UI", 11, "bold"), bg="#fee2e2", fg="#dc2626", activebackground="#fca5a5",
                      activeforeground="#dc2626", relief="flat", bd=0, cursor="hand2", padx=6, pady=1,
                      command=lambda fs=fecha_str: self._quitar_bloqueo_fecha(fs)).pack(side="right", padx=6)

