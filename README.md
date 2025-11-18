This is a short sample about how to create Python extensions for `Nexus` using the [Nexus.Agent for Python](https://github.com/nexus-main/nexus-sources-remote/tree/master/src/agent/python).

Run the following commands to launch the preconfigured instances of `Nexus` and `Nexus.Agent`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdir data
chmod -R 777 data

mkdir nexus
chmod -R 777 nexus

mkdir nexus-agent
chmod -R 777 nexus-agent

podman-compose up -d
```

You should now be able to open the web page of [Nexus](http:/localhost:5000/) and the Swagger UI of [Nexus.Agent](http://localhost:8000/docs).
