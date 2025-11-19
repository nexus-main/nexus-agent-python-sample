This brief example shows how to build Python extensions for `Nexus` using the [Nexus.Agent for Python](https://github.com/nexus-main/nexus-sources-remote/tree/master/src/agent/python).

# Run

Start the preconfigured `Nexus` and `Nexus.Agent` containers:

```bash
podman-compose up -d

# or
docker-compose up -d
```

Once the containers are running, open the Nexus web UI at [http://localhost:5000/](http://localhost:5000/) and the Nexus.Agent Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs).

# Develop

To develop the Python extension, create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```