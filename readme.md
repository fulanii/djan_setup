# Django Setup 
A cli tool to setup django for you


## Features
* install django if not already installed
* creates django project
* creates django app 
* creates settings folder
* creates settings files: `base.py`, `developmemt.py`, `production.py`
* creates `.gitignore`, `.env.dev`, `.env,prod`, and `requirements.txt`
* updates `INSTALLED_APPS`, `DEBUG`, `ALLOWED_HOST` and `BASE_DIR`
* creates `app_name/urls.py`
* add `app_name/urls.py` to `project_name/urls.py` urlpatterns uisng `include()`
* update prod settings in prod file
* update django to use either env.dev or env.prod based on env var

## Usage

1. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. install the package
```bash
pip install djang-setup
```

3. run it and follow the prompt
```bash
djang-setup
```

![domo](./djang-setup-demo.gif)


## Support
* Star the project :)