// Jenkinsfile Corregido
pipeline {
    agent any

    stages {
        // Etapa 1: Descargar el código fuente del repositorio
        stage('Checkout Source Code') {
            steps {
                echo 'Clonando el repositorio...'
                checkout scm
            }
        }

        // Etapa 2: Inicializar variables de entorno según el SO
        stage('Initialize') {
            steps {
                script {
                    // Este es el modo correcto de asignar una variable condicional
                    // Se usa un bloque 'script' para poder usar la lógica de Groovy
                    if (isUnix()) {
                        env.VENV_ACTIVATE = 'source .venv/bin/activate'
                    } else {
                        env.VENV_ACTIVATE = 'call .venv\\Scripts\\activate.bat'
                    }
                    echo "Comando de activación de venv: ${env.VENV_ACTIVATE}"
                }
            }
        }

        // Etapa 3: Construir el entorno. Se hace UNA SOLA VEZ.
        stage('Build Environment') {
            steps {
                echo '--- Preparando Entorno de Python ---'
                // Crea el entorno virtual
                bat 'python -m venv .venv'
                
                // Activa el entorno e instala dependencias usando la variable preparada
                bat "${env.VENV_ACTIVATE} && pip install -r requirements.txt"
            }
        }

        // Etapa 4: Analizar la calidad del código con Flake8
        stage('Code Quality Analysis') {
            steps {
                echo '--- Ejecutando Análisis de Calidad de Código con Flake8 ---'
                bat "${env.VENV_ACTIVATE} && flake8 --output-file=flake8-report.txt --tee"
            }
        }

        // Etapa 5: Ejecutar las pruebas unitarias con Pytest
        stage('Unit Tests') {
            steps {
                echo '--- Ejecutando Pruebas Unitarias con Pytest ---'
                bat "${env.VENV_ACTIVATE} && pytest"
            }
        }
        
        // Etapa 6: Desplegar la aplicación y ejecutar la comparación
        stage('Deploy & Execute') {
            steps {
                withCredentials([
                    string(credentialsId: 'GMAIL_LOGIN',           variable: 'EMAIL_HOST_USER'),
                    string(credentialsId: 'GMAIL_APP_PASSWORD',    variable: 'EMAIL_HOST_PASSWORD'),
                    string(credentialsId: 'GMAIL_RECEIVER_EMAIL',  variable: 'RECIPIENT_EMAIL')
                ]) {
                    withEnv([
                        "EMAIL_HOST=smtp.gmail.com",
                        "EMAIL_PORT=587"
                    ]) {
                        echo '--- Desplegando la aplicación ---'
                        bat 'chmod +x deploy.sh'
                        bat './deploy.sh'
                        
                        echo '--- Ejecutando Script de Comparación de PDFs ---'
                        bat "${env.VENV_ACTIVATE} && python compare_pdfs.py DocumentoA_1.pdf DocumentoA2.pdf"
                        bat "${env.VENV_ACTIVATE} && python compare_pdfs.py DocumentoA_1.pdf DocumentoB1.pdf"
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Limpiando el espacio de trabajo...'
            archiveArtifacts artifacts: 'flake8-report.txt', allowEmptyArchive: true
            cleanWs()
        }
        success {
            echo 'Pipeline completado exitosamente.'
        }
        failure {
            script {
                echo 'Pipeline falló. Revisar los logs.'
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