pipeline {
    agent any

    environment {
        IMAGE_NAME = "adarshmali/fooderpbackend"
        IMAGE_TAG = "latest"
        DOCKER_USERNAME = 'adarshmali'
        DOCKER_PASSWORD = 'Adm@514040'
        DOCKER_HUB_USER = "adarshmali"
        REGISTRY = "${DOCKER_HUB_USER}/${IMAGE_NAME}"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('Login to Docker') {
            steps {
                script {
                    sh """
                    echo '${DOCKER_PASSWORD}' | docker login -u '${DOCKER_USERNAME}' --password-stdin
                    """
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}:${IMAGE_TAG}'
                sh 'docker push ${REGISTRY}:${IMAGE_TAG}'
            }
        }

        stage('Deploy on EC2') {
            steps {
                sh """
                    docker stop backend-container || true
                    docker rm backend-container || true
                    docker pull ${REGISTRY}:${IMAGE_TAG}
                    docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true
                    docker run -d -p 8000:8000 --name backend-container ${REGISTRY}:${IMAGE_TAG}

                """
            }
        }
    }

    post {
        always {
            sh 'docker logout'
        }
    }
}

