::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFC5naTa+GG6pDaET+NTf7vmPgEIcRuYDfobV27qNKeEfp0znephgxnRd1Z5bWUIVSRulagAjuiBLtWvl
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSTk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFC5naTa+GG6pDaET+NTf7vmPgEIcRuYDUYHN36eaLeUd/mT0Zdgozn86
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if not errorlevel 1 set "PYTHON=py"
if not defined PYTHON (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON=python"
)
if not defined PYTHON (
  echo Python no esta instalado o no esta disponible en PATH.
  echo Instala Python desde https://www.python.org/downloads/windows/
  echo y marca "Add python.exe to PATH" durante la instalacion.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual...
  %PYTHON% -m venv .venv
  if errorlevel 1 goto :error
)

echo Comprobando dependencias...
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo La instalacion de dependencias fallo. El mensaje anterior indica el motivo.
  pause
  exit /b 1
)

echo Iniciando Dashboard de Inversiones...
call ".venv\Scripts\python.exe" -m streamlit run streamlit_app.py
if errorlevel 1 goto :error
goto :end

:error
echo.
echo No se pudo preparar o iniciar el dashboard.
pause
exit /b 1

:end
endlocal