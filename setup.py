from setuptools import setup, find_packages

setup(
    name='github-reports',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'matplotlib',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'github-reports=github_reports.cli:main',
        ],
    },
    author='Your Name',
    description='CLI tool for GitHub project management charts',
    python_requires='>=3.7',
)
