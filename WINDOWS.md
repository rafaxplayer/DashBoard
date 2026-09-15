# Ejecutar en Windows

## Opcion sencilla

1. Instala Python 3.10 o posterior desde [python.org](https://www.python.org/downloads/windows/).
2. Durante la instalacion activa **Add python.exe to PATH**.
3. Haz doble clic en `run_dashboard.bat`.

La primera ejecucion crea un entorno virtual e instala las dependencias. Despues abre Streamlit en el navegador. Para cerrar la app, cierra la ventana negra de la terminal.

## Ejecucion manual

En PowerShell, desde la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

La direccion habitual es `http://localhost:8501`. Aunque utiliza una direccion local, no necesitas instalar ni configurar un servidor: Streamlit se inicia y se detiene junto con la aplicacion.
