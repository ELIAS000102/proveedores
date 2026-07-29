"""
Estilo Global & Paleta de Colores
---------------------------------------------------------------------------
Todas las constantes visuales (colores, fuentes) y de dominio relacionadas
con los días de la semana. Cualquier ajuste de "look & feel" de la app se
hace aquí, en un solo lugar, sin tocar la lógica de negocio.
"""

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
ORDEN_VENTA = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]

COLOR_BG = "#f1f5f9"
COLOR_SIDEBAR_BG = "#0f172a"
COLOR_SIDEBAR_HOVER = "#1e293b"
COLOR_SIDEBAR_ACTIVE = "#2563eb"

COLOR_PANEL = "#ffffff"
COLOR_PRIMARY = "#0f172a"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_HOVER = "#1d4ed8"
COLOR_ACCENT_SOFT = "#eff6ff"

COLOR_HOY_ROW_BG = "#eff6ff"
COLOR_HOY_BORDER = "#2563eb"

COLOR_HEADER_BG = "#1e293b"
COLOR_HEADER_TXT = "#ffffff"
COLOR_BORDER = "#cbd5e1"
COLOR_CARD_BORDER = "#e2e8f0"
COLOR_TEXT = "#0f172a"
COLOR_MUTED = "#64748b"

COLOR_F_VENTA = "#fef08a"
COLOR_F_VENTA_TXT = "#713f12"

COLOR_REPORTE = "#fbcfe8"
COLOR_REPORTE_TXT = "#831843"

COLOR_PREP = "#bae6fd"
COLOR_PREP_TXT = "#0369a1"

COLOR_TRANSITO_CD = "#e9d5ff"
COLOR_TRANSITO_CD_TXT = "#6b21a8"

COLOR_INGRESO_CD = "#f97316"
COLOR_INGRESO_CD_TXT = "#ffffff"

COLOR_DESPACHO = "#bbf7d0"
COLOR_DESPACHO_TXT = "#14532d"

COLOR_BLOQUEADO = "#0f172a"

# Color para días declarados INOPERATIVOS (feriados / casos únicos) vía "Ajustes Sistema".
# Es distinto del "bloqueado" gris oscuro de arriba (que solo indica "sin actividad
# configurada" ese día de la semana); este rojo marca un día puntual del calendario
# que fue deshabilitado manualmente para uno o varios proveedores.
COLOR_DIA_INOPERATIVO = "#ef4444"
COLOR_DIA_INOPERATIVO_TXT = "#ffffff"

FONT_BASE = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI", 9, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SUBTITLE = ("Segoe UI", 10, "bold")
FONT_HEADER = ("Segoe UI", 8, "bold")
FONT_SMALL = ("Segoe UI", 8)
FONT_BRAND = ("Segoe UI", 12, "bold")
FONT_CAPTION = ("Segoe UI", 8)
