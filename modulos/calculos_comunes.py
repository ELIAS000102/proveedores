"""
Utilidades comunes a los flujos DDC y DVR
---------------------------------------------------------------------------
Funciones pequeñas que usan tanto el cálculo del ciclo DDC como el DVR (y
las vistas que dibujan sus matrices), para no duplicarlas en ambos módulos.
"""
from datetime import date, timedelta

from modulos.estilos import (
    COLOR_F_VENTA, COLOR_F_VENTA_TXT,
    COLOR_REPORTE, COLOR_REPORTE_TXT,
    COLOR_PREP, COLOR_PREP_TXT,
    COLOR_INGRESO_CD, COLOR_INGRESO_CD_TXT,
    COLOR_DESPACHO, COLOR_DESPACHO_TXT,
    COLOR_PANEL, COLOR_TEXT,
)


def fechas_semana_actual():
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    return [lunes + timedelta(days=i) for i in range(7)]


def _estilo_marcador_flujo(texto):
    """Devuelve (texto, bg, fg) según el tipo de marcador de la matriz DDC/DVR."""
    if texto == "F. VENTA":
        return texto, COLOR_F_VENTA, COLOR_F_VENTA_TXT
    if texto == "0-Reporte":
        return texto, COLOR_REPORTE, COLOR_REPORTE_TXT
    if texto.endswith("-Prep"):
        return texto, COLOR_PREP, COLOR_PREP_TXT
    if texto == "INGRESO CD":
        return texto, COLOR_INGRESO_CD, COLOR_INGRESO_CD_TXT
    if texto == "DESPACHO":
        return texto, COLOR_DESPACHO, COLOR_DESPACHO_TXT
    return texto, COLOR_PANEL, COLOR_TEXT
