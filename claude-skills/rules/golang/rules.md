# Go Rules

Language-specific rules for Go development. Extends `common/` rules.

## Formatting and Style

- **Formatter**: `gofmt` / `goimports` (non-negotiable, run on save)
- **Linter**: `golangci-lint` with `errcheck`, `govet`, `staticcheck`, `gosec`
- Go version: 1.21+ for new projects
- Package naming: short, lowercase, single word — no underscores

## Error Handling

Always wrap errors with context:

```go
// WRONG
return err

// CORRECT
return fmt.Errorf("fetch user %s: %w", userID, err)
```

Never ignore errors:
```go
// WRONG
os.Remove(tmpFile)

// CORRECT
if err := os.Remove(tmpFile); err != nil {
    log.Printf("cleanup failed: %v", err)
}
```

## Interfaces

Define interfaces at the point of use (consumer), not the producer:

```go
// In the package that needs it
type UserStore interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}
```

## Context

Always pass `context.Context` as first parameter:

```go
func FetchUser(ctx context.Context, id string) (*User, error)
```

Never store context in a struct — pass it explicitly.

## Goroutines

```go
// Always handle goroutine lifecycle
func startWorker(ctx context.Context, jobs <-chan Job) {
    for {
        select {
        case <-ctx.Done():
            return
        case job, ok := <-jobs:
            if !ok {
                return
            }
            process(job)
        }
    }
}
```

## Testing

- Table-driven tests for all public functions
- `testify/assert` for assertions (or stdlib `t.Errorf`)
- Run with `-race` flag in CI

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name  string
        email string
        want  bool
    }{
        {"valid", "user@example.com", true},
        {"empty", "", false},
        {"no at", "notanemail", false},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := ValidateEmail(tt.email)
            if got != tt.want {
                t.Errorf("ValidateEmail(%q) = %v, want %v", tt.email, got, tt.want)
            }
        })
    }
}
```

## Tools

```bash
go vet ./...
golangci-lint run
go test -race -cover ./...
gosec ./...
```
