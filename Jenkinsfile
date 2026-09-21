pipeline {
    agent {
        docker {
            image 'python:3.11'
        }
    }
    environment {
        TEST_DATABASE_URL = 'postgresql://palette:palette123@host.docker.internal:5432/palette_test'
    }
    stages {
        stage('Install') {
            steps {
                sh 'python -m venv .venv'
                sh '.venv/bin/pip install -r backend/requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'cd backend && ../.venv/bin/pytest tests/ --junitxml=report.xml'
            }
        }
    }
    post {
        always {
            junit 'backend/report.xml'
        }
    }
}
