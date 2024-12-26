import os
import subprocess
try:
    # For when running as part of the package
    from .console import console
    from .cli import Cli
except ImportError:
    # For when running directly
    from console import console
    from cli import Cli

def main():
    subprocess.run(["clear"])
    console.rule("[bold red]Welcome to the Django project creator!")

    project_name = console.input("Enter the [bold red]Django project[/] name: ")
    app_name = console.input("Enter the [bold red]Django app[/] name: ")

    django_cli = Cli(project_name, app_name)
    django_cli.run_setup()


if __name__ == "__main__":
    main()