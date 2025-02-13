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
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "django"],
                    check=True,
                )
                
            try:
                subprocess.run(
                    ["django-admin", "startproject", self.django_project_name],
                    check=True,
                )
                console.print(
                    f"\nDjango project '{self.django_project_name}' created successfully! ✅",
                    style="bold on blue",
                )
                return True
            except Exception as e:
                return False
            
        else:
            console.print(f"\nDjango project already exists. ❌", style="bold red")
            return False

    def _create_app(self) -> bool:
        """Create a new Django app, return True if successful, False otherwise."""
        try:
            os.chdir(self.project_root)
            subprocess.run(
                [
                    sys.executable,
                    os.path.join(self.project_root, "manage.py"),
                    "startapp",
                    self.django_app_name,
                ],
                check=True,
            )
            console.print(
                f"\nDjango app '{self.django_app_name}' created successfully! ✅",
                style="bold on blue",
            )
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
            with open(".env.prod", "w") as file:
                file.write("DEBUG=False\n")
                file.write("ALLOWED_HOSTS='*' # Add your domains in production separated by commas\n")
                file.write("SECRET_KEY='' # generate and add new secret key using Django shell\n")

            console.print(
                "\nCreated requirements.txt, Readme, and .env files successfully! ✅",
                style="bold on blue",
            )
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

            console.print(
                f"\nDjango project '{self.django_project_name}' Settings folder and files created successfully! ✅",
                style="bold on blue",
            )
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
            new_code = """
env = environ.Env()
ENVIRONMENT = os.getenv('SETTING_FILE_PATH')

# Load environment-specific .env file
if ENVIRONMENT == 'project.settings.production':
    environ.Env.read_env('.env.prod')
elif ENVIRONMENT == "project.settings.development":
    environ.Env.read_env('.env.dev')
            """
            
            # cd into project settings  folder
            os.chdir(self.settings_folder)

            # open base.py file
            with open("base.py", "r") as file:
                tree = ast.parse(file.read())
                
                # Create a new import node
                os_import = ast.parse("import os").body[0]
                environ_impoort = ast.parse("import environ").body[0]

                # Find the last import statement
                last_import_index = -1
                for index, node in enumerate(tree.body):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        last_import_index = index

                # Insert the new import after the last import statement
                tree.body.insert(last_import_index + 1, os_import)
                tree.body.insert(last_import_index + 2, environ_impoort)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        if node.targets[0].id == "INSTALLED_APPS":
                            node.value.elts.append(ast.Constant(s=self.django_app_name))

                        if node.targets[0].id == "ALLOWED_HOSTS":
                            node.value.elts.append(ast.Constant(s="*"))

                        if node.targets[0].id == "BASE_DIR":
                            # Create the AST for Path(__file__).resolve().parent.parent.parent
                            node.value = ast.Call(
                                func=ast.Attribute(
                                    value=ast.Call(
                                        func=ast.Name(id="Path", ctx=ast.Load()),  # Path()
                                        args=[ast.Name(id="__file__", ctx=ast.Load())],  # __file__
                                        keywords=[],
                                    ),
                                    attr="resolve",  # resolve()
                                    ctx=ast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            )

                            # Add `.parent.parent.parent` to the result
                            node.value = ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Attribute(
                                        value=node.value, attr="parent", ctx=ast.Load()  # first parent
                                    ),
                                    attr="parent",  # second parent
                                    ctx=ast.Load(),
                                ),
                                attr="parent",  # third parent
                                ctx=ast.Load(),
                            )

                new_nodes = ast.parse(new_code).body
                for i, new_node in enumerate(new_nodes):
                    tree.body.insert(last_import_index + 3 + i, new_node)

                # Iterate over the AST nodes and add a blank line after assignments
                for index, node in enumerate(tree.body):
                    # Check if the node is an assignment (Store, Assignment or AugAssign)
                    if isinstance(node, ast.Assign):
                        # Insert a 'pass' node to simulate a blank line
                        tree.body.insert(index + 1, "\n")

            # write the changes to the file, with indentation and spaces
            with open("base.py", "w") as file:
                file.write(astor.to_source(tree))

            # run black to format the code on base.py
            subprocess.run(["black", "base.py"], check=True)
            console.print(
                f"\nUpdated settings/base.py successfully! ✅", style="bold on blue"
            )
            return True
        except Exception as e:
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

            console.print(
                f"\nUpdated settings/development.py successfully! ✅",
                style="bold on blue",
            )
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
                file.write("DEBUG = env('DEBUG')\n")
                file.write("SECRET_KEY = env('SECRET_KEY')\n")
                file.write(
                    "ALLOWED_HOSTS = env('ALLOWED_HOSTS').split(',')\n"
                )
                file.write(
                    "DATABASES = {} # Add your production database settings here\n"
                )

            console.print(
                f"\nUpdated settings/production.py successfully! ✅", style="bold on blue"
            )
            return True
        except Exception as e:
            # print(f"An error occurred while updating the production settings file. {e}") # for debugging
            return False

    def _create_app_urls_file(self) -> bool:
        """
        create a urls.py file in the app folder.
        returns: True if successful, False otherwise.
        """

        try:
            # cd into the app folder
            os.chdir(os.path.join(self.project_root, self.django_app_name))

            # create urls.py file
            open("urls.py", "w").close()

            console.print(
                f"\nCreated '{self.django_app_name}/urls.py' successfully! ✅",
                style="bold on blue",
            )
            return True
        except Exception as e:
            return False

    def _add_app_urls_to_project_urls(self) -> bool:
        """
        Add the app urls to the project urls file.
        returns: True if successful, False otherwise.
        """
        os.chdir(self.project_configs)

        try:
            with open("urls.py", "r") as file:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module == "django.urls":
                            # add the include function to the import statement, if it doesn't exist
                            if not any(alias.name == "include" for alias in node.names):
                                node.names.append(ast.alias(name="include", asname=None))

                for node in ast.walk(tree):
                    if not any(isinstance(node, ast.Assign) for node in ast.walk(tree)):
                        if isinstance(node, ast.Assign):
                            if node.targets[0].id == "urlpatterns":
                                node.value.elts.append(
                                    ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Name(id="path", ctx=ast.Load()),
                                            attr="include",
                                            ctx=ast.Load(),
                                        ),
                                        args=[
                                            ast.Constant(
                                                s=f"{self.django_app_name}.urls", kind=None
                                            )
                                        ],
                                        keywords=[],
                                    )
                                )

            with open("urls.py", "w") as file:
                file.write(astor.to_source(tree))

            subprocess.run(["black", "urls.py"], check=True)
            console.print(f"\nAdded app urls to project urls.py successfully! ✅", style="bold on blue")
            return True
        except Exception as e:
            return False
    
    def _update_settings_path(self):
        """
        Updates manage.py setting path
        return True if successful False otherwise
        """
        try:
            os.chdir(self.project_root)

            with open("manage.py", "r") as file:
                tree = ast.parse(file.read())
                
                # Check if "from django.conf import settings" is already imported
                import_already_exists = any(
                    isinstance(node, ast.ImportFrom)
                    and node.module == "django.conf"
                    and any(alias.name == "settings" for alias in node.names)
                    for node in tree.body
                )

                # if not import_already_exists:
                #     env_import = ast.parse("from django.conf import settings").body[0]
                #     last_import_index = -1
                #     for index, node in enumerate(tree.body):
                #         if isinstance(node, (ast.Import, ast.ImportFrom)):
                #             last_import_index = index

                #     # Insert the new import after the last import statement
                #     tree.body.insert(last_import_index + 1, env_import)

                # Find and update the `os.environ.setdefault` call
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "main":
                        for stmt in node.body:
                            if (
                                isinstance(stmt, ast.Expr)
                                and isinstance(stmt.value, ast.Call)
                                and isinstance(stmt.value.func, ast.Attribute)
                                and isinstance(stmt.value.func.value, ast.Attribute)
                                and isinstance(stmt.value.func.value.value, ast.Name)
                                and stmt.value.func.value.value.id == "os"
                                and stmt.value.func.value.attr == "environ"
                                and stmt.value.func.attr == "setdefault"
                            ):
                                # Update the second argument of the call
                                stmt.value.args[1] = ast.parse(
                                    'os.getenv("SETTING_FILE_PATH")'
                                ).body[0].value


            # write the changes to the file, with indentation and spaces
            with open("manage.py", "w") as file:
                file.write(astor.to_source(tree))

            subprocess.run(["black", "manage.py"], check=True)
            console.print(f"\nUpdated manage.py successfully! ✅", style="bold on blue")
            return True
        except Exception as e:
            return False

    def run_setup(self):
        """Main method that creates everything"""
        steps = [
            (self._create_project),
            (self._create_app),
            (self._create_settings),
            (self._update_base_setting),
            (self._update_dev_setting),
            (self._update_prod_setting),
            (self._create_project_util_files),
            (self._create_app_urls_file),
            (self._add_app_urls_to_project_urls),
            (self._update_settings_path),
        ]
        success = True

        for step in steps:
            result = step()
            if not result:
                success = False
                break
        
        if success:
            console.print(f"\nMake sure you set the env 'SETTING_FILE_PATH' to '{self.django_project_name}.settings.development' (for your development enviroment)\nor '{self.django_project_name}.settings.production' (for your production enviroment) before running the server.", style="bold white on yellow")
