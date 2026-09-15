# Versión Streamlit — Ejecutar localmente

Pasos rápidos:

1. Crear un entorno virtual (recomendado) e instalar dependencias:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Ejecutar la app:

```bash
streamlit run streamlit_app.py
```

3. La app se abrirá en tu navegador (http://localhost:8501). Los importes se gestionan en euros y los datos se guardan en `investments_streamlit.json` en la carpeta del proyecto.

Empaquetar a EXE (opcional)
- Instala PyInstaller:

```bash
pip install pyinstaller
```

- Genera un ejecutable (modo simple):

```bash
pyinstaller --onefile --add-data "investments_streamlit.json;." streamlit_app.py
```

Nota: PyInstaller genera un único ejecutable, pero Streamlit abre el navegador por defecto; para una app de escritorio más pulida se recomienda usar `streamlit` + herramienta como `nativefier` o empaquetar con Electron (usando un wrapper). Puedo preparar un `spec` de PyInstaller o un script de empaquetado si lo deseas.
