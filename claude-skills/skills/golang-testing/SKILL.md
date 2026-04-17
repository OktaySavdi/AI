---
name: "golang-testing"
description: >
  Go testing patterns: table-driven tests, benchmarks, mocks, integration tests,
  fuzz testing, and TDD workflow. Activate for any Go test writing or review.
metadata:
  version: 1.0.0
  category: engineering
---

# Golang Testing Skill

## Test File Structure

```go
package mypackage_test  // black-box testing preferred

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)
```

Use `require` for fatal assertions, `assert` for non-fatal:
```go
result, err := DoThing(input)
require.NoError(t, err)      // stops test on failure
assert.Equal(t, want, result) // continues on failure
```

## Table-Driven Tests

```go
func TestAdd(t *testing.T) {
    t.Parallel()
    tests := []struct {
        name string; a, b, want int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
    }
    for _, tt := range tests {
        tt := tt // capture range variable
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            assert.Equal(t, tt.want, Add(tt.a, tt.b))
        })
    }
}
```

## Mocking with Interfaces

```go
type MockUserRepo struct {
    mock.Mock
}
func (m *MockUserRepo) FindByID(ctx context.Context, id string) (*User, error) {
    args := m.Called(ctx, id)
    return args.Get(0).(*User), args.Error(1)
}

// In test
repo := new(MockUserRepo)
repo.On("FindByID", mock.Anything, "123").Return(&User{ID: "123"}, nil)
svc := NewService(repo)
```

## Benchmarks

```go
func BenchmarkProcess(b *testing.B) {
    data := makeTestData()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

Run: `go test -bench=. -benchmem ./...`

## Fuzz Testing (Go 1.18+)

```go
func FuzzParse(f *testing.F) {
    f.Add("valid-input")
    f.Add("")
    f.Fuzz(func(t *testing.T, input string) {
        // Must not panic
        _ = Parse(input)
    })
}
```

## Integration Tests

Tag with build tags or naming convention:
```go
//go:build integration

func TestDatabaseIntegration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }
    // use real DB via testcontainers
}
```

## Test Helpers

```go
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("postgres", testDSN)
    require.NoError(t, err)
    t.Cleanup(func() { db.Close() })
    return db
}
```

## Commands

```bash
go test ./...                    # all tests
go test -race ./...              # race condition detection
go test -cover ./...             # coverage
go test -run TestValidate ./...  # specific test
go test -bench=. -benchmem ./... # benchmarks
go test -short ./...             # skip slow tests
```
