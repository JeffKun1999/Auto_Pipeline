pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'PipelineAuto',
                    url: 'https://github.com/JeffKun1999/Auto_Pipeline.git'
            }
        }

        stage('Build') {
            steps {
                echo 'Compilando el proyecto...'
            }
        }

        stage('Deploy Simulation') {
            steps {
                echo 'Simulando despliegue exitoso!'
            }
        }
    }
}
