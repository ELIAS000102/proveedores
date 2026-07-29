"""
Cálculo del Flujo DVR (Despacho Vía Ripley)
---------------------------------------------------------------------------
Toda la lógica de negocio para calcular el ciclo DVR (reporte, preparación,
ingreso a CD y despacho) a partir de una fecha de venta, incluyendo el
recálculo cuando algún día del ciclo cae sobre un día declarado inoperativo
y el manejo del desfase configurado por proveedor. No contiene nada de
interfaz gráfica.

IMPORTANTE: esta lógica de cálculo no debe modificarse al hacer cambios de
estilo/interfaz en otros módulos.
"""
from datetime import timedelta

def _calcular_ciclo_dvr_regular(venta_date, nombre_dia_venta, proveedor, limite_dias=35):
    """Cálculo original (sin considerar días inoperativos)."""
    plazo_adic = proveedor.dvr_plazos_adicionales.get(nombre_dia_venta, 0)
    objetivo_ingreso = venta_date + timedelta(days=plazo_adic + 1)

    d_ing = objetivo_ingreso
    intentos = 0
    while d_ing.weekday() not in proveedor.dvr_ingreso_dias:
        d_ing += timedelta(days=1)
        intentos += 1
        if intentos > limite_dias:
            return None
    fecha_ingreso_base = d_ing

    plazo_min_config = proveedor.dvr_plazos_minimos.get(nombre_dia_venta, 1)
    desfase_val = proveedor.dvr_desfaces.get(nombre_dia_venta, 0) if proveedor.dvr_usar_desface else 0
    plazo_min_efectivo_base = plazo_min_config + desfase_val

    objetivo_despacho = fecha_ingreso_base + timedelta(days=plazo_min_efectivo_base)

    d_desp = objetivo_despacho
    intentos = 0
    while d_desp.weekday() not in proveedor.dvr_despacho_dias:
        d_desp += timedelta(days=1)
        intentos += 1
        if intentos > limite_dias:
            return None
    fecha_despacho = d_desp

    plazo_minimo_dinamico = (fecha_despacho - fecha_ingreso_base).days

    fecha_ingreso_visual = fecha_ingreso_base
    cursor = fecha_despacho - timedelta(days=1)
    while cursor >= fecha_ingreso_base:
        if cursor.weekday() in proveedor.dvr_ingreso_dias:
            fecha_ingreso_visual = cursor
            break
        cursor -= timedelta(days=1)

    fecha_reporte = None
    fechas_prep_proveedor = []
    fechas_transito_cd = set()
    contador_prep = 1

    curr = venta_date + timedelta(days=1)
    while curr < fecha_despacho:
        if curr < fecha_ingreso_visual:
            wd = curr.weekday()
            if fecha_reporte is None:
                if wd in proveedor.dvr_reporte_dias:
                    fecha_reporte = curr
            elif curr > fecha_reporte:
                if wd in proveedor.dvr_preparacion_dias:
                    fechas_prep_proveedor.append((curr, contador_prep))
                    contador_prep += 1
        elif curr > fecha_ingreso_visual:
            fechas_transito_cd.add(curr)

        curr += timedelta(days=1)

    return (fecha_reporte, fechas_prep_proveedor, fecha_ingreso_base, fecha_ingreso_visual,
            fecha_despacho, plazo_minimo_dinamico, fechas_transito_cd, plazo_adic)


