"""
Modelo de Datos y Persistencia
---------------------------------------------------------------------------
Define la entidad Proveedor y toda la lectura/escritura de los archivos
JSON (proveedores.json y bloqueos.json), además de las funciones puras para
saber si un proveedor está afectado por un bloqueo. No contiene nada de
interfaz gráfica: solo datos y su persistencia.
"""
import os
import json
from dataclasses import dataclass, field, asdict
from datetime import date
from tkinter import messagebox

from modulos.estilos import ORDEN_VENTA

# Archivo donde se guardará la información de los proveedores
ARCHIVO_JSON = "proveedores.json"


@dataclass
class Proveedor:
    nombre: str
    tvi: str = ""
    tfi: str = ""
    
    # Flujo DDC
    ddc_activo: bool = False
    ddc_reporte_dias: set = field(default_factory=set)
    ddc_preparacion_dias: set = field(default_factory=set)
    ddc_despacho_dias: set = field(default_factory=set)
    ddc_plazos_adicionales: dict = field(default_factory=lambda: {d: 7 for d in ORDEN_VENTA})
    
    # Flujo DVR
    dvr_activo: bool = False
    dvr_reporte_dias: set = field(default_factory=set)
    dvr_preparacion_dias: set = field(default_factory=set)
    dvr_ingreso_dias: set = field(default_factory=set)
    dvr_despacho_dias: set = field(default_factory=set)
    dvr_plazos_adicionales: dict = field(default_factory=lambda: {d: 7 for d in ORDEN_VENTA})
    dvr_plazos_minimos: dict = field(default_factory=lambda: {d: 1 for d in ORDEN_VENTA})
    
    # Configuración de Desfase DVR
    dvr_usar_desface: bool = False
    dvr_desfaces: dict = field(default_factory=lambda: {d: 0 for d in ORDEN_VENTA})

    def to_dict(self):
        data = asdict(self)
        data['ddc_reporte_dias'] = list(self.ddc_reporte_dias)
        data['ddc_preparacion_dias'] = list(self.ddc_preparacion_dias)
        data['ddc_despacho_dias'] = list(self.ddc_despacho_dias)
        
        data['dvr_reporte_dias'] = list(self.dvr_reporte_dias)
        data['dvr_preparacion_dias'] = list(self.dvr_preparacion_dias)
        data['dvr_ingreso_dias'] = list(self.dvr_ingreso_dias)
        data['dvr_despacho_dias'] = list(self.dvr_despacho_dias)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data.get('nombre', ''),
            tvi=data.get('tvi', ''),
            tfi=data.get('tfi', ''),
            
            ddc_activo=data.get('ddc_activo', False),
            ddc_reporte_dias=set(data.get('ddc_reporte_dias', [])),
            ddc_preparacion_dias=set(data.get('ddc_preparacion_dias', [])),
            ddc_despacho_dias=set(data.get('ddc_despacho_dias', [])),
            ddc_plazos_adicionales=data.get('ddc_plazos_adicionales', {d: 7 for d in ORDEN_VENTA}),
            
            dvr_activo=data.get('dvr_activo', False),
            dvr_reporte_dias=set(data.get('dvr_reporte_dias', [])),
            dvr_preparacion_dias=set(data.get('dvr_preparacion_dias', [])),
            dvr_ingreso_dias=set(data.get('dvr_ingreso_dias', [])),
            dvr_despacho_dias=set(data.get('dvr_despacho_dias', [])),
            dvr_plazos_adicionales=data.get('dvr_plazos_adicionales', {d: 7 for d in ORDEN_VENTA}),
            dvr_plazos_minimos=data.get('dvr_plazos_minimos', {d: 1 for d in ORDEN_VENTA}),
            
            dvr_usar_desface=data.get('dvr_usar_desface', False),
            dvr_desfaces=data.get('dvr_desfaces', {d: 0 for d in ORDEN_VENTA})
        )


def cargar_proveedores_json():
    if not os.path.exists(ARCHIVO_JSON):
        pass

    try:
        with open(ARCHIVO_JSON, "r", encoding="utf-8") as f:
            datos_raw = json.load(f)
            return {nombre: Proveedor.from_dict(p_data) for nombre, p_data in datos_raw.items()}
    except Exception as e:
        messagebox.showerror("Error al Cargar", f"No se pudo leer '{ARCHIVO_JSON}': {e}")
        return {}


def guardar_proveedores_json(proveedores_dict):
    try:
        data_to_save = {nombre: prov.to_dict() for nombre, prov in proveedores_dict.items()}
        with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error al Guardar", f"No se pudo guardar la información: {e}")


ARCHIVO_BLOQUEOS = "bloqueos.json"
TODOS_LOS_PROVEEDORES = "TODOS"


def cargar_bloqueos_json():
    if not os.path.exists(ARCHIVO_BLOQUEOS):
        return {}
    try:
        with open(ARCHIVO_BLOQUEOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error al Cargar Bloqueos", f"No se pudo leer '{ARCHIVO_BLOQUEOS}': {e}")
        return {}


def guardar_bloqueos_json(bloqueos_dict):
    try:
        with open(ARCHIVO_BLOQUEOS, "w", encoding="utf-8") as f:
            json.dump(bloqueos_dict, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error al Guardar Bloqueos", f"No se pudo guardar la configuración de días inoperativos: {e}")


def proveedor_afectado_por_bloqueo(nombre_proveedor, info_bloqueo):
    provs = info_bloqueo.get("proveedores", [])
    return TODOS_LOS_PROVEEDORES in provs or nombre_proveedor in provs


def fechas_bloqueadas_de_proveedor(bloqueos_dict, nombre_proveedor):
    """Devuelve el set de fechas (date) declaradas inoperativas que afectan a un proveedor específico."""
    fechas = set()
    for fecha_str, info in bloqueos_dict.items():
        if proveedor_afectado_por_bloqueo(nombre_proveedor, info):
            try:
                fechas.add(date.fromisoformat(fecha_str))
            except ValueError:
                pass
    return fechas


