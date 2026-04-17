---
name: "springboot-verification"
description: >
  Spring Boot verification loop: build, test, lint, security scan, and
  Docker image validation. Activate when verifying a Spring Boot implementation.
metadata:
  version: 1.0.0
  category: engineering
---

# Spring Boot Verification Loop Skill

## Verification Sequence

```bash
# 1. Compile
mvn compile -q

# 2. Unit tests
mvn test -q

# 3. Code style (Checkstyle)
mvn checkstyle:check

# 4. Static analysis (SpotBugs)
mvn spotbugs:check

# 5. Dependency vulnerability scan
mvn dependency-check:check

# 6. Integration tests
mvn verify -P integration-tests

# 7. Build Docker image
mvn spring-boot:build-image -DskipTests

# 8. Container security scan
trivy image myapp:latest
```

## Full CI Script

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Compile ===" && mvn compile -q
echo "=== Unit Tests ===" && mvn test -q
echo "=== Style ===" && mvn checkstyle:check
echo "=== Static Analysis ===" && mvn spotbugs:check
echo "=== Security ===" && mvn dependency-check:check
echo "=== Integration ===" && mvn verify -P integration-tests
echo "=== Build Image ===" && mvn spring-boot:build-image -DskipTests
echo "=== Image Scan ===" && trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest
echo "All checks passed."
```

## pom.xml Verification Plugins

```xml
<plugin>
  <groupId>com.github.spotbugs</groupId>
  <artifactId>spotbugs-maven-plugin</artifactId>
  <version>4.8.3.1</version>
  <configuration><failOnError>true</failOnError></configuration>
</plugin>
<plugin>
  <groupId>org.owasp</groupId>
  <artifactId>dependency-check-maven</artifactId>
  <version>9.0.9</version>
  <configuration><failBuildOnCVSS>7</failBuildOnCVSS></configuration>
</plugin>
```
