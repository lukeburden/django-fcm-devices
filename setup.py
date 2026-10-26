from setuptools import find_packages, setup


name = "django-fcm-devices"
description = (
    "Minimalistic device registration and push notifications with FCM and Django"
)
author = "Luke Burden"
author_email = "lukeburden@gmail.com"
url = "https://github.com/lukeburden/django-fcm-devices"

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "django>=3.2,<6",
    "pyfcm>=2.0.8,<3",
    "django-konst>=3,<4",
    "google-auth>=2.22.0",  # for loading credentials.
]

tests_require = [
    "pytest>=7",
    "pytest-django>=4.5",
    "pytest-mock>=3",
    "model_bakery>=1.3.3",
]

setup(
    name=name,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="2.0.0",
    license="MIT",
    url=url,
    packages=find_packages(exclude=["tests", "testproj"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.2",
    ],
    python_requires=">=3.10",
    install_requires=install_requires,
    test_suite="runtests.runtests",
    tests_require=tests_require,
    zip_safe=False,
)
