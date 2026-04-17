# Go Build Fix

Invoke the `go-build-resolver` agent to fix Go compilation or test errors.

## Usage

```
/go-build
```

Paste the error output after invoking.

## Common Go Errors

```bash
# Module issues
go mod tidy
go mod download

# Verbose build for missing packages
go build -v ./...

# Race detector
go test -race ./...
```

## Quick Checks

```bash
go vet ./...              # static analysis
golangci-lint run         # comprehensive linting
go build ./...            # compilation check without tests
```
