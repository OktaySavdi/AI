---
name: "java-coding-standards"
description: >
  Java coding standards for Java 17+: records, sealed classes, pattern matching,
  streams, Optional, and clean architecture patterns. Activate for Java code.
metadata:
  version: 1.0.0
  category: engineering
---

# Java Coding Standards Skill

## Records (Java 16+)

```java
// Immutable value object
public record Money(long amountCents, Currency currency) {
    // Compact constructor for validation
    public Money {
        if (amountCents < 0) throw new IllegalArgumentException("Amount cannot be negative");
        Objects.requireNonNull(currency, "currency");
    }
}
```

## Sealed Classes (Java 17+)

```java
public sealed interface Result<T> permits Result.Success, Result.Failure {
    record Success<T>(T value) implements Result<T> {}
    record Failure<T>(String error) implements Result<T> {}
}

// Pattern matching switch (Java 21)
String message = switch (result) {
    case Result.Success<User> s -> "Found: " + s.value().name();
    case Result.Failure<User> f -> "Error: " + f.error();
};
```

## Optional — Use Correctly

```java
// WRONG — Optional as nullable field type
private Optional<String> name;  // never do this

// CORRECT — Optional as return type only
public Optional<User> findById(String id) {
    return users.stream()
        .filter(u -> u.id().equals(id))
        .findFirst();
}

// Chaining
String displayName = findById(id)
    .map(User::name)
    .orElse("Unknown");
```

## Streams

```java
// Collect to immutable list (Java 16+)
List<String> names = users.stream()
    .filter(u -> u.active())
    .map(User::name)
    .sorted()
    .toList();  // unmodifiable

// Grouping
Map<Department, List<Employee>> byDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::department));
```

## Dependency Injection (Spring-style)

```java
@Service
public class UserService {
    private final UserRepository repo;
    private final EmailService emailer;

    // Constructor injection — always preferred over @Autowired fields
    public UserService(UserRepository repo, EmailService emailer) {
        this.repo = repo;
        this.emailer = emailer;
    }
}
```

## Exception Hierarchy

```java
public class AppException extends RuntimeException {
    public AppException(String message) { super(message); }
    public AppException(String message, Throwable cause) { super(message, cause); }
}

public class NotFoundException extends AppException {
    public NotFoundException(String entity, String id) {
        super(entity + " not found: " + id);
    }
}
```

## Immutability

```java
// Use Collections.unmodifiableList or List.copyOf
public List<String> getTags() {
    return List.copyOf(tags);  // defensive copy
}

// Builder pattern for complex objects
User user = User.builder()
    .id(UUID.randomUUID().toString())
    .name("Alice")
    .email("alice@example.com")
    .build();
```

## Tools

```bash
mvn verify                  # build, test, analyze
mvn test -pl module-name    # specific module
mvn checkstyle:check        # style enforcement
mvn spotbugs:check          # static analysis
```
