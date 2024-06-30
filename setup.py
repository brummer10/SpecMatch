#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Distutils installer for specmatch
#----------------------------------------------------#


from distutils.core import setup, Extension


setup(
    name = "specmatch",
    version = "0.9",
    description = "Calculate an IR to match a spectrum",
    packages = ['specmatch'],
    scripts = ['scripts/specmatch'],
    package_data = {'specmatch': ['specmatch.glade']},
    data_files = [('share/applications', ['desktop/specmatch.desktop']),
                  ('share/mime/packages', ['desktop/specmatch.xml']),
                  ],
    install_requires = ['matplotlib','numpy','scipy','soundfile','PyGObject','pydub','resampy'],
    )
