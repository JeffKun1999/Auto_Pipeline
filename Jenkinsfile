// Jenkinsfile (Versión Definitiva y Explícita)
pipeline {
    // Usamos 'agent none' para tener control total en cada etapa
    agent none

    // Opción para evitar que Jenkins clone el repo automáticamente en cada etapa
    options {
        skipDefaultCheckout()
    }

    stages {
        // ETAPA 1: Descargar el código UNA SOLA VEZ
        stage('Checkout Source Code') {
            agent any
            steps {
                echo 'Clonando el repositorio una sola vez...'
                checkout scm
            }
        }

        // ETAPA 2: Ejecutar todo dentro de un contenedor Docker controlado
        stage('Build and Execute in Docker') {
            // Usamos un agente simple solo para iniciar el bloque de script
            agent any
            steps {
                // Usamos un bloque 'script' para poder usar la sintaxis .inside()
                script {
                    // Esta es la forma más robusta de usar un contenedor.
                    // Le decimos a Jenkins que use esta imagen y ejecute todo lo que está
                    // dentro de las llaves DENTRO del contenedor.
                    docker.image('python:3.9-slim').inside('-w /app') {
                        
                        // El bloque withCredentials funciona igual aquí dentro
                        withCredentials([
                            string(credentialsId: 'GMAIL_SENDER_EMAIL', variable: 'GMAIL_SENDER_EMAIL'),
                            string(credentialsId: 'GMAIL_RECEIVER_EMAIL', variable: 'GMAIL_RECEIVER_EMAIL'),
                            string(credentialsId: 'GMAIL_LOGIN', variable: 'GMAIL_LOGIN'),
                            string(credentialsId: 'GMAIL_APP_PASSWORD', variable: 'GMAIL_APP_PASSWORD')
                        ]) {
                            sh 'echo "--- Preparando Entorno ---"'
                            sh 'python -m venv .venv'
                            sh 'source .venv/bin/activate'
                            sh 'pip install -r requirements.txt'
                            
                            sh 'echo "--- Ejecutando Script ---"'
                            sh 'python compare_pdfs.py DocumentoA_1.pdf DocumentoA2.pdf'
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            
            node {
                echo 'Limpiando el espacio de trabajo...'
                cleanWs()
            }
        }
    }
}