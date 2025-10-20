// Jenkinsfile Final - Lógica de limpieza corregida
pipeline {
    agent any

    stages {
        // ... (tus etapas 'stage' se mantienen exactamente igual que en tu versión) ...
        stage('Checkout Source Code') {
            steps {
                echo 'Clonando el repositorio...'
                checkout scm
            }
        }

        stage('Initialize') {
            steps {
                script {
                    if (isUnix()) {
                        env.VENV_ACTIVATE = 'source .venv/bin/activate'
                    } else {
                        env.VENV_ACTIVATE = 'call .venv\\Scripts\\activate.bat'
                    }
                    echo "Comando de activación de venv: ${env.VENV_ACTIVATE}"
                }
            }
        }

        stage('Build Environment') {
            steps {
                echo '--- Preparando Entorno de Python ---'
                bat 'python -m venv .venv'
                bat "${env.VENV_ACTIVATE} && pip install -r requirements.txt"
            }
        }

        stage('Code Quality Analysis') {
            steps {
                script {
                    echo '--- Ejecutando Análisis de Calidad de Código con Flake8 ---'
                    def flake8_status = bat script: "${env.VENV_ACTIVATE} && flake8 --output-file=flake8-report.txt --tee", returnStatus: true
                    if (flake8_status != 0) {
                        echo "Flake8 encontró problemas. Marcando el build como INESTABLE, pero continuando."
                        currentBuild.result = 'UNSTABLE'
                    } else {
                        echo "El análisis de Flake8 pasó sin problemas."
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                echo '--- Ejecutando Pruebas Unitarias con Pytest ---'
                bat "${env.VENV_ACTIVATE} && pytest"
            }
        }
        
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
                        bat 'deploy.bat'
                        
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
            // 'always' ahora solo archiva, para asegurar que el reporte esté disponible.
            echo 'Archivando artefactos...'
            archiveArtifacts artifacts: 'flake8-report.txt', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline completado exitosamente.'
            // La limpieza se hace al final de cada bloque.
            cleanWs()
        }
        unstable {
            script {
                echo 'Pipeline completado con advertencias (UNSTABLE). Enviando reporte por correo...'
                def report = fileExists('flake8-report.txt') ? readFile('flake8-report.txt') : 'No se encontró el reporte de Flake8.'
                withCredentials([string(credentialsId: 'GMAIL_RECEIVER_EMAIL', variable: 'RECIPIENT_EMAIL')]) {
                    emailext (
                        to: "${env.RECIPIENT_EMAIL}",
                        subject: "ADVERTENCIA: Pipeline '${env.JOB_NAME}' - Build #${env.BUILD_NUMBER} Inestable",
                        body: """<h1>Estado del Pipeline: INESTABLE</h1><p>El pipeline para el proyecto <b>${env.JOB_NAME}</b> ha finalizado con advertencias.</p><p><b>Build:</b> <a href="${env.BUILD_URL}">${env.BUILD_NUMBER}</a></p><hr><h2>Reporte de Calidad de Código (Flake8):</h2><pre>${report}</pre><hr><p>Se recomienda revisar los problemas de calidad de código encontrados.</p>""",
                        mimeType: 'text/html',
                        attachLog: true,
                        attachmentsPattern: 'flake8-report.txt'
                    )
                }
                // La limpieza se hace al final de cada bloque.
                cleanWs()
            }
        }
        failure {
            script {
                echo 'Pipeline falló. Enviando notificación por correo...'
                withCredentials([string(credentialsId: 'GMAIL_RECEIVER_EMAIL', variable: 'RECIPIENT_EMAIL')]) {
                    emailext (
                        to: "${env.RECIPIENT_EMAIL}",
                        subject: "FALLO: Pipeline '${env.JOB_NAME}' - Build #${env.BUILD_NUMBER} Falló",
                        body: """<h1>Estado del Pipeline: FALLIDO</h1><p>El pipeline para el proyecto <b>${env.JOB_NAME}</b> ha fallado.</p><p><b>Build:</b> <a href="${env.BUILD_URL}">${env.BUILD_NUMBER}</a></p><p>Revisa el log adjunto para identificar la causa del error.</p>""",
                        mimeType: 'text/html',
                        attachLog: true
                    )
                }
                // La limpieza se hace al final de cada bloque.
                cleanWs()
            }
        }
    }
}