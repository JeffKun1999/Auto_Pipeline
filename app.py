"""
Aplicación Flask INTENCIONALMENTE VULNERABLE para pruebas DevSecOps
ADVERTENCIA: Esta aplicación contiene vulnerabilidades a propósito para probar
herramientas de seguridad como Safety (SAST) y Wapiti (DAST).
NUNCA usar este código en producción.
"""

from flask import Flask, request, render_template_string, redirect, make_response
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-super-secreta-123'  # Vulnerabilidad: clave hardcodeada

# Crear base de datos de prueba
def init_db():
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (2, 'user', 'user123', 'user')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return '''
        <html>
        <head><title>Aplicación Vulnerable - Demo DevSecOps</title></head>
        <body>
            <h1>🔓 Sitio de Prueba DevSecOps (Vulnerable)</h1>
            <p><strong>ADVERTENCIA:</strong> Esta aplicación contiene vulnerabilidades intencionales.</p>

            <h2>Funcionalidades Vulnerables:</h2>
            <ul>
                <li><a href="/login">Login (SQL Injection)</a></li>
                <li><a href="/search">Búsqueda (XSS)</a></li>
                <li><a href="/profile?user=admin">Perfil (XSS Reflejado)</a></li>
                <li><a href="/file?name=test.txt">Descarga de Archivos (Path Traversal)</a></li>
            </ul>
        </body>
        </html>
    '''

# VULNERABILIDAD 1: SQL Injection
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # VULNERABLE: Query SQL sin sanitización
        conn = sqlite3.connect('vulnerable.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

        try:
            cursor.execute(query)  # SQL Injection aquí!
            user = cursor.fetchone()
            conn.close()

            if user:
                return f"<h1>✅ Login exitoso!</h1><p>Bienvenido {user[1]}, rol: {user[3]}</p>"
            else:
                return "<h1>❌ Login fallido</h1><p>Credenciales incorrectas</p>"
        except Exception as e:
            return f"<h1>❌ Error</h1><p>{str(e)}</p>"

    return '''
        <html>
        <body>
            <h1>Login Vulnerable</h1>
            <form action="/login" method="POST">
                Usuario: <input type="text" name="username"><br><br>
                Password: <input type="password" name="password"><br><br>
                <input type="submit" value="Ingresar">
            </form>
            <p><em>Prueba SQL Injection: admin' OR '1'='1</em></p>
        </body>
        </html>
    '''

# VULNERABILIDAD 2: XSS (Cross-Site Scripting)
@app.route('/search')
def search():
    query = request.args.get('q', '')

    # VULNERABLE: No sanitiza el input del usuario
    return f'''
        <html>
        <body>
            <h1>Búsqueda Vulnerable</h1>
            <form action="/search" method="GET">
                <input type="text" name="q" value="{query}">
                <input type="submit" value="Buscar">
            </form>
            <h2>Resultados para: {query}</h2>
            <p>No se encontraron resultados.</p>
            <p><em>Prueba XSS: &lt;script&gt;alert('XSS')&lt;/script&gt;</em></p>
        </body>
        </html>
    '''

# VULNERABILIDAD 3: XSS Reflejado
@app.route('/profile')
def profile():
    username = request.args.get('user', 'invitado')

    # VULNERABLE: Refleja directamente el parámetro sin sanitizar
    html = f'''
        <html>
        <body>
            <h1>Perfil de Usuario</h1>
            <p>Nombre de usuario: {username}</p>
            <p><em>Prueba XSS: ?user=&lt;img src=x onerror=alert('XSS')&gt;</em></p>
        </body>
        </html>
    '''
    return html

# VULNERABILIDAD 4: Path Traversal / Directory Traversal
@app.route('/file')
def download_file():
    filename = request.args.get('name', '')

    # VULNERABLE: No valida el path, permite acceso a cualquier archivo
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return f'''
            <html>
            <body>
                <h1>Contenido del archivo: {filename}</h1>
                <pre>{content}</pre>
                <p><em>Prueba Path Traversal: ?name=../../etc/passwd</em></p>
            </body>
            </html>
        '''
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

# VULNERABILIDAD 5: Debug mode en producción
# VULNERABILIDAD 6: Información sensible expuesta
@app.route('/debug')
def debug_info():
    return f'''
        <html>
        <body>
            <h1>Información de Debug (VULNERABLE)</h1>
            <p>SECRET_KEY: {app.config['SECRET_KEY']}</p>
            <p>Variables de entorno: {dict(os.environ)}</p>
        </body>
        </html>
    '''

# VULNERABILIDAD 7: CORS permisivo
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # Demasiado permisivo
    return response

if __name__ == '__main__':
    print("=" * 60)
    print("⚠️  APLICACIÓN VULNERABLE INICIADA")
    print("=" * 60)
    print("Esta aplicación contiene vulnerabilidades intencionales:")
    print("1. SQL Injection en /login")
    print("2. XSS en /search")
    print("3. XSS Reflejado en /profile")
    print("4. Path Traversal en /file")
    print("5. Debug mode habilitado")
    print("6. Secret key hardcodeada")
    print("7. CORS permisivo")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)  # debug=True es vulnerable