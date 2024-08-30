from click import style
from invoke import task
from rich.console import Console
from rich.style import Style
from rich.panel import Panel
from rich.text import Text

console = Console()

# Define custom styles for different log levels
info_style = Style(color="cyan", bold=True)
warning_style = Style(color="yellow", bold=True)
error_style = Style(color="red", bold=True)
success_style = Style(color="green", bold=True)
debug_style = Style(color="magenta", bold=True)
highlight_style = Style(color="bright_magenta", bold=True)
background_style = Style(bgcolor="black", color="white")


def print_header(text, author="Diyarbek"):
    """Print a header panel with a custom label."""
    header_text = Text(text, style=highlight_style)
    author_text = Text(f" - by {author}", style="dim")
    console.print(Panel(header_text + author_text, style=highlight_style, title="Task", subtitle="Header", title_align="left", subtitle_align="right"))



@task()
def test(c):
    print_header("Running Tests")
    console.print("Running tests...", style=info_style)
    result = c.run('docker exec -i ustudy_test_task_web python manage.py test', warn=True)
    if result.failed:
        console.print("Tests failed. Aborting build.", style=error_style)
        raise Exception("Tests failed. Build aborted.")
    console.print("Tests passed.", style=success_style)


@task
def build(c):
    print_header("Building Docker Images")
    console.print("Building Docker images...", style=info_style)
    with console.status("[bold green]Building images..."):
        c.run('docker-compose build')
    console.print("Build completed.", style=success_style)


@task
def start(c):
    print_header("Starting Docker Containers")
    console.print("Starting Docker containers...", style=info_style)
    c.run('docker-compose up -d')
    console.print("Containers started.", style=success_style)


@task
def prepare(c):
    print_header("Preparing Application")
    console.print("Preparing the application...", style=info_style)
    with console.status("[bold green]Applying migrations..."):
        c.run('docker exec -i ustudy_test_task_web python manage.py makemigrations')
    console.print("Migrations created.", style=success_style)
    with console.status("[bold green]Applying migrations..."):
        c.run('docker exec -i ustudy_test_task_web python manage.py migrate')
    console.print("Migrations applied.", style=success_style)
    with console.status("[bold green]Collecting static files..."):
        c.run('docker exec -i ustudy_test_task_web python manage.py collectstatic --noinput')
    console.print("Static files collected.", style=success_style)
    console.print("Preparation completed.", style=success_style)


@task
def stop(c):
    print_header("Stopping Docker Containers")
    console.print("Stopping Docker containers...", style=info_style)
    c.run('docker-compose down')
    console.print("Containers stopped.", style=success_style)


@task
def restart(c):
    print_header("Restarting Docker Containers")
    console.print("Restarting Docker containers...", style=info_style)
    c.run('docker-compose down')
    c.run('docker-compose up -d')
    console.print("Containers restarted.", style=success_style)


@task
def remove(c):
    print_header("Removing Docker Containers")
    console.print("Removing Docker containers...", style=info_style)
    c.run('docker-compose down -v --remove-orphans')
    console.print("Containers removed.", style=success_style)


@task
def setup(c):
    print_header("Setting Up Application")
    console.print("Setting up the application...", style=info_style)
    build(c)
    start(c)
    prepare(c)
    console.print("Setup completed.", style=success_style)


@task(
    help={
        "container": "Names of the containers from which logs will be obtained."
                     " You can specify a single one, or several comma-separated names."
                     " Default: None (show logs for all containers)"
    },
)
def logs(c, tail=10, follow=True, container=None):
    """Obtain last logs of current environment."""
    print_header("Fetching Logs")
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
    print_header("Backing Up Database")
    console.print("Backing up the database...", style=info_style)
    backup_cmd = (
        'docker exec -i ustudy_test_task_db pg_dump -U postgres -d ustudy_task -F c -b -v -f /tmp/backup.sql'
    )
    result = c.run(backup_cmd, warn=True)
    if result.failed:
        console.print("Backup failed.", style=error_style)
        raise Exception("Backup failed.")

    # Copy the backup file from the Docker container to the local machine
    c.run('docker cp ustudy_test_task_db:/tmp/backup.sql ./backup.sql')

    console.print("Backup completed.", style=success_style)


@task
def restoredb(c):
    print_header("Restoring Database")
    console.print("Restoring the database...", style=info_style)
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

    console.print("Dropping the existing database...", style=info_style)
    drop_result = c.run(drop_cmd, warn=True)
    if drop_result.failed:
        console.print("Failed to drop the existing database.", style=error_style)
        raise Exception("Database drop failed.")

    console.print("Creating a new database...", style=info_style)
    create_result = c.run(create_cmd, warn=True)
    if create_result.failed:
        console.print("Failed to create a new database.", style=error_style)
        raise Exception("Database creation failed.")

    console.print("Restoring the database from the backup...", style=info_style)
    restore_result = c.run(restore_cmd, warn=True)
    if restore_result.failed:
        console.print("Restore failed.", style=error_style)
        raise Exception("Restore failed.")

    console.print("Restore completed.", style=success_style)


@task
def demodb(c):
    print_header("Loading Demo Data")
    console.print("Loading demo data...", style=info_style)
    c.run('docker exec -i ustudy_test_task_web python manage.py load_demo_data')
    console.print("Demo data loaded.", style=success_style)


@task
def cleardb(c):
    print_header("Clearing Database")
    console.print("Clearing the database...", style=info_style)
    c.run('docker exec -i ustudy_test_task_db psql -U postgres -c "DROP DATABASE IF EXISTS ustudy_task;"')
    c.run('docker exec -i ustudy_test_task_db psql -U postgres -c "CREATE DATABASE ustudy_task;"')
    c.run('docker exec -i ustudy_test_task_web python manage.py migrate')
    console.print("Database cleared.", style=success_style)


@task
def purge(c):
    print_header("Purging Environment")
    console.print("Purging the full environment...", style=info_style)
    stop(c)
    c.run('docker-compose down -v --remove-orphans --rmi all -t 1')
    console.print("Purge completed.", style=success_style)


@task
def webshell(c):
    print_header("Accessing Django Shell")
    console.print("Accessing the Django shell...", style=info_style)
    c.run('docker exec -i ustudy_test_task_web python manage.py shell')
    console.print("Django shell session ended.", style=success_style)
