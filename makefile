virtualenv:
	mkdir .venv
	python3 -m venv /.venv

requirements:	
	pip install -r requirements.txt
	pip install -e .

test:
	pytest -v -s