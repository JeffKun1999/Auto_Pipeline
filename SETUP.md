# Guía de Configuración del Pipeline DevSecOps

Esta guía explica cómo configurar el pipeline DevSecOps en CircleCI.

## 1. Configuración de Variables de Entorno en CircleCI

El pipeline necesita credenciales de email para enviar notificaciones. Debes configurar estas variables en CircleCI.

### Paso 1: Acceder a la Configuración del Proyecto

1. Ve a CircleCI: https://app.circleci.com/
2. Selecciona tu proyecto: `JeffKun1999/Auto_Pipeline`
3. Haz clic en **"Project Settings"** (⚙️ arriba a la derecha)

### Paso 2: Configurar Variables de Entorno

1. En el menú lateral, selecciona **"Environment Variables"**
2. Haz clic en **"Add Environment Variable"**
3. Agrega las siguientes variables:

#### Variables Requeridas para Email:

| Variable Name | Descripción | Ejemplo |
|---------------|-------------|---------|
| `EMAIL_HOST_USER` | Tu dirección de Gmail | `tu-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Contraseña de aplicación de Gmail | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Email que recibirá notificaciones | `tu-email@gmail.com` |

**IMPORTANTE:** Para `EMAIL_HOST_PASSWORD` **NO uses tu contraseña de Gmail normal**. Debes crear una "Contraseña de aplicación".

### Paso 3: Crear Contraseña de Aplicación en Gmail

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Selecciona **"Seguridad"** en el menú lateral
3. En "Cómo inicias sesión en Google", activa **"Verificación en dos pasos"** (si no está activada)
4. Busca **"Contraseñas de aplicaciones"**
5. Crea una nueva contraseña de aplicación:
   - Nombre: "CircleCI Pipeline"
   - Copia la contraseña generada (formato: `xxxx xxxx xxxx xxxx`)
6. Usa esta contraseña en la variable `EMAIL_HOST_PASSWORD` de CircleCI

### Paso 4: Verificar la Configuración

Después de configurar las variables, el próximo push al repositorio debería:
- ✅ Ejecutar el pipeline completo
- ✅ Enviar email de notificación al finalizar

---

## 2. LaunchDarkly - Feature Flags (OPCIONAL)

### ¿Qué es LaunchDarkly?

LaunchDarkly es un sistema de **Feature Flags** que permite activar/desactivar funcionalidades sin cambiar código.

En este proyecto, se usaba para controlar si el script `compare_pdfs.py` se ejecutaba o no.

### Estado Actual

- ✅ **NO es necesario para que funcione el pipeline**
- ✅ El código ya está configurado para funcionar **sin LaunchDarkly**
- ⚠️ La versión de prueba de 15 días expiró

### Cómo Funciona Actualmente

El código en `compare_pdfs.py:76-98` está configurado así:

```python
ld_sdk_key = os.getenv('LD_SDK_KEY')
feature_enabled = True  # Por defecto, está habilitado

if not ld_sdk_key:
    print("Advertencia: LD_SDK_KEY no configurada. Ejecutando sin Feature Flags (modo habilitado por defecto).")
else:
    # Solo usa LaunchDarkly si está configurado
    ldclient.set_config(Config(ld_sdk_key))
    feature_enabled = ldclient.get().variation("enable-pdf-comparison", context, False)
```

**Resultado:** Si no hay `LD_SDK_KEY`, el código se ejecuta normalmente.

### Opción A: Usar sin LaunchDarkly (Recomendado)

**No hacer nada.** El pipeline funciona perfectamente sin LaunchDarkly.

### Opción B: Configurar LaunchDarkly (Si tienes cuenta activa)

Si tienes una cuenta activa de LaunchDarkly:

1. Ve a: https://app.launchdarkly.com/
2. Crea un proyecto
3. Obtén tu SDK Key
4. En CircleCI, agrega la variable:
   - Name: `LD_SDK_KEY`
   - Value: `sdk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
5. En LaunchDarkly, crea una feature flag llamada: `enable-pdf-comparison`
6. Actívala o desactívala según necesites

### Opción C: Remover LaunchDarkly Completamente

Si quieres eliminar LaunchDarkly del proyecto:

