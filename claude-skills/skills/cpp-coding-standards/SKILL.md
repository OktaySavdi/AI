---
name: "cpp-coding-standards"
description: >
  C++ coding standards from C++ Core Guidelines: modern C++17/20 idioms, RAII,
  smart pointers, const-correctness, and safe patterns. Activate for C++ code.
metadata:
  version: 1.0.0
  category: engineering
---

# C++ Coding Standards Skill

## Core Principles

- Prefer RAII — resources managed by objects, not manual new/delete
- Prefer stack allocation over heap allocation
- Use smart pointers; never raw owning pointers
- Const-correctness on all functions and parameters that don't mutate

## Resource Management (RAII)

```cpp
// WRONG — manual resource management
void process(const std::string& path) {
    FILE* f = fopen(path.c_str(), "r");
    // ... if exception thrown, f is leaked
    fclose(f);
}

// CORRECT — RAII with ifstream
void process(const std::string& path) {
    std::ifstream f(path);
    if (!f) throw std::runtime_error("Cannot open: " + path);
    // f closes automatically at end of scope
}
```

## Smart Pointers

```cpp
// Unique ownership
auto widget = std::make_unique<Widget>(params);

// Shared ownership (use sparingly — prefer unique_ptr)
auto shared = std::make_shared<Config>(settings);

// Non-owning observer
void render(const Widget* widget);  // raw pointer = non-owning observer
```

Never use `new`/`delete` directly. Always `make_unique` or `make_shared`.

## Const Correctness

```cpp
class UserService {
public:
    // Const member functions don't mutate state
    std::optional<User> findById(const std::string& id) const;

    // Non-const mutation function
    void updateEmail(const std::string& id, std::string email);

private:
    mutable std::mutex mutex_;  // mutable: lock in const functions
};
```

## Error Handling

```cpp
// Prefer std::expected (C++23) or outcome/result patterns
std::expected<User, std::string> loadUser(const std::string& id) {
    if (id.empty()) return std::unexpected("id cannot be empty");
    // ...
}

// Or use exceptions for truly exceptional conditions
struct UserNotFound : std::runtime_error {
    explicit UserNotFound(const std::string& id)
        : std::runtime_error("User not found: " + id) {}
};
```

## Move Semantics

```cpp
class Buffer {
public:
    Buffer(Buffer&& other) noexcept
        : data_(std::exchange(other.data_, nullptr))
        , size_(std::exchange(other.size_, 0)) {}

    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = std::exchange(other.data_, nullptr);
            size_ = std::exchange(other.size_, 0);
        }
        return *this;
    }
};
```

## Containers

```cpp
// Prefer std::vector for sequences
std::vector<int> nums{1, 2, 3};
nums.reserve(expected_size);  // pre-allocate if size known

// Range-based for (always)
for (const auto& item : container) { /* ... */ }

// Structured bindings (C++17)
for (const auto& [key, value] : map) { /* ... */ }
```

## Tools

```bash
clang-tidy --checks='cppcoreguidelines-*,modernize-*' src/
clang-format -i src/**/*.cpp src/**/*.h
valgrind --leak-check=full ./tests
address_sanitizer: -fsanitize=address,undefined
```
