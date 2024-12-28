from setuptools import setup, find_packages

setup(
    name='djang-setup',
    version='0.0.6',
    include_package_data=True,
    install_requires=[
        "astor==0.8.1",
        "black==24.10.0",
        "click==8.1.8",
        "rich==13.9.4",
        "django-environ==0.11.2"
    ],
    entry_points={
        'console_scripts': [
            'djang-setup=cli.script:main',
        ],
    },
    packages=find_packages(include=['cli', 'cli.*']),
    author='Yassine',
    author_email='yassine@yassinecodes.dev',
    description='A CLI tool to set up Django projects for you',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fulanii/djnago_setup', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)