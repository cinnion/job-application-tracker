def buildBadge = addEmbeddableBadgeConfiguration(id: "buildBadge", subject: "Builds")
def testsBadge = addEmbeddableBadgeConfiguration(id: "testBadge", subject: "Tests/Coverage")

def RunBuild() {
    sh "docker compose -p job-application-tracker build"
}

def RunTests() {
    withCredentials([
        file(
            credentialsId: 'job-application-tracker-env',
            variable: 'credvar')
    ]) {
        sh 'rm -f .env'
        sh 'cp "\$credvar" .env'
        sh "docker compose -p job-application-tracker --profile testing build tester"
        sh "docker compose up tester"
    }
}

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
                    // Read the docker-compose file after cutting out the BUILD ONLY block
                    def template = sh(script: "sed '/#### BUILD ONLY START ####/,/#### BUILD ONLY END ####/d' < docker-compose.yml", returnStdout: true)

                    // Replace the variables for interior production
                    def resolvedContentInternal = template.replaceAll(/\$\{REGISTRY\}/, env.REGISTRY)
                                                  .replaceAll(/\$\{TAG\}/, env.TAG)
                                                  .replaceAll(/\$\{DOCKER_NODE\}/, 'docker')

                    // Write the resolved content to a new file for interior production
                    writeFile(file: 'job-application-tracker-docker.yml', text: resolvedContentInternal)

                    // Replace the variables for exterior production
                    def resolvedContentExternal = template.replaceAll(/\$\{REGISTRY\}/, env.REGISTRY)
                                                  .replaceAll(/\$\{TAG\}/, env.TAG)
                                                  .replaceAll(/\$\{DOCKER_NODE\}/, 'beta')

                    // Write the resolved content to a new file for exterior production
                    writeFile(file: 'job-application-tracker-beta.yml', text: resolvedContentExternal)
                }
            }
        }

        stage("Build and test in parallel") {
            parallel {
                stage("Build production") {
                    steps {
                        script {
                            buildBadge.setStatus("running")
                            try {
                                RunTests()
                                buildBadge.setStatus("passing")
                            } catch (Exception err) {
                                buildBadge.setStatus("Failing")
                                echo "Build failed: ${e.toString()}"
                                echo "Detailed message: ${e.getMessage()}"
                                error "Ending build"
                            }
                        }
                    }
                }

                stage("Test") {
                    steps {
                        script {
                            testsBadge.setStatus("running")
                            try {
                                RunBuild()
                            } catch (Exception err) {
                                testsBadge.setStatus("Failing")
                                echo "Tests failed: ${e.toString()}"
                                echo "Detailed message: ${e.getMessage()}"
                                error "Ending tests"
                            }
                        }
                    }
                }
            }
        }

        stage("Push coverage report") {
            steps {
                sshagent(credentials: ['jenkins-ssh']) {
                    sh '''
                           rsync -az --delete htmlcov/ root@beta:/var/www/coverage/job-application-tracker/
                           ssh root@beta 'chown -R apache:apache /var/www/coverage/job-application-tracker'
                       '''
                }
            }
            post {
                cleanup {
                    sh "sudo rm -rf htmlcov"
                }
            }
        }

        stage('Push') {
            steps {
                sh "docker push ${REGISTRY}/job-application-tracker-py-wsgi:${TAG}"
                sh "docker push ${REGISTRY}/job-application-tracker-py-wsgi:latest"
                sh "docker push ${REGISTRY}/job-application-tracker-web:${TAG}"
                sh "docker push ${REGISTRY}/job-application-tracker-web:latest"
            }
        }

        stage('Record Coverage') {
            steps {
                recordCoverage(
                    tools: [[parser: 'COBERTURA', pattern: 'coverage.xml']],
                    sourceCodeRetention: 'EVERY_BUILD', // Options: NEVER, LAST_BUILD, EVERY_BUILD
                    qualityGates: [
                        [threshold: 60.0, metric: 'LINE', baseline: 'PROJECT', criticality: 'UNSTABLE']  // Fails build if <60%
                    ]
                )
            }
            post {
                failure {
                    script {
                        testsBadge.setStatus("Failing")
                    }
                }
                unstable {
                    script {
                        testsBadge.setStatus("Unstable")
                    }
                }
                success {
                    script {
                        testsBadge.setStatus("Passing")
                    }
                }
            }
        } 


        stage('Deploy to internal') {
            when {
                not { branch 'main' }
            }
            steps {
                sshagent(credentials: ['jenkins-ssh']) {
                    sh '''
                           scp -p job-application-tracker-docker.yml root@docker:~/docker-compose/job-application-tracker.yml
                           ssh root@docker 'docker stack deploy --detach -c ~/docker-compose/job-application-tracker.yml job-application-tracker'
                       '''
                }
            }
        }


        stage('Deploy to production (beta)') {
            when {
                branch 'main'
            }
            steps {
                sshagent(credentials: ['jenkins-ssh']) {
                    sh '''
                        scp -p job-application-tracker-beta.yml root@beta:~/docker-compose/job-application-tracker.yml
                        ssh root@beta 'docker stack deploy --detach -c ~/docker-compose/job-application-tracker.yml job-application-tracker'
                    '''
                }
            }
        }

    }
}
// Local Variables:
// eval: (auto-fill-mode -1)
// End:
