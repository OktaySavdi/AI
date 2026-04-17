---
name: "springboot-security"
description: >
  Spring Boot security: Spring Security 6.x, JWT, OAuth2, CORS, rate limiting,
  and secrets management. Activate for Spring Boot security work.
metadata:
  version: 1.0.0
  category: engineering
---

# Spring Boot Security Skill

## Spring Security 6.x Configuration

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)  // API — CSRF via JWT
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}
```

## JWT Filter

```java
@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {
    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        String header = req.getHeader("Authorization");
        if (header == null || !header.startsWith("Bearer ")) {
            chain.doFilter(req, res);
            return;
        }
        String token = header.substring(7);
        String username = jwtService.extractUsername(token);
        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = userDetailsService.loadUserByUsername(username);
            if (jwtService.isValid(token, userDetails)) {
                UsernamePasswordAuthenticationToken auth =
                    new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        }
        chain.doFilter(req, res);
    }
}
```

## Method-Level Security

```java
@Service
public class UserService {
    @PreAuthorize("hasRole('ADMIN') or #id == authentication.principal.id")
    public UserResponse getUser(String id) { ... }

    @PreAuthorize("hasRole('ADMIN')")
    public void deleteUser(String id) { ... }
}
```

## CORS

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://myapp.example.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
    config.setMaxAge(3600L);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
```

## Secrets Management

```yaml
# application.yml — no secrets
spring:
  datasource:
    url: ${DATABASE_URL}
    username: ${DB_USER}
    password: ${DB_PASSWORD}

app:
  jwt-secret: ${JWT_SECRET}
```

## Security Checklist

- [ ] Passwords hashed with BCrypt (cost ≥ 12)
- [ ] JWT signed with RS256 or HS512 with a strong secret (≥256 bits)
- [ ] HTTPS enforced (`server.ssl.enabled=true` or behind proxy)
- [ ] Sensitive endpoints require authentication
- [ ] No secrets in `application.properties`/`application.yml`
- [ ] Actuator endpoints restricted (`management.endpoints.web.exposure.include=health,info`)
- [ ] CORS origin whitelist is explicit (not `*` in production)
