// Jenkinsfile (Versión Final Corregida)
pipeline {
    agent none

    options {
        skipDefaultCheckout()
    }

    stages {
        stage('Checkout Source Code') {
            // Este agente es necesario para descargar el código
            agent any
            steps {
                echo 'Clonando el repositorio una sola vez...'
                checkout scm
            }
        }

        stage('Build and Execute in Docker') {
            // HEMOS ELIMINADO EL 'agent any' DE ESTA ETAPA
            steps {
                script {
                    // El comando .inside() provee su propio entorno de ejecución
                    docker.image('python:3.9-slim').inside('-w /app') {
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
}