from setuptools import setup, find_packages

setup(
    name="swasthyavani",
    version="0.1.0",
    package_dir={"": "."},  # Crucial for root-level packages
    packages=find_packages(where=".", exclude=["tests*", "scripts*"]),
    install_requires=[
        line.strip() for line in open("requirements.txt") 
        if line.strip() and not line.startswith("#")
    ],
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],  # Root level files
        "pipeline": ["triage/*", "triage/helpers/*", "triage/prompts/*"],
        "config": ["*.py"],
        "chathistory": ["*.json"],
    },
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'swasthyavani=app:main',  # If app.py has main()
        ],
    }
)
