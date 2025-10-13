// Jenkinsfile
pipeline {
    // Definimos el agente que ejecutará el pipeline.
    // Usar Docker es una práctica moderna que asegura un entorno limpio y consistente.
    agent {
        docker { image 'python:3.9-slim' }
        args '-w /app'
    }

    stages {
        // ETAPA 1: Clonar el código desde el repositorio de GitHub
        stage('Checkout') {
            steps {
                echo 'Clonando el repositorio...'
                // 'checkout scm' es un comando especial de Jenkins que clona el repo
                // configurado en el trabajo.
                checkout scm
            }
        }

        // ETAPA 2: Preparar el entorno y dependencias (Build)
        stage('Build') {
            steps {
                echo 'Creando entorno virtual e instalando dependencias...'
                // 'sh' ejecuta comandos de shell dentro del contenedor Docker
                sh '''
                    python -m venv .venv
                    source .venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
        
        // ETAPA 3: Ejecutar el script de comparación (Execute)
        stage('Execute Comparison') {
            steps {
                // El bloque withCredentials inyecta de forma segura las credenciales de Jenkins
                // como variables de entorno, que nuestro script de Python leerá.
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
        // Este bloque se ejecuta siempre al final, sin importar si el pipeline falló o tuvo éxito.
        always {
            echo 'Limpiando el espacio de trabajo...'
            // cleanWs() es una función de Jenkins que borra los archivos del workspace.
            cleanWs()
        }
    }
}