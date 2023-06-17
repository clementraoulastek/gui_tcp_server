virtualenv:
	mkdir .venv
	python3 -m venv /.venv

requirements:	
	pip install -r requirements.txt
	pip install -e .

test:
	pytest -v -s

launch server:
	python src/launch_server.py

launch client:
	python src/launch_client.py