---
name: "golang-patterns"
description: >
  Go idioms and best practices: error handling, interfaces, goroutines, channels,
  context propagation, testing. Activate for any Go development task.
metadata:
  version: 1.0.0
  category: engineering
---

# Golang Patterns Skill

## Error Handling

Always wrap with context:
```go
// WRONG
return err
// CORRECT
return fmt.Errorf("fetch user %s: %w", id, err)
```

Sentinel errors and custom types:
```go
var ErrNotFound = errors.New("not found")

type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation: %s: %s", e.Field, e.Message)
}
```

## Interfaces

Define at the point of use (consumer side):
```go
// In the package that USES storage — not in the storage package
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, u *User) error
}
```

Keep interfaces small — prefer 1-2 methods:
```go
type Reader interface { Read([]byte) (int, error) }
type Writer interface { Write([]byte) (int, error) }
type ReadWriter interface { Reader; Writer }
```

## Context Propagation

Always first parameter, never stored in struct:
```go
func (s *Service) GetUser(ctx context.Context, id string) (*User, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    return s.repo.FindByID(ctx, id)
}
```

## Goroutines and Channels

Always handle lifecycle:
```go
func startWorker(ctx context.Context, jobs <-chan Job) {
    for {
        select {
        case <-ctx.Done():
            return
        case job, ok := <-jobs:
            if !ok { return }
            processJob(job)
        }
    }
}
```

Use `sync.WaitGroup` for fan-out:
```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(i Item) {
        defer wg.Done()
        process(i)
    }(item)
}
wg.Wait()
```

## Structs and Constructors

```go
type Config struct {
    Host    string
    Port    int
    Timeout time.Duration
}

func NewConfig(host string, port int) *Config {
    return &Config{
        Host:    host,
        Port:    port,
        Timeout: 30 * time.Second, // sensible default
    }
}
```

## Table-Driven Tests

```go
func TestValidate(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        wantErr bool
    }{
        {"valid", "user@example.com", false},
        {"empty", "", true},
        {"no-at", "notanemail", true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := Validate(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("Validate(%q) error = %v, wantErr = %v", tt.input, err, tt.wantErr)
            }
        })
    }
}
```

## Anti-Patterns

- `init()` functions with side effects — use explicit initialization
- Global mutable state — pass through function arguments
- `interface{}` / `any` without type assertion guards
- Goroutines that can never be cancelled or joined
- Returning error AND logging it — pick one

## Tools

```bash
go vet ./...
golangci-lint run
go test -race -cover ./...
gosec ./...
```
