node {
    def confUrl = 'https://vijaik.atlassian.net/wiki/rest/api/content/33141?expand=body.storage'
    def appName = 'RMI Platform'

    stage('Get Services Info') {
        checkout scm

        withCredentials([usernamePassword(credentialsId: 'CONFLUENCE', usernameVariable: 'CONFLUENCE_USERNAME', passwordVariable: 'CONFLUENCE_APITOKEN')]) {
            script {
                def serviceInfoCommand = """
                    python -m pip install -r requirements.txt --user
                    python service-getter.py -u $confUrl -a "$appName"
                    
                """
                
                // Capture the output of the Python script
                def scriptOutput = bat(script: serviceInfoCommand, returnStatus: true).trim()

                // Print the output
                echo "Python Script Output: ${scriptOutput}"
            }
        }
    }
}
