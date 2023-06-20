
# Hello 

This project provide:
- TCP server
- GUI client

You Need the backend API, to register/connect to the app

100% Python project in Qt

The TCP client (last updated on 17/06/2023):

![Alt text](./resources/images/readme_pic.png?raw=true "Client GUI")

# Clone the repository and ...

create virtual env:
 - mkdir .venv
 -  python3 -m venv .venv

Activate the virtualenv:
- source ./.venv/bin/activate

for installating dependencies (need to be in the venv):
 - pip install -r requirements.txt
 - pip install -e .
 
## Launch project
Launch the server:
- python src/launch_server.py

Launch a client:
- python src/launch_client.py


