#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Este script compara dos archivos PDF para determinar si son idénticos
y envía una notificación por correo electrónico con el resultado.
"""

import os
import sys
import hashlib
import argparse
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv


# --- NUEVO: Importaciones de LaunchDarkly ---
import ldclient
from ldclient.config import Config
from ldclient import Context

def calculate_hash(file_path):
    """Calcula el hash MD5 de un archivo para una comparación rápida y fiable."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # Lee el archivo en trozos para no consumir demasiada memoria
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta: {file_path}")
        return None
    except IOError as e:
        print(f"Error al leer el archivo {file_path}: {e}")
        return None

def send_email_notification(subject, message_body):
    """Envía una notificación por correo usando credenciales de variables de entorno."""
    # --- Lee las credenciales de forma segura desde las variables de entorno ---
    host = os.getenv('EMAIL_HOST')
    port = os.getenv('EMAIL_PORT')
    user = os.getenv('EMAIL_HOST_USER')
    password = os.getenv('EMAIL_HOST_PASSWORD')
    recipient = os.getenv('RECIPIENT_EMAIL')

    # --- Valida que todas las variables necesarias estén configuradas ---
    if not all([host, port, user, password, recipient]):
        print("Error: Faltan variables de entorno para el envío de correo.")
        print("Asegúrate de configurar: EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, RECIPIENT_EMAIL")
        return

    # --- Construye el correo ---
    msg = MIMEText(message_body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient

    # --- Envía el correo ---
    try:
        with smtplib.SMTP(host, int(port)) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, recipient, msg.as_string())
        print("Notificación por correo enviada correctamente.")
    except smtplib.SMTPException as e:
        print(f"Error al enviar el correo: {e}")

#
def main():
    """Función principal orquestada con Feature Flag."""
    load_dotenv()
    
    # --- NUEVO: Inicialización de LaunchDarkly ---
    ld_sdk_key = os.getenv('LD_SDK_KEY')
    if not ld_sdk_key:
        print("Advertencia: LD_SDK_KEY no configurada. Ejecutando sin Feature Flags.")
        # Aquí decides si fallar o continuar por defecto.
        # Por seguridad, asumiremos ejecución normal si no hay key, o return.
    else:
        ldclient.set_config(Config(ld_sdk_key))

    # Definir el contexto (quién está ejecutando esto, puede ser el nombre del servicio)
    context = Context.builder('jenkins-pipeline-bot').name('Jenkins CI').build()

    # Verificar la Feature Flag
    # Si la bandera 'enable-pdf-comparison' es False, no hacemos nada.
    # El tercer parámetro (False) es el valor por defecto si falla la conexión.
    feature_enabled = ldclient.get().variation("enable-pdf-comparison", context, False)

    if not feature_enabled:
        print("--- FEATURE FLAG: La comparación de PDFs está DESACTIVADA en LaunchDarkly ---")
        print("Saltando ejecución de lógica principal.")
        ldclient.get().close()
        return  # Salimos exitosamente pero sin hacer el trabajo
    
    print("--- FEATURE FLAG: Funcionalidad ACTIVA. Procediendo... ---")
        
    """Función principal que orquesta la comparación y la notificación."""
    load_dotenv()  # Carga las variables de entorno desde el archivo .env
    parser = argparse.ArgumentParser(description="Compara dos archivos PDF y notifica el resultado.")
    parser.add_argument("file1", help="Ruta al primer archivo PDF.")
    parser.add_argument("file2", help="Ruta al segundo archivo PDF.")
    args = parser.parse_args()

    # --- Etapa de 'Build/Preparación': Verificar que los archivos existen ---
    if not os.path.exists(args.file1) or not os.path.exists(args.file2):
        print("Error: Uno o ambos archivos PDF no existen. Por favor, verifica las rutas.")
        sys.exit(1) # Termina el script con un código de error

    # --- Etapa de 'Test/Ejecución': Comparar los archivos ---
    print(f"Comparando '{os.path.basename(args.file1)}' y '{os.path.basename(args.file2)}'...")
    hash1 = calculate_hash(args.file1)
    hash2 = calculate_hash(args.file2)

    if hash1 and hash2:
        if hash1 == hash2:
            resultado = "Los archivos son idénticos."
            print(f"Resultado: {resultado}")
        else:
            resultado = "Los archivos son diferentes."
            print(f"Resultado: {resultado}")
        
        # --- Etapa de 'Notificación' ---
        email_subject = "Resultado de Comparación de PDFs"
        email_body = (
            f"Se ha completado la comparación de los siguientes archivos:\n"
            f"- Archivo 1: {os.path.basename(args.file1)}\n"
            f"- Archivo 2: {os.path.basename(args.file2)}\n\n"
            f"Resultado: {resultado}"
        )
        send_email_notification(email_subject, email_body)
    else:
        print("No se pudo completar la comparación debido a un error al leer los archivos.")
        sys.exit(1)
 # Cerrar el cliente al finalizar correctamente
    if ld_sdk_key:
        ldclient.get().close() # <--- CORRECCIÓN AQUÍ

if __name__ == "__main__":
    main()