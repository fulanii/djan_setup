# Django Boilerplate
A cli tool to setup django for you


## Features
* install django if not already installed
* creates django project
* creates django app 
* creates settings folder
* creates settings files: `base.py`, `developmemt.py`, `production.py`
* creates `.gitignore`, `.env.dev`, `.env,prod`, and `requirements.txt`
* updates `INSTALLED_APPS`, `DEBUG`, `ALLOWED_HOST` and `BASE_DIR`


## To add 
* creates app_name/urls.py
* add app_name/urls.py to project_name/urls.py urlpatterns uisng `include()`
* update prod settings in prod file
* update django to use either env.dev or env.prod based on env var