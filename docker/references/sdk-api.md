# Docker SDK & Engine API Reference

## Table of Contents
- [Python SDK (docker-py)](#python-sdk-docker-py)
- [Docker Engine REST API](#docker-engine-rest-api)
- [Mode Selection Guide](#mode-selection-guide)

## Python SDK (docker-py)

### Installation

```bash
pip install docker
```

### Connection

```python
import docker

# From environment (reads DOCKER_HOST, etc.)
client = docker.from_env()

# Explicit connection
client = docker.DockerClient(base_url='unix:///var/run/docker.sock')

# Docker Desktop on Linux
client = docker.DockerClient(
    base_url='unix:///home/user/.docker/desktop/docker.sock'
)

# Remote Docker host
client = docker.DockerClient(base_url='tcp://192.168.1.100:2376')
```

### Containers

```python
# Run container
container = client.containers.run(
    "ubuntu:24.04",
    "echo hello",
    detach=True,
    name="myapp",
    ports={'80/tcp': 8080},
    volumes={'/host/data': {'bind': '/data', 'mode': 'rw'}},
    environment={'MY_VAR': 'value'},
    restart_policy={'Name': 'unless-stopped'},
    remove=True,  # auto-remove on exit
)

# List containers
containers = client.containers.list()           # Running
containers = client.containers.list(all=True)    # All

# Get specific container
container = client.containers.get("myapp")

# Container operations
container.start()
container.stop(timeout=10)
container.restart()
container.kill()
container.remove(force=True)
container.pause()
container.unpause()

# Logs
logs = container.logs(tail=100, follow=False)
print(logs.decode('utf-8'))

# Stream logs
for line in container.logs(stream=True, follow=True):
    print(line.decode('utf-8'), end='')

# Execute command
exit_code, output = container.exec_run("ls /app")
print(output.decode('utf-8'))

# Execute interactive
exit_code, output = container.exec_run(
    "bash",
    stdin=True,
    tty=True,
    workdir="/app"
)

# Container stats
stats = container.stats(stream=False)
print(f"CPU: {stats['cpu_stats']}")
print(f"Memory: {stats['memory_stats']['usage']}")

# Container info
print(container.status)          # running, exited, etc.
print(container.name)
print(container.short_id)
print(container.attrs)           # Full inspect data
```

### Images

```python
# Pull
image = client.images.pull("nginx", tag="alpine")
image = client.images.pull("registry.io/myapp", tag="v1")

# Build
image, logs = client.images.build(
    path="./",
    tag="myapp:v1",
    dockerfile="Dockerfile",
    buildargs={'VERSION': '1.0'},
    rm=True,
    nocache=False,
)
for chunk in logs:
    if 'stream' in chunk:
        print(chunk['stream'], end='')

# List
images = client.images.list()
for img in images:
    print(f"{img.tags} - {img.short_id}")

# Remove
client.images.remove("myapp:v1")

# Tag
image.tag("registry.io/myapp", tag="v1")

# Push
client.images.push("registry.io/myapp", tag="v1")

# Prune
client.images.prune(filters={'dangling': True})
```

### Networks

```python
# Create
network = client.networks.create("mynet", driver="bridge")

# List
networks = client.networks.list()

# Connect/disconnect container
network.connect(container)
network.disconnect(container)

# Inspect
print(network.attrs)

# Remove
network.remove()
```

### Volumes

```python
# Create
volume = client.volumes.create(name="mydata")

# List
volumes = client.volumes.list()

# Inspect
print(volume.attrs)

# Remove
volume.remove()

# Prune
client.volumes.prune()
```

### System

```python
# Info
info = client.info()
print(f"Containers: {info['Containers']}")
print(f"Images: {info['Images']}")

# Disk usage
df = client.df()

# Prune everything
client.containers.prune()
client.images.prune()
client.networks.prune()
client.volumes.prune()

# Events (streaming)
for event in client.events(decode=True):
    print(f"{event['Type']}: {event['Action']} {event.get('Actor', {}).get('Attributes', {}).get('name', '')}")

# Ping
client.ping()  # Returns True if daemon accessible
```

### Error Handling

```python
import docker
from docker.errors import (
    ContainerError,
    ImageNotFound,
    APIError,
    NotFound,
)

try:
    container = client.containers.get("nonexistent")
except NotFound:
    print("Container not found")

try:
    client.containers.run("nonexistent:image", remove=True)
except ImageNotFound:
    print("Image not found")

try:
    container.stop()
except APIError as e:
    print(f"Docker API error: {e}")
```

---

## Docker Engine REST API

The Docker daemon exposes a REST API via Unix socket (or TCP).

### Via curl (Unix Socket)

```bash
# Ping
curl --unix-socket /var/run/docker.sock http://localhost/_ping

# List containers
curl -s --unix-socket /var/run/docker.sock \
  http://localhost/v1.47/containers/json | jq

# List containers (all)
curl -s --unix-socket /var/run/docker.sock \
  'http://localhost/v1.47/containers/json?all=true' | jq

# Create container
curl -s --unix-socket /var/run/docker.sock \
  -X POST http://localhost/v1.47/containers/create?name=myapp \
  -H "Content-Type: application/json" \
  -d '{"Image":"nginx:alpine","HostConfig":{"PortBindings":{"80/tcp":[{"HostPort":"8080"}]}}}' | jq

# Start container
curl -s --unix-socket /var/run/docker.sock \
  -X POST http://localhost/v1.47/containers/myapp/start

# Stop container
curl -s --unix-socket /var/run/docker.sock \
  -X POST http://localhost/v1.47/containers/myapp/stop

# Container logs
curl -s --unix-socket /var/run/docker.sock \
  'http://localhost/v1.47/containers/myapp/logs?stdout=true&tail=50'

# List images
curl -s --unix-socket /var/run/docker.sock \
  http://localhost/v1.47/images/json | jq

# System info
curl -s --unix-socket /var/run/docker.sock \
  http://localhost/v1.47/info | jq

# Disk usage
curl -s --unix-socket /var/run/docker.sock \
  http://localhost/v1.47/system/df | jq
```

### Common API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/_ping` | GET | Health check |
| `/containers/json` | GET | List containers |
| `/containers/create` | POST | Create container |
| `/containers/{id}/start` | POST | Start |
| `/containers/{id}/stop` | POST | Stop |
| `/containers/{id}/restart` | POST | Restart |
| `/containers/{id}/kill` | POST | Kill |
| `/containers/{id}` | DELETE | Remove |
| `/containers/{id}/logs` | GET | Logs |
| `/containers/{id}/exec` | POST | Create exec instance |
| `/containers/{id}/json` | GET | Inspect |
| `/images/json` | GET | List images |
| `/images/create` | POST | Pull image |
| `/build` | POST | Build image |
| `/networks` | GET | List networks |
| `/networks/create` | POST | Create network |
| `/volumes` | GET | List volumes |
| `/volumes/create` | POST | Create volume |
| `/system/df` | GET | Disk usage |
| `/info` | GET | System info |
| `/version` | GET | Version info |

### When to Use Engine API

| Scenario | Use |
|----------|-----|
| Shell scripts, quick ops | Docker CLI |
| Multi-service orchestration | Docker Compose |
| Python application code | Python SDK (`docker`) |
| CI/CD pipelines (no SDK) | Engine API via `curl` |
| Custom monitoring/tooling | Engine API or SDK |
| Remote Docker management | TCP-based Engine API or SDK |

---

## Mode Selection Guide

```
Need to manage Docker?
    │
    ├─ Interactive terminal ops?
    │   → Docker CLI (docker run, build, ps)
    │
    ├─ Multi-service apps?
    │   → Docker Compose (compose.yaml)
    │
    ├─ Python project integration?
    │   → Python SDK (pip install docker)
    │
    ├─ CI/CD without SDK?
    │   → Engine API via curl (Unix socket)
    │
    └─ Command inside container?
        → docker exec (CLI) or container.exec_run() (SDK)
```