1. Edita `compare_pdfs.py` y remueve la sección de LaunchDarkly (líneas 75-98)
2. Edita `requirements.txt` y remueve: `launchdarkly-server-sdk>=9.0.0`
3. Haz commit y push

---

## 3. Estructura de Archivos de Dependencias

### requirements.txt
Contiene las **versiones seguras** de todas las dependencias.
- Se usa para instalar el entorno del pipeline
- Garantiza que el pipeline funcione correctamente
- Incluye: Flask, pytest, flake8, safety, wapiti3, yagmail, etc.

### requirements-vulnerable.txt
Contiene **versiones vulnerables intencionales** para pruebas.
- **NO se instala en el entorno**
- Solo se usa para análisis de Safety (SAST)
- Demuestra que Safety detecta vulnerabilidades conocidas (CVEs)

### Flujo de Ejecución:

```
1. pip install -r requirements.txt          # Instala versiones seguras
2. safety check -r requirements-vulnerable.txt  # Analiza versiones vulnerables
```

De esta forma:
- ✅ El pipeline funciona (usa versiones seguras)
- ✅ Safety detecta vulnerabilidades (analiza versiones vulnerables)
- ✅ No hay conflictos de dependencias

---

## 4. Verificar que Todo Funciona

### Test 1: Verificar Variables de Entorno

```bash
# Hacer un pequeño cambio
echo "Test configuración" >> README.md

# Commit y push
git add README.md
git commit -m "Test configuración de email"
git push origin ArgoCD
```

### Test 2: Ver Logs en CircleCI

1. Ve a: https://app.circleci.com/pipelines/github/JeffKun1999/Auto_Pipeline
2. Observa el pipeline ejecutándose
3. Verifica que la etapa "Security Audit - SAST (Safety)" se ejecuta correctamente
4. Al finalizar, deberías recibir un email

### Test 3: Verificar Email

Deberías recibir un email con:
- Asunto: `ÉXITO: Pipeline 'main-workflow' - Build #XX Completado`
- O: `ADVERTENCIA: Pipeline 'main-workflow' - Build #XX Inestable` (si Flake8 encuentra problemas)
- O: `FALLO: Pipeline 'main-workflow' - Build #XX Falló` (si algo falla)

---

## 5. Solución de Problemas

### Error: "No module named 'yagmail'"

**Causa:** Conflicto de dependencias (versiones duplicadas)

**Solución:** Ya está arreglado con la separación de archivos requirements.txt y requirements-vulnerable.txt

### Error: "LD_SDK_KEY not configured"

**Causa:** LaunchDarkly no está configurado

**Solución:** Esto es **normal y esperado**. El pipeline funciona sin LaunchDarkly.

### No recibo emails

**Causa:** Variables de entorno no configuradas en CircleCI

**Solución:** Seguir la sección 1 de este documento para configurar:
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD` (contraseña de aplicación de Gmail)
- `RECIPIENT_EMAIL`

### Safety no detecta vulnerabilidades

**Causa:** Está analizando el archivo equivocado

**Solución:** Verificar que `.circleci/config.yml` usa: `safety check -r requirements-vulnerable.txt`

---

## 6. Comandos Útiles

### Ejecutar localmente:

```bash
# Instalar dependencias seguras
pip install -r requirements.txt

# Verificar vulnerabilidades
safety check -r requirements-vulnerable.txt

# Ejecutar aplicación vulnerable
python app.py

# Ejecutar tests
pytest
```

### Trigger del pipeline:

```bash
git add .
git commit -m "Tu mensaje"
git push origin ArgoCD
```

---

## 7. Resumen de Configuración Mínima

Para que el pipeline funcione completamente, necesitas:

1. ✅ **Configurar en CircleCI:**
   - `EMAIL_HOST_USER`
   - `EMAIL_HOST_PASSWORD`
   - `RECIPIENT_EMAIL`

2. ✅ **Crear contraseña de aplicación en Gmail**

3. ⚠️ **LaunchDarkly es OPCIONAL** (no es necesario)

Eso es todo! Con eso el pipeline funciona al 100%.

---

## 8. Contacto y Soporte

Si tienes problemas:
1. Verifica los logs en CircleCI
2. Revisa las variables de entorno
3. Consulta este documento
