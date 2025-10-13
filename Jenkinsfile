// Jenkinsfile (Versión corregida y robusta)
pipeline {
   
    agent none

    stages {
        // ETAPA 1: Usamos un agente simple para clonar el código en el nodo principal.
        stage('Checkout') {
            agent any
            steps {
                echo 'Clonando el repositorio...'
                checkout scm
            }
        }

        // ETAPA 2: Preparamos el entorno y ejecutamos el script DENTRO de Docker.
        stage('Build and Execute') {
            // 2. Aquí es donde definimos nuestro agente de Docker.
            // Al aislarlo a esta etapa, Jenkins maneja mejor el contexto y las rutas.
            agent {
                docker {
                    image 'python:3.9-slim'
                    args '-w /app'
                }
            }
            steps {
                echo 'Creando entorno virtual e instalando dependencias...'
                sh '''
                    python -m venv .venv
                    source .venv/bin/activate
                    pip install -r requirements.txt
                '''
                
                // El bloque withCredentials inyecta las variables de entorno de forma segura
                withCredentials([
                    string(credentialsId: 'GMAIL_SENDER_EMAIL', variable: 'GMAIL_SENDER_EMAIL'),
                    string(credentialsId: 'GMAIL_RECEIVER_EMAIL', variable: 'GMAIL_RECEIVER_EMAIL'),
                    string(credentialsId: 'GMAIL_LOGIN', variable: 'GMAIL_LOGIN'),
                    string(credentialsId: 'GMAIL_APP_PASSWORD', variable: 'GMAIL_APP_PASSWORD')
                ]) {
                    echo 'Ejecutando el script de comparación de PDFs...'
                    sh '''
                        source .venv/bin/activate
                        python compare_pdfs.py DocumentoA_1.pdf DocumentoA2.pdf
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo 'Limpiando el espacio de trabajo...'
            // cleanWs() necesita ejecutarse en un nodo para saber qué limpiar.
            // Al moverlo aquí, aseguramos que siempre tenga un contexto.
            node('master') {
                cleanWs()
            }
        }
    }
}