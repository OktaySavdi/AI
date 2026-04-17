---
name: "jpa-patterns"
description: >
  JPA/Hibernate patterns: entity design, repository patterns, N+1 prevention,
  fetch strategies, transactions, and query optimization. Activate for JPA work.
metadata:
  version: 1.0.0
  category: engineering
---

# JPA Patterns Skill

## Entity Design

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false, length = 255)
    private String email;

    // LAZY by default for @OneToMany — never EAGER
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Order> orders = new ArrayList<>();

    // Proper equals/hashCode based on business key
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User u)) return false;
        return Objects.equals(email, u.email);
    }
}
```

## Repository Pattern (Spring Data)

```java
public interface UserRepository extends JpaRepository<User, String> {
    // Derived query
    Optional<User> findByEmail(String email);

    // JPQL for complex queries
    @Query("SELECT u FROM User u LEFT JOIN FETCH u.orders WHERE u.id = :id")
    Optional<User> findByIdWithOrders(@Param("id") String id);

    // Projection to avoid loading full entity
    List<UserSummary> findByActiveTrue();
}
```

## N+1 Prevention

```java
// BAD — N+1 for orders
List<User> users = repo.findAll();
users.forEach(u -> u.getOrders().size()); // N queries

// GOOD — JOIN FETCH
@Query("SELECT DISTINCT u FROM User u LEFT JOIN FETCH u.orders")
List<User> findAllWithOrders();

// Or EntityGraph
@EntityGraph(attributePaths = {"orders"})
List<User> findAll();
```

## Transactions

```java
@Service
@Transactional(readOnly = true)  // default read-only for the service
public class OrderService {

    @Transactional  // override to read-write for mutations
    public Order createOrder(String userId, List<String> productIds) {
        User user = userRepo.findById(userId)
            .orElseThrow(() -> new NotFoundException("User", userId));
        // ...
    }
}
```

## Projections

```java
// Interface projection — only load required columns
public interface UserSummary {
    String getId();
    String getEmail();
    @Value("#{target.firstName + ' ' + target.lastName}")
    String getFullName();
}
```

## Auditing

```java
@EntityListeners(AuditingEntityListener.class)
@MappedSuperclass
public abstract class AuditableEntity {
    @CreatedDate
    @Column(updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;
}
```

## Common Pitfalls

- Never use `FetchType.EAGER` on collections — always LAZY
- Never expose JPA entities directly from REST endpoints — use DTOs
- Avoid `CascadeType.ALL` unless you own the lifecycle of children
- Always use `Optional` as return type for single-entity lookups
- Bidirectional relationships need `mappedBy` and helper methods to keep both sides in sync
