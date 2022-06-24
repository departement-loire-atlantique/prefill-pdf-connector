#! /usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='prefill-pdf-connector',
    author='Julie LANIAU',
    author_email='julie.laniau@loire-atlantique.fr',
    url='https://gitlab.loire-atlantique.fr/developpement/publik/prefill-pdf-connector',
    packages=find_packages(where="prefill_pdf"),
    package_dir={"": "prefill_pdf"},
    include_package_data=True,
)