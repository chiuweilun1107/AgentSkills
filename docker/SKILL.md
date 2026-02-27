---
name: docker
description: 'Docker container management, Dockerfile authoring, Docker Compose orchestration, and Python SDK. Use when user mentions docker, container, 容器, dockerfile, docker-compose, image, 部署, "build image", "跑容器", "docker掛了". Covers CLI, Compose, Exec, Engine API, Python SDK, and troubleshooting.'
---

# Docker Operations

Comprehensive Docker skill covering CLI, Compose, Dockerfile, Exec, Engine API, and Python SDK. Choose the right mode for each task.

## Mode Decision Flow

```
Docker task?
    │
    ├─ Build / run / manage containers?
    │   → CLI (docker build / run / ps / logs)
    │
    ├─ Multi-service orchestration?
    │   → Compose (docker compose up / down / logs)
    │
    ├─ Execute command inside running container?
    │   → Exec (docker exec -it <container> <cmd>)
    │
    ├─ Programmatic container management?
    │   → Python SDK (import docker)
    │
    ├─ Write / optimize Dockerfile?
    │   → See Dockerfile Best Practices below
    │
    └─ Debug / troubleshoot?
        → See Troubleshooting below
```

## Quick Reference

### Container Lifecycle

```bash
# Run
docker run -d --name myapp -p 8080:80 -v ./data:/data --env-file .env myimage:latest
docker run -it --rm ubuntu:24.04 bash     # Interactive, auto-remove

# Status
docker ps                                  # Running containers
docker ps -a                               # All containers
docker logs -f --tail 100 myapp            # Follow logs
docker stats                               # Live resource usage
docker inspect myapp                       # Full container details

# Manage
docker stop myapp && docker rm myapp       # Stop + remove
docker restart myapp
docker exec -it myapp bash                 # Shell into container
docker exec myapp cat /etc/hosts           # Run command

# Cleanup
docker system prune -a --volumes           # Remove ALL unused (images, containers, volumes)
docker image prune -a                      # Remove unused images
docker volume prune                        # Remove unused volumes
```

### Image Management

```bash
docker build -t myapp:v1 .                 # Build from Dockerfile
docker build -t myapp:v1 -f deploy/Dockerfile .  # Custom Dockerfile path
docker images                              # List images
docker tag myapp:v1 registry.io/myapp:v1   # Tag for registry
docker push registry.io/myapp:v1           # Push to registry
docker pull nginx:alpine                   # Pull image
docker rmi myapp:v1                        # Remove image
```

### Docker Compose (Essential)

```bash
docker compose up -d                       # Start all services (detached)
docker compose up -d --build               # Rebuild + start
docker compose down                        # Stop + remove containers/networks
docker compose down -v                     # Also remove volumes (DESTRUCTIVE)
docker compose ps                          # List services
docker compose logs -f [service]           # Follow logs
docker compose exec db psql -U postgres    # Exec into service
docker compose restart [service]           # Restart specific service
docker compose pull                        # Pull latest images
docker compose config                      # Validate compose file
```

### Network & Volume

```bash
# Network
docker network ls
docker network create mynet
docker network connect mynet myapp
docker network inspect mynet

# Volume
docker volume ls
docker volume create mydata
docker volume inspect mydata
```

## Dockerfile Best Practices

```dockerfile
# 1. Use specific base image tag (never :latest in production)
FROM node:22-alpine AS builder

# 2. Set working directory
WORKDIR /app

# 3. Copy dependency files FIRST (layer caching)
COPY package.json package-lock.json ./
RUN npm ci --production

# 4. Copy source AFTER dependencies
COPY . .
RUN npm run build

# 5. Multi-stage: slim final image
FROM node:22-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

# 6. Non-root user
RUN addgroup -S app && adduser -S app -G app
USER app

# 7. Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:3000/health || exit 1

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Key Rules:**
- Pin base image versions (`node:22-alpine`, not `node:latest`)
- Copy dependency manifests before source (cache layers)
- Multi-stage builds to reduce final image size
- Run as non-root user
- Use `.dockerignore` to exclude `node_modules/`, `.git/`, etc.
- One process per container

## Mode Comparison

| Mode | When | Example |
|------|------|---------|
| **CLI** | Direct container/image ops | `docker run`, `docker build` |
| **Compose** | Multi-service apps | `docker compose up -d` |
| **Exec** | Commands inside container | `docker exec db psql` |
| **Engine API** | HTTP automation, CI/CD | `curl --unix-socket /var/run/docker.sock` |
| **Python SDK** | Programmatic management | `docker.from_env().containers.run()` |

## Troubleshooting

| Problem | Command / Solution |
|---------|-------------------|
| Container won't start | `docker logs myapp` — check error output |
| Port already in use | `lsof -i :8080` then stop conflicting process |
| Out of disk space | `docker system df` then `docker system prune -a` |
| Build cache stale | `docker build --no-cache -t myapp .` |
| Can't connect between containers | Check same network: `docker network inspect` |
| Permission denied | Check USER in Dockerfile, volume mount ownership |
| Container keeps restarting | `docker inspect --format='{{.State.ExitCode}}' myapp` |
| Compose services not starting | `docker compose config` to validate YAML |
| Slow build | Order Dockerfile layers (deps before source) |
| Image too large | Use multi-stage build + alpine base |

## References

Extended documentation in `references/`:
- **`cli.md`** — Complete CLI command reference (containers, images, networks, volumes, system)
- **`compose.md`** — Docker Compose commands, file syntax, patterns, profiles, watch mode
- **`sdk-api.md`** — Python SDK, Docker Engine REST API, programmatic management
