# UStudy Test Task

This project for task management based on Django and Django REST Framework.

## Prerequisites

- Docker (https://docs.docker.com/get-docker/)
- Docker Compose (https://docs.docker.com/compose/install/)
- Python 3.x (for local development) (https://www.python.org/downloads/)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Diyarbekoralbaev/ustudy-test-task.git
   cd ustudy-test-task
   ```

2. Create a `.env` file in the project root with the following content:
   ```
   SECRET_KEY=diyarbed54861e74d7fe449d874a2c2bb499c1af321f8458a354256f72fcff3d4cf83
   DEBUG=True
   ALLOWED_HOSTS=*
   CORS_ALLOW_ALL_ORIGINS=True
   TIME_ZONE=Asia/Tashkent

   DB_HOST=ustudy_test_task_db
   DB_NAME=ustudy_task
   DB_USER=postgres
   DB_PASSWORD=02052005
   DB_PORT=5432

   ACCESS_TOKEN_LIFETIME=60
   REFRESH_TOKEN_LIFETIME=1440

   PROJECT_PORT=8000
   DEPLOYMENT_URL=http://localhost:8000
   ```

   Note: The `PROJECT_PORT` variable is used to specify the port on which the application will run locally.

3. Install the required Python packages:
   ```
   sudo apt install pipx && pipx install invoke && sudo pipx ensurepath && pipx runpip invoke install rich
   ```

## Usage

This project uses Invoke to manage tasks. Here are the available commands:

### Setup and Deployment

- `invoke setup`: Set up the application (build, start, and prepare)
- `invoke build`: Build Docker images
- `invoke start`: Start Docker containers
- `invoke stop`: Stop Docker containers
- `invoke restart`: Restart Docker containers
- `invoke remove`: Remove Docker containers
- `invoke purge`: Purge the full environment (stop containers, remove volumes, images, and orphans)

### Database Management

- `invoke prepare`: Prepare the application (apply migrations and collect static files)
- `invoke backupdb`: Backup the database
- `invoke restoredb`: Restore the database from a backup
- `invoke demodb`: Load demo data
- `invoke cleardb`: Clear the database

### Development and Debugging

- `invoke test`: Run tests
- `invoke logs [--tail=10] [--follow] [--container=<container_name>]`: Fetch logs from Docker containers
  - `--tail`: Number of lines to show from the end of the logs (default: 10)
  - `--follow`: Follow log output (default: True)
  - `--container`: Specify container(s) to fetch logs from (comma-separated for multiple)
- `invoke webshell`: Access the Django shell

To run a command, use:

```
invoke <command-name>
```

For example, to set up the application:

```
invoke setup
```

### Additional Useful Commands

- `invoke -l`: List all available tasks
- `invoke --help <task-name>`: Show help for a specific task

## Detailed Task Descriptions

### Setup and Deployment

- `setup`: This task runs `build`, `start`, and `prepare` in sequence to fully set up the application.
- `build`: Builds the Docker images defined in your docker-compose.yml file.
- `start`: Starts the Docker containers in detached mode.
- `stop`: Stops the running Docker containers.
- `restart`: Stops and then starts the Docker containers.
- `remove`: Removes the Docker containers, networks, and volumes.
- `purge`: Stops containers, removes containers, networks, volumes, and images created by docker-compose up.

### Database Management

- `prepare`: Runs database migrations, creates necessary database tables, and collects static files.
- `backupdb`: Creates a backup of the current database state.
- `restoredb`: Restores the database from the most recent backup.
- `demodb`: Loads demo data into the database for testing purposes.
- `cleardb`: Clears all data from the database and re-runs migrations.

### Development and Debugging

- `test`: Runs the project's test suite.
- `logs`: Displays the logs from the Docker containers. You can specify which container's logs to view and how many lines to display.
- `webshell`: Opens an interactive Django shell for debugging and development purposes.

## Development Workflow

For local development, you can use the following workflow:

1. Make your changes
2. Set up the environment: `invoke setup`
3. Run tests: `invoke test`
4. If tests pass, commit your changes

## Deployment

To deploy the application:

1. Set up the environment: `invoke setup`

The application will be available at `http://localhost:8000` (or the port specified in your .env file).

## Troubleshooting

If you encounter any issues:

1. Check the logs: `invoke logs`
2. Restart the containers: `invoke restart`
3. If problems persist, try purging the environment and setting up again: `invoke purge` followed by `invoke setup`

For more information on each command, you can use `invoke --help <command-name>`.

## Environment Variables

The `.env` file contains important configuration for the project. Here's a brief explanation of each variable:

- `SECRET_KEY`: Django secret key for cryptographic signing
- `DEBUG`: Set to True for development, False for production
- `ALLOWED_HOSTS`: Hosts/domain names that this Django site can serve
- `CORS_ALLOW_ALL_ORIGINS`: Allow all origins for CORS if set to True
- `TIME_ZONE`: The time zone for the application
- `DB_*`: Database connection details
- `ACCESS_TOKEN_LIFETIME`: Lifetime of access tokens in minutes
- `REFRESH_TOKEN_LIFETIME`: Lifetime of refresh tokens in minutes
- `PROJECT_PORT`: The port on which the application will run locally
- `DEPLOYMENT_URL`: The URL where the application is deployed

Make sure to adjust these variables according to your environment and requirements.
