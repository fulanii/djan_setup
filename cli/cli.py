import os
import sys
import subprocess
import astor
import ast
try:
    # For when running as part of the package
    from .console import console
except ImportError:
    # For when running directly
    from console import console


class Cli:
    def __init__(self, project_name, app_name):
        self.django_project_name = project_name
        self.django_app_name = app_name
        self.project_root = os.path.join(os.getcwd(), self.django_project_name)
        self.project_configs = os.path.join(self.project_root, self.django_project_name)
        self.settings_folder = os.path.join(self.project_configs, "settings")
        self.settings_file = os.path.join(self.settings_folder, "settings.py") 
    
    def _create_project(self) -> bool:
        """ 
        Create a new Django project, return True if successful, False otherwise. 
        Project already exists if project already exists. 
        """
        
        # check if a project already exists
        if not os.path.exists(self.project_root):
            try:
                import django
            except ImportError:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "django"], check=True) 
            try:
                subprocess.run(["django-admin", "startproject", self.django_project_name], check=True)
                return True
            except Exception as e:
                print(f"An error occurred while creating the Django project. {e}")
                return False
        else:
            return "Project already exists."
    
    def _create_app(self) -> bool:
        """ Create a new Django app, return True if successful, False otherwise. """
        try:
            os.chdir(self.project_root) 
            subprocess.run([sys.executable, os.path.join(self.project_root, "manage.py"), "startapp", self.django_app_name], check=True)
            return True
        except Exception as e:
            print("An error occurred while creating the Django app." + str(e))
            return False
    
    def _create_project_util_files(self) -> None:
        """ 
        Creates: 
            .gitignore,
            requirements.txt, 
            README.md,
            .env.dev,
            .env.prod,
        """
        os.chdir(self.project_root)
        try:
            with open(".gitignore", "w") as file:
                file.write("*.pyc\n")
                file.write("__pycache__/\n")
                file.write("*.sqlite3\n")
                file.write("db.sqlite3\n")
                file.write("env\n")
                file.write(".env.dev\n")
                file.write(".env.prod\n")
                file.write(".vscode\n")
                file.write(".idea\n")
                file.write("*.DS_Store\n")
            
            open("requirements.txt", "a").close()
            open("README.md", "a").close()
            open(".env.dev", "a").close()
            open(".env.prod", "a").close()
        except FileExistsError as e:
            print(f"An error occurred while creating the project utility files. {e}")

    def _create_settings(self) -> None:
        """
        Creates a settings folder of the Django project.
        settings/base.py: Base settings
        settings/develoment.py: Development settings
        settings/production.py: Production settings

        returns: None
        """

        # cd into project folder
        os.chdir(self.project_configs)

        # create folder called settings
        os.makedirs("settings", exist_ok=True)

        # move settings.py into new settings folder and rename it to base.py
        os.rename(self.settings_file, os.path.join(self.project_configs, "settings", "base.py"))

        # move into new folder
        os.chdir(self.settings_folder)

        try:
            open("__init__.py", "a").close()
            open("development.py", "a").close()
            open("production.py", "a").close()
        except FileExistsError as e:
            print(F"An error occurred while creating the settings folder. {e}")

        console.print("Settings folder and files created successfully! ✅", style="bold on blue")

    def _update_base_setting(self) -> None:
        """
        Fill the base settings file with the necessary configurations.
        returns: None
        """

        # cd into project settings  folder
        os.chdir(self.settings_folder)

        # open base.py file
        with open("base.py", "r") as file:
            tree = ast.parse(file.read())            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    if node.targets[0].id == "INSTALLED_APPS":
                        node.value.elts.append(ast.Constant(s=self.django_app_name))

                    if node.targets[0].id == "ALLOWED_HOSTS":
                        node.value.elts.append(ast.Constant(s="*"))

                    if node.targets[0].id == "BASE_DIR":
                        node.value = ast.Call(
                            func=ast.Attribute(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id="Path", ctx=ast.Load()),
                                        attr="__file__",
                                        ctx=ast.Load()
                                    ),
                                    args=[],
                                    keywords=[]
                                ),
                                attr="resolve",
                                ctx=ast.Load()
                            ),
                            args=[],
                            keywords=[]
                        )
                        # Add `.parent.parent.parent` to the call
                        node.value = ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Attribute(value=node.value, attr="parent", ctx=ast.Load()),
                                attr="parent",
                                ctx=ast.Load()
                            ),
                            attr="parent",
                            ctx=ast.Load()
                        )

        # write the changes to the file, with indentation and spaces
        with open("base.py", "w") as file:
            file.write(astor.to_source(tree))

        # run black to format the code on base.py
        subprocess.run(["black", "base.py"], check=True)

    def _update_dev_setting(self) -> None:
        """
        Fill the development settings file with the necessary configurations.
        returns: None
        """

        # cd into project settings folder
        os.chdir(self.settings_folder)

        # open development.py file
        with open("development.py", "w") as file:
            file.write("from .base import *")

    def _update_dev_setting(self) -> None:
        """
        Fill the production settings file with the necessary configurations.
        returns: None
        """

        # cd into project settings folder
        os.chdir(self.settings_folder)

        # open development.py file
        with open("production.py", "w") as file:
            file.write("from .base import *\n")
            file.write("import os\n\n")
            file.write("DEBUG = False\n")
            file.write("SECRET_KEY = os.environ.get('SECRET_KEY')\n")
            file.write("ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')\n")
            file.write("DATABASES = {} # Add your production database settings here\n")


    def entry(self):
        """ Main method that creates a Django project and app. """
        
        self._create_project()
        self._create_app()
        # console.print("Django project and app created successfully! ✅", style="bold on blue")
        # self._create_settings()
        # console.print("Settings folder created successfully! ✅", style="bold on blue")
        # self._update_base_setting()
        # console.print("Updated settings/base.py successfully! ✅", style="bold on blue")
        # self._update_dev_setting()
        # console.print("Updated settings/development.py successfully! ✅", style="bold on blue")
        # self._create_project_util_files()
        # console.print("Updated settings/production.py successfully! ✅", style="bold on blue")
        