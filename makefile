requirements:
	pip install -e .
	pip install -r requirements.txt
	
test:
	pytest -v -s

server:
	python src/launch_server.py

client:
	python src/launch_client.py