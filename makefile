requirements:
	pip install -e .
	pip install -r requirements.txt
	
test:
	pytest -v -s

launch-server:
	python src/launch_server.py

launch-client:
	python src/launch_client.py