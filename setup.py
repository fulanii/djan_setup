from setuptools import setup, find_packages

setup(
    name='django_boilerplate',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'rich',
        'black',
        'astor',
    ],
    entry_points={
        'console_scripts': [
            'django_boilerplate=script:main',
        ],
    },
    author='Yassine',
    author_email='yassine@yassinecodes.dev',
    description='A cli tool to setup django for you',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/django_boilerplate',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)