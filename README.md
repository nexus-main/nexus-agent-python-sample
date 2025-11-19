This is a short sample about how to create Python extensions for `Nexus` using the [Nexus.Agent for Python](https://github.com/nexus-main/nexus-sources-remote/tree/master/src/agent/python).

# Run

Run the following command to launch the preconfigured instances of `Nexus` and `Nexus.Agent`:

```bash
podman-compose up -d

# or
docker-compose up -d
```

You should now be able to open the web page of [Nexus](http:/localhost:5000/) and the Swagger UI of [Nexus.Agent](http://localhost:8000/docs).

# Develop

To edit the python extension in an editor, create a virtual environment and install the requirements first:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```