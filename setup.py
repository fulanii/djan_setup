from setuptools import setup, find_packages

setup(
    name='Django Project Setup Tool',
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
            'new_django=cli.script:main',
        ],
    },
    packages=find_packages(include=['cli', ]),
    author='Yassine',
    author_email='yassine@yassinecodes.dev',
    description='A CLI tool to set up Django projects for you',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
    url='',  # Add repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)