from setuptools import setup, find_packages

setup(
    name="references-manager-phd",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'google-api-python-client==2.88.0',
        'google-auth-httplib2==0.1.0',
        'google-auth-oauthlib==1.0.0',
        'PyGithub==1.58.2',
        'pandas==2.0.3',
        'requests==2.31.0',
        'python-dotenv==1.0.0',
        'bibtexparser==1.4.0',
        'watchdog==3.0.0',
        'click==8.1.3',
        'rich==13.4.2',
        'pathlib==1.0.1',
    ],
    author="Yassine",
    author_email="y.ait mohamed@yahoo.com",
    description="Gestionnaire de références PhD avec accès Google Drive, GitHub et fichiers locaux",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yassine-ait-mohamed/references-manager-phd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'refs=src.main:cli',
        ],
    },
)