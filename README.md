# TAAS

This project is built using Django, Django Rest Framework (DRF), and Docker Compose.

## Platform for ticket management

This project aims to [describe what your project does or its purpose].

## Setup Instructions

To run this project locally, you need to have Docker and Docker Compose installed on your machine.

1. Navigate to the project directory:
 ```bash
 git clone [<repository_url>](https://github.com/aakashjsr/taas_public.git)
 cd <project_directory>
 ```

2. Create a .env file in the env_files directory with the following environment variables:
```dotenv
# Django settings
DEBUG=1
SECRET_KEY=<your_secret_key>

# PostgreSQL settings
POSTGRES_USER=taas
POSTGRES_PASSWORD=taas
POSTGRES_DB=taas
```
3. Build and start the Docker containers using Docker Compose:
 ```bash
docker-compose up --build
 ```





