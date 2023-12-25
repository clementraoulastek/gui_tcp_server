# Messenger desktop application

The GUI desktop client (last updated on 14/10/2023):

![Alt text](./resources/images/readme_pic.png?raw=true "Client GUI")

This application need to be run with the server application. 
- The TCP server [here](https://github.com/clementraoulastek/tcp_server)
- The backend API [here](https://github.com/clementraoulastek/backend_tcp_server)


# Conda env

A virtual environment is used to run the project. It is managed by conda.

## Create the environment

```bash
conda env create -f environment.yml
```

## Activate the environment

```bash
conda activate gui-messenger
```

# Run the app 

## In dev mode
```bash
make run
```

## In prod mode

```bash
make run
```

# Run the tests

```bash
make test
```


