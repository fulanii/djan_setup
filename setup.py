from setuptools import setup, find_packages

setup(
    name='django_setup',
    version='0.1.0',
    include_package_data=True,
    install_requires=[
        'click',
        'rich',
        'black',
        'astor',
    ],
    entry_points={
        'console_scripts': [
            'django_setup=cli.script:main',
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