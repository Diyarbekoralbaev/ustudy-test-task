from datetime import datetime
import time
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
footer_style = Style(color="blue", bold=True)
highlight_style = Style(color="bright_magenta", bold=True)
background_style = Style(bgcolor="black", color="white")

task_start_time = None


def print_header(text, author="Diyarbek"):
    """Print a header panel with a custom label."""
    global task_start_time
    task_start_time = datetime.now()
    header_text = Text(text, style=highlight_style)
    author_text = Text(f" - by {author}", style="dim")
    console.print(
        Panel(header_text + author_text, style=highlight_style, title="Task", subtitle="by Diyarbek", title_align="left",
              subtitle_align="right"))


def print_footer(text):
    """Print a footer panel with a custom label, timestamp, and task duration."""
    global task_start_time
    end_time = datetime.now()
    timestamp = end_time.strftime("%Y-%m-%d %H:%M:%S")

    if task_start_time:
        duration = end_time - task_start_time
        duration_str = str(duration).split('.')[0]  # Remove microseconds
    else:
        duration_str = "Unknown"

    footer_text = Text(text, style=footer_style)
    timestamp_text = Text(f" - Completed at: {timestamp}", style="dim")
    duration_text = Text(f" - Duration: {duration_str}", style="dim")

    console.print(Panel(
        footer_text + timestamp_text + "\n" + duration_text,
        style=footer_style,
        title="Task",
        subtitle="by Diyarbek",
        title_align="left",
        subtitle_align="right"
    ))

    # Reset the start time for the next task
    task_start_time = None


def wait_for_postgres(c, max_retries=5, delay=5):
    """Wait for PostgreSQL to be ready."""
    print_header("Waiting for PostgreSQL")
    retries = 0
    while retries < max_retries:
        try:
            # Try to connect to the database
            result = c.run('docker exec -i ustudy_test_task_db pg_isready -U postgres', hide=True, warn=True)
            if result.ok:
                console.print("PostgreSQL is ready!", style=success_style)
                return True
        except Exception as e:
            console.print(f"Error checking PostgreSQL: {str(e)}", style=warning_style)

        retries += 1
        console.print(f"PostgreSQL is not ready yet. Retrying in {delay} seconds...", style=info_style)
        time.sleep(delay)

    console.print("Max retries reached. PostgreSQL might not be ready.", style=error_style)
    return False

@task()
def test(c):
    print_header("Running Tests")
    console.print("Running tests...", style=info_style)
    result = c.run('docker exec -i ustudy_test_task_web python manage.py test', warn=True)
    if result.failed:
        console.print("Tests failed. Aborting build.", style=error_style)
        raise Exception("Tests failed. Build aborted.")
    print_footer("Tests completed.")


@task
def build(c):
    print_header("Building Docker Images")
    console.print("Building Docker images...", style=info_style)
    with console.status("[bold green]Building images..."):
        c.run('docker-compose build')
    print_footer("Build completed.")


@task
def start(c):
    print_header("Starting Docker Containers")
    console.print("Starting Docker containers...", style=info_style)
    c.run('docker-compose up -d')
    print_footer("Containers started.")


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
    print_footer("Application prepared.")


@task
def stop(c):
    print_header("Stopping Docker Containers")
    console.print("Stopping Docker containers...", style=info_style)
    c.run('docker-compose down')
    print_footer("Containers stopped.")


@task
def restart(c):
    print_header("Restarting Docker Containers")
    console.print("Restarting Docker containers...", style=info_style)
    c.run('docker-compose down')
    c.run('docker-compose up -d')
    print_footer("Containers restarted.")


@task
def remove(c):
    print_header("Removing Docker Containers")
    console.print("Removing Docker containers...", style=info_style)
    c.run('docker-compose down -v --remove-orphans')
    print_footer("Containers removed.")


@task
def setup(c):
    print_header("Setting Up Application")
    console.print("Setting up the application...", style=info_style)
    build(c)
    start(c)

    if not wait_for_postgres(c):
        console.print("Setup aborted: PostgreSQL is not ready", style=error_style)
        return

    prepare(c)
    print_footer("Application setup completed.")


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

    print_footer("Backup completed.")


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

    print_footer("Database restored.")


@task
def demodb(c):
    print_header("Loading Demo Data")
    console.print("Loading demo data...", style=info_style)
    c.run('docker exec -i ustudy_test_task_web python manage.py load_demo_data')
    print_footer("Demo data loaded.")


@task
def cleardb(c):
    print_header("Clearing Database")
    console.print("Clearing the database...", style=info_style)
    c.run('docker exec -i ustudy_test_task_db psql -U postgres -c "DROP DATABASE IF EXISTS ustudy_task;"')
    c.run('docker exec -i ustudy_test_task_db psql -U postgres -c "CREATE DATABASE ustudy_task;"')
    c.run('docker exec -i ustudy_test_task_web python manage.py migrate')
    print_footer("Database cleared.")


@task
def purge(c):
    print_header("Purging Environment")
    console.print("Purging the full environment...", style=info_style)
    stop(c)
    c.run('docker-compose down -v --remove-orphans --rmi all -t 1')
    print_footer("Project purged. All containers, networks, and volumes removed. Goodbye!")


@task
def webshell(c):
    print_header("Accessing Django Shell")
    console.print("Accessing the Django shell...", style=info_style)
    c.run('docker exec -i ustudy_test_task_web python manage.py shell')
