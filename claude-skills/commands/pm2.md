# /pm2 — PM2 Service Lifecycle Management

Manages Node.js application processes via PM2: start, stop, restart, logs, and
status. Generates and updates `ecosystem.config.js` for multi-service setups.

## Usage

```
/pm2 start
/pm2 stop <app-name>
/pm2 restart all
/pm2 logs <app-name>
/pm2 status
/pm2 generate-config
```

## What It Does

- `start` — starts all processes in ecosystem.config.js
- `stop <name>` — stops a specific process by name
- `restart` — graceful restart with zero-downtime reload
- `logs` — tails process logs (last 50 lines)
- `status` — table of running processes, CPU, memory, restart count
- `generate-config` — scaffolds ecosystem.config.js for the current project

## Example Generated Config

```javascript
module.exports = {
  apps: [
    {
      name: "api",
      script: "src/index.js",
      instances: "max",
      exec_mode: "cluster",
      watch: false,
      env: { NODE_ENV: "production" }
    }
  ]
};
```

## Related Commands

- `/setup-pm` — configure package manager
