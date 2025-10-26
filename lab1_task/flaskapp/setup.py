from setuptools import setup, find_packages

setup(
    name="flask-image-blender",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==2.3.3",
        "opencv-python-headless==4.8.1.78",
        "numpy==1.24.3",
        "matplotlib==3.7.2",
        "requests==2.31.0",
        "Pillow==10.0.0",
    ],
    author="Elena",
    author_email="perkova.ev@gmale.com",
    description="Flask application for image blending with CAPTCHA protection",
    keywords="flask image processing opencv",
    python_requires=">=3.8",
)
