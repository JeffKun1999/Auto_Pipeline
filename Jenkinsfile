// Jenkinsfile (Versión para Ejecución Nativa en Windows)
pipeline {
    // El agente 'any' ejecutará los pasos directamente en el nodo principal de Jenkins (tu máquina Windows)
    agent any

    stages {
        stage('Checkout Source Code') {
            steps {
                echo 'Clonando el repositorio...'
                // Este paso no cambia
                checkout scm
            }
        }

        stage('Build and Execute Python Script') {
            steps {
                // El bloque 'withCredentials' sigue siendo la forma segura de manejar secretos
                withCredentials([
                    string(credentialsId: 'EMAIL_HOST', variable: 'EMAIL_HOST'),
                    string(credentialsId: 'EMAIL_PORT', variable: 'EMAIL_PORT'),
                    string(credentialsId: 'EMAIL_HOST_USER', variable: 'EMAIL_HOST_USER'),
                    string(credentialsId: 'EMAIL_HOST_PASSWORD', variable: 'EMAIL_HOST_PASSWORD'),
                    string(credentialsId: 'RECIPIENT_EMAIL', variable: 'RECIPIENT_EMAIL')
                ]) {
                    // Usamos el paso 'bat' para ejecutar comandos de batch de Windows
                    bat '''
                        echo "--- Preparando Entorno de Python ---"
                        
                        REM Crea el entorno virtual
                        python -m venv .venv
                        
                        REM Activa el entorno virtual y luego instala las dependencias
                        call .venv\\Scripts\\activate.bat && pip install -r requirements.txt
                        
                        echo "--- Ejecutando Script de Python ---"
                        
                        REM Ejecuta el script. 'call' asegura que el flujo continúe.
                        call python compare_pdfs.py DocumentoA_1.pdf DocumentoA2.pdf
                    '''
                }
            }
        }
    }
    
    post {
        always {
            // La limpieza ahora funcionará sin problemas en el agente principal
            echo 'Limpiando el espacio de trabajo...'
            cleanWs()
        }
    }
}