#!/bin/bash
# Este es el equivalente de '@echo off' y 'echo --- Iniciando...'
set -e
echo "--- Iniciando el despliegue (script de Linux) ---"

# Define el directorio de "producción" (en Linux)
# Usamos una carpeta local llamada 'produccion'
PROD_DIR="./produccion"

# Equivalente de 'if exist %PROD_DIR% ('
if [ -d "$PROD_DIR" ]; then
    echo "El directorio de produccion existe. Limpiando..."
    # Equivalente de 'rmdir /s /q %PROD_DIR%'
    rm -rf "$PROD_DIR"
fi

echo "Creando directorio de produccion..."
# Equivalente de 'mkdir %PROD_DIR%'
mkdir -p "$PROD_DIR"

echo "Copiando archivos..."
# Equivalente de 'copy *.pdf %PROD_DIR%'
cp *.pdf "$PROD_DIR"
cp *.py "$PROD_DIR"

echo "Despliegue completado."