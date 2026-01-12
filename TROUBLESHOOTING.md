# Troubleshooting - Solución de Problemas del Pipeline

Esta guía documenta problemas comunes y sus soluciones.

---

## Problema: Wapiti - "Invalid base URL was specified"

### Error Completo
```
Invalid base URL was specified, please give a complete URL with protocol scheme and slash after the domain name.
```

### Causa
Wapiti 3.x es muy estricto con la sintaxis de la URL:
- ❌ `http://localhost:5000` (sin barra final)
- ✅ `http://localhost:5000/` (con barra final)

Además, algunas opciones de Wapiti pueden causar conflictos.

### Solución
```bash
# Sintaxis correcta para Wapiti 3.x
wapiti -u "http://localhost:5000/" -f html -o "reporte_seguridad/wapiti_report.html"
```

**Opciones que funcionan:**
- `-u URL` - URL objetivo (CON barra final)
- `-f FORMAT` - Formato de salida: html, json, txt, xml
- `-o FILE` - Archivo de salida

**Opciones que pueden causar problemas:**
- `--flush-session` - Innecesario en Wapiti 3.x
- `--scope url` - Puede causar errores de parsing
- `-v LEVEL` - Puede interferir con el output

### Verificación
1. Flask debe estar corriendo y respondiendo HTTP 200
2. La URL debe terminar en `/`
3. El directorio de salida debe existir (`mkdir -p reporte_seguridad`)

---

## Problema: Safety - Error de Encoding

### Error Completo
```
'charmap' codec can't decode byte 0x8d in position 912: character maps to <undefined>
```

### Causa
- El archivo `requirements-vulnerable.txt` tenía line endings de Windows (CRLF)
- Safety no puede procesar archivos con CRLF en algunos sistemas

### Solución
1. **Convertir a Unix line endings:**
   ```bash
   dos2unix requirements-vulnerable.txt
   # O con sed:
   sed -i 's/\r$//' requirements-vulnerable.txt
   ```

2. **Usar .gitattributes:**
   ```gitattributes
   requirements.txt text eol=lf
   requirements-vulnerable.txt text eol=lf
   ```

3. **Actualizar Safety:**
   ```bash
   # Comando viejo (deprecated)
   safety check -r requirements.txt

   # Comando nuevo
   safety scan --file requirements.txt
   ```

---

## Problema: Artifact de Wapiti No Aparece

### Síntomas
- El pipeline pasa exitosamente
- Solo aparece artifact de Flake8
- No hay `wapiti_report.html` en ARTIFACTS

### Diagnóstico
Verificar en los logs del step "Web Vulnerability Scan - DAST":

1. **Flask se levantó correctamente?**
   ```
   ✓ Flask respondió exitosamente después de X segundos
   ```

2. **Wapiti se ejecutó?**
   ```
   Ejecutando Wapiti...
   Wapiti-3.0.3 (wapiti.sourceforge.io)
   ```

3. **Se generó el reporte?**
   ```
   ✓✓✓ ÉXITO: Reporte generado ✓✓✓
   Tamaño: XXXXX bytes
   ```

### Posibles Causas y Soluciones

#### Causa 1: Flask No Se Levantó
**Logs:**
```
❌ ERROR: Flask no respondió después de 30 segundos
```

**Solución:**
- Descargar artifact `Flask Logs/flask.log`
- Verificar errores de Python o imports faltantes
- Asegurar que app.py está en el directorio correcto

#### Causa 2: Error de Sintaxis de Wapiti
**Logs:**
```
Invalid base URL was specified
```

**Solución:**
- Agregar barra final a la URL: `http://localhost:5000/`
- Simplificar comando Wapiti (solo `-u`, `-f`, `-o`)

#### Causa 3: Wapiti No Instalado
**Logs:**
```
wapiti: command not found
```

**Solución:**
- Verificar que `wapiti3` está en `requirements.txt`
- Verificar que se instaló en el step "Build Environment"

#### Causa 4: Path Incorrecto
**Logs:**
```
No artifact files found at /home/circleci/project/reporte_seguridad/wapiti_report.html
```

