Crear entorno virtual

Desde la raíz del proyecto:

python -m venv env

Esto crea la carpeta env/.

Activar entorno virtual

En PowerShell (Windows):

.\env\Scripts\Activate.ps1

Si usas CMD:

env\Scripts\activate.bat

Si te bloquea PowerShell por permisos:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\env\Scripts\Activate.ps1

Instalar Django

Con el entorno activo:

pip install django
