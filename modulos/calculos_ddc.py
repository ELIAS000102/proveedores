"""
Cálculo del Flujo DDC (Despacho Directo del Proveedor al Cliente)
---------------------------------------------------------------------------
Toda la lógica de negocio para calcular el ciclo DDC (reporte, preparación
y despacho) a partir de una fecha de venta, incluyendo el recálculo cuando
algún día del ciclo cae sobre un día declarado inoperativo. No contiene
nada de interfaz gráfica.

IMPORTANTE: esta lógica de cálculo no debe modificarse al hacer cambios de
estilo/interfaz en otros módulos.
"""
from datetime import timedelta

def _calcular_ciclo_ddc_regular(venta_date, nombre_dia_venta, proveedor, limite_dias=35):
    """Cálculo original (sin considerar días inoperativos)."""
    plazo = proveedor.ddc_plazos_adicionales.get(nombre_dia_venta, 0)
    objetivo_despacho = venta_date + timedelta(days=plazo + 1)

    d = objetivo_despacho
    intentos = 0
    while d.weekday() not in proveedor.ddc_despacho_dias:
        d += timedelta(days=1)
        intentos += 1
        if intentos > limite_dias:
            return None
    fecha_despacho = d

    fecha_reporte = None
    fechas_prep = []
    contador_prep = 1

    curr = venta_date + timedelta(days=1)
    while curr < fecha_despacho:
        wd = curr.weekday()

        if fecha_reporte is None:
            if wd in proveedor.ddc_reporte_dias:
                fecha_reporte = curr
            curr += timedelta(days=1)
            continue

        if curr > fecha_reporte:
            if wd in proveedor.ddc_preparacion_dias:
                fechas_prep.append((curr, contador_prep))
                contador_prep += 1

        curr += timedelta(days=1)

    return fecha_reporte, fechas_prep, fecha_despacho, plazo


def _recalcular_ddc_por_bloqueo(venta_date, proveedor, target_preps, fechas_bloqueadas, limite_dias):
    """
    Recorre día a día desde la venta (sin poder usar ningún día bloqueado para
    reportar, preparar o despachar), manteniendo la MISMA cantidad de días de
    reporte/preparación que el ciclo regular (no se agregan días de más).
    El despacho se busca recién después de completar reporte + preparaciones,
    de modo que si dos pasos "chocan" en la misma fecha por el corrimiento,
    el siguiente paso se recalcula en cascada.
    """
    fecha_reporte = None
    fechas_prep = []
    contador_prep = 1
    requiere_reporte = bool(proveedor.ddc_reporte_dias)

    curr = venta_date + timedelta(days=1)
    intentos = 0
    while intentos < limite_dias:
        intentos += 1
        if curr in fechas_bloqueadas:
            curr += timedelta(days=1)
            continue

        wd = curr.weekday()

        if requiere_reporte and fecha_reporte is None:
            if wd in proveedor.ddc_reporte_dias:
                fecha_reporte = curr
            curr += timedelta(days=1)
            continue

        if len(fechas_prep) < target_preps:
            if wd in proveedor.ddc_preparacion_dias:
                fechas_prep.append((curr, contador_prep))
                contador_prep += 1
            curr += timedelta(days=1)
            continue

        if wd in proveedor.ddc_despacho_dias:
            return fecha_reporte, fechas_prep, curr
        curr += timedelta(days=1)

    return None


def calcular_ciclo_ddc_plazo(venta_date, nombre_dia_venta, proveedor, limite_dias=35, fechas_bloqueadas=None):
    """
    Devuelve (fecha_reporte, fechas_prep, fecha_despacho, plazo_adicional_efectivo, afectado_por_bloqueo).
    `plazo_adicional_efectivo` es igual al configurado salvo que el ciclo haya
    tenido que correrse por un día inoperativo, en cuyo caso es un valor
    TEMPORAL calculado solo para esa fecha de venta (no modifica la
    configuración del proveedor).
    """
    if not proveedor.ddc_despacho_dias:
        return None

    bloqueadas = fechas_bloqueadas or set()

    regular = _calcular_ciclo_ddc_regular(venta_date, nombre_dia_venta, proveedor, limite_dias)
    if regular is None:
        return None
    fecha_reporte, fechas_prep, fecha_despacho, plazo_cfg = regular

    fechas_del_ciclo = [fecha_despacho] + [f for f, _ in fechas_prep]
    if fecha_reporte:
        fechas_del_ciclo.append(fecha_reporte)

    if not bloqueadas or not any(f in bloqueadas for f in fechas_del_ciclo):
        return fecha_reporte, fechas_prep, fecha_despacho, plazo_cfg, False

    target_preps = len(fechas_prep)
    recalculo = _recalcular_ddc_por_bloqueo(venta_date, proveedor, target_preps, bloqueadas, max(limite_dias, 60))
    if recalculo is None:
        return None
    fecha_reporte_n, fechas_prep_n, fecha_despacho_n = recalculo
    plazo_efectivo = (fecha_despacho_n - venta_date).days - 1
    return fecha_reporte_n, fechas_prep_n, fecha_despacho_n, plazo_efectivo, True


def resolver_marcadores_ddc(venta_date, fecha_reporte, fechas_prep, fecha_despacho, fechas_bloqueadas=None):
    """
    Devuelve un dict {fecha: texto} con la posición de cada marcador a dibujar
    (F. VENTA, 0-Reporte, N-Prep, DESPACHO). La fecha de venta NUNCA se mueve
    ni cambia de color, así caiga sobre un día inoperativo: siempre se dibuja
    en su propia columna. Los demás pasos (reporte/preparación/despacho) ya
    vienen calculados evitando los días bloqueados, por lo que no requieren
    ningún corrimiento adicional para dibujarse.
    """
    resultado = {}
    if fecha_reporte:
        resultado[fecha_reporte] = "0-Reporte"
    for f_prep, n in fechas_prep:
        resultado[f_prep] = f"{n}-Prep"
    if fecha_despacho:
        resultado[fecha_despacho] = "DESPACHO"
    resultado[venta_date] = "F. VENTA"
    return resultado


