# Pipeline DevSecOps Automatizado

Pipeline CI/CD con integración de herramientas de seguridad (DevSecOps) usando CircleCI.

## Inicio Rápido

**⚠️ IMPORTANTE:** Antes de ejecutar el pipeline, debes configurar las variables de entorno en CircleCI.

👉 **[Ver guía completa de configuración en SETUP.md](SETUP.md)**

## Descripción

Este proyecto implementa un pipeline completo DevSecOps que integra:
- **Dev:** Python, Flask, Pytest
- **Ops:** CircleCI, Docker, Notificaciones por email
- **Sec:** Safety (SAST), Wapiti (DAST)

## Flujo del Pipeline

```
1. Checkout                    # Obtener código del repositorio
2. Build Environment           # Crear entorno virtual e instalar dependencias
3. SAST (Safety)              # Análisis estático de seguridad
4. Code Quality (Flake8)      # Análisis de calidad de código
5. Unit Tests (Pytest)        # Pruebas unitarias
6. Deploy & Execute           # Despliegue de la aplicación
7. DAST (Wapiti)              # Análisis dinámico de seguridad
8. Store Artifacts            # Guardar reportes
9. Notifications              # Enviar notificaciones por email
```

## Aplicación Vulnerable de Prueba

**ADVERTENCIA:** El archivo `app.py` contiene una aplicación Flask INTENCIONALMENTE VULNERABLE para demostrar las capacidades de las herramientas de seguridad.

### Vulnerabilidades Incluidas:

1. **SQL Injection** (`/login`) - Consultas SQL sin sanitización
2. **XSS** (`/search`) - Cross-Site Scripting sin escape
3. **XSS Reflejado** (`/profile`) - Parámetros reflejados sin validación
4. **Path Traversal** (`/file`) - Acceso a archivos sin validación de path
5. **Debug Mode** - Modo debug habilitado en producción
6. **Hardcoded Secrets** - Claves secretas en el código
7. **CORS Permisivo** - Headers CORS mal configurados

### Dependencias Vulnerables:

El archivo `requirements-vulnerable.txt` incluye versiones antiguas con CVEs conocidos:
- `urllib3==1.24.1` (CVE-2019-11324)
- `requests==2.20.0` (CVE-2018-18074)
- `cryptography==2.3` (Múltiples CVEs)
- `Jinja2==2.10.1` (CVE-2019-8341)
- `PyYAML==3.13` (CVE-2017-18342)
- `Django==2.0.0` (Múltiples CVEs)
- `Flask==2.0.0` (Vulnerabilidades conocidas)

**Nota:** El pipeline instala `requirements.txt` (versiones seguras) para funcionar correctamente, pero Safety analiza `requirements-vulnerable.txt` para detectar las vulnerabilidades.

## Herramientas de Seguridad

### Safety (SAST)
Escanea las dependencias en `requirements.txt` y detecta vulnerabilidades conocidas (CVEs).

**Resultado esperado:** Múltiples vulnerabilidades detectadas en las versiones antiguas.

### Wapiti (DAST)
Escanea la aplicación web en ejecución buscando vulnerabilidades como:
- SQL Injection
- XSS (Cross-Site Scripting)
- Path Traversal
- CSRF
- Y más...

**Resultado esperado:** Detectará las 7 vulnerabilidades implementadas en `app.py`.

## Visualizar Resultados

### En CircleCI:
1. Ve a: https://app.circleci.com/pipelines/github/JeffKun1999/Auto_Pipeline
2. Haz clic en el último workflow
3. Ve a "ARTIFACTS" para descargar:
   - `flake8-report.txt` - Reporte de calidad
   - `reporte_seguridad/wapiti_report.html` - Reporte DAST completo

### Localmente:
```bash
# Ver reportes de seguridad locales
ls reporte_seguridad/
```

## Ejecutar Localmente

### Ejecutar la aplicación vulnerable:
```bash
python app.py
# Accede a http://localhost:5000
```

### Probar vulnerabilidades:
```bash
# SQL Injection
curl -X POST http://localhost:5000/login -d "username=admin' OR '1'='1&password=cualquiera"

# XSS
curl "http://localhost:5000/search?q=<script>alert('XSS')</script>"

# Path Traversal
curl "http://localhost:5000/file?name=../../etc/passwd"
```

## Trigger del Pipeline

Cualquier push a la rama `ArgoCD` ejecuta automáticamente el pipeline:

```bash
git add .
git commit -m "Test pipeline DevSecOps"
git push origin ArgoCD
```

## Arquitectura

```
Pipeline_Auto/
├── .circleci/
│   └── config.yml          # Configuración del pipeline CircleCI
├── app.py                  # Aplicación Flask vulnerable (demo)
├── compare_pdfs.py         # Script de comparación de PDFs
├── requirements.txt        # Dependencias (incluye vulnerables)
├── test_compare.py         # Pruebas unitarias
├── deploy.sh              # Script de despliegue
└── reporte_seguridad/     # Reportes de Wapiti
```

## Estado del Pipeline

[![CircleCI](https://circleci.com/gh/JeffKun1999/Auto_Pipeline/tree/ArgoCD.svg?style=shield)](https://circleci.com/gh/JeffKun1999/Auto_Pipeline/tree/ArgoCD)

### Última Actualización

**Fecha:** 2026-01-11

**Cambios recientes:**
- ✅ Resuelto conflicto de dependencias (yagmail error)
- ✅ Separación de requirements.txt y requirements-vulnerable.txt
- ✅ Actualización de documentación (SETUP.md)
- ✅ Configuración de LaunchDarkly como opcional
- ✅ Pipeline completamente funcional

**Estado actual:**
- 🟢 Build Environment: Funcionando
- 🟢 SAST (Safety): Detectando vulnerabilidades
- 🟢 Code Quality (Flake8): Funcionando
- 🟢 Unit Tests (Pytest): Funcionando
- 🟢 Deploy & Execute: Funcionando
- 🟢 DAST (Wapiti): Escaneando vulnerabilidades
- 🟡 Notifications: Requiere configuración de email en CircleCI

## Notas Importantes

- **NO usar en producción:** Este código contiene vulnerabilidades intencionales
- **Solo para aprendizaje:** Propósito educativo de DevSecOps
- **Actualizar dependencias:** En producción usar versiones seguras

## Autor

Proyecto educativo para demostración de pipeline DevSecOps automatizado.