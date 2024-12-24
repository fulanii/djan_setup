import os
from cli import Cli
import subprocess
from console import console



def main():
    subprocess.run(["clear"])
    console.rule("Welcome to the Django project creator!")

    project_name = console.input("Enter the [bold red]Django project[/] name: ")
    app_name = console.input("Enter the [bold red]Django app[/] name: ")

    django_cli = Cli(project_name, app_name)
    django_cli.main()


if __name__ == "__main__":
    main()