def _recalcular_dvr_por_bloqueo(venta_date, proveedor, target_preps, fechas_bloqueadas,
                                 plazo_min_config, desfase_val, limite_dias):
    """
    Análogo a `_recalcular_ddc_por_bloqueo` pero con un paso adicional: se
    corren reporte -> preparaciones -> ingreso al CD (equivalente al
    "despacho" del DDC para efectos del corrimiento), y luego el despacho
    final se ubica en el día hábil de despacho MÁS CERCANO al ingreso al CD
    (sin forzar el plazo mínimo configurado como distancia mínima), evitando
    siempre los días bloqueados.
    """
    fecha_reporte = None
    fechas_prep = []
    contador_prep = 1
    requiere_reporte = bool(proveedor.dvr_reporte_dias)

    curr = venta_date + timedelta(days=1)
    intentos = 0
    fecha_ingreso_base = None
    while intentos < limite_dias:
        intentos += 1
        if curr in fechas_bloqueadas:
            curr += timedelta(days=1)
            continue
        wd = curr.weekday()
        if requiere_reporte and fecha_reporte is None:
            if wd in proveedor.dvr_reporte_dias:
                fecha_reporte = curr
            curr += timedelta(days=1)
            continue
        if len(fechas_prep) < target_preps:
            if wd in proveedor.dvr_preparacion_dias:
                fechas_prep.append((curr, contador_prep))
                contador_prep += 1
            curr += timedelta(days=1)
            continue
        if wd in proveedor.dvr_ingreso_dias:
            fecha_ingreso_base = curr
            break
        curr += timedelta(days=1)

    if fecha_ingreso_base is None:
        return None

    # A diferencia del ciclo regular (donde plazo_min_config+desfase_val es un
    # mínimo de días que SÍ se exige entre ingreso y despacho), en el
    # recálculo por bloqueo ese valor deja de usarse como distancia forzada:
    # el despacho se ubica en el día hábil (no bloqueado) más cercano posible
    # al ingreso al CD, tal como ya hace `_recalcular_ddc_por_bloqueo`. El
    # plazo mínimo "efectivo" resultante se deriva después, en
    # `calcular_ciclo_dvr_plazo`, a partir de dónde quedó el despacho.
    d = fecha_ingreso_base + timedelta(days=1)
    intentos2 = 0
    while d.weekday() not in proveedor.dvr_despacho_dias or d in fechas_bloqueadas:
        d += timedelta(days=1)
        intentos2 += 1
        if intentos2 > limite_dias:
            return None
    fecha_despacho = d

    # A diferencia del cálculo regular (que "acerca" visualmente el Ingreso CD
    # al despacho para mostrar más días como preparación), en el recálculo por
    # bloqueo el Ingreso CD SIEMPRE se ubica en el día habilitado más cercano
    # posible (fecha_ingreso_base): no tiene sentido correrlo más de lo
    # necesario solo por estética, así que el tiempo sobrante hasta el
    # despacho se muestra como Tránsito CD.
    fecha_ingreso_visual = fecha_ingreso_base

    # Se vuelve a rellenar reporte/preparaciones/tránsito con las fechas ya
    # definitivas, tal como hace el cálculo regular, PERO sin superar nunca la
    # misma cantidad de N-Prep que tendría el ciclo regular (target_preps):
    # el hueco extra que deja el desfase/plazo mínimo hacia el despacho no
    # debe convertirse en más días de preparación de los ya configurados.
    fechas_prep_final = []
    fechas_transito_final = set()
    contador_prep2 = 1
    curr2 = venta_date + timedelta(days=1)
    while curr2 < fecha_despacho:
        if curr2 in fechas_bloqueadas:
            curr2 += timedelta(days=1)
            continue
        if curr2 < fecha_ingreso_visual:
            wd2 = curr2.weekday()
            if (fecha_reporte is None or curr2 > fecha_reporte) and len(fechas_prep_final) < target_preps:
                if wd2 in proveedor.dvr_preparacion_dias:
                    fechas_prep_final.append((curr2, contador_prep2))
                    contador_prep2 += 1
        elif curr2 > fecha_ingreso_visual:
            fechas_transito_final.add(curr2)
        curr2 += timedelta(days=1)

    return fecha_reporte, fechas_prep_final, fecha_ingreso_base, fecha_ingreso_visual, fecha_despacho, fechas_transito_final


