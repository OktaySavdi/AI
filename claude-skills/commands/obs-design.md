Using the observability-designer skill, design a full observability stack for: $ARGUMENTS

Produce:
1. SLO definition (SLI metric, target %, error budget)
2. ServiceMonitor YAML (scrape the app's /metrics endpoint)
3. PrometheusRule YAML with:
   - Availability SLO burn rate alerts (fast + slow)
   - Resource pressure alerts (CPU, memory, restart rate)
   - Business-logic alerts if applicable
4. Key Loki log queries for this service
5. Alert runbook for the critical alert (what to check, how to fix)

All alerts must have: severity label, summary annotation, runbook_url annotation.
All YAML must be complete and production-ready.
