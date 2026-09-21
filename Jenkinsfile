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
                sh 'pip install -r backend/requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'cd backend && pytest tests/ --junitxml=report.xml'
            }
        }
    }
    post {
        always {
            junit 'backend/report.xml'
        }
    }
}
