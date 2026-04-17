---
name: "springboot-tdd"
description: >
  Spring Boot TDD with JUnit 5, Mockito, and @SpringBootTest: test slices,
  MockMvc, WireMock, TestContainers. Activate for Spring Boot TDD work.
metadata:
  version: 1.0.0
  category: engineering
---

# Spring Boot TDD Skill

## Unit Tests (no Spring context)

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock private UserRepository repo;
    @InjectMocks private UserService service;

    @Test
    void shouldReturnEmptyWhenUserNotFound() {
        when(repo.findById("unknown")).thenReturn(Optional.empty());
        assertThat(service.findById("unknown")).isEmpty();
    }

    @Test
    void shouldThrowWhenEmailAlreadyExists() {
        when(repo.existsByEmail("dup@example.com")).thenReturn(true);
        var request = new CreateUserRequest("dup@example.com", "Test");
        assertThatThrownBy(() -> service.create(request))
            .isInstanceOf(ConflictException.class)
            .hasMessageContaining("dup@example.com");
    }
}
```

## Web Layer Tests (@WebMvcTest)

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired MockMvc mvc;
    @MockBean UserService service;

    @Test
    void returnsUserWhenFound() throws Exception {
        var user = new UserResponse("1", "alice@example.com", "Alice");
        when(service.findById("1")).thenReturn(Optional.of(user));

        mvc.perform(get("/api/v1/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.email").value("alice@example.com"));
    }

    @Test
    void returns404WhenNotFound() throws Exception {
        when(service.findById("missing")).thenReturn(Optional.empty());
        mvc.perform(get("/api/v1/users/missing"))
            .andExpect(status().isNotFound());
    }
}
```

## Repository Tests (@DataJpaTest)

```java
@DataJpaTest
class UserRepositoryTest {

    @Autowired TestEntityManager em;
    @Autowired UserRepository repo;

    @Test
    void findsUserByEmail() {
        em.persist(new User("1", "alice@example.com", "Alice"));
        em.flush();

        Optional<User> found = repo.findByEmail("alice@example.com");
        assertThat(found).isPresent().hasValueSatisfying(u ->
            assertThat(u.getName()).isEqualTo("Alice")
        );
    }
}
```

## Integration Tests (TestContainers)

```java
@SpringBootTest
@Testcontainers
class UserIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void configureDb(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired TestRestTemplate rest;

    @Test
    void fullCreateAndGetFlow() {
        var created = rest.postForObject("/api/v1/users",
            new CreateUserRequest("full@example.com", "Full Test"), UserResponse.class);
        assertThat(created.email()).isEqualTo("full@example.com");
    }
}
```

## Test Commands

```bash
mvn test                                    # unit tests
mvn test -Dgroups=integration               # integration tests
mvn verify                                  # all including failsafe
mvn test -Dtest=UserServiceTest             # specific class
```