def calcular_ciclo_dvr_plazo(venta_date, nombre_dia_venta, proveedor, limite_dias=35,
                              fechas_bloqueadas=None, plazo_adicional_ddc=None):
    """
    Devuelve (fecha_reporte, fechas_prep, fecha_ingreso_visual, fecha_despacho,
    plazo_minimo_efectivo, fechas_transito_cd, plazo_adicional_efectivo,
    afectado_por_bloqueo).

    Si el ciclo se ve afectado por un día inoperativo, `plazo_adicional_efectivo`
    se muestra igual al del DDC del mismo día de venta (obligatorio: pasar
    `plazo_adicional_ddc` con ese valor cuando el proveedor tenga DDC activo),
    y `plazo_minimo_efectivo` es el nuevo plazo mínimo temporal calculado a
    partir del corrimiento. Ninguno de los dos modifica la configuración
    guardada del proveedor.
    """
    if not proveedor.dvr_ingreso_dias or not proveedor.dvr_despacho_dias:
        return None

    bloqueadas = fechas_bloqueadas or set()

    regular = _calcular_ciclo_dvr_regular(venta_date, nombre_dia_venta, proveedor, limite_dias)
    if regular is None:
        return None
    (fecha_reporte, fechas_prep, fecha_ingreso_base, fecha_ingreso_visual,
     fecha_despacho, plazo_minimo_dinamico, fechas_transito_cd, plazo_adic_cfg) = regular

    fechas_del_ciclo = [fecha_ingreso_visual, fecha_despacho] + [f for f, _ in fechas_prep]
    if fecha_reporte:
        fechas_del_ciclo.append(fecha_reporte)

    if not bloqueadas or not any(f in bloqueadas for f in fechas_del_ciclo):
        return (fecha_reporte, fechas_prep, fecha_ingreso_visual, fecha_despacho,
                plazo_minimo_dinamico, fechas_transito_cd, plazo_adic_cfg, False)

    target_preps = len(fechas_prep)
    plazo_min_config = proveedor.dvr_plazos_minimos.get(nombre_dia_venta, 1)
    desfase_val = proveedor.dvr_desfaces.get(nombre_dia_venta, 0) if proveedor.dvr_usar_desface else 0

    recalculo = _recalcular_dvr_por_bloqueo(
        venta_date, proveedor, target_preps, bloqueadas,
        plazo_min_config, desfase_val, max(limite_dias, 60)
    )
    if recalculo is None:
        return None
    (fecha_reporte_n, fechas_prep_n, fecha_ingreso_base_n, fecha_ingreso_visual_n,
     fecha_despacho_n, fechas_transito_n) = recalculo

    # Obligatorio: el plazo adicional del DVR se muestra igual al del DDC del
    # mismo día de venta cuando el ciclo está afectado por un bloqueo.
    if plazo_adicional_ddc is not None:
        plazo_adic_efectivo = plazo_adicional_ddc
    else:
        plazo_adic_efectivo = (fecha_ingreso_base_n - venta_date).days - 1

    # Cuadros entre la fecha de venta (sin contarla) y el despacho (sin
    # contarlo), menos el plazo adicional del DDC de ese mismo día de venta.
    cuadros_venta_a_despacho = (fecha_despacho_n - venta_date).days - 1
    plazo_minimo_efectivo = cuadros_venta_a_despacho - plazo_adic_efectivo

    return (fecha_reporte_n, fechas_prep_n, fecha_ingreso_visual_n, fecha_despacho_n,
            plazo_minimo_efectivo, fechas_transito_n, plazo_adic_efectivo, True)


def resolver_marcadores_dvr(venta_date, fecha_reporte, fechas_prep, fecha_ingreso_visual,
                             fecha_despacho, fechas_bloqueadas=None):
    """
    Análogo a `resolver_marcadores_ddc` pero incluyendo el marcador INGRESO CD.
    La fecha de venta NUNCA se mueve ni cambia de color.
    """
    resultado = {}
    if fecha_reporte:
        resultado[fecha_reporte] = "0-Reporte"
    for f_prep, n in fechas_prep:
        resultado[f_prep] = f"{n}-Prep"
    if fecha_ingreso_visual:
        resultado[fecha_ingreso_visual] = "INGRESO CD"
    if fecha_despacho:
        resultado[fecha_despacho] = "DESPACHO"
    resultado[venta_date] = "F. VENTA"
    return resultado


