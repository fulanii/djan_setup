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
        self.settings_file = os.path.join(self.project_configs, "settings.py") 
    
    def _create_project(self) -> bool:
        """ 
        Create a new Django project, 
        return True if successful, False otherwise. 
        """
        
        # check if a project already exists
        if not os.path.exists(self.project_root):
            try:
                import django
            except ImportError:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "django"], check=True) 
            try:
                subprocess.run(["django-admin", "startproject", self.django_project_name], check=True)
                console.print(f"Django project '{self.django_project_name}' created successfully! ✅", style="bold on blue")
                return True
            except Exception as e:
                # console.print(f"An error occurred while creating '{self.django_project_name}'. {e} ❌", style="bold red") # for debugging
                return False
        else:
            console.print(f"Django project already exists. ❌", style="bold red")
            return False
    
    def _create_app(self) -> bool:
        """ Create a new Django app, return True if successful, False otherwise. """
        try:
            os.chdir(self.project_root) 
            subprocess.run([sys.executable, os.path.join(self.project_root, "manage.py"), "startapp", self.django_app_name], check=True)
            console.print(f"Django app '{self.django_app_name}' created successfully! ✅", style="bold on blue")
            return True
        except Exception as e:
            # print("An error occurred while creating the Django app." + str(e)) # for debugging
            return False 
    
    def _create_project_util_files(self) -> bool:
        """ 
        Creates: 
            .gitignore,
            requirements.txt, 
            README.md,
            .env.dev,
            .env.prod,

        returns: True if successful, False otherwise.
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
            console.print("Created requirements.txt, Readme, and .env files successfully! ✅", style="bold on blue")
            return True
        except FileExistsError as e:
            # print(f"An error occurred while creating the project utility files. {e}") # for debugging
            return False
        
    def _create_settings(self) -> bool:
        """
        Creates a settings folder of the Django project.
        settings/base.py: Base settings
        settings/develoment.py: Development settings
        settings/production.py: Production settings

        returns: True if successful, False otherwise.
        """

        # cd into project folder
        os.chdir(self.project_configs)

        # create folder called settings
        os.makedirs("settings", exist_ok=True)
   
        # move into new folder
        os.chdir(self.settings_folder)

        # move settings.py into new settings folder and rename it to base.py
        os.rename(self.settings_file, os.path.join(self.settings_folder, "base.py"))   
        
        try:
            open("__init__.py", "a").close()
            open("development.py", "a").close()
            open("production.py", "a").close()

            console.print(f"Django project '{self.django_project_name}' Settings folder and files created successfully! ✅", style="bold on blue")
            return True
        except FileExistsError as e:
            # print(F"An error occurred while creating the settings folder. {e}") # for debugging
            return False

    def _update_base_setting(self) -> bool:
        """
        Fill the base settings file with the necessary configurations.
        returns: True if successful, False otherwise.
        """
        try:
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
            console.print(f"Updated settings/base.py successfully! ✅", style="bold on blue")
            return True
        except Exception as e:
            # print(f"An error occurred while updating the base settings file. {e}") # for debugging
            return False

    def _update_dev_setting(self) -> bool:
        """
        Fill the development settings file with the necessary configurations.
        returns: True if successful, False otherwise.
        """
        try:
            # cd into project settings folder
            os.chdir(self.settings_folder)

            # open development.py file
            with open("development.py", "w") as file:
                file.write("from .base import *")

            console.print(f"Updated settings/development.py successfully! ✅", style="bold on blue")
            return True
        except Exception as e:
            # print(f"An error occurred while updating the development settings file. {e}") # for debugging
            return False
        
    def _update_prod_setting(self) -> bool:
        """
        Fill the production settings file with the necessary configurations.
        returns: True if successful, False otherwise.
        """

        try:
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
            
            console.print(f"Updated settings/production.py successfully! ✅", style="bold on blue")
            return True
        except Exception as e:
            # print(f"An error occurred while updating the production settings file. {e}") # for debugging
            return False
        
    def run_setup(self):
        """ Main method that creates a Django project and app. """
        steps = [
            (self._create_project),
            (self._create_app),
            (self._create_settings),
            (self._update_base_setting),
            (self._update_dev_setting),
            (self._update_prod_setting),
            (self._create_project_util_files),
        ]
        
        for step in steps:
            result = step() 
            if not result:
                break
