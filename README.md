# Granalys

Granalys is a Windows-compatible static code analysis software for Python, that executes software metrics on AST with the help of [Neo4j](https://neo4j.com/) graph database.

## Prerequisites
* Python 3.9.x
* Docker

## Installation

### For both the command-line tool and web application
    
* #### Run Neo4j 5.7.0 docker container
        docker run -p7687:7687 --name neo4j --env NEO4J_AUTH=neo4j/password  neo4j:5.7.0

* #### Setup Python virtual environment
    In the `granalys` root folder create a Python virtual environment and activate it:

        python -m venv ".venv"
        .\.venv\Scripts\activate.bat

    After activating the virtual environment, install the Python modules in requirements.txt, and setup the environment variables by running:

        pip install -r requirements.txt
        python setup.py

        

### For the web application

In addition to the previous steps, for the web application you'll also need to:

 * #### Run MongoDB 6.0 docker container (for the web application)
        docker run -p7687:7687 --name neo4j --env NEO4J_AUTH=neo4j/password  neo4j:5.7.0

* ### Install [ngrok](https://ngrok.com/download) to provide configure a public IP
    
    After installation execute the following command:

        ngrok http 5000

    Copy the public URL from the `Forwarding` field and [configure it as a webhook](#web-application) URL in your GitHub repository.

        Forwarding                    <example_public_url> -> http://localhost:5000       

## Usage
* ### Command-line Tool
    To start the command-line tool activate the previously created virtual environment and from the `granalys` directory run:

        python cmd/granalys_cmd.py

* ### GitHub integration with the Web Application

    * For automatic static analysis execution on a GitHub repository, create a webhook following the guide: https://docs.github.com/en/webhooks-and-events/webhooks/creating-webhooks

        * Set the `Payload URL` to the URL created in the [web installation steps](#for-the-web-application).

        * Set the `Content type` to  `application/json`.

        * Set a `Secret` ([guide](https://docs.github.com/en/webhooks-and-events/webhooks/securing-your-webhooks)) and append it to the `granalys/.env` file:

                SECRET_TOKEN = '<example_secret_token>'

    * In the `granalys/web/granalys_web.yml` configuration file set the `granalys.web.url` attribute to the URL created in the [web installation steps](#for-the-web-application), and set the `github.auth.token` attribute to your [Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

            granalys.web.url: <example_public_url>
            github.auth.token: <example_personal_access_token>

    * To start the web application activate the previously created virtual environment and from the `granalys` directory run:

            python web/app.py
