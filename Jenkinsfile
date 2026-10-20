pipeline {
    agent any
    environment {
        TEST_DATABASE_URL = 'postgresql://palette:palette123@host.docker.internal:5432/palette_test'
    }
    stages {
        stage('Install') {
            steps {
                dir('backend') {
                    sh 'python3 -m venv venv'
                    sh './venv/bin/pip install -r requirements.txt'
                }
            }
        }
        stage('Test') {
            steps {
                sh './backend/venv/bin/pytest --junitxml=report.xml'
            }
        }
    }
    post {
        always {
            junit 'report.xml'
        }
    }
}
