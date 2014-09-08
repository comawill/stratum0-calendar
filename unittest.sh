#!/bin/bash
nosetests -vs --with-coverage --cover-package=calendargenerator
pep8 --ignore=E501,W191,E128 *.py tests/*.py