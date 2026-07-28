Supply Chain Flow Monitor - Dashboard Principal

Aplicación de escritorio para la gestión y visualización de flujos de proveedores (DDC/DVR), con exportación de reportes a Excel.

Requisitos previos
Sistema operativo: Windows 10 u 11
Python: versión 3.9 o superior
1. Instalar Python
Descarga el instalador desde: https://www.python.org/downloads/windows/
Ejecuta el instalador y marca la casilla "Add Python to PATH" antes de continuar.
Verifica que la opción "tcl/tk and IDLE" esté marcada (viene así por defecto). Esto es necesario para que funcione la interfaz gráfica del programa.
Finaliza la instalación.
Para confirmar que quedó instalado correctamente, abre la terminal (CMD o PowerShell) y ejecuta:
bash
python --version

Debe mostrarte la versión instalada (por ejemplo, Python 3.12.x).

2. Instalar las librerías necesarias

El programa usa únicamente librerías estándar de Python (ya incluidas) más una librería externa: openpyxl, necesaria para exportar los reportes a Excel.

Abre la terminal en la carpeta donde está el archivo VeV_prov.py y ejecuta:

bash
pip install openpyxl

Si tienes varias versiones de Python instaladas, usa:

bash
py -m pip install openpyxl
3. Ejecutar el programa

Desde la terminal, ubícate en la carpeta del proyecto y ejecuta:

bash
python VeV_prov.py

Esto abrirá la ventana principal "Supply Chain Flow Monitor - Dashboard Principal".

4. Archivos que genera el programa

Al ejecutarse por primera vez, el programa creará automáticamente en la misma carpeta:

proveedores.json — información de los proveedores configurados.
bloqueos_sistema.json — días declarados inoperativos (feriados o casos especiales).

No es necesario crear estos archivos manualmente; si no existen, el programa los genera con datos por defecto.

5. Exportar reportes a Excel

Desde el menú de exportación puedes generar un archivo .xlsx con formato y colores. Esta función requiere que openpyxl esté instalado (paso 2); si no lo está, el programa mostrará un mensaje indicándolo.

Notas
Todos los archivos (.json, .xlsx) se generan en la misma carpeta donde se ejecuta VeV_prov.py, a menos que se indique otra ruta al exportar.
Si aparece un error relacionado con tkinter, reinstala Python asegurándote de marcar la opción "tcl/tk and IDLE" mencionada en el paso 1.
