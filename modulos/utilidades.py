"""
Utilidad de Geometría Adaptativa (ventanas ajustadas al tamaño de pantalla)
---------------------------------------------------------------------------
"""


def _geometria_adaptativa(ventana, ancho_ideal, alto_ideal, ancho_min, alto_min, margen=0.90):
    """
    Calcula un tamaño de ventana que nunca excede el espacio disponible en
    pantalla (dejando un margen), respetando un mínimo utilizable, y centra
    la ventana. Se usa tanto para la ventana principal como para los
    diálogos de configuración, para evitar que queden más grandes que la
    pantalla del usuario.
    """
    ventana.update_idletasks()
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    ancho = min(ancho_ideal, int(pantalla_ancho * margen))
    alto = min(alto_ideal, int(pantalla_alto * margen))
    ancho = max(ancho, min(ancho_min, pantalla_ancho - 40))
    alto = max(alto, min(alto_min, pantalla_alto - 40))

    x = max(0, (pantalla_ancho - ancho) // 2)
    y = max(0, (pantalla_alto - alto) // 2)

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    ventana.minsize(min(ancho_min, ancho), min(alto_min, alto))
