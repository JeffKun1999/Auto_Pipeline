// Jenkinsfile Final - Corregido para limpieza y SMTP
pipeline {
    agent any

    stages {
        // ... (todas tus etapas 'stage' se mantienen exactamente igual) ...
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
                    if (isUnix()) {
                        env.VENV_ACTIVATE = 'source .venv/bin/activate'
                    } else {
                        env.VENV_ACTIVATE = 'call .venv\\Scripts\\activate.bat'
                    }
                    echo "Comando de activación de venv: ${env.VENV_ACTIVATE}"
                }
            }
        }

        // Etapa 3: Construir el entorno
        stage('Build Environment') {
            steps {
                echo '--- Preparando Entorno de Python ---'
                bat 'python -m venv .venv'
                bat "${env.VENV_ACTIVATE} && pip install -r requirements.txt"
            }
        }

        // Etapa 4: Analizar la calidad del código con Flake8
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
                        bat 'deploy.bat'
                        
                        echo '--- Ejecutando Script de Comparación de PDFs ---'
                        bat "${env.VENV_ACTIVATE} && python compare_pdfs.py DocumentoA_1.pdf DocumentoA2.pdf"
                        bat "${env.VENV_ACTIVATE} && python compare_pdfs.py DocumentoA_1.pdf DocumentoB1.pdf"
                    }
                }
            }
        }
    }
    
    // =================================================================
    // SECCIÓN POST CORREGIDA - LÓGICA DE LIMPIEZA AJUSTADA
    // =================================================================
    post {
        always {
            // 'always' ahora solo archiva, no limpia.
            echo 'Archivando artefactos...'
            archiveArtifacts artifacts: 'flake8-report.txt', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline completado exitosamente.'
            // Limpiamos el workspace al final.
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
                // Limpiamos el workspace al final.
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
                // Limpiamos el workspace al final.
                cleanWs()
            }
        }
    }
}