#!/bin/bash

# ======================================================
# SCRIPT DE DESPLIEGUE - COPIA ARTEFACTOS A "PRODUCCIÓN"
# ======================================================

set -e # Termina el script si algún comando falla

# 1. Definir el directorio de "producción"
# En un pipeline real, esto podría ser una ruta en un servidor remoto.
PROD_DIR="production_build"

echo "Iniciando el despliegue..."
echo "Directorio de producción simulado: ./${PROD_DIR}/"

# 2. Limpiar el directorio de producción anterior
if [ -d "$PROD_DIR" ]; then
    echo "Limpiando despliegue anterior..."
    rm -rf "$PROD_DIR"
fi

# 3. Crear el directorio de producción
mkdir -p "$PROD_DIR"

# 4. Copiar los artefactos necesarios al directorio de producción
echo "Copiando archivos de la aplicación..."
cp compare_pdfs.py "$PROD_DIR/"
cp requirements.txt "$PROD_DIR/"
# Añade aquí cualquier otro archivo que tu script necesite, como los PDFs si fueran fijos.

echo "Verificación de archivos en producción:"
ls -l "$PROD_DIR"

echo "Despliegue completado. El script está listo para ser ejecutado desde el directorio '${PROD_DIR}'."

exit 0