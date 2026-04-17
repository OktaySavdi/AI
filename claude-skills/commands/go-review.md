# Go Review

Invoke the `go-reviewer` agent for a Go-specific code review.

## Usage

```
/go-review
```

Then provide the file path or paste the Go code to review.

## Covers

- Error handling (wrapped with context, not bare `return err`)
- Idiomatic Go (no Java-style abstractions, interfaces only when needed)
- Goroutine safety (no data races, proper channel usage)
- Context propagation
- Test coverage and table-driven tests

## Quick Reference

```go
// Idiomatic error wrapping
if err != nil {
    return fmt.Errorf("operation failed: %w", err)
}

// Table-driven tests
func TestFoo(t *testing.T) {
    tests := []struct { name, input, want string }{
        {"empty", "", ""},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Foo(tt.input)
            if got != tt.want {
                t.Errorf("got %q, want %q", got, tt.want)
            }
        })
    }
}
```
