#!/bin/sh
pytest --cov=custom_components/ytmdesktop_remote tests/ --cov-report term-missing --cov-report html
