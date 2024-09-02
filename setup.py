from setuptools import setup, find_packages

setup(
    name="syslog_manager",
    version="1.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "attrs==24.2.0",
        "colorama==0.4.6",
        "coverage==7.6.1",
        "iniconfig==2.0.0",
        "jsonschema==4.23.0",
        "jsonschema-specifications==2023.12.1",
        "mirakuru==2.5.2",
        "packaging==24.1",
        "pluggy==1.5.0",
        "port-for==0.7.2",
        "psutil==6.0.0",
        "psycopg2==2.9.9",
        "pytest==8.3.2",
        "pytest-mock==3.14.0",
        "referencing==0.35.1",
        "rpds-py==0.20.0",
    ],
    entry_points={
        'console_scripts': [
            'syslog_manager = main:main',
        ],
    },
)
