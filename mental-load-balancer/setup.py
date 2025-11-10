from setuptools import setup, find_packages

setup(
    name="mental-load-balancer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'psutil>=5.9.0',
        'pyperclip>=1.8.0',
    ],
    extras_require={
        'gui': ['PyQt6>=6.0.0'],
        'keyboard': ['keyboard>=0.13.0'],
        'vscode': ['pywin32>=300;platform_system=="Windows"],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'mental-load-balancer=mental_load_balancer:main',
        ],
    },
    python_requires='>=3.8',
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to monitor and manage cognitive load with smart interventions",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/mental-load-balancer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
)