**Solución:**
- Verificar que Wapiti creó el archivo en la ubicación correcta
- Descargar artifact `Wapiti Logs/wapiti.log` para ver mensajes
- Buscar archivos HTML: `find . -name "*.html"`

---

## Problema: Email Notifications No Funcionan

### Error
```
ModuleNotFoundError: No module named 'yagmail'
```

### Causa
Variables de entorno no configuradas en CircleCI.

### Solución
Ver **SETUP.md** sección 1 para configurar:
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD` (contraseña de aplicación de Gmail)
- `RECIPIENT_EMAIL`

---

## Problema: LaunchDarkly - "set_config was not called"

### Error Completo
```
Exception: set_config was not called
```

### Causa
El código intentaba usar LaunchDarkly sin que esté configurado.

### Solución
Ya está arreglado en `compare_pdfs.py:76-98`. El código ahora funciona sin LaunchDarkly:
```python
ld_sdk_key = os.getenv('LD_SDK_KEY')
feature_enabled = True  # Por defecto habilitado

if not ld_sdk_key:
    print("Advertencia: Ejecutando sin Feature Flags")
else:
    # Solo usa LaunchDarkly si está configurado
```

**LaunchDarkly es OPCIONAL** - el pipeline funciona perfectamente sin él.

---

## Problema: Conflicto de Dependencias

### Error
```
ModuleNotFoundError: No module named 'yagmail'
```

### Causa
Versiones duplicadas en requirements.txt:
```
requests==2.32.5    # Línea 20 (segura)
requests==2.20.0    # Línea 41 (vulnerable) ← SOBREESCRIBE
```

### Solución
Separar archivos:
- `requirements.txt` → Versiones seguras (para instalar)
- `requirements-vulnerable.txt` → Versiones vulnerables (solo para Safety scan)

Pipeline:
```bash
pip install -r requirements.txt              # Instala seguras
safety scan --file requirements-vulnerable.txt  # Analiza vulnerables
```

---

## Debugging: Cómo Investigar Problemas

### Paso 1: Ver Logs del Pipeline
1. Ir a CircleCI
2. Expandir el step que falló
3. Leer los mensajes de error

### Paso 2: Descargar Artifacts de Logs
Desde CircleCI → ARTIFACTS:
- `Flask Logs/flask.log` - Errores de la aplicación Flask
- `Wapiti Logs/wapiti.log` - Errores de Wapiti
- `flake8-report.txt` - Problemas de calidad de código

### Paso 3: Reproducir Localmente
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar Safety
safety scan --file requirements-vulnerable.txt

# 3. Ejecutar Flask
python app.py &
FLASK_PID=$!

# 4. Esperar y probar
sleep 5
curl http://localhost:5000/

# 5. Ejecutar Wapiti
mkdir -p reporte_seguridad
wapiti -u "http://localhost:5000/" -f html -o "reporte_seguridad/wapiti_report.html"

# 6. Limpiar
kill $FLASK_PID
```

### Paso 4: Verificar Versiones
```bash
python --version
safety --version
wapiti --version
flask --version
```

---

## Comandos Útiles para Debugging

### Verificar que Flask está corriendo
```bash
curl -v http://localhost:5000/
netstat -tuln | grep 5000
lsof -i :5000
```

### Verificar archivos generados
```bash
find . -name "*.html" -type f
ls -lah reporte_seguridad/
```

### Ver procesos de Python
```bash
ps aux | grep python
ps aux | grep flask
```

### Matar proceso Flask si se quedó colgado
```bash
pkill -f "python app.py"
lsof -ti:5000 | xargs kill -9
```

---

## Recursos Adicionales

- **Wapiti Documentation:** http://wapiti.sourceforge.net/
- **Safety Documentation:** https://github.com/pyupio/safety
- **CircleCI Docs:** https://circleci.com/docs/
- **Flask Docs:** https://flask.palletsprojects.com/

---

## Contacto

Si encuentras un problema no documentado aquí, por favor:
1. Revisa los logs en CircleCI
2. Descarga los artifacts de logs
3. Documenta el error y la solución en este archivo
