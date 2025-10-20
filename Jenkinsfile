// Jenkinsfile Final Estructurado
pipeline {
    agent any

    // Define las variables de entorno para activar el venv en los stages
    environment {
        // La variable VENV_PATH se usará para activar el entorno virtual de forma consistente
        // Se ajusta dinámicamente si el agente es Windows ('bat') o Linux/macOS ('sh')
        VENV_PATH = isUnix() ? '.venv/bin/activate' : '.venv\\Scripts\\activate.bat'
    }

    stages {
        // Etapa 1: Descargar el código fuente del repositorio
        stage('Checkout Source Code') {
            steps {
                echo 'Clonando el repositorio...'
                checkout scm
            }
        }

        // Etapa 2: Construir el entorno. Se hace UNA SOLA VEZ.
        stage('Build Environment') {
            steps {
                echo '--- Preparando Entorno de Python ---'
                // Crea el entorno virtual
                bat 'python -m venv .venv'
                
                // Activa el entorno e instala dependencias de requirements.txt
                bat "call %VENV_PATH% && pip install -r requirements.txt"
            }
        }

        // Etapa 3: Analizar la calidad del código con Flake8
        stage('Code Quality Analysis') {
            steps {
                echo '--- Ejecutando Análisis de Calidad de Código con Flake8 ---'
                // Ejecuta flake8, guarda el reporte en un archivo y lo muestra en consola
                bat "call %VENV_PATH% && flake8 . --output-file=flake8-report.txt --tee"
            }
        }

        // Etapa 4: Ejecutar las pruebas unitarias con Pytest
        stage('Unit Tests') {
            steps {
                echo '--- Ejecutando Pruebas Unitarias con Pytest ---'
                bat "call %VENV_PATH% && pytest"
            }
        }
        
        // Etapa 5: Desplegar la aplicación y ejecutar la comparación
        stage('Deploy & Execute') {
            steps {
                // Inyecta las credenciales de correo electrónico de forma segura
                withCredentials([
                    string(credentialsId: 'GMAIL_LOGIN',           variable: 'EMAIL_HOST_USER'),
                    string(credentialsId: 'GMAIL_APP_PASSWORD',    variable: 'EMAIL_HOST_PASSWORD'),
                    string(credentialsId: 'GMAIL_RECEIVER_EMAIL',  variable: 'RECIPIENT_EMAIL')
                ]) {
                    // Añade las variables de entorno no secretas
                    withEnv([
                        "EMAIL_HOST=smtp.gmail.com",
                        "EMAIL_PORT=587"
                    ]) {
                        // Primero, se ejecuta el despliegue simulado
                        echo '--- Desplegando la aplicación ---'
                        // Damos permisos de ejecución al script de deploy
                        bat 'chmod +x deploy.sh'
                        bat './deploy.sh'
                        
                        echo '--- Ejecutando Script de Comparación de PDFs ---'
                        // Luego, se ejecuta la lógica principal del script
                        bat "call %VENV_PATH% && python compare_pdfs.py DocumentoA_1.pdf DocumentoA2.pdf"
                        bat "call %VENV_PATH% && python compare_pdfs.py DocumentoA_1.pdf DocumentoB1.pdf"
                    }
                }
            }
        }
    }
    
    // Acciones que se ejecutan al final del pipeline
    post {
        always {
            echo 'Limpiando el espacio de trabajo...'
            // archiva los reportes generados para poder revisarlos después
            archiveArtifacts artifacts: 'flake8-report.txt', allowEmptyArchive: true
            cleanWs()
        }
        success {
            echo '✅ Pipeline completado exitosamente.'
            // Aquí podrías añadir una notificación a Slack o Teams
        }
        failure {
            script {
                echo '❌ Pipeline falló. Revisar los logs.'
                // Si el pipeline falla, lee y muestra el reporte de flake8 en la consola
                if (fileExists('flake8-report.txt')) {
                    def report = readFile 'flake8-report.txt'
                    echo "--- Resumen de Errores de Calidad de Código ---"
                    echo "${report}"
                    echo "------------------------------------------------"
                }
            }
        }
    }
}