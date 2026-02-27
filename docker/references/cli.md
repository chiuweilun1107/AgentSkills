# Docker CLI Complete Reference

## Container Commands

### Run

```bash
# Basic run
docker run <image>
docker run -d <image>                      # Detached (background)
docker run -it <image> bash                # Interactive terminal
docker run --rm <image>                    # Auto-remove on exit
docker run --name myapp <image>            # Named container

# Port mapping
docker run -p 8080:80 <image>              # host:container
docker run -p 127.0.0.1:8080:80 <image>    # Bind to localhost only
docker run -P <image>                      # Map all exposed ports

# Volume mount
docker run -v /host/path:/container/path <image>       # Bind mount
docker run -v myvolume:/container/path <image>          # Named volume
docker run -v /host/path:/container/path:ro <image>     # Read-only
docker run --tmpfs /tmp <image>                         # tmpfs mount

# Environment
docker run -e MY_VAR=value <image>
docker run --env-file .env <image>

# Resource limits
docker run --memory=512m --cpus=1.5 <image>

# Restart policy
docker run --restart=unless-stopped <image>
docker run --restart=always <image>
docker run --restart=on-failure:5 <image>   # Max 5 retries

# Network
docker run --network=mynet <image>
docker run --hostname=myhost <image>
docker run --dns=8.8.8.8 <image>

# Security
docker run --user 1000:1000 <image>
docker run --read-only <image>
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE <image>
```

### Lifecycle

```bash
docker start <container>
docker stop <container>                     # Graceful (SIGTERM → SIGKILL after 10s)
docker stop -t 30 <container>              # Custom timeout
docker restart <container>
docker kill <container>                     # Immediate (SIGKILL)
docker pause <container>
docker unpause <container>
docker rm <container>
docker rm -f <container>                   # Force remove running
docker rename <old> <new>
```

### Inspect & Debug

```bash
docker ps                                  # Running containers
docker ps -a                               # All containers
docker ps -q                               # IDs only
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

docker logs <container>
docker logs -f <container>                 # Follow
docker logs --tail 50 <container>          # Last 50 lines
docker logs --since 1h <container>         # Last hour
docker logs --timestamps <container>       # With timestamps

docker inspect <container>
docker inspect --format '{{.State.Status}}' <container>
docker inspect --format '{{.NetworkSettings.IPAddress}}' <container>
docker inspect --format '{{json .State}}' <container> | jq

docker stats                               # All containers
docker stats <container>                   # Specific container
docker top <container>                     # Processes in container

docker diff <container>                    # Changed files
docker port <container>                    # Port mappings
```

### Execute & Copy

```bash
docker exec -it <container> bash           # Interactive shell
docker exec -it <container> sh             # For alpine/minimal
docker exec <container> ls /app            # Run command
docker exec -u root <container> cmd        # Run as root
docker exec -w /app <container> cmd        # Set working directory
docker exec -e MY_VAR=val <container> cmd  # With env var

docker cp <container>:/path/file ./local   # Container → host
docker cp ./local <container>:/path/file   # Host → container
```

## Image Commands

```bash
# Build
docker build -t name:tag .
docker build -t name:tag -f path/Dockerfile .
docker build --build-arg VERSION=1.0 -t name:tag .
docker build --no-cache -t name:tag .
docker build --target builder -t name:tag .    # Multi-stage target
docker build --platform linux/amd64 -t name:tag .

# List & Info
docker images
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
docker image ls --filter "dangling=true"
docker image history <image>

# Registry
docker pull <image>:<tag>
docker push <image>:<tag>
docker tag source:tag target:tag
docker login [registry]
docker logout [registry]
docker search <term>

# Cleanup
docker rmi <image>
docker rmi $(docker images -q --filter "dangling=true")
docker image prune                         # Remove dangling
docker image prune -a                      # Remove all unused
```

## Network Commands

```bash
docker network ls
docker network create <name>
docker network create --driver bridge <name>
docker network create --subnet 172.20.0.0/16 <name>
docker network inspect <name>
docker network connect <network> <container>
docker network disconnect <network> <container>
docker network rm <name>
docker network prune
```

### Network Drivers

| Driver | Use Case |
|--------|----------|
| `bridge` | Default. Containers on same host communicate |
| `host` | Container uses host network directly |
| `none` | No networking |
| `overlay` | Multi-host (Swarm) |
| `macvlan` | Container gets MAC address on physical network |

## Volume Commands

```bash
docker volume ls
docker volume create <name>
docker volume inspect <name>
docker volume rm <name>
docker volume prune                        # Remove unused volumes
```

### Mount Types

| Type | Syntax | Use Case |
|------|--------|----------|
| Bind mount | `-v /host:/container` | Development, config files |
| Named volume | `-v name:/container` | Database persistence |
| tmpfs | `--tmpfs /path` | Temporary data, secrets |

## System Commands

```bash
docker version                             # Client + server version
docker info                                # System-wide info
docker system df                           # Disk usage
docker system df -v                        # Detailed disk usage
docker system prune                        # Remove unused data
docker system prune -a                     # Remove ALL unused (incl. images)
docker system prune -a --volumes           # Also remove volumes
docker system events                       # Real-time events
```

## Common Patterns

### Stop All Containers
```bash
docker stop $(docker ps -q)
```

### Remove All Stopped Containers
```bash
docker rm $(docker ps -aq --filter status=exited)
```

### Export / Import
```bash
docker export <container> > backup.tar
docker import backup.tar newimage:tag
docker save <image> > image.tar
docker load < image.tar
```

### Health Check in Run
```bash
docker run --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-retries=3 \
  <image>
```
