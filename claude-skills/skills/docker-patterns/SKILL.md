---
name: "docker-patterns"
description: >
  Docker Compose, networking, volumes, multi-stage builds, and container security.
  Activate for Dockerfile authoring, Docker Compose, or container runtime work.
metadata:
  version: 1.0.0
  category: engineering
---

# Docker Patterns Skill

## Multi-Stage Build (Node.js)

```dockerfile
# Stage 1: deps
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: build
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: runtime (minimal)
FROM node:22-alpine AS runtime
WORKDIR /app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## Multi-Stage Build (Go)

```dockerfile
FROM golang:1.22-alpine AS build
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /api ./cmd/api

FROM gcr.io/distroless/static:nonroot
COPY --from=build /api /api
ENTRYPOINT ["/api"]
```

## Security Hardening

```dockerfile
# Never run as root
USER nonroot:nonroot

# Read-only filesystem (use volumes for writable paths)
# Set in docker-compose or k8s: readOnlyRootFilesystem: true

# No secrets in ENV — use runtime secrets
# BAD: ENV DB_PASSWORD=secret123
# GOOD: use Docker secrets or K8s secrets mounted as volumes
```

## Docker Compose

```yaml
---
services:
  api:
    build:
      context: .
      target: runtime
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "3000:3000"
    networks:
      - internal
    read_only: true
    tmpfs:
      - /tmp

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - internal

volumes:
  pgdata:

networks:
  internal:
    driver: bridge
```

## .dockerignore

```
.git
.env
node_modules
dist
*.log
**/*.test.ts
.claude
```

## Layer Caching Tips

- Copy dependency files (`package.json`, `go.mod`) before source code
- `RUN npm ci` before `COPY . .` so code changes don't bust the dep cache
- Pin base image digests in production: `FROM node:22-alpine@sha256:...`

## Useful Commands

```bash
docker build --target runtime -t myapp:latest .
docker compose up -d --wait           # wait for healthchecks
docker compose logs -f api            # follow logs
docker compose exec api sh            # shell into container
docker system prune -af               # clean up unused resources
```
