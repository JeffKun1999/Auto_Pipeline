@echo off
set PROD_DIR="production_build"
echo "--- Iniciando el despliegue ---"

if exist %PROD_DIR% (
    echo "--- Limpiando despliegue anterior ---"
    rmdir /s /q %PROD_DIR%
)

echo "--- Creando directorio y copiando archivos ---"
mkdir %PROD_DIR%
copy compare_pdfs.py %PROD_DIR% > nul
copy requirements.txt %PROD_DIR% > nul

echo "--- Verificacion de archivos en produccion: ---"
dir %PROD_DIR%

echo "--- Despliegue completado ---"
exit /b 0