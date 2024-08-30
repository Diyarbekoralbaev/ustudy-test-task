from invoke import task
from rich.console import Console

console = Console()


@task()
def test(c):
    console.print("Running tests...", style="bold yellow")
    result = c.run('docker exec -i ustudy_test_task_web python manage.py test', warn=True)
    if result.failed:
        console.print("Tests failed. Aborting build.", style="bold red")
        raise Exception("Tests failed. Build aborted.")
    console.print("Tests passed.", style="bold green")


@task
def build(c):
    console.print("Building Docker images...", style="bold yellow")
    c.run('docker-compose build')
    console.print("Build completed.", style="bold green")


@task
def start(c):
    console.print("Starting Docker containers...", style="bold yellow")
    c.run('docker-compose up -d')
    console.print("Containers started.", style="bold green")


@task
def prepare(c):
    console.print("Preparing the application...", style="bold yellow")
    with console.status("[bold green]Applying migrations..."):
        c.run('docker exec -i ustudy_test_task_web python manage.py makemigrations')
    console.print("Migrations created.", style="bold green")
    with console.status("[bold green]Applying migrations..."):
        c.run('docker exec -i ustudy_test_task_web python manage.py migrate')
    console.print("Migrations applied.", style="bold green")
    with console.status("[bold green]Collecting static files..."):
        c.run('docker exec -i ustudy_test_task_web python manage.py collectstatic --noinput')
    console.print("Static files collected.", style="bold green")
    console.print("Preparation completed.", style="bold green")


@task
def stop(c):
    console.print("Stopping Docker containers...", style="bold yellow")
    c.run('docker-compose down')
    console.print("Containers stopped.", style="bold green")


@task
def restart(c):
    console.print("Restarting Docker containers...", style="bold yellow")
    c.run('docker-compose down')
    c.run('docker-compose up -d')
    console.print("Containers restarted.", style="bold green")


@task
def remove(c):
    console.print("Removing Docker containers...", style="bold yellow")
    c.run('docker-compose down -v --remove-orphans')
    console.print("Containers removed.", style="bold green")


@task
def setup(c):
    console.print("Setting up the application...", style="bold yellow")
    build(c)
    start(c)
    prepare(c)
    console.print("Setup completed.", style="bold green")


@task(
    help={
        "container": "Names of the containers from which logs will be obtained."
                     " You can specify a single one, or several comma-separated names."
                     " Default: None (show logs for all containers)"
    },
)
def logs(c, tail=10, follow=True, container=None):
    """Obtain last logs of current environment."""
    cmd = "docker-compose logs"
    if follow:
        cmd += " -f"
    if tail:
        cmd += f" --tail {tail}"
    if container:
        cmd += f" {container.replace(',', ' ')}"
    c.run(cmd, pty=True)


@task
def backupdb(c):
    console.print("Backing up the database...", style="bold yellow")
    backup_cmd = (
        'docker exec -i ustudy_test_task_db pg_dump -U postgres -d ustudy_task -F c -b -v -f /tmp/backup.sql'
    )
    result = c.run(backup_cmd, warn=True)
    if result.failed:
        console.print("Backup failed.", style="bold red")
        raise Exception("Backup failed.")

    # Copy the backup file from the Docker container to the local machine
    c.run('docker cp ustudy_test_task_db:/tmp/backup.sql ./backup.sql')

    console.print("Backup completed.", style="bold green")


@task
def restoredb(c):
    console.print("Restoring the database...", style="bold yellow")
    drop_cmd = (
        'docker exec -i ustudy_test_task_db psql -U postgres -c "DROP DATABASE IF EXISTS ustudy_task;"'
    )
    create_cmd = (
        'docker exec -i ustudy_test_task_db psql -U postgres -c "CREATE DATABASE ustudy_task;"'
    )
    restore_cmd = (
        'docker exec -i ustudy_test_task_db pg_restore -U postgres -d ustudy_task /tmp/backup.sql'
    )

    # Copy the backup file from the local machine to the Docker container
    c.run('docker cp ./backup.sql ustudy_test_task_db:/tmp/backup.sql')

    console.print("Dropping the existing database...", style="bold yellow")
    drop_result = c.run(drop_cmd, warn=True)
    if drop_result.failed:
        console.print("Failed to drop the existing database.", style="bold red")
        raise Exception("Database drop failed.")

    console.print("Creating a new database...", style="bold yellow")
    create_result = c.run(create_cmd, warn=True)
    if create_result.failed:
        console.print("Failed to create a new database.", style="bold red")
        raise Exception("Database creation failed.")

    console.print("Restoring the database from the backup...", style="bold yellow")
    restore_result = c.run(restore_cmd, warn=True)
    if restore_result.failed:
        console.print("Restore failed.", style="bold red")
        raise Exception("Restore failed.")

    console.print("Restore completed.", style="bold green")


@task
def demodb(c):
    console.print("Loading demo data...", style="bold yellow")
    c.run('docker exec -i ustudy_test_task_web python manage.py load_demo_data')
    console.print("Demo data loaded.", style="bold green")


@task
def cleardb(c):
    console.print("Clearing the database...", style="bold yellow")
    c.run('docker exec -i ustudy_test_task_db psql -U postgres -c "DROP DATABASE IF EXISTS ustudy_task;"')
    c.run('docker exec -i ustudy_test_task_db psql -U postgres -c "CREATE DATABASE ustudy_task;"')
    c.run('docker exec -i ustudy_test_task_web python manage.py migrate')
    console.print("Database cleared.", style="bold green")


@task
def purge(c):
    console.print("Purging the full environment...", style="bold yellow")
    stop(c)
    c.run('docker-compose down -v --remove-orphans --rmi all -t 1')
    console.print("Purge completed.", style="bold green")


@task
def webshell(c):
    console.print("Accessing the Django shell...", style="bold yellow")
    c.run('docker exec -i ustudy_test_task_web python manage.py shell')
    console.print("Django shell session ended.", style="bold green")
