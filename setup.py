from setuptools import setup, find_packages

setup(
    name="syslog_manager",
    version="2.0.0",
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
        "pycsvschema==0.0.6",
        "pytest==8.3.2",
        "pytest-mock==3.14.0",
        "referencing==0.35.1",
        "rfc3986==2.0.0",
        "rpds-py==0.20.0",
    ],
    entry_points={
        'console_scripts': [
            'syslog_manager = syslog_manager.main:main',
        ],
    },
)
