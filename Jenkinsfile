// Jenkinsfile (Versión Corregida con los IDs correctos)
pipeline {
    agent any

    stages {
        stage('Checkout Source Code') {
            steps {
                echo 'Clonando el repositorio...'
                checkout scm
            }
        }

        stage('Build and Execute Python Script') {
            steps {
                // Este bloque inyectará las variables de entorno que tu script necesita.
                // credentialsId: El ID exacto que tienes en Jenkins.
                // variable: El nombre que tu script de Python leerá con os.getenv().
                withCredentials([
                    string(credentialsId: 'GMAIL_LOGIN',           variable: 'EMAIL_HOST_USER'),
                    string(credentialsId: 'GMAIL_APP_PASSWORD',    variable: 'EMAIL_HOST_PASSWORD'),
                    string(credentialsId: 'GMAIL_RECEIVER_EMAIL',  variable: 'RECIPIENT_EMAIL')
                ]) {
                    // Usamos withEnv para añadir las variables que no son secretas.
                    withEnv([
                        "EMAIL_HOST=smtp.gmail.com",
                        "EMAIL_PORT=587"
                    ]) {
                        bat '''
                            echo "--- Preparando Entorno de Python ---"
                            
                            REM Crea el entorno virtual
                            python -m venv .venv
                            
                            REM Activa el entorno virtual y luego instala las dependencias
                            call .venv\\Scripts\\activate.bat && pip install -r requirements.txt
                            
                            echo "--- Ejecutando Script de Python ---"
                            
                            REM Ejecuta el script.
                            call python compare_pdfs.py DocumentoA_1.pdf DocumentoA2.pdf
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Limpiando el espacio de trabajo...'
            cleanWs()
        }
    }
}