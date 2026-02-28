# Docker Compose Reference

## Table of Contents
- [Commands](#commands)
- [Compose File Syntax](#compose-file-syntax)
- [Multi-Environment Pattern](#multi-environment-pattern)
- [Common Patterns](#common-patterns)

## Commands

### Service Lifecycle

```bash
docker compose up                          # Start (foreground)
docker compose up -d                       # Start (detached)
docker compose up -d --build               # Rebuild images + start
docker compose up -d --force-recreate      # Recreate even if unchanged
docker compose up -d --remove-orphans      # Remove undefined services
docker compose up -d --scale web=3         # Scale service
docker compose down                        # Stop + remove containers/networks
docker compose down -v                     # Also remove volumes (DESTRUCTIVE!)
docker compose down --rmi all              # Also remove images
docker compose start [service]             # Start existing containers
docker compose stop [service]              # Stop without removing
docker compose restart [service]           # Restart
docker compose pause [service]
docker compose unpause [service]
docker compose kill [service]              # Force stop (SIGKILL)
```

### Inspect & Debug

```bash
docker compose ps                          # List containers
docker compose ps -a                       # Include stopped
docker compose ls                          # List all compose projects
docker compose logs                        # All services
docker compose logs -f                     # Follow
docker compose logs -f --tail 50 web       # Specific service, last 50 lines
docker compose top                         # Running processes
docker compose stats                       # Resource usage
docker compose events                      # Real-time events
docker compose config                      # Validate + render compose file
docker compose images                      # List images used
docker compose port web 80                 # Show mapped port
```

### Execute & Build

```bash
docker compose exec web bash               # Shell into running service
docker compose exec db psql -U postgres    # Run command in service
docker compose exec -u root web cmd        # As root
docker compose run --rm web npm test       # One-off command (new container)
docker compose build                       # Build all services
docker compose build --no-cache web        # Rebuild without cache
docker compose pull                        # Pull latest images
docker compose push                        # Push built images
docker compose cp web:/app/data ./local    # Copy files
```

### Watch Mode (Hot Reload)

```bash
docker compose watch                       # Watch for file changes
docker compose up --watch                  # Start + watch
```

## Compose File Syntax

### Basic Structure

```yaml
# compose.yaml (or docker-compose.yml)
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

### Build Options

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        NODE_VERSION: 22
      target: production           # Multi-stage target
      cache_from:
        - myapp:cache
    image: myapp:latest            # Tag built image
```

### Port Mapping

```yaml
ports:
  - "8080:80"                      # host:container
  - "127.0.0.1:8080:80"           # Bind localhost only
  - "8080-8090:80-90"             # Range
expose:
  - "3000"                         # Internal only (no host mapping)
```

### Volume Mounts

```yaml
services:
  web:
    volumes:
      - ./src:/app/src             # Bind mount (development)
      - ./config.yml:/app/config.yml:ro  # Read-only
      - node_modules:/app/node_modules   # Named volume
      - type: tmpfs
        target: /tmp

volumes:
  node_modules:                    # Named volume declaration
  pgdata:
    driver: local
```

### Environment Variables

```yaml
services:
  web:
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    env_file:
      - .env
      - .env.local
```

### Networking

```yaml
services:
  web:
    networks:
      - frontend
      - backend
  db:
    networks:
      - backend

networks:
  frontend:
  backend:
    driver: bridge
```

### Health Checks

```yaml
services:
  web:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  db:
    depends_on:
      web:
        condition: service_healthy  # Wait for health check
```

### Resource Limits

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: "1.5"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M
```

### Profiles (Selective Startup)

```yaml
services:
  web:
    # No profile = always starts

  debug:
    profiles: ["debug"]            # Only with --profile debug

  test:
    profiles: ["test"]             # Only with --profile test
```

```bash
docker compose up -d                       # Only web
docker compose --profile debug up -d       # web + debug
docker compose --profile debug --profile test up -d  # All
```

### Watch Mode Config

```yaml
services:
  web:
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: ./package.json
        - action: sync+restart
          path: ./config
          target: /app/config
```

| Action | When |
|--------|------|
| `sync` | Copy changed files into container |
| `rebuild` | Rebuild image + recreate container |
| `sync+restart` | Copy files + restart container |

## Multi-Environment Pattern

```
compose.yaml              # Base config (shared)
compose.override.yaml     # Dev overrides (auto-loaded)
compose.prod.yaml         # Production overrides
```

```bash
# Development (auto-loads override)
docker compose up -d

# Production (explicit)
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

### Base (`compose.yaml`)
```yaml
services:
  web:
    image: myapp:latest
    restart: unless-stopped
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
```

### Dev Override (`compose.override.yaml`)
```yaml
services:
  web:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./src:/app/src
    environment:
      - NODE_ENV=development
```

### Production (`compose.prod.yaml`)
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
    environment:
      - NODE_ENV=production
```

## Common Patterns

### Database + App

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

### Reverse Proxy

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web

  web:
    build: .
    expose:
      - "3000"
```
