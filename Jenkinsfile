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
                dir('backend') {
                    sh './venv/bin/pytest tests/ --junitxml=report.xml'
                }
            }
        }
    }
    post {
        always {
            junit 'backend/report.xml'
        }
    }
}
