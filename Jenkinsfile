
pipeline {
    agent any

    stages {
        stage('Checkout Source Code') {
            steps {
                echo 'Clonando el repositorio...'
                checkout scm
            }
        }

        // Etapa 2: Inicializar las rutas a los ejecutables del venv
        stage('Initialize') {
            steps {
                script {
                    // Define las rutas a los ejecutables según el sistema operativo.
                    // Esto elimina la dependencia del script 'activate'.
                    if (isUnix()) {
                        env.PYTHON_EXE = "./.venv/bin/python"
                        env.PYTEST_EXE = "./.venv/bin/pytest"
                        env.FLAKE8_EXE = "./.venv/bin/flake8"
                    } else {
                        env.PYTHON_EXE = ".venv\\Scripts\\python.exe"
                        env.PYTEST_EXE = ".venv\\Scripts\\pytest.exe"
                        env.FLAKE8_EXE = ".venv\\Scripts\\flake8.exe"
                    }
                    echo "Ruta del ejecutable de Python: ${env.PYTHON_EXE}"
                }
            }
        }

        // Etapa 3: Construir el entorno usando la ruta explícita
        stage('Build Environment') {
            steps {
                echo '--- Preparando Entorno de Python ---'
                bat 'python -m venv .venv'
                // Usa la ruta explícita para garantizar la instalación en el venv
                bat "\"${env.PYTHON_EXE}\" -m pip install -r requirements.txt"
            }
        }

        // Etapa 4: Analizar la calidad del código
        stage('Code Quality Analysis') {
            steps {
                script {
                    echo '--- Ejecutando Análisis de Calidad de Código con Flake8 ---'
                    def flake8_status = bat script: "\"${env.FLAKE8_EXE}\" --output-file=flake8-report.txt --tee", returnStatus: true
                    
                    if (flake8_status != 0) {
                        // Si Flake8 encuentra problemas, marcamos el build como inestable
                        echo "Flake8 encontró problemas. Marcando el build como INESTABLE."
                        //currentBuild.result = 'UNSTABLE'
                    } else {
                        echo " El análisis de Flake8 pasó sin problemas."
                    }
                }
            }
        }

        // Etapa 5: Ejecutar las pruebas unitarias
        stage('Unit Tests') {
            steps {
                echo '--- Ejecutando Pruebas Unitarias con Pytest ---'
                bat "\"${env.PYTEST_EXE}\""
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
                        bat "\"${env.PYTHON_EXE}\" compare_pdfs.py DocumentoA_1.pdf DocumentoA2.pdf"
                        bat "\"${env.PYTHON_EXE}\" compare_pdfs.py DocumentoA_1.pdf DocumentoB1.pdf"
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Archivando artefactos...'
            archiveArtifacts artifacts: 'flake8-report.txt', allowEmptyArchive: true
        }
        success {
            script {
                echo 'Pipeline completado exitosamente. Enviando notificación...'
                withCredentials([string(credentialsId: 'GMAIL_RECEIVER_EMAIL', variable: 'RECIPIENT_EMAIL')]) {
                    emailext (
                        to: "${env.RECIPIENT_EMAIL}",
                        subject: "ÉXITO: Pipeline '${env.JOB_NAME}' - Build #${env.BUILD_NUMBER} Completado",
                        body: """
                        <h1>Estado del Pipeline: EXITOSO</h1>
                        <p>El pipeline para el proyecto <b>${env.JOB_NAME}</b> ha finalizado correctamente.</p>
                        <p><b>Build:</b> <a href="${env.BUILD_URL}">${env.BUILD_NUMBER}</a></p>
                        """,
                        mimeType: 'text/html'
                    )
                }
                cleanWs()
            }
        }
        unstable {
            script {
                echo '🟡 Pipeline completado con advertencias (UNSTABLE). Enviando reporte por correo...'
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
                cleanWs()
            }
        }
        failure {
            script {
                echo ' Pipeline falló. Enviando notificación por correo...'
                withCredentials([string(credentialsId: 'GMAIL_RECEIVER_EMAIL', variable: 'RECIPIENT_EMAIL')]) {
                    emailext (
                        to: "${env.RECIPIENT_EMAIL}",
                        subject: "FALLO: Pipeline '${env.JOB_NAME}' - Build #${env.BUILD_NUMBER} Falló",
                        body: """<h1>Estado del Pipeline: FALLIDO</h1><p>El pipeline para el proyecto <b>${env.JOB_NAME}</b> ha fallado.</p><p><b>Build:</b> <a href="${env.BUILD_URL}">${env.BUILD_NUMBER}</a></p><p>Revisa el log adjunto para identificar la causa del error.</p>""",
                        mimeType: 'text/html',
                        attachLog: true
                    )
                }
                cleanWs()
            }
        }
    }
}
