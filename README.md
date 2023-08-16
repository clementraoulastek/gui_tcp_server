
# Robot Messenger 

This project provide:
- TCP server
- GUI client

This project need the Robot Messenger backend API, to register/connect to the app

The TCP client (last updated on 16/08/2023):

![Alt text](./resources/images/readme_pic.png?raw=true "Client GUI")

# Init the repository

create virtual env:
 -  mkdir .venv
 -  python3 -m venv .venv

Activate the virtualenv:
- source .venv/bin/activate

for installating dependencies (need to be in the venv):
 - pip install -e .
 - pip install -r requirements.txt

 
## Launch project
Launch the server:
- python src/launch_server.py

Launch a client:
- python src/launch_client.py


