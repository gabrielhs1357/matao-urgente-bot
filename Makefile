SHELL:=/bin/bash

.PHONY: environment
environment:
	pyenv install -s 3.12.1
	pyenv uninstall --force matao-urgente-bot
	pyenv virtualenv 3.12.1 --force matao-urgente-bot
	pyenv local matao-urgente-bot

.PHONY: requirements-update
requirements-update:
	pip freeze > requirements.txt

.PHONY: install
install:
	pip install -r requirements.txt
