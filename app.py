from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    # Un formulario simple para que Wapiti intente inyectar cosas
    return '''
        <h1>Sitio de Prueba DevSecOps</h1>
        <form action="/login" method="POST">
            Usuario: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Ingresar">
        </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    return "Intento de login recibido"

if __name__ == '__main__':
    app.run(debug=True, port=5000)