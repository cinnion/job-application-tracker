pipeline {
    agent any
    environment {
        BUILD_DATE_TIME = "${sh(script: 'date +%Y-%m-%d\\ %H:%M:%S\\ %Z', returnStdout: true).trim()}"
        REGISTRY = 'registry.ka8zrt.com:5000'
        TAG = "${env.BUILD_ID}"
        DOCKER_NODE = "docker"
    }
    stages {
        stage('Get Tag Name') {
            steps {
                script {
                    def gitTag = sh(script: 'git tag --points-at HEAD', returnStdout: true).trim()

                    if (gitTag) {
                        env.GIT_TAG = gitTag
                        echo "Found Git tag: ${env.GIT_TAG}"
                    } else {
                        env.GIT_TAG = "None"
                        echo "No Git tag found on current commit. Defaulting to ${env.GIT_TAG}"
                    }
                }
            }
        }
        stage('Generate Build Info JSON') {
            steps {
                script {
                    // Define a Groovy map with the build information
                    def buildInfo = [
                        'BUILD_NUMBER': env.BUILD_NUMBER,
                        'BUILD_ID': env.BUILD_ID,
                        'JOB_NAME': env.JOB_NAME,
                        'BUILD_URL': env.BUILD_URL,
                        'GIT_COMMIT': env.GIT_COMMIT,
                        'GIT_BRANCH': env.GIT_BRANCH,
                        'GIT_TAG': env.GIT_TAG,
                        'BUILD_DATE': env.BUILD_DATE_TIME,
                    ]

                    // Convert the Groovy map to a JSON formatted string
                    def jsonString = groovy.json.JsonOutput.prettyPrint(groovy.json.JsonOutput.toJson(buildInfo))

                    // Write the JSON string to a file named 'build_info.json' in the workspace
                    writeFile(file: 'build_info.json', text: jsonString)
                }
            }
        }

        stage('Resolve docker-compose file') {
            steps {
                script {
                    // Read the docker-compose-prod file
                    def template = readFile 'docker-compose-prod.yml'

                    // Replace the variables for interior production
                    def resolvedContentInternal = template.replaceAll(/\$\{REGISTRY\}/, env.REGISTRY)
                                                  .replaceAll(/\$\{TAG\}/, env.TAG)
                                                  .replaceAll(/\$\{DOCKER_NODE\}/, 'docker')

                    // Write the resolved content to a new file for interior production
                    writeFile(file: 'unemployment-docker.yml', text: resolvedContentInternal)

                    // Replace the variables for exterior production
                    def resolvedContentExternal = template.replaceAll(/\$\{REGISTRY\}/, env.REGISTRY)
                                                  .replaceAll(/\$\{TAG\}/, env.TAG)
                                                  .replaceAll(/\$\{DOCKER_NODE\}/, 'beta')

                    // Write the resolved content to a new file for exterior production
                    writeFile(file: 'unemployment-beta.yml', text: resolvedContentExternal)
                }
            }
        }

        stage('Build') {
            steps {
                sh 'docker compose -f docker-compose-prod.yml -p unemployment build'
            }
        }

        stage('Push') {
            steps {
                sh "docker push ${REGISTRY}/unemployment-py-wsgi:${TAG}"
                sh "docker push ${REGISTRY}/unemployment-py-wsgi:latest"
                sh "docker push ${REGISTRY}/unemployment-web:${TAG}"
                sh "docker push ${REGISTRY}/unemployment-web:latest"
            }
        }

        stage('Deploy') {
            steps {
                sshagent(credentials: ['jenkins-ssh']) {
                    sh '''
                        scp -p unemployment-docker.yml root@docker:~/docker-compose/unemployment.yml
                        ssh root@docker 'docker stack deploy --detach -c ~/docker-compose/unemployment.yml unemployment'

                        scp -p unemployment-beta.yml root@beta:~/docker-compose/unemployment.yml
                        ssh root@beta 'docker stack deploy --detach -c ~/docker-compose/unemployment.yml unemployment'
                    '''
                }
            }
        }
    }
}
