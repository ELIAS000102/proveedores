"""
Punto de entrada de la aplicación.
---------------------------------------------------------------------------
Ejecutar con:  python main.py

Toda la app está organizada en el paquete `modulos/`, separada por
responsabilidad, para que modificar una pantalla o un cálculo puntual no
requiera buscar en un único archivo de miles de líneas:

    modulos/estilos.py              -> colores, fuentes y constantes de días
    modulos/utilidades.py           -> utilidades genéricas de interfaz
    modulos/modelo_datos.py         -> entidad Proveedor y persistencia JSON
    modulos/calculos_comunes.py     -> helpers compartidos por DDC y DVR
    modulos/calculos_ddc.py         -> lógica de cálculo del flujo DDC
    modulos/calculos_dvr.py         -> lógica de cálculo del flujo DVR
    modulos/panel_configuracion.py  -> modal para crear/editar un proveedor
    modulos/vista_principal.py      -> pantalla de inicio (grilla de proveedores)
    modulos/vista_ajustes_sistema.py-> calendario de días inoperativos
    modulos/vista_detalle_proveedor.py -> pantalla de detalle (CRUD)
    modulos/tarjetas_flujo.py       -> matrices DDC/DVR y exportación a Excel
    modulos/app.py                  -> ventana raíz que combina todas las vistas
"""
from modulos.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
