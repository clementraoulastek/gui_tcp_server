
ACTIVATE := $(shell source .venv/bin/acticate)

create-virtualenv:
	python3 -m venv .venv

activate-venv:
	$(ACTIVATE)

requirements:
	$(ACTIVATE)
	pip install -r requirements.txt
	pip install -e .

test:
	$(ACTIVATE)
	pytest -v -s

launch-server:
	$(ACTIVATE)
	python src/launch_server.py

launch-client:
	$(ACTIVATE)
	python src/launch_client.py