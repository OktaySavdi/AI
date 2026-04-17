---
name: "springboot-patterns"
description: >
  Spring Boot 3.x patterns: controllers, services, repositories, configuration,
  exception handling, and async. Activate for Spring Boot development.
metadata:
  version: 1.0.0
  category: engineering
---

# Spring Boot Patterns Skill

## Layer Architecture

```
Controller → Service → Repository → Database
              ↓
           Domain Model (plain Java objects)
```

## Controller

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUser(@PathVariable String id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserResponse createUser(@Valid @RequestBody CreateUserRequest request) {
        return userService.create(request);
    }
}
```

## Service

```java
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class UserService {
    private final UserRepository repo;
    private final PasswordEncoder encoder;

    public Optional<UserResponse> findById(String id) {
        return repo.findById(id).map(UserMapper::toResponse);
    }

    @Transactional
    public UserResponse create(CreateUserRequest req) {
        if (repo.existsByEmail(req.email())) {
            throw new ConflictException("Email already in use: " + req.email());
        }
        User user = new User(UUID.randomUUID().toString(), req.email(), req.name());
        return UserMapper.toResponse(repo.save(user));
    }
}
```

## Repository (Spring Data JPA)

```java
public interface UserRepository extends JpaRepository<User, String> {
    boolean existsByEmail(String email);
    Optional<User> findByEmail(String email);

    @Query("SELECT u FROM User u WHERE u.active = true ORDER BY u.createdAt DESC")
    Page<User> findAllActive(Pageable pageable);
}
```

## Global Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ProblemDetail handleNotFound(NotFoundException ex) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail detail = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
        detail.setProperty("errors", ex.getBindingResult().getFieldErrors()
            .stream().map(e -> e.getField() + ": " + e.getDefaultMessage()).toList());
        return detail;
    }
}
```

## Configuration Properties

```java
@ConfigurationProperties(prefix = "app")
@Validated
public record AppProperties(
    @NotBlank String jwtSecret,
    @Min(3600) int jwtExpirySeconds,
    @NotNull MailProperties mail
) {
    public record MailProperties(@NotBlank String from, @NotBlank String host) {}
}
```

## Async

```java
@Service
public class EmailService {
    @Async
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public CompletableFuture<Void> sendWelcomeEmail(String email) {
        // runs in thread pool
        return CompletableFuture.completedFuture(null);
    }
}
```
