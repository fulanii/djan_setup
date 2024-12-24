import os
import sys
import subprocess
from console import console

class Cli:
    def __init__(self, project_name, app_name):
        self.django_project_name = project_name
        self.django_app_name = app_name
        self.project_path = os.path.join(os.getcwd(), self.django_project_name)
        self.project_exist = os.path.exists(self.project_path)
        self.project_folder = os.path.join(self.project_path, self.django_project_name)
        self.settings_folder = os.path.join(self.project_folder, "settings")
        self.settings_file = os.path.join(self.project_path, self.django_project_name, "settings.py") 
    
    def _create_project(self) -> bool:
        """ 
        Create a new Django project, return True if successful, False otherwise. 
        Project already exists if project already exists. 
        """

        # Check if the project already exists
        if not self.project_exist:
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

        if self._create_project() == True:
            try:
                os.chdir(self.project_path) 
                subprocess.run([sys.executable, os.path.join(self.project_path, "manage.py"), "startapp", self.django_app_name], check=True)
                return True
            except Exception as e:
                print("An error occurred while creating the Django app." + str(e))
                return False

    def _create_settings(self) -> None:
        """
        Creates a settings folder of the Django project.
        settings/base.py: Base settings
        settings/develoment.py: Development settings
        settings/production.py: Production settings

        returns: None
        """

        # cd into project folder
        os.chdir(self.project_folder)

        # create folder called settings
        os.makedirs("settings", exist_ok=True)

        # move settings.py into new settings folder and rename it to base.py
        os.rename(self.settings_file, os.path.join(self.project_folder, "settings", "base.py"))

        # move into new folder
        os.chdir(self.settings_folder)

        try:
            open("__init__.py", "a").close()
            open("development.py", "a").close()
            open("production.py", "a").close()
        except FileExistsError as e:
            print(F"An error occurred while creating the settings folder. {e}")

        console.print("Settings folder and files created successfully! ✅", style="bold on blue")

    def fill_settings(self) -> None:
        """
        Fill the settings files with the necessary configurations.
        returns: None
        """
        import astor
        import ast

        # cd into project settings  folder
        os.chdir(self.settings_folder)

        # open base.py file
        with open("base.py", "r") as file:
            tree = ast.parse(file.read())
            
            # print(astor.to_source(tree))
            
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





    def main(self):
        """ Main method that creates a Django project and app. """
        if self._create_app():
            console.print("Django project and app created successfully! ✅", style="bold on blue")
            self._create_settings()
            self.fill_settings()

